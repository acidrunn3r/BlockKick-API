from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChallengeRequest(BaseModel):
    wallet_address: str = Field(
        ...,
        pattern=r"^[a-fA-F0-9]{64}$",
        description="Ed25519 public key in hexadecimal format (64 characters)",
    )


class ChallengeResponse(BaseModel):
    nonce: str = Field(..., description="One-time cryptographic challenge")
    expires_at: datetime = Field(..., description="Timestamp when the nonce expires")


class LoginRequest(BaseModel):
    wallet_address: str = Field(
        ...,
        pattern=r"^[a-fA-F0-9]{64}$",
        description="Ed25519 public key that signed the message",
    )
    nonce: str = Field(..., description="The nonce received from /auth/challenge")
    signature: str = Field(
        ...,
        min_length=128,
        max_length=128,
        description="Ed25519 signature in hex format (64 bytes = 128 hex chars)",
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = Field(..., description="Access token lifetime in seconds")


class RefreshRequest(BaseModel):
    """Request model for token refresh endpoint."""

    refresh_token: str = Field(
        ..., description="Valid refresh token issued by /auth/login"
    )


class UserMeResponse(BaseModel):
    """Response model for current user profile."""

    wallet_address: str = Field(
        ...,
        pattern=r"^[a-fA-F0-9]{64}$",
        description="Ed25519 public key in hexadecimal format",
    )
    display_name: str = Field(..., description="User's public display name")
    bio: str = Field(default="", description="Short biography or description")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "wallet_address": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
                "display_name": "User_a1b2c3",
                "bio": "Blockchain enthusiast",
            }
        }
    )
