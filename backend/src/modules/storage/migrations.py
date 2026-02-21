from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List


@dataclass(frozen=True)
class SQLiteMigration:
    version: int
    name: str
    statements: List[str]


MIGRATIONS: List[SQLiteMigration] = [
    SQLiteMigration(
        version=1,
        name="baseline_schema",
        statements=[
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                locale TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS admin_sessions (
                session_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked INTEGER NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS assessment_submissions (
                submission_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                responses_json TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS assessment_scores (
                user_id TEXT PRIMARY KEY,
                phq9_score INTEGER NOT NULL,
                gad7_score INTEGER NOT NULL,
                pss10_score INTEGER NOT NULL,
                cssrs_positive INTEGER NOT NULL,
                scl90_global_index REAL,
                scl90_dimension_scores_json TEXT,
                scl90_moderate_or_above INTEGER NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS triage_decisions (
                user_id TEXT PRIMARY KEY,
                channel TEXT NOT NULL,
                reasons_json TEXT NOT NULL,
                halt_coaching INTEGER NOT NULL,
                show_hotline INTEGER NOT NULL,
                dialogue_risk_level TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS reassessment_schedules (
                user_id TEXT PRIMARY KEY,
                due_dates_json TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS test_results (
                result_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                test_id TEXT NOT NULL,
                answers_json TEXT NOT NULL,
                summary_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_test_results_user_id
            ON test_results (user_id, created_at)
            """,
        ],
    ),
]


def _ensure_migration_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )


def _load_applied_versions(connection: sqlite3.Connection) -> set:
    rows = connection.execute("SELECT version FROM schema_migrations").fetchall()
    return {int(row[0]) for row in rows}


def apply_sqlite_migrations(connection: sqlite3.Connection, migrations: Iterable[SQLiteMigration] = MIGRATIONS) -> int:
    _ensure_migration_table(connection)
    applied_versions = _load_applied_versions(connection)

    applied_count = 0
    for migration in sorted(migrations, key=lambda item: item.version):
        if migration.version in applied_versions:
            continue

        for statement in migration.statements:
            connection.execute(statement)

        connection.execute(
            """
            INSERT INTO schema_migrations (version, name, applied_at)
            VALUES (?, ?, ?)
            """,
            (
                migration.version,
                migration.name,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        applied_count += 1

    connection.commit()
    return applied_count
