import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from utils.config import settings
from utils.logging import setup_logging, get_module_logger
from database.session import db_plugin

from api.v1 import v1_router

setup_logging()
logger = get_module_logger(__name__)

import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application booting up... running table creation workflows.")
    db_plugin.create_all_tables()

    yield

    logger.info("Application shutting down smoothly.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Scalable Factory-Architecture backend layout featuring multi-database drivers and unified logging.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Checks",
            "description": "Liveness check endpoints.",
        },
        {
            "name": "Auth",
            "description": "Operations handling registration, lookups, and account states.",
        },
        {
            "name": "Users",
            "description": "Endpoints for users",
        },
    ],
)

app.include_router(v1_router)


@app.get("/", include_in_schema=False)
def read_root():
    logger.info("Base endpoint hit.")
    return f"Welcome to {settings.PROJECT_NAME}"
