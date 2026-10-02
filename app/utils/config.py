import os
from typing import Annotated
from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def empty_string_to_none(v: str | None) -> str | None:
    if v == "" or (isinstance(v, str) and v.strip() == ""):
        return None
    return v


OptionalInt = Annotated[int | None, BeforeValidator(empty_string_to_none)]
OptionalStr = Annotated[str | None, BeforeValidator(empty_string_to_none)]


class Settings(BaseSettings):
    # Core Global Configurations
    PROJECT_NAME: str = "FastAPI Factory Architecture"
    APP_ENV: str = "development"

    DB_TYPE: str = "sqlite"  # Choices: sqlite, postgres, mysql
    DB_NAME: str = "address_book"

    DB_USER: OptionalStr = None
    DB_PASSWORD: OptionalStr = None
    DB_HOST: OptionalStr = None
    DB_PORT: OptionalInt = None

    SECRET_KEY: str = "DEFAULT_FALLBACK_NOT_SECURE_SIGNATURE_KEY_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @property
    def DATABASE_URL(self) -> str:
        """Dynamically builds connection wrappers."""
        db_type_clean = self.DB_TYPE.strip().lower()

        if db_type_clean == "sqlite":
            return f"sqlite:///./{self.DB_NAME}.db"

        elif db_type_clean in ["postgres", "postgresql"]:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        elif db_type_clean == "mysql":
            return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        raise ValueError(
            f"Unsupported database layout type configuration: {self.DB_TYPE}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
