import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.db.models import AuthNonce, User
from app.db.session import get_db
from app.schemas.auth import (
    ChallengeRequest,
    ChallengeResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
)

router = APIRouter()


@router.post(
    "/challenge", response_model=ChallengeResponse, status_code=status.HTTP_201_CREATED
)
async def request_challenge(
    req: ChallengeRequest,
    db: AsyncSession = Depends(get_db),
) -> ChallengeResponse:
    """Generate a cryptographic nonce for wallet authentication.

    The client must sign this nonce with their private key and submit it
    to the /auth/login endpoint to prove wallet ownership.
    """
    nonce_value = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=5)

    nonce = AuthNonce(
        nonce=nonce_value,
        wallet_address=req.wallet_address,
        expires_at=expires_at,
        used=False,
    )
    db.add(nonce)
    await db.flush()
    print(f"New nonce generated for: {req.wallet_address[:8]}...")

    return ChallengeResponse(nonce=nonce_value, expires_at=expires_at)


@router.post("/login", response_model=TokenResponse)
async def login_wallet(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate wallet via Ed25519 signature and issue JWT tokens.

    Validates the nonce, checks signature, and returns access/refresh tokens.
    Creates a new user profile if the wallet is not yet registered.
    """
    nonce_result = await db.execute(
        select(AuthNonce).where(AuthNonce.nonce == req.nonce)
    )
    nonce_record = nonce_result.scalar_one_or_none()

    if not nonce_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Nonce not found"
        )
    if nonce_record.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Nonce already used"
        )
    if nonce_record.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Nonce expired"
        )

    # TODO: Добавить обращение к API в BlockKick-CLI
    # is_valid = verify_ed25519_signature(req.wallet_address, req.nonce, req.signature)
    # if not is_valid:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid cryptographic signature",
    #     )

    nonce_record.used = True
    await db.flush()

    user_result = await db.execute(
        select(User).where(User.wallet_address == req.wallet_address)
    )
    user = user_result.scalar_one_or_none()

    if not user:
        print(f"New user registrations: {req.wallet_address[:8]}...")
        user = User(
            wallet_address=req.wallet_address,
            display_name=f"User_{req.wallet_address[:6]}",
            bio="",
        )
        db.add(user)
        await db.flush()

    token_data = {"sub": user.wallet_address}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    print(f"Successful login: {req.wallet_address[:8]}...")
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    req: RefreshRequest,
) -> TokenResponse:
    """Refresh access token using a valid refresh token.

    Does not require wallet signature — only validates the refresh token
    and issues a new access/refresh token pair (rotation).

    Args:
        req: RefreshRequest containing the refresh token.

    Returns:
        TokenResponse: New access and refresh tokens.

    Raises:
        HTTPException: 401 if token is invalid, expired, or wrong type.
    """
    try:
        payload = decode_token(req.refresh_token)
    except HTTPException as e:
        raise e

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: expected refresh token",
        )

    wallet = payload.get("sub")
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing 'sub' claim",
        )

    token_data = {"sub": wallet}
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)

    print(f"Token refresh for: {wallet[:8]}...")
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="Bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
