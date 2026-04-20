"""
Alert service: fetches weather data and computes disease risk alerts
for a farmer's region using known disease-weather correlations.
"""
from __future__ import annotations

import structlog
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.alert import Alert
from app.models.disease import Disease
from app.schemas.history import AlertResponse
from app.core.exceptions import WeatherAPIError

logger = structlog.get_logger()

WEATHER_CACHE_TTL = 3600  # 1 hour


class WeatherData(BaseModel):
    humidity: float            # percent (0-100)
    temp_max: float            # Celsius
    temp_min: float            # Celsius
    description: str


# Disease-weather trigger rules: (disease_id, metric, operator, threshold)
DISEASE_WEATHER_RULES: list[tuple[str, str, str, float]] = [
    ("wheat_brown_rust",    "humidity", ">", 80.0),
    ("tomato_late_blight",  "humidity", ">", 85.0),
    ("tomato_early_blight", "temp_max", ">", 30.0),
    ("rice_leaf_blast",     "humidity", ">", 90.0),
    ("rice_neck_blast",     "humidity", ">", 90.0),
    ("potato_late_blight",  "humidity", ">", 85.0),
    ("rice_brown_spot",     "humidity", ">", 80.0),
    ("corn_common_rust",    "humidity", ">", 75.0),
]

# Alert text templates
ALERT_TEMPLATES: dict[str, dict[str, dict[str, str]]] = {
    "wheat_brown_rust": {
        "en": {
            "title": "⚠️ Wheat Brown Rust Risk - High Humidity",
            "body": "Humidity is above 80%. Brown rust risk is high for wheat. Apply Propiconazole 25% EC (1 mL/L) as preventive spray.",
        },
        "hi": {
            "title": "⚠️ गेहूं भूरा किट्ट का खतरा - अधिक नमी",
            "body": "नमी 80% से अधिक है। गेहूं के लिए भूरा किट्ट का खतरा अधिक है। बचाव के लिए प्रोपिकोनाज़ोल 25% EC (1 mL/L) का छिड़काव करें।",
        },
        "pa": {
            "title": "⚠️ ਕਣਕ ਭੂਰਾ ਕਿੱਟ ਦਾ ਖਤਰਾ - ਵਧੇਰੇ ਨਮੀ",
            "body": "ਨਮੀ 80% ਤੋਂ ਵੱਧ ਹੈ। ਕਣਕ ਲਈ ਭੂਰੇ ਕਿੱਟ ਦਾ ਖਤਰਾ ਵਧੇਰੇ ਹੈ। ਪ੍ਰੋਪੀਕੋਨਾਜ਼ੋਲ 25% EC (1 mL/L) ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
        },
    },
    "tomato_late_blight": {
        "en": {
            "title": "🔴 Tomato Late Blight Alert - Danger Level",
            "body": "Humidity exceeds 85%. Conditions are ideal for late blight. Apply Metalaxyl + Mancozeb immediately.",
        },
        "hi": {
            "title": "🔴 टमाटर पछेती झुलसा चेतावनी - खतरनाक स्तर",
            "body": "नमी 85% से अधिक है। पछेती झुलसे के लिए अनुकूल परिस्थितियां। तत्काल मेटालैक्सिल + मैन्कोज़ेब का छिड़काव करें।",
        },
        "pa": {
            "title": "🔴 ਟਮਾਟਰ ਪਛੇਤੀ ਝੁਲਸ ਚੇਤਾਵਨੀ - ਖਤਰੇ ਦਾ ਪੱਧਰ",
            "body": "ਨਮੀ 85% ਤੋਂ ਵੱਧ ਹੈ। ਮੇਟਾਲੈਕਸਿਲ + ਮੈਨਕੋਜ਼ੇਬ ਦਾ ਤੁਰੰਤ ਛਿੜਕਾਅ ਕਰੋ।",
        },
    },
    "tomato_early_blight": {
        "en": {
            "title": "🟡 Tomato Early Blight Warning - High Temperature",
            "body": "Maximum temperature above 30°C. Early blight conditions are favorable. Monitor crops and apply Mancozeb if symptoms appear.",
        },
        "hi": {
            "title": "🟡 टमाटर अगेती झुलसा चेतावनी - अधिक तापमान",
            "body": "अधिकतम तापमान 30°C से अधिक है। फसल की निगरानी करें और लक्षण दिखने पर मैन्कोज़ेब का छिड़काव करें।",
        },
        "pa": {
            "title": "🟡 ਟਮਾਟਰ ਅਗੇਤੀ ਝੁਲਸ ਚੇਤਾਵਨੀ - ਵਧੇਰੇ ਤਾਪਮਾਨ",
            "body": "ਵੱਧ ਤੋਂ ਵੱਧ ਤਾਪਮਾਨ 30°C ਤੋਂ ਵੱਧ ਹੈ। ਮੈਨਕੋਜ਼ੇਬ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
        },
    },
    "rice_leaf_blast": {
        "en": {
            "title": "🔴 Rice Leaf Blast Alert - Extreme Humidity",
            "body": "Humidity above 90% creates prime conditions for leaf blast. Apply Tricyclazole 75% WP immediately.",
        },
        "hi": {
            "title": "🔴 चावल पत्ती झुलसा चेतावनी - अत्यधिक नमी",
            "body": "90% से अधिक नमी पत्ती झुलसे के लिए अनुकूल है। तत्काल ट्राइसाइक्लाज़ोल 75% WP का छिड़काव करें।",
        },
        "pa": {
            "title": "🔴 ਚਾਵਲ ਪੱਤੀ ਝੁਲਸ ਚੇਤਾਵਨੀ - ਬਹੁਤ ਵੱਧ ਨਮੀ",
            "body": "ਨਮੀ 90% ਤੋਂ ਵੱਧ ਹੈ। ਟਰਾਈਸਾਈਕਲਾਜ਼ੋਲ 75% WP ਦਾ ਤੁਰੰਤ ਛਿੜਕਾਅ ਕਰੋ।",
        },
    },
    "rice_neck_blast": {
        "en": {
            "title": "🔴 Rice Neck Blast Alert - Extreme Humidity",
            "body": "Humidity above 90%. Neck blast risk is critical at flowering stage. Apply Isoprothiolane 40% EC.",
        },
        "hi": {
            "title": "🔴 चावल गर्दन झुलसा चेतावनी",
            "body": "नमी 90% से अधिक। फूल आने पर गर्दन झुलसे का खतरा। आइसोप्रोथिओलेन 40% EC का छिड़काव करें।",
        },
        "pa": {
            "title": "🔴 ਚਾਵਲ ਗਰਦਨ ਝੁਲਸ ਚੇਤਾਵਨੀ",
            "body": "ਨਮੀ 90% ਤੋਂ ਵੱਧ। ਆਈਸੋਪ੍ਰੋਥਿਓਲੇਨ 40% EC ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
        },
    },
    "potato_late_blight": {
        "en": {
            "title": "🔴 Potato Late Blight Danger Alert",
            "body": "Humidity above 85%. Potato late blight can destroy entire fields within days. Apply Cymoxanil + Mancozeb immediately.",
        },
        "hi": {
            "title": "🔴 आलू पछेती झुलसा खतरा",
            "body": "नमी 85% से अधिक। पछेती झुलसा कुछ दिनों में पूरी फसल नष्ट कर सकता है। साइमोक्सानिल + मैन्कोज़ेब का तत्काल छिड़काव करें।",
        },
        "pa": {
            "title": "🔴 ਆਲੂ ਪਛੇਤੀ ਝੁਲਸ ਖਤਰਾ",
            "body": "ਨਮੀ 85% ਤੋਂ ਵੱਧ। ਸਾਈਮੋਕਸਾਨਿਲ + ਮੈਨਕੋਜ਼ੇਬ ਦਾ ਤੁਰੰਤ ਛਿੜਕਾਅ ਕਰੋ।",
        },
    },
    "rice_brown_spot": {
        "en": {
            "title": "🟡 Rice Brown Spot Warning - High Humidity",
            "body": "Humidity above 80% favors brown spot development. Apply Propiconazole 25% EC as preventive measure.",
        },
        "hi": {
            "title": "🟡 चावल भूरा धब्बा चेतावनी",
            "body": "नमी 80% से अधिक। बचाव के लिए प्रोपिकोनाज़ोल 25% EC का छिड़काव करें।",
        },
        "pa": {
            "title": "🟡 ਚਾਵਲ ਭੂਰਾ ਧੱਬਾ ਚੇਤਾਵਨੀ",
            "body": "ਨਮੀ 80% ਤੋਂ ਵੱਧ। ਪ੍ਰੋਪੀਕੋਨਾਜ਼ੋਲ 25% EC ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
        },
    },
    "corn_common_rust": {
        "en": {
            "title": "🟡 Corn Common Rust Warning",
            "body": "High humidity detected. Monitor corn leaves for rust pustules. Apply Mancozeb 75% WP if spots appear.",
        },
        "hi": {
            "title": "🟡 मक्का सामान्य किट्ट चेतावनी",
            "body": "अधिक नमी है। मक्के की पत्तियों पर किट्ट के pustules की जांच करें। लक्षण दिखने पर मैन्कोज़ेब का छिड़काव करें।",
        },
        "pa": {
            "title": "🟡 ਮੱਕੀ ਸਾਧਾਰਨ ਕਿੱਟ ਚੇਤਾਵਨੀ",
            "body": "ਵਧੇਰੇ ਨਮੀ ਹੈ। ਮੱਕੀ ਦੀਆਂ ਪੱਤੀਆਂ ਦੀ ਜਾਂਚ ਕਰੋ। ਮੈਨਕੋਜ਼ੇਬ ਦਾ ਛਿੜਕਾਅ ਕਰੋ।",
        },
    },
}

ALERT_TYPE_MAP: dict[str, str] = {
    "tomato_late_blight": "danger",
    "rice_leaf_blast": "danger",
    "rice_neck_blast": "danger",
    "potato_late_blight": "danger",
    "wheat_brown_rust": "warning",
    "tomato_early_blight": "warning",
    "rice_brown_spot": "warning",
    "corn_common_rust": "info",
}


class AlertService:
    def __init__(self, redis_client) -> None:
        self._redis = redis_client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        reraise=True,
    )
    async def fetch_weather(self, region: str) -> WeatherData:
        """
        Fetch current weather for a region from OpenWeatherMap.
        Results are cached in Redis for 1 hour to minimize API calls.

        Args:
            region: Indian region/city name (e.g. "Punjab", "Delhi NCR").
        Returns:
            WeatherData with humidity and temperature info.
        Raises:
            WeatherAPIError: If API call fails after 3 retries.
        Side effects:
            Caches result in Redis with 1-hour TTL.
        """
        cache_key = f"weather:{region}"

        cached = await self._redis.get(cache_key)
        if cached:
            logger.debug("weather_cache_hit", region=region)
            return WeatherData.model_validate_json(cached)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{settings.WEATHER_API_URL}/weather",
                    params={
                        "q": f"{region},IN",
                        "appid": settings.WEATHER_API_KEY,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except httpx.HTTPError as exc:
            logger.error("weather_api_error", region=region, error=str(exc))
            raise WeatherAPIError(f"Weather API failed for region {region}: {exc}") from exc

        weather = WeatherData(
            humidity=float(data["main"]["humidity"]),
            temp_max=round(data["main"]["temp_max"] - 273.15, 1),
            temp_min=round(data["main"]["temp_min"] - 273.15, 1),
            description=data["weather"][0]["description"],
        )
        await self._redis.setex(cache_key, WEATHER_CACHE_TTL, weather.model_dump_json())
        logger.info("weather_fetched", region=region, humidity=weather.humidity, temp_max=weather.temp_max)
        return weather

    def _threshold_met(self, weather: WeatherData, metric: str, operator: str, threshold: float) -> bool:
        """
        Evaluate whether a weather metric meets a disease-trigger threshold.

        Args:
            weather: Current weather data.
            metric: "humidity" | "temp_max" | "temp_min".
            operator: ">" | "<" | ">=" | "<=".
            threshold: Numeric threshold value.
        Returns:
            True if the threshold condition is met.
        """
        value = getattr(weather, metric, None)
        if value is None:
            return False
        if operator == ">":
            return value > threshold
        if operator == ">=":
            return value >= threshold
        if operator == "<":
            return value < threshold
        if operator == "<=":
            return value <= threshold
        return False

    async def compute_alerts(
        self,
        region: str,
        language: str,
        db: AsyncSession,
    ) -> list[AlertResponse]:
        """
        Evaluate disease-weather rules for a region and return triggered alerts.
        Creates or updates Alert records in DB for triggered conditions.

        Args:
            region: Indian region name.
            language: ISO language code for response localization.
            db: Async DB session.
        Returns:
            List of AlertResponse objects for triggered disease risks.
        Side effects:
            May insert new Alert rows into the DB.
        """
        try:
            weather = await self.fetch_weather(region)
        except WeatherAPIError:
            logger.warning("weather_fetch_failed_returning_empty", region=region)
            return []

        triggered: list[AlertResponse] = []

        for disease_id, metric, operator, threshold in DISEASE_WEATHER_RULES:
            if not self._threshold_met(weather, metric, operator, threshold):
                continue

            templates = ALERT_TEMPLATES.get(disease_id, {})
            lang_template = templates.get(language, templates.get("en", {}))
            if not lang_template:
                continue

            alert_type = ALERT_TYPE_MAP.get(disease_id, "info")
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            en_t = templates.get("en", lang_template)
            hi_t = templates.get("hi", lang_template)
            pa_t = templates.get("pa", lang_template)

            # Upsert Alert in DB
            existing = await db.execute(
                select(Alert).where(
                    Alert.region == region,
                    Alert.related_disease_id == disease_id,
                    Alert.expires_at > datetime.now(timezone.utc),
                )
            )
            alert_row = existing.scalars().first()

            if not alert_row:
                alert_row = Alert(
                    region=region,
                    alert_type=alert_type,
                    title_en=en_t.get("title", ""),
                    title_hi=hi_t.get("title", ""),
                    title_pa=pa_t.get("title", ""),
                    body_en=en_t.get("body", ""),
                    body_hi=hi_t.get("body", ""),
                    body_pa=pa_t.get("body", ""),
                    related_disease_id=disease_id,
                    expires_at=expires_at,
                )
                db.add(alert_row)
                await db.flush()

            title = lang_template.get("title", en_t.get("title", ""))
            body = lang_template.get("body", en_t.get("body", ""))

            triggered.append(
                AlertResponse(
                    alert_id=str(alert_row.id),
                    region=region,
                    alert_type=alert_type,
                    title=title,
                    body=body,
                    related_disease_id=disease_id,
                    expires_at=expires_at.isoformat(),
                )
            )

        if triggered:
            await db.commit()

        logger.info("alerts_computed", region=region, count=len(triggered))
        return triggered

    async def get_active_alerts(
        self,
        region: str,
        language: str,
        db: AsyncSession,
    ) -> list[AlertResponse]:
        """
        Return currently active (non-expired) alerts for a region from DB.
        Falls back to compute_alerts if no alerts exist.

        Args:
            region: Indian region name.
            language: Language code for localization.
            db: Async DB session.
        Returns:
            List of localized AlertResponse objects.
        """
        result = await db.execute(
            select(Alert).where(
                Alert.region == region,
                Alert.expires_at > datetime.now(timezone.utc),
            ).order_by(Alert.created_at.desc())
        )
        rows = result.scalars().all()

        if not rows:
            return await self.compute_alerts(region, language, db)

        alerts: list[AlertResponse] = []
        for row in rows:
            if language == "hi":
                title, body = row.title_hi, row.body_hi
            elif language == "pa":
                title, body = row.title_pa, row.body_pa
            else:
                title, body = row.title_en, row.body_en

            alerts.append(AlertResponse(
                alert_id=str(row.id),
                region=row.region,
                alert_type=row.alert_type,
                title=title,
                body=body,
                related_disease_id=row.related_disease_id,
                expires_at=row.expires_at.isoformat(),
            ))
        return alerts
