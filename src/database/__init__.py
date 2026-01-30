from src.database.models import (
    Base,
    MovieModel,
    ActorModel,
    LanguageModel,
)

from src.database.session_sqlite import reset_sqlite_database as reset_database

import os

environment = os.getenv("ENVIRONMENT", "developing")

if environment == "testing":
    from src.database.session_sqlite import (
        get_sqlite_db_contextmanager as get_db_contextmanager,
        get_sqlite_db as get_db,
    )
else:
    from src.database.session_postgresql import (
        get_postgresql_db_contextmanager as get_db_contextmanager,
        get_postgresql_db as get_db,
    )

__all__ = [
    "Base",
    "MovieModel",
    "ActorModel",
    "LanguageModel",
    "get_db",
    "get_db_contextmanager",
    "reset_database",
]
