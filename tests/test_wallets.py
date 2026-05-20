import json

import pytest

from app.db.models import IndexedTransaction

ADDR_A = "a" * 64
ADDR_B = "b" * 64
ADDR_C = "c" * 64

BASE = "/api/v1/wallets"


def _make_tx(
    tx_id: str,
    tx_type: str = "Transfer",
    from_address: str | None = ADDR_A,
    to_address: str | None = ADDR_B,
    amount: int | None = 100,
    block_height: int = 1,
    project_id: str | None = None,
) -> IndexedTransaction:
    return IndexedTransaction(
        tx_id=tx_id,
        tx_type=tx_type,
        from_address=from_address,
        to_address=to_address,
        amount=amount,
        project_id=project_id,
        block_height=block_height,
        timestamp=1_700_000_000,
        raw_data=json.dumps({"id": tx_id}),
    )


@pytest.mark.unit
class TestWalletTransactionsEndpoint:
    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_txs(self, async_client):
        response = await async_client.get(f"{BASE}/{ADDR_A}/transactions")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_returns_txs_where_address_is_sender(self, async_client, db_session):
        db_session.add(_make_tx("tw001", from_address=ADDR_A, to_address=ADDR_B))
        await db_session.flush()

        response = await async_client.get(f"{BASE}/{ADDR_A}/transactions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["tx_id"] == "tw001"
        assert data[0]["tx_type"] == "Transfer"
        assert data[0]["from_address"] == ADDR_A
        assert data[0]["to_address"] == ADDR_B
        assert data[0]["amount"] == 100

    @pytest.mark.asyncio
    async def test_returns_txs_where_address_is_recipient(
        self, async_client, db_session
    ):
        db_session.add(_make_tx("tw002", from_address=ADDR_C, to_address=ADDR_B))
        await db_session.flush()

        response = await async_client.get(f"{BASE}/{ADDR_B}/transactions")
        assert response.status_code == 200
        tx_ids = [tx["tx_id"] for tx in response.json()]
        assert "tw002" in tx_ids

    @pytest.mark.asyncio
    async def test_excludes_unrelated_txs(self, async_client, db_session):
        db_session.add(_make_tx("tw003", from_address=ADDR_B, to_address=ADDR_C))
        await db_session.flush()

        response = await async_client.get(f"{BASE}/{ADDR_A}/transactions")
        assert response.status_code == 200
        tx_ids = [tx["tx_id"] for tx in response.json()]
        assert "tw003" not in tx_ids

    @pytest.mark.asyncio
    async def test_returns_both_sent_and_received(self, async_client, db_session):
        db_session.add(
            _make_tx("tw004", from_address=ADDR_A, to_address=ADDR_B, block_height=5)
        )
        db_session.add(
            _make_tx("tw005", from_address=ADDR_C, to_address=ADDR_A, block_height=3)
        )
        await db_session.flush()

        response = await async_client.get(f"{BASE}/{ADDR_A}/transactions")
        assert response.status_code == 200
        tx_ids = [tx["tx_id"] for tx in response.json()]
        assert "tw004" in tx_ids
        assert "tw005" in tx_ids

    @pytest.mark.asyncio
    async def test_ordered_by_block_height_descending(self, async_client, db_session):
        db_session.add(_make_tx("tw006", from_address=ADDR_A, block_height=1))
        db_session.add(_make_tx("tw007", from_address=ADDR_A, block_height=10))
        db_session.add(_make_tx("tw008", from_address=ADDR_A, block_height=5))
        await db_session.flush()

        response = await async_client.get(f"{BASE}/{ADDR_A}/transactions")
        assert response.status_code == 200
        heights = [tx["block_height"] for tx in response.json()]
        relevant = [h for h in heights if h in (1, 5, 10)]
        assert relevant == sorted(relevant, reverse=True)

    @pytest.mark.asyncio
    async def test_coinbase_tx_has_no_sender(self, async_client, db_session):
        db_session.add(
            _make_tx(
                "tw009",
                tx_type="Coinbase",
                from_address=None,
                to_address=ADDR_A,
                amount=50,
            )
        )
        await db_session.flush()

        response = await async_client.get(f"{BASE}/{ADDR_A}/transactions")
        assert response.status_code == 200
        coinbase = next(tx for tx in response.json() if tx["tx_id"] == "tw009")
        assert coinbase["from_address"] is None
        assert coinbase["amount"] == 50

    @pytest.mark.asyncio
    async def test_create_project_tx_includes_project_id(
        self, async_client, db_session
    ):
        db_session.add(
            _make_tx(
                "tw010",
                tx_type="CreateProject",
                from_address=ADDR_A,
                to_address=None,
                amount=None,
                project_id="proj_abc123def456ab01",
            )
        )
        await db_session.flush()

        response = await async_client.get(f"{BASE}/{ADDR_A}/transactions")
        assert response.status_code == 200
        proj_tx = next(tx for tx in response.json() if tx["tx_id"] == "tw010")
        assert proj_tx["project_id"] == "proj_abc123def456ab01"
        assert proj_tx["amount"] is None

    @pytest.mark.asyncio
    async def test_short_address_returns_422(self, async_client):
        response = await async_client.get(f"{BASE}/tooshort/transactions")
        assert response.status_code == 422
