from fastapi import APIRouter

from app.api.v1.endpoints import chain

# Главный роутер для версии API v1
api_router = APIRouter()

# Подключаем роутеры из endpoints
api_router.include_router(chain.router, prefix="/chain", tags=["Chain"])
