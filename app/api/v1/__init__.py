from fastapi import APIRouter
from .user import auth_router
from .address import address_router

v1_router = APIRouter(prefix="/api/v1")

v1_router.include_router(auth_router)
v1_router.include_router(address_router)
