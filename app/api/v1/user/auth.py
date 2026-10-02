from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db_session
from utils.logging import get_module_logger
from utils.security import verify_password, create_access_token

from schemas.user.account import AccountCreate, AccountLogin, AccountResponse
from services.user.account import account_crud

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

logger = get_module_logger(__name__)


@router.post("/login", tags=["Auth"])
def login(payload: AccountLogin, db: Session = Depends(get_db_session)):
    """
    Authenticate account credentials and return an authorized Bearer JWT token.
    """
    logger.info(
        f"Login path execution triggered for identity: '{payload.username_or_email}'"
    )

    account = account_crud.get_by_username_or_email(
        db, identity=payload.username_or_email
    )

    if not account or not verify_password(payload.password, account.password_hash):
        logger.warning(
            f"Authentication failed for identity: '{payload.username_or_email}'"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password credentials.",
        )

    if not account.is_active:
        logger.warning(
            f"Login block execution: Account ID {account.id} is flagged inactive."
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated by an administrator.",
        )

    access_token = create_access_token(data={"sub": str(account.id)})

    logger.info(
        f"Authentication complete! JWT access token granted for Account ID {account.id}."
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", tags=["Auth"], status_code=status.HTTP_201_CREATED)
def register(payload: AccountCreate, db: Session = Depends(get_db_session)):
    """
    Register a unique system Account entity.
    Returns a success confirmation string alongside filtered account metadata.
    """
    logger.info(
        f"Registration path execution triggered for: '{payload.username}' ({payload.email})"
    )

    if account_crud.get_by_username_or_email(
        db, identity=payload.username
    ) or account_crud.get_by_username_or_email(db, identity=payload.email):
        logger.warning(
            f"Registration aborted. Conflict detected for fields matching: '{payload.username}'"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or Email address is already registered.",
        )

    new_account = account_crud.create(db, obj_in=payload)

    logger.info(
        f"Account successfully built! Assigned Database Row ID: {new_account.id}"
    )

    return {"message": "Account created successfully"}
