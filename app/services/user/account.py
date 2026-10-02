from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user.account import Account
from schemas.user.account import AccountCreate
from utils.security import hash_password


class CRUDAccount:

    def list(self, db: Session, page: int = 1, limit: int = 100) -> list[Account]:
        """
        Function for generating accounts list
        """

        return db.query(Account).offset(page - 1).limit(limit).all()

    def get_by_username_or_email(self, db: Session, identity: str) -> Account | None:
        """
        Queries the database to find an account matching either the username or email.
        """
        return (
            db.query(Account)
            .filter(or_(Account.username == identity, Account.email == identity))
            .first()
        )

    def get_by_username(self, db: Session, username: str) -> Account | None:
        return db.query(Account).filter(Account.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Account | None:
        return db.query(Account).filter(Account.email == email).first()

    def create(self, db: Session, obj_in: AccountCreate) -> Account:
        """
        Hashes the incoming payload password and commits a new Account row.
        """
        secure_hash = hash_password(obj_in.password)

        db_obj = Account(
            username=obj_in.username,
            email=obj_in.email,
            password_hash=secure_hash,
            name=obj_in.name,
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


account_crud = CRUDAccount()
