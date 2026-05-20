import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, func
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


class IndexedTransaction(Base):
    """Transaction record indexed from the blockchain node."""

    __tablename__ = "indexed_transactions"

    tx_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
        index=True,
        comment="SHA-256 of canonical tx JSON",
    )
    tx_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="Transfer | CreateProject | FundProject | Coinbase",
    )
    from_address: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    to_address: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    amount: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    project_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    block_height: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    timestamp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    raw_data: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<IndexedTransaction(id='{self.tx_id[:8]}...', type='{self.tx_type}')>"
