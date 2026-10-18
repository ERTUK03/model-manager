from fastapi import APIRouter

from app.api import auth, health, history, models

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(models.router)
api_router.include_router(history.router)
