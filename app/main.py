import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from app.api.v1.api import api_router
from app.config import settings
from app.core.client import client
from app.core.indexer import run_indexer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print(f"Starting BlockKick API (env={settings.ENV}, debug={settings.DEBUG})")

    await client.init()

    indexer_task = asyncio.create_task(run_indexer())

    yield

    print("Shutting down...")

    indexer_task.cancel()
    with suppress(asyncio.CancelledError):
        await indexer_task

    await client.close()


app = FastAPI(
    title="BlockKick API",
    description="Aggregator API for BlockKick blockchain",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Auth", "description": "Wallet authentication endpoints"},
        {"name": "Users", "description": "User profile management"},
        {"name": "Chain", "description": "Blockchain state queries"},
        {"name": "Projects", "description": "Crowdfunding projects"},
        {"name": "Wallets", "description": "Wallet transaction history"},
    ],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "blockkick-api",
        "env": settings.ENV,
        "debug": settings.DEBUG,
    }


@app.get("/", include_in_schema=False, response_model=None)
async def root_redirect() -> RedirectResponse | dict[str, str]:
    if settings.DEBUG:
        return RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)
    return {"message": "BlockKick API is running"}
