from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from .base import DatabaseInterface

Base = declarative_base()


class SQLiteDatabase(DatabaseInterface):
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url, connect_args={"check_same_thread": False}
        )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_all_tables(self) -> None:
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Generator[Session, None, None]:
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
