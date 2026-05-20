import asyncio
import json
import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from app.config import settings
from app.core.client import client as blockchain_client
from app.db.models import IndexedTransaction
from app.db.session import async_session_maker

logger = logging.getLogger(__name__)


def _extract_tx_fields(tx: dict[str, Any], block_height: int) -> dict[str, Any]:
    data: dict[str, Any] = tx.get("data") or {}
    return {
        "tx_id": tx.get("id", ""),
        "tx_type": tx.get("tx_type", ""),
        "from_address": tx.get("from"),
        "to_address": tx.get("to"),
        "amount": data.get("amount"),
        "project_id": data.get("project_id"),
        "block_height": block_height,
        "timestamp": tx.get("timestamp", 0),
        "raw_data": json.dumps(tx),
    }


async def _get_last_indexed_height() -> int:
    async with async_session_maker() as session:
        result = await session.execute(
            select(func.max(IndexedTransaction.block_height))
        )
        val = result.scalar()
        return val if val is not None else -1


async def _index_block(height: int) -> int:
    block = await blockchain_client.get_block(height)
    txs = block.get("transactions", [])
    if not txs:
        return 0

    async with async_session_maker() as session:
        for tx in txs:
            fields = _extract_tx_fields(tx, height)
            if not fields["tx_id"]:
                continue
            stmt = (
                insert(IndexedTransaction)
                .values(**fields)
                .on_conflict_do_nothing(index_elements=["tx_id"])
            )
            await session.execute(stmt)
        await session.commit()

    return len(txs)


async def run_indexer() -> None:
    logger.info("Transaction indexer started")
    while True:
        try:
            chain = await blockchain_client.get_chain_info()
            current_height: int = chain["height"]
            last_height = await _get_last_indexed_height()

            for height in range(last_height + 1, current_height + 1):
                count = await _index_block(height)
                if count:
                    logger.info("Indexed block %d: %d tx(s)", height, count)
        except asyncio.CancelledError:
            logger.info("Transaction indexer stopped")
            return
        except Exception as exc:
            logger.warning("Indexer error: %s", exc)

        await asyncio.sleep(settings.INDEXER_POLL_INTERVAL)
