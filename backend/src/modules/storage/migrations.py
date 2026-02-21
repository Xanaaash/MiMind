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
    SQLiteMigration(
        version=2,
        name="api_audit_logs",
        statements=[
            """
            CREATE TABLE IF NOT EXISTS api_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                request_payload_json TEXT NOT NULL,
                response_payload_json TEXT NOT NULL,
                user_id TEXT,
                client_ref TEXT,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_api_audit_logs_created_at
            ON api_audit_logs (created_at)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_api_audit_logs_user_id
            ON api_audit_logs (user_id)
            """,
        ],
    ),
    SQLiteMigration(
        version=3,
        name="user_password_auth_fields",
        statements=[
            "ALTER TABLE users ADD COLUMN password_hash TEXT",
            "ALTER TABLE users ADD COLUMN auth_provider TEXT NOT NULL DEFAULT 'guest'",
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique
            ON users(email)
            """,
        ],
    ),
    SQLiteMigration(
        version=4,
        name="auth_and_audit_compatibility_backfill",
        statements=[
            """
            CREATE TABLE IF NOT EXISTS api_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                request_payload_json TEXT NOT NULL,
                response_payload_json TEXT NOT NULL,
                user_id TEXT,
                client_ref TEXT,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_api_audit_logs_created_at
            ON api_audit_logs (created_at)
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_api_audit_logs_user_id
            ON api_audit_logs (user_id)
            """,
            "ALTER TABLE users ADD COLUMN password_hash TEXT",
            "ALTER TABLE users ADD COLUMN auth_provider TEXT NOT NULL DEFAULT 'guest'",
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique
            ON users(email)
            """,
        ],
    ),
    SQLiteMigration(
        version=5,
        name="encrypted_sensitive_storage",
        statements=[
            """
            CREATE TABLE IF NOT EXISTS assessment_submissions_secure (
                submission_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                payload_encrypted TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_assessment_submissions_secure_user_id
            ON assessment_submissions_secure (user_id, submitted_at)
            """,
            """
            CREATE TABLE IF NOT EXISTS assessment_scores_secure (
                user_id TEXT PRIMARY KEY,
                payload_encrypted TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS test_results_secure (
                result_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                test_id TEXT NOT NULL,
                payload_encrypted TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_test_results_secure_user_id
            ON test_results_secure (user_id, created_at)
            """,
            """
            CREATE TABLE IF NOT EXISTS coach_sessions_secure (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                style_id TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                active INTEGER NOT NULL,
                halted_for_safety INTEGER NOT NULL,
                turns_encrypted TEXT NOT NULL
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS idx_coach_sessions_secure_user_id
            ON coach_sessions_secure (user_id, started_at)
            """,
        ],
    ),
    SQLiteMigration(
        version=6,
        name="user_email_verification_fields",
        statements=[
            "ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE users ADD COLUMN email_verification_token TEXT",
            "ALTER TABLE users ADD COLUMN email_verification_expires_at TEXT",
            """
            CREATE INDEX IF NOT EXISTS idx_users_email_verification_token
            ON users(email_verification_token)
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
            try:
                connection.execute(statement)
            except sqlite3.OperationalError as error:
                message = str(error).lower()
                if "duplicate column name" in message:
                    continue
                raise
            except sqlite3.IntegrityError as error:
                message = str(error).lower()
                if "idx_users_email_unique" in statement.lower() and "unique constraint failed" in message:
                    continue
                raise

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
