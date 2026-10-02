from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db_session
from utils.logging import get_module_logger

from schemas.user.account import AccountListResponse
from services.user.account import account_crud
from api.deps import get_current_account

router = APIRouter(
    prefix="/user", tags=["Users"], dependencies=[Depends(get_current_account)]
)

logger = get_module_logger(__name__)


@router.get("/list", response_model=AccountListResponse)
def list_accounts(
    page: int = Query(
        default=1, ge=1, description="The page number to fetch. Starts at 1."
    ),
    limit: int = Query(
        default=20, ge=1, le=100, description="The maximum results to display per page."
    ),
    db: Session = Depends(get_db_session),
):
    """
    Fetch an indexed roster list of active accounts inside the network matrix.
    Utilizes skip and limit query adjustments to preserve connection speed profiles.
    """
    logger.info(
        f"Roster list requested with batch rules -> Skip Index: {page} | Vol Limit: {limit}"
    )

    accounts_records = account_crud.list(db, page=page, limit=limit)

    batch_count = len(accounts_records)

    logger.info(
        f"Roster delivery successful. Packaged {batch_count} records to user stream."
    )

    return {
        "total_records": batch_count,
        "current_page": page,
        "limit": limit,
        "data": accounts_records,
    }
