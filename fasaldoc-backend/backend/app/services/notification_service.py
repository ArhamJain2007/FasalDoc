"""
FCM notification service using firebase-admin SDK.
Supports single-device and regional broadcast (batches of 500).
"""
import asyncio
import structlog
from concurrent.futures import ThreadPoolExecutor

import firebase_admin
from firebase_admin import credentials, messaging

from app.config import settings

logger = structlog.get_logger()
_executor = ThreadPoolExecutor(max_workers=2)
_firebase_initialized = False


def _chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


class NotificationService:
    """
    Wraps firebase-admin messaging with async support.
    Initialized once at application startup.
    """

    @classmethod
    def init(cls) -> None:
        """
        Initialize the Firebase Admin SDK.
        Must be called once before sending any notifications.
        Side effects: Initializes global firebase_admin app.
        """
        global _firebase_initialized
        if _firebase_initialized:
            return
        try:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            _firebase_initialized = True
            logger.info("firebase_initialized")
        except Exception as exc:
            logger.warning("firebase_init_failed", error=str(exc))

    def _send_sync(
        self,
        token: str,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> str | None:
        """
        Blocking FCM single-device send. Runs in thread pool.

        Args:
            token: FCM registration token.
            title: Notification title.
            body: Notification body text.
            data: Optional dict of string key-value pairs.
        Returns:
            FCM message ID string, or None on failure.
        """
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={k: str(v) for k, v in (data or {}).items()},
            token=token,
            android=messaging.AndroidConfig(priority="high"),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound="default")
                )
            ),
        )
        try:
            response = messaging.send(message)
            logger.info("fcm_sent", message_id=response, token_prefix=token[:10])
            return response
        except Exception as exc:
            logger.error("fcm_failed", error=str(exc), token_prefix=token[:10])
            return None

    async def send_alert(
        self,
        token: str,
        title: str,
        body: str,
        data: dict | None = None,
    ) -> str | None:
        """
        Async FCM single-device push notification.

        Args:
            token: FCM registration token.
            title: Notification title.
            body: Notification body text.
            data: Optional dict of extra data (values coerced to str).
        Returns:
            FCM message ID on success, None on failure.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor, self._send_sync, token, title, body, data
        )

    def _multicast_sync(
        self,
        tokens: list[str],
        title: str,
        body: str,
    ) -> int:
        """
        Blocking FCM multicast send for up to 500 tokens.

        Args:
            tokens: List of FCM registration tokens (max 500).
            title: Notification title.
            body: Notification body text.
        Returns:
            Number of successfully delivered messages.
        """
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            tokens=tokens,
            android=messaging.AndroidConfig(priority="high"),
        )
        try:
            result = messaging.send_each_for_multicast(message)
            logger.info(
                "fcm_multicast_sent",
                success=result.success_count,
                failure=result.failure_count,
            )
            return result.success_count
        except Exception as exc:
            logger.error("fcm_multicast_failed", error=str(exc))
            return 0

    async def broadcast_region(
        self,
        tokens: list[str],
        title: str,
        body: str,
    ) -> int:
        """
        Send FCM push to all tokens in a region, batching 500 at a time.

        Args:
            tokens: All FCM tokens for the target region.
            title: Notification title (already localized).
            body: Notification body (already localized).
        Returns:
            Total number of successfully delivered messages.
        Side effects:
            Sends FCM messages to all provided tokens.
        """
        loop = asyncio.get_event_loop()
        total_success = 0
        for batch in _chunks(tokens, 500):
            success = await loop.run_in_executor(
                _executor, self._multicast_sync, batch, title, body
            )
            total_success += success
        return total_success
