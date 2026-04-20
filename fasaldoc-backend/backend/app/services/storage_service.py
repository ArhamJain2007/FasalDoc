"""
S3 storage service for image uploads and downloads.
All images are stored in S3 — never on local disk.
"""
import asyncio
import structlog
from concurrent.futures import ThreadPoolExecutor

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings
from app.core.exceptions import StorageError

logger = structlog.get_logger()

_executor = ThreadPoolExecutor(max_workers=4)


class StorageService:
    """
    Wrapper around boto3 S3 client with async support via thread-pool offloading.
    """

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def _upload_sync(self, data: bytes, key: str, content_type: str) -> str:
        """
        Blocking S3 put_object call. Runs in thread pool.

        Args:
            data: Raw image bytes.
            key: S3 object key (e.g. "scans/user-id/uuid.jpg").
            content_type: MIME type of the image.
        Returns:
            Public HTTPS URL of the uploaded object.
        Raises:
            StorageError: If S3 upload fails.
        """
        try:
            self._client.put_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
            url = (
                f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}"
                f".amazonaws.com/{key}"
            )
            return url
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 upload failed", key=key, error=str(exc))
            raise StorageError(f"S3 upload failed for key {key}: {exc}") from exc

    async def upload(
        self,
        data: bytes,
        key: str,
        content_type: str = "image/jpeg",
    ) -> str:
        """
        Async S3 upload. Offloads blocking boto3 call to thread pool.

        Args:
            data: Raw image bytes.
            key: S3 object key.
            content_type: MIME type string.
        Returns:
            Public HTTPS URL of the stored object.
        Raises:
            StorageError: If the upload fails.
        """
        loop = asyncio.get_event_loop()
        url = await loop.run_in_executor(
            _executor, self._upload_sync, data, key, content_type
        )
        logger.info("S3 upload complete", key=key, url=url)
        return url

    def _download_sync(self, key: str) -> bytes:
        """
        Blocking S3 get_object call.

        Args:
            key: S3 object key.
        Returns:
            Raw bytes of the stored object.
        Raises:
            StorageError: If the download fails.
        """
        try:
            resp = self._client.get_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
            return resp["Body"].read()
        except (BotoCoreError, ClientError) as exc:
            logger.error("S3 download failed", key=key, error=str(exc))
            raise StorageError(f"S3 download failed for key {key}: {exc}") from exc

    async def download(self, key: str) -> bytes:
        """
        Async S3 download.

        Args:
            key: S3 object key.
        Returns:
            Raw bytes of the stored object.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._download_sync, key)

    def _delete_sync(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
        except (BotoCoreError, ClientError) as exc:
            logger.warning("S3 delete failed", key=key, error=str(exc))

    async def delete(self, key: str) -> None:
        """
        Async S3 object deletion.

        Args:
            key: S3 object key to delete.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(_executor, self._delete_sync, key)
