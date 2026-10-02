from sqlalchemy.orm import declarative_base, declared_attr
from utils.config import settings


class CustomBase:
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Dynamically extracts parent folder categories to apply custom table prefixes.
        Example: app.models.authentication.user.Account -> auth_accounts
        Example: app.models.inventory.address.Address -> inv_addresses
        """
        module_parts = cls.__module__.split(".")

        if "models" in module_parts:
            models_index = module_parts.index("models")

            if len(module_parts) > models_index + 1:
                category = module_parts[models_index + 1]

                shorthand = {"authentication": "auth", "inventory": "inv"}
                prefix = shorthand.get(category, category)

                raw_name = cls.__name__.lower()
                plural_suffix = (
                    "es" if raw_name.endswith(("s", "x", "z", "ch", "sh")) else "s"
                )

                return f"{prefix}_{raw_name}{plural_suffix}"

        raw_name = cls.__name__.lower()
        plural_suffix = "es" if raw_name.endswith(("s", "x", "z", "ch", "sh")) else "s"
        return f"{raw_name}{plural_suffix}"


Base = declarative_base(cls=CustomBase)


def get_active_plugin():
    """
    Inline factory resolver to completely break circular import loops.
    """
    from database.factory import DatabaseFactory

    return DatabaseFactory.get_database(settings.DB_TYPE, settings.DATABASE_URL)


db_plugin = get_active_plugin()
