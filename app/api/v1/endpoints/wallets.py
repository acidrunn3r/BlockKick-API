from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import IndexedTransaction
from app.db.session import get_db
from app.schemas.transactions import TransactionResponse

router = APIRouter()


@router.get(
    "/{address}/transactions",
    response_model=list[TransactionResponse],
)
async def get_wallet_transactions(
    address: str,
    db: AsyncSession = Depends(get_db),
) -> list[TransactionResponse]:
    """Return all indexed transactions where the wallet is sender or recipient,
    ordered newest block first.
    """
    if len(address) != 64:
        raise HTTPException(
            status_code=422,
            detail="address must be exactly 64 hex characters",
        )

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
