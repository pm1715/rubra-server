from __future__ import annotations

from functools import lru_cache

from rubra.core.storage.db import RubraStorage, init_storage

from app.config import settings


@lru_cache(maxsize=1)
def get_storage() -> RubraStorage:
    """Single shared storage instance for the process lifetime."""
    return init_storage(settings.rubra_database_url)
