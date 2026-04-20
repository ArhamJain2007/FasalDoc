"""
Shared FastAPI dependency injection: DB session, authenticated user.
"""
from uuid import UUID

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.user import User

logger = structlog.get_logger()
bearer_scheme = HTTPBearer()


async def get_db() -> AsyncSession:
    """Yield an async database session per request."""
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Decode JWT from Authorization header and return the matching User.

    Args:
        credentials: Bearer token from Authorization header.
        db: Async DB session.
    Returns:
        Authenticated User ORM instance.
    Raises:
        HTTPException 401: If token is missing, expired, or invalid.
        HTTPException 401: If user referenced in token no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "UNAUTHORIZED", "message": "Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = UUID(user_id_str)
    except (JWTError, ValueError) as exc:
        logger.warning("JWT decode failed", error=str(exc))
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception

    return user
