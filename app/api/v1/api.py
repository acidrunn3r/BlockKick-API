from fastapi import APIRouter

from app.api.v1.endpoints import auth, chain, projects, users

api_router = APIRouter()

api_router.include_router(chain.router, prefix="/chain", tags=["Chain"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
