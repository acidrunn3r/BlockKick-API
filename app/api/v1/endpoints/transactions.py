from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IndexedTransaction
from app.db.session import get_db
from app.schemas.transactions import TransactionResponse

router = APIRouter()


@router.get(
    "",
    response_model=list[TransactionResponse],
    summary="List transactions for a wallet address",
)
async def list_transactions(
    address: str = Query(
        ...,
        min_length=64,
        max_length=64,
        description="Hex-encoded Ed25519 public key (64 chars)",
    ),
    db: AsyncSession = Depends(get_db),
) -> list[TransactionResponse]:
    """Return all indexed transactions where the wallet is sender or recipient,
    ordered newest block first.
    """
    result = await db.execute(
        select(IndexedTransaction)
        .where(
            or_(
                IndexedTransaction.from_address == address,
                IndexedTransaction.to_address == address,
            )
        )
        .order_by(IndexedTransaction.block_height.desc())
    )
    txs = result.scalars().all()
    return [TransactionResponse.model_validate(tx) for tx in txs]
