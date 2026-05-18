import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.unit
class TestChainEndpoints:
    def test_get_chain_info(self, client):
        response = client.get("/chain/info")
        assert response.status_code == 200
        assert "height" in response.json()
        assert "block_hash" in response.json()
