import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings
from app.core.jwt import create_access_token, create_refresh_token
from app.db.models import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Override settings for test environment."""
    os.environ["ENV"] = "testing"
    os.environ["DEBUG"] = "True"
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://test:test@localhost:5432/blockkick_test"
    )
    os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only-1234567890"
    os.environ["BLOCKCHAIN_NODE_URL"] = "http://mock-blockchain:3000"

    get_settings.cache_clear()
    return get_settings()


@pytest.fixture(autouse=True)
def override_settings(test_settings: Settings) -> None:
    """Apply test settings to all tests."""
    from app import config

    config.settings = test_settings


@pytest_asyncio.fixture(scope="session")
async def test_engine(test_settings: Settings):
    """Create test database engine."""
    engine = create_async_engine(
        test_settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(
    test_engine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a new DB session for each test with rollback."""
    session_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    session = session_maker()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency to use test session."""

    async def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(override_get_db) -> Generator[TestClient, None, None]:
    """Sync TestClient for simple tests."""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTPX client for async endpoint tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_wallet_address() -> str:
    """Valid test wallet address (64 hex chars)."""
    return "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"


@pytest.fixture
def access_token(test_wallet_address: str) -> str:
    """Valid access token for testing."""
    return create_access_token({"sub": test_wallet_address})


@pytest.fixture
def refresh_token(test_wallet_address: str) -> str:
    """Valid refresh token for testing."""
    return create_refresh_token({"sub": test_wallet_address})


@pytest.fixture
def auth_header(access_token: str) -> dict[str, str]:
    """Authorization header with Bearer token."""
    return {"Authorization": f"Bearer {access_token}"}
