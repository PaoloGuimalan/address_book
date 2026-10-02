from fastapi import APIRouter
from utils.logging import get_module_logger

router = APIRouter(
    prefix="/ready",
    tags=["Checks"],
)

logger = get_module_logger(__name__)


@router.get("")
def readyz():
    logger.info("ready endpoint hit.")
    return {"status": "OK", "message": "ready"}
