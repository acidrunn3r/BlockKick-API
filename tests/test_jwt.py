import pytest
from fastapi import HTTPException

from app.core.jwt import create_access_token, decode_token


@pytest.mark.unit
class TestCreateAccessToken:
    def test_creates_valid_token(self, test_wallet_address: str):
        token = create_access_token({"sub": test_wallet_address})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_expected_claims(self, test_wallet_address: str):
        token = create_access_token({"sub": test_wallet_address, "role": "user"})
        payload = decode_token(token)
        assert payload["sub"] == test_wallet_address
        assert payload["role"] == "user"
        assert payload["type"] == "access"


@pytest.mark.unit
class TestDecodeToken:
    def test_decodes_valid_token(self, access_token: str, test_wallet_address: str):
        payload = decode_token(access_token)
        assert payload["sub"] == test_wallet_address

    def test_raises_on_invalid_token(self):
        with pytest.raises(HTTPException) as exc:
            decode_token("invalid.token.here")
        assert exc.value.status_code == 401
        assert "Invalid or expired token" in exc.value.detail

    def test_raises_on_expired_token(self):
        from datetime import UTC, datetime, timedelta

        from jose import jwt

        from app.config import settings

        expired_payload = {
            "sub": "test",
            "exp": datetime.now(UTC) - timedelta(seconds=1),
            "type": "access",
        }
        token = jwt.encode(
            expired_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
        )
        with pytest.raises(HTTPException) as exc:
            decode_token(token)
        assert exc.value.status_code == 401
