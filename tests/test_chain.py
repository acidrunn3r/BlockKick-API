import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.unit
class TestChainEndpoints:
    def test_get_chain_info(self, client, override_blockchain_client):
        response = client.get("/api/v1/chain/info")
        assert response.status_code == 200
        assert "height" in response.json()
        assert "latest_hash" in response.json()
