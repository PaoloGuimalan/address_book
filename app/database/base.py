from abc import ABC, abstractmethod
from typing import Generator
from sqlalchemy.orm import Session


class DatabaseInterface(ABC):
    @abstractmethod
    def create_all_tables(self) -> None:
        """Create schema tables if they do not exist (mainly used for SQLite/testing)."""
        pass

    @abstractmethod
    def get_db(self) -> Generator[Session, None, None]:
        """A generator dependency that yields a database session context."""
        pass
