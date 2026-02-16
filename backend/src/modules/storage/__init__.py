from __future__ import annotations

import os

from modules.storage.in_memory import InMemoryStore
from modules.storage.sqlite_store import SQLiteStore


def build_application_store() -> InMemoryStore:
    """Build the default runtime store with persistent relational backing."""
    db_path = os.getenv("MINDCOACH_DB_PATH", "data/mindcoach.sqlite3")
    return SQLiteStore(db_path=db_path)


__all__ = ["InMemoryStore", "SQLiteStore", "build_application_store"]
