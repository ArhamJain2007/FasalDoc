from functools import lru_cache

import os
from pydantic_settings import BaseSettings   # or from pydantic import BaseSettings (depending on your setup)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
print("CONFIG BASE DIR:", BASE_DIR)
class Settings(BaseSettings):
    MODEL_PATH: str = os.path.join(BASE_DIR, "models", "plant_disease_efficientnet.keras")
    TFLITE_MODEL_PATH: str = os.path.join(BASE_DIR, "models", "plant_disease.tflite")

    MODEL_INPUT_SIZE: int = 224
    CONFIDENCE_THRESHOLD: float = 0.5

    # App
    APP_NAME: str = "FasalDoc API"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Database
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET: str
    AWS_REGION: str = "ap-south-1"

    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"

    # Weather API
    WEATHER_API_KEY: str
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
