from fastapi import APIRouter

from app.api.v1.endpoints import chain, projects

api_router = APIRouter()

api_router.include_router(chain.router, prefix="/chain", tags=["Chain"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
