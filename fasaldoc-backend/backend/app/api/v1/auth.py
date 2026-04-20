"""
Authentication endpoints: phone-number-based register and login.
Designed for Indian farmers — no email required, just phone + password.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import PhoneAlreadyRegisteredError, InvalidCredentialsError
from app.dependencies import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse

router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new farmer account",
)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Register with Indian phone number, name, region, and password.
    Returns a JWT access token on success.

    Args:
        body: RegisterRequest with phone, name, region, language, primary_crops, password.
        db: Async DB session.
    Returns:
        TokenResponse with access_token and user metadata.
    Raises:
        409: Phone number already registered.
    """
    # Check duplicate phone
    existing = await db.execute(select(User).where(User.phone == body.phone))
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "PHONE_ALREADY_REGISTERED",
                "message": f"Phone number {body.phone} is already registered.",
                "detail": {},
            },
        )

    user = User(
        phone=body.phone,
        name=body.name,
        region=body.region,
        language=body.language,
        primary_crops=body.primary_crops,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(
        subject=str(user.id),
        extra_claims={"region": user.region, "lang": user.language},
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        name=user.name,
        region=user.region,
        language=user.language,
    )


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="Login with phone number and password",
)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login with Indian phone number and password.
    Returns a JWT with 7-day expiry.

    Args:
        body: LoginRequest with phone and password.
        db: Async DB session.
    Returns:
        TokenResponse with access_token.
    Raises:
        401: Invalid phone or password.
    """
    result = await db.execute(select(User).where(User.phone == body.phone))
    user = result.scalars().first()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid phone number or password.",
                "detail": {},
            },
        )

    token = create_access_token(
        subject=str(user.id),
        extra_claims={"region": user.region, "lang": user.language},
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=str(user.id),
        name=user.name,
        region=user.region,
        language=user.language,
    )
