from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import UserMeResponse

router = APIRouter()


@router.get("/me", response_model=UserMeResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserMeResponse:
    """Get authenticated user's public profile.

    Requires valid Bearer access token in Authorization header.
    Returns only public fields: wallet address, display name, bio, avatar.

    Args:
        current_user: Injected authenticated user from JWT.

    Returns:
        UserMeResponse: Public profile data.
    """
    return UserMeResponse.model_validate(current_user)


@router.put("/me", response_model=UserMeResponse)
async def update_current_user_profile(
    display_name: str,
    bio: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserMeResponse:
    """Update authenticated user's public profile.

    Only the wallet owner can update their profile (verified via JWT).

    Args:
        display_name: New public display name.
        bio: Short biography or description.
        current_user: Injected authenticated user.
        db: Async database session.

    Returns:
        UserMeResponse: Updated profile data.
    """
    current_user.display_name = display_name
    current_user.bio = bio
    await db.flush()

    print(f"Profile updated: {current_user.wallet_address[:8]}...")
    return UserMeResponse.model_validate(current_user)
