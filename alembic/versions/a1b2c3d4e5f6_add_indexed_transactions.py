"""add indexed_transactions table

Revision ID: a1b2c3d4e5f6
Revises: 575dbddddba0
Create Date: 2026-05-20 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "575dbddddba0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "indexed_transactions",
        sa.Column(
            "tx_id",
            sa.String(length=64),
            nullable=False,
            comment="SHA-256 of canonical tx JSON",
        ),
        sa.Column(
            "tx_type",
            sa.String(length=32),
            nullable=False,
            comment="Transfer | CreateProject | FundProject | Coinbase",
        ),
        sa.Column("from_address", sa.String(length=64), nullable=True),
        sa.Column("to_address", sa.String(length=64), nullable=True),
        sa.Column("amount", sa.BigInteger(), nullable=True),
        sa.Column("project_id", sa.String(length=32), nullable=True),
        sa.Column("block_height", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column("raw_data", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("tx_id"),
    )
    op.create_index(
        op.f("ix_indexed_transactions_tx_id"),
        "indexed_transactions",
        ["tx_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_indexed_transactions_from_address"),
        "indexed_transactions",
        ["from_address"],
        unique=False,
    )
    op.create_index(
        op.f("ix_indexed_transactions_to_address"),
        "indexed_transactions",
        ["to_address"],
        unique=False,
    )
    op.create_index(
        op.f("ix_indexed_transactions_block_height"),
        "indexed_transactions",
        ["block_height"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_indexed_transactions_block_height"),
        table_name="indexed_transactions",
    )
    op.drop_index(
        op.f("ix_indexed_transactions_to_address"),
        table_name="indexed_transactions",
    )
    op.drop_index(
        op.f("ix_indexed_transactions_from_address"),
        table_name="indexed_transactions",
    )
    op.drop_index(
        op.f("ix_indexed_transactions_tx_id"),
        table_name="indexed_transactions",
    )
    op.drop_table("indexed_transactions")
