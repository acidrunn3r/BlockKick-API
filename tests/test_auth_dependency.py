import pytest

from app.core.jwt import create_access_token, create_refresh_token
from app.db.models import User


@pytest.mark.unit
class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_returns_401_with_no_token(self, async_client):
        response = await async_client.get("/api/v1/users/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_401_for_refresh_token(
        self, async_client, test_wallet_address: str
    ):
        token = create_refresh_token({"sub": test_wallet_address})
        response = await async_client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert "token type" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_returns_401_when_user_not_in_db(
        self, async_client, test_wallet_address: str
    ):
        token = create_access_token({"sub": test_wallet_address})
        response = await async_client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_returns_200_for_valid_token_and_existing_user(
        self, async_client, db_session, test_wallet_address: str
    ):
        user = User(
            wallet_address=test_wallet_address,
            display_name="Test User",
            bio="",
        )
        db_session.add(user)
        await db_session.flush()

        token = create_access_token({"sub": test_wallet_address})
        response = await async_client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["wallet_address"] == test_wallet_address
