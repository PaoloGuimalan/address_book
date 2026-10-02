from fastapi import APIRouter
from .health import router as health_router
from .ready import router as ready_router

checks_endpoints = APIRouter()

checks_endpoints.include_router(health_router)
checks_endpoints.include_router(ready_router)
