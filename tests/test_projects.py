import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.unit
class TestProjectEndpoints:
    def test_list_projects(self, client, override_blockchain_client):
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
