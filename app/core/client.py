import time
from typing import Any, cast

import httpx

from app.config import settings


class BlockchainClient:
    """Async HTTP client for interacting with the BlockKick blockchain node.

    Manages a persistent connection pool and caches read-only responses
    to reduce load on the underlying Rust node.
    """

    def __init__(self) -> None:
        self.base_url = settings.BLOCKCHAIN_NODE_URL.rstrip("/")
        self.timeout = settings.BLOCKCHAIN_REQUEST_TIMEOUT
        self.client: httpx.AsyncClient | None = None
        self._cache: dict[str, tuple[Any, float]] = {}
        self._cache_ttl: float = 10.0  # Seconds

    async def init(self) -> None:
        """Initialize the underlying httpx client (connection pool)."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    async def close(self) -> None:
        """Gracefully close the client and release connections."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def _fetch_with_cache(
        self, cache_key: str, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        """Fetch JSON data with simple time-based cache."""
        now = time.monotonic()
        cached = self._cache.get(cache_key)
        if cached:
            value, expiry = cached
            if now < expiry:
                return value

        if not self.client:
            raise RuntimeError("BlockchainClient is not initialized")

        response = await self.client.get(path, params=params)
        response.raise_for_status()
        data = response.json()

        self._cache[cache_key] = (data, now + self._cache_ttl)
        return data

    async def get_chain_info(self) -> dict[str, Any]:
        """Get current blockchain state (height & latest hash)."""
        return cast(
            dict[str, Any], await self._fetch_with_cache("chain_info", "/api/v1/chain")
        )

    async def get_projects(self) -> list[dict[str, Any]]:
        """Get list of all crowdfunding projects."""
        return cast(
            list[dict[str, Any]],
            await self._fetch_with_cache("projects", "/api/v1/projects"),
        )

    async def get_project(self, project_id: str) -> dict[str, Any] | None:
        """Return a single project by ID, or None if not found."""
        projects = await self.get_projects()
        return next((p for p in projects if p.get("project_id") == project_id), None)

    async def get_block(self, height: int) -> dict[str, Any]:
        """Fetch a single block by height (no cache — used by indexer)."""
        if not self.client:
            raise RuntimeError("BlockchainClient is not initialized")
        response = await self.client.get(f"/api/v1/block/{height}")
        response.raise_for_status()
        return cast(dict[str, Any], response.json())


# Module-level singleton
client = BlockchainClient()
