from datetime import UTC, datetime, timedelta

import pytest

from app.core.jwt import create_refresh_token
from app.db.models import AuthNonce, User

WALLET = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
SIGNATURE = "a" * 128


@pytest.mark.unit
class TestChallengeEndpoint:
    @pytest.mark.asyncio
    async def test_returns_201_with_nonce(self, async_client):
        response = await async_client.post(
            "/api/v1/auth/challenge", json={"wallet_address": WALLET}
        )
        assert response.status_code == 201
        data = response.json()
        assert "nonce" in data
        assert "expires_at" in data

    @pytest.mark.asyncio
    async def test_rejects_invalid_wallet_address(self, async_client):
        response = await async_client.post(
            "/api/v1/auth/challenge", json={"wallet_address": "not-a-wallet"}
        )
        assert response.status_code == 422


@pytest.mark.unit
class TestLoginEndpoint:
    @pytest.mark.asyncio
    async def test_returns_tokens_and_creates_user(
        self, async_client, db_session, test_wallet_address: str
    ):
        nonce = AuthNonce(
            nonce="valid-nonce",
            wallet_address=test_wallet_address,
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
            used=False,
        )
        db_session.add(nonce)
        await db_session.flush()

        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "wallet_address": test_wallet_address,
                "nonce": "valid-nonce",
                "signature": SIGNATURE,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_returns_200_for_existing_user(
        self, async_client, db_session, test_wallet_address: str
    ):
        user = User(
            wallet_address=test_wallet_address,
            display_name="Existing User",
            bio="",
        )
        db_session.add(user)
        nonce = AuthNonce(
            nonce="existing-user-nonce",
            wallet_address=test_wallet_address,
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
            used=False,
        )
        db_session.add(nonce)
        await db_session.flush()

        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "wallet_address": test_wallet_address,
                "nonce": "existing-user-nonce",
                "signature": SIGNATURE,
            },
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_404_for_unknown_nonce(
        self, async_client, test_wallet_address: str
    ):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "wallet_address": test_wallet_address,
                "nonce": "nonexistent-nonce",
                "signature": SIGNATURE,
            },
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_returns_400_for_used_nonce(
        self, async_client, db_session, test_wallet_address: str
    ):
        nonce = AuthNonce(
            nonce="used-nonce",
            wallet_address=test_wallet_address,
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
            used=True,
        )
        db_session.add(nonce)
        await db_session.flush()

        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "wallet_address": test_wallet_address,
                "nonce": "used-nonce",
                "signature": SIGNATURE,
            },
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_returns_400_for_expired_nonce(
        self, async_client, db_session, test_wallet_address: str
    ):
        nonce = AuthNonce(
            nonce="expired-nonce",
            wallet_address=test_wallet_address,
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
            used=False,
        )
        db_session.add(nonce)
        await db_session.flush()

        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "wallet_address": test_wallet_address,
                "nonce": "expired-nonce",
                "signature": SIGNATURE,
            },
        )
        assert response.status_code == 400


@pytest.mark.unit
class TestRefreshEndpoint:
    @pytest.mark.asyncio
    async def test_returns_new_tokens_for_valid_refresh_token(
        self, async_client, test_wallet_address: str
    ):
        token = create_refresh_token({"sub": test_wallet_address})
        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_returns_401_for_access_token_instead_of_refresh(
        self, async_client, access_token: str
    ):
        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": access_token}
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_returns_401_for_invalid_token(self, async_client):
        response = await async_client.post(
            "/api/v1/auth/refresh", json={"refresh_token": "not.a.token"}
        )
        assert response.status_code == 401
