from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting BlockKick API (env={settings.ENV}, debug={settings.DEBUG})")
    
    # Initializing...
    
    yield
    
    print("Shutting down...")
    
    # Shutting down...


app = FastAPI(
    title="BlockKick API",
    description="Aggregator API for BlockKick blockchain",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "service": "blockkick-api",
        "env": settings.ENV,
        "debug": settings.DEBUG,
    }


@app.get("/", include_in_schema=False)
async def root_redirect():
    if settings.DEBUG:
        return RedirectResponse(url="/docs", status_code=status.HTTP_302_FOUND)
    return {"message": "BlockKick API is running"}


# Routers here
