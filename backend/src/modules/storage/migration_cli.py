from __future__ import annotations

import os
import sqlite3
import sys

from modules.storage.migrations import apply_sqlite_migrations


def _resolve_db_path(argv: list) -> str:
    if len(argv) >= 2 and argv[1].strip():
        return argv[1].strip()
    return os.getenv("MIMIND_DB_PATH", os.getenv("MINDCOACH_DB_PATH", "data/mimind.sqlite3"))


def main() -> int:
    db_path = _resolve_db_path(sys.argv)
    directory = os.path.dirname(db_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    connection = sqlite3.connect(db_path)
    try:
        applied = apply_sqlite_migrations(connection)
    finally:
        connection.close()

    print(f"[PASS] sqlite migrations applied={applied} db_path={db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
