from fastapi import FastAPI

from app.api import api_router

app = FastAPI(
    title="Model Manager API",
    version="0.1.0",
    # Dokumentacja pod /api/..., żeby działała przez proxy nginx
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)

app.include_router(api_router, prefix="/api")
