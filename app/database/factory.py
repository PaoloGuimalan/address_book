from utils.logging import get_module_logger
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .base import DatabaseInterface
from .session import Base  # Your centralized Declarative Base metadata registry

logger = get_module_logger(__name__)


class SQLiteDatabase(DatabaseInterface):
    """Concrete database plugin specifically tailored for local SQLite engines."""

    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url, connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_all_tables(self) -> None:
        logger.info("SQLite engine building missing tables from metadata catalog.")
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


class NetworkDatabase(DatabaseInterface):
    """Concrete database plugin for enterprise network-based servers (PostgreSQL, MySQL)."""

    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_all_tables(self) -> None:
        logger.info("Network engine verifying/building schemas from metadata catalog.")
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()


class DatabaseFactory:
    """The master architectural gateway to resolve and build connection engines dynamically."""

    @staticmethod
    def get_database(db_type: str, db_url: str) -> DatabaseInterface:
        logger.info(
            f"DatabaseFactory reading rules for target engine configuration: '{db_type}'"
        )

        db_type_clean = db_type.strip().lower()

        if db_type_clean == "sqlite":
            return SQLiteDatabase(db_url)

        elif db_type_clean in ["postgres", "postgresql", "mysql"]:
            return NetworkDatabase(db_url)

        else:
            logger.critical(
                f"DatabaseFactory failed. Configuration string '{db_type}' matches no known engine drivers."
            )
            raise ValueError(
                f"Database engine layout type '{db_type}' is unsupported by this application factory."
            )
