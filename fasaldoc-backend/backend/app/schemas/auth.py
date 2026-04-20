import re
from pydantic import BaseModel, field_validator, Field
from typing import Literal

INDIAN_PHONE_RE = re.compile(r"^[6-9]\d{9}$")


class RegisterRequest(BaseModel):
    phone: str = Field(..., description="Indian mobile number (10 digits, starting 6-9)")
    name: str = Field(..., min_length=2, max_length=100)
    region: str = Field(..., min_length=2, max_length=100)
    language: Literal["en", "hi", "pa"] = "en"
    primary_crops: list[str] = Field(default_factory=list)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip().lstrip("+91").lstrip("0")
        if not INDIAN_PHONE_RE.match(v):
            raise ValueError(
                "Phone must be a valid Indian mobile number (10 digits, starting with 6-9)"
            )
        return v


class LoginRequest(BaseModel):
    phone: str
    password: str

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        return v.strip().lstrip("+91").lstrip("0")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int             # seconds
    user_id: str
    name: str
    region: str
    language: str


class UserResponse(BaseModel):
    id: str
    phone: str
    name: str
    region: str
    language: str
    primary_crops: list[str]
