import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.unit
class TestProjectEndpoints:
    def test_list_projects(self, client):
        response = client.get("/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
