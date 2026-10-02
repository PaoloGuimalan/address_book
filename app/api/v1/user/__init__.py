from fastapi import APIRouter
from .auth import router as auth_endpoints
from .accounts import router as account_endpoints

auth_router = APIRouter(prefix="")

auth_router.include_router(auth_endpoints)
auth_router.include_router(account_endpoints)
