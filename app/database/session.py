import sys
from sqlalchemy.orm import declarative_base, declared_attr
from utils.config import settings


class CustomBase:
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Automatically generates table names with category folder prefixes.
        Example: app.models.authentication.user.User -> auth_users
        """
        module_parts = cls.__module__.split(".")

        if len(module_parts) > 3 and module_parts[1] == "models":
            category = module_parts[2]

            # Optional: Shorthand mappings to keep table names clean (e.g., authentication -> auth)
            shorthand = {}
            prefix = shorthand.get(category, category)

            return f"{prefix}_{cls.__name__.lower()}s"

        return f"{cls.__name__.lower()}s"


Base = declarative_base(cls=CustomBase)


def get_active_plugin():
    """
    Inline factory resolver to completely break circular import loops.
    """
    from database.factory import DatabaseFactory

    return DatabaseFactory.get_database(settings.DB_TYPE, settings.DATABASE_URL)


db_plugin = get_active_plugin()
