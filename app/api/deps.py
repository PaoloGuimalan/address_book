import logging
import jwt
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from utils.config import settings
from database.session import db_plugin, Base
from models.user.account import Account
from services.user.account import account_crud
from utils.logging import get_module_logger

security_scheme = HTTPBearer(auto_error=True)

logger = get_module_logger(__name__)


def get_db_session() -> Generator[Session, None, None]:
    """Unified session generator powered by the active factory engine plugin."""
    yield from db_plugin.get_db()


def get_current_account(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db_session),
) -> Account:
    """
    Validates the token from the standard global single-input Authorization text field modal.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate authorization signatures.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    raw_token = credentials.credentials

    try:
        payload = jwt.decode(
            raw_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        account_id: str = payload.get("sub")
        if account_id is None:
            raise credentials_exception

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise credentials_exception

    account = db.query(Account).filter(Account.id == int(account_id)).first()
    if account is None or not account.is_active:
        raise credentials_exception

    return account
