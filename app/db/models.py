import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):  # type: ignore[misc]
    """Base class for all SQLAlchemy models."""

    pass


class User(Base):
    """User profile linked to a blockchain wallet."""

    __tablename__ = "users"

    wallet_address: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        index=True,
        comment="Hex-encoded Ed25519 public key (64 chars)",
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str] = mapped_column(Text, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<User(wallet='{self.wallet_address[:8]}...', name='{self.display_name}')>"
        )


class AuthNonce(Base):
    """One-time cryptographic nonce for wallet authentication."""

    __tablename__ = "auth_nonces"

    nonce: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="Unique challenge string",
    )
    wallet_address: Mapped[str] = mapped_column(
        String(64),
        index=True,
        nullable=False,
        comment="Wallet address this nonce is bound to",
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    def __repr__(self) -> str:
        return f"<AuthNonce(nonce='{self.nonce[:8]}...', used={self.used})>"
