from datetime import UTC, datetime, timedelta
from typing import Any, cast

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.config import settings


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Generate a short-lived JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return cast(
        str,
        jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM),
    )


def create_refresh_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Generate a long-lived JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return cast(
        str,
        jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token.

    Raises:
        HTTPException: 401 if token is invalid, expired, or malformed.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return cast(dict[str, Any], payload)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        ) from e
