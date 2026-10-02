from fastapi import APIRouter
from .address import router as address_endpoints, public_router

address_router = APIRouter(prefix="")

address_router.include_router(address_endpoints)
address_router.include_router(public_router)
