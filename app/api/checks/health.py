from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.deps import get_db_session
from utils.logging import get_module_logger
from utils.config import settings

router = APIRouter(
    prefix="/health",
    tags=["Checks"],
)

logger = get_module_logger(__name__)


@router.get("")
def database_health_check(db: Session = Depends(get_db_session)):
    """
    Actively checks the operational readiness of the application backend
    and verifies the live connectivity pipeline to the database engine.
    """
    try:
        db.execute(text("SELECT 1")).fetchone()

        logger.info(
            f"Health check passed. Live connection verified on engine: '{settings.DB_TYPE}'"
        )
        return {
            "status": "healthy",
            "database": {"engine": settings.DB_TYPE, "connected": True},
        }

    except Exception as error:
        logger.critical(
            f"Health check failed! Engine connectivity dropped: {str(error)}",
            exc_info=True,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": {
                    "engine": settings.DB_TYPE,
                    "connected": False,
                    "error": "Unable to communicate with the database container or file.",
                },
            },
        )
