import json

import pytest
from fastapi.testclient import TestClient

from app.db.models import IndexedTransaction
from app.main import app

client = TestClient(app)

ADDR_A = "a" * 64
PROJ_ID = "proj_cf183ff5549af78b"

_PROJECT_DATA = {
    "project_id": PROJ_ID,
    "name": "Open Source Game",
    "description": "A fun open source game",
    "goal_amount": 1000,
    "raised_amount": 250,
    "status": "ACTIVE",
    "deadline_timestamp": 1_800_000_000,
    "creator_wallet": ADDR_A,
}


def _make_fund_tx(
    tx_id: str, amount: int = 50, block_height: int = 1
) -> IndexedTransaction:
    return IndexedTransaction(
        tx_id=tx_id,
        tx_type="FundProject",
        from_address=ADDR_A,
        to_address=None,
        amount=amount,
        project_id=PROJ_ID,
        block_height=block_height,
        timestamp=1_700_000_000 + block_height,
        raw_data=json.dumps({"id": tx_id}),
    )


@pytest.mark.unit
class TestListProjectsEndpoint:
    def test_list_projects(self, client, override_blockchain_client):
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.unit
class TestGetProjectEndpoint:
    @pytest.mark.asyncio
    async def test_returns_project_detail(
        self, async_client, override_blockchain_client
    ):
        override_blockchain_client.get_project.return_value = _PROJECT_DATA

        response = await async_client.get(f"/api/v1/projects/{PROJ_ID}")
        assert response.status_code == 200
        data = response.json()
        assert data["project_id"] == PROJ_ID
        assert data["name"] == "Open Source Game"
        assert data["goal_amount"] == 1000
        assert data["raised_amount"] == 250
        assert data["status"] == "ACTIVE"
        assert data["recent_backers"] == []

    @pytest.mark.asyncio
    async def test_returns_404_when_project_not_found(
        self, async_client, override_blockchain_client
    ):
        override_blockchain_client.get_project.return_value = None

        response = await async_client.get("/api/v1/projects/proj_doesnotexist0000")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_includes_recent_backers(
        self, async_client, db_session, override_blockchain_client
    ):
        override_blockchain_client.get_project.return_value = _PROJECT_DATA

        for i in range(1, 4):
            db_session.add(_make_fund_tx(f"tp00{i}", amount=i * 10, block_height=i))
        await db_session.flush()

        response = await async_client.get(f"/api/v1/projects/{PROJ_ID}")
        assert response.status_code == 200
        backers = response.json()["recent_backers"]
        assert len(backers) == 3
        assert backers[0]["from_address"] == ADDR_A
        assert backers[0]["amount"] == 30

    @pytest.mark.asyncio
    async def test_recent_backers_capped_at_five(
        self, async_client, db_session, override_blockchain_client
    ):
        override_blockchain_client.get_project.return_value = _PROJECT_DATA

        for i in range(1, 9):
            db_session.add(_make_fund_tx(f"tpcap{i}", block_height=i))
        await db_session.flush()

        response = await async_client.get(f"/api/v1/projects/{PROJ_ID}")
        assert response.status_code == 200
        assert len(response.json()["recent_backers"]) == 5

    @pytest.mark.asyncio
    async def test_returns_503_when_node_unreachable(
        self, async_client, override_blockchain_client
    ):
        import httpx

        override_blockchain_client.get_project.side_effect = httpx.RequestError(
            "connection refused"
        )

        response = await async_client.get(f"/api/v1/projects/{PROJ_ID}")
        assert response.status_code == 503
