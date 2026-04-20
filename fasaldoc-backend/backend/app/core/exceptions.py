"""
Custom exception classes for FasalDoc API.
All exceptions are mapped to HTTP responses in main.py exception handlers.
"""
from fastapi import HTTPException


class FasalDocException(Exception):
    """Base exception for all FasalDoc application errors."""
    def __init__(self, message: str, detail: dict | None = None):
        self.message = message
        self.detail = detail or {}
        super().__init__(message)


class LowConfidenceError(FasalDocException):
    """Raised when model confidence is below CONFIDENCE_THRESHOLD."""
    pass


class InferenceError(FasalDocException):
    """Raised when ML model inference fails unexpectedly."""
    pass


class ModelNotLoadedError(FasalDocException):
    """Raised when a request arrives before the model has finished loading."""
    pass


class InvalidImageError(FasalDocException):
    """Raised when uploaded file is not a valid image."""
    pass


class FileTooLargeError(FasalDocException):
    """Raised when uploaded image exceeds maximum allowed size."""
    pass


class StorageError(FasalDocException):
    """Raised when S3 upload or download fails."""
    pass


class WeatherAPIError(FasalDocException):
    """Raised when OpenWeatherMap API call fails after retries."""
    pass


class NotificationError(FasalDocException):
    """Raised when FCM push notification delivery fails."""
    pass


class DuplicateScanError(FasalDocException):
    """Raised when syncing an offline record that already exists."""
    pass


class UserNotFoundError(FasalDocException):
    """Raised when queried user does not exist."""
    pass


class InvalidCredentialsError(FasalDocException):
    """Raised when login credentials are invalid."""
    pass


class PhoneAlreadyRegisteredError(FasalDocException):
    """Raised when registering a phone number that already has an account."""
    pass
