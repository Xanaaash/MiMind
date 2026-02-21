from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime, timezone
from threading import Lock
from typing import Any, Dict, List, Optional

from modules.admin.models import AdminSession
from modules.assessment.models import AssessmentScoreSet, AssessmentSubmission, ReassessmentSchedule
from modules.coach.models import CoachSession, CoachTurn
from modules.observability.models import APIAuditLogRecord
from modules.security.crypto import DataEncryptor
from modules.storage.in_memory import InMemoryStore
from modules.storage.migrations import apply_sqlite_migrations
from modules.tests.models import TestResult
from modules.triage.models import RiskLevel, TriageChannel, TriageDecision
from modules.user.models import User


class SQLiteStore(InMemoryStore):
    """Hybrid storage: relational persistence for scale/test flows, memory for the rest."""

    def __init__(self, db_path: str) -> None:
        super().__init__()
        self._db_path = db_path
        self._lock = Lock()
        self._encryptor = DataEncryptor.from_env()
        self._connection = self._connect(db_path)
        self._initialize_schema()

    @property
    def db_path(self) -> str:
        return self._db_path

    def _connect(self, db_path: str) -> sqlite3.Connection:
        if db_path != ":memory:":
            directory = os.path.dirname(db_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

        connection = sqlite3.connect(db_path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_schema(self) -> None:
        with self._lock:
            apply_sqlite_migrations(self._connection)

    def _encrypt_json(self, payload: Any) -> str:
        return self._encryptor.encrypt_json(payload)

    def _decrypt_json(self, value: str) -> Any:
        return self._encryptor.decrypt_json(value)

    @staticmethod
    def _score_payload(scores: AssessmentScoreSet) -> Dict[str, Any]:
        return {
            "phq9_score": scores.phq9_score,
            "gad7_score": scores.gad7_score,
            "pss10_score": scores.pss10_score,
            "cssrs_positive": bool(scores.cssrs_positive),
            "scl90_global_index": scores.scl90_global_index,
            "scl90_dimension_scores": scores.scl90_dimension_scores,
            "scl90_moderate_or_above": bool(scores.scl90_moderate_or_above),
        }

    @staticmethod
    def _hydrate_score_payload(payload: Dict[str, Any]) -> AssessmentScoreSet:
        return AssessmentScoreSet(
            phq9_score=int(payload["phq9_score"]),
            gad7_score=int(payload["gad7_score"]),
            pss10_score=int(payload["pss10_score"]),
            cssrs_positive=bool(payload["cssrs_positive"]),
            scl90_global_index=float(payload["scl90_global_index"])
            if payload.get("scl90_global_index") is not None
            else None,
            scl90_dimension_scores=dict(payload["scl90_dimension_scores"])
            if payload.get("scl90_dimension_scores") is not None
            else None,
            scl90_moderate_or_above=bool(payload.get("scl90_moderate_or_above", False)),
        )

    @staticmethod
    def _serialize_turns(turns: List[CoachTurn]) -> List[dict]:
        return [
            {
                "role": turn.role,
                "message": turn.message,
                "created_at": turn.created_at.isoformat(),
            }
            for turn in turns
        ]

    @staticmethod
    def _hydrate_turns(items: List[dict]) -> List[CoachTurn]:
        turns: List[CoachTurn] = []
        for item in items:
            turns.append(
                CoachTurn(
                    role=str(item.get("role", "")),
                    message=str(item.get("message", "")),
                    created_at=datetime.fromisoformat(str(item.get("created_at"))),
                )
            )
        return turns

    def save_user(self, user: User) -> None:
        super().save_user(user)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO users (
                    user_id,
                    email,
                    locale,
                    password_hash,
                    auth_provider,
                    email_verified,
                    email_verification_token,
                    email_verification_expires_at,
                    password_reset_token,
                    password_reset_expires_at,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    email = excluded.email,
                    locale = excluded.locale,
                    password_hash = excluded.password_hash,
                    auth_provider = excluded.auth_provider,
                    email_verified = excluded.email_verified,
                    email_verification_token = excluded.email_verification_token,
                    email_verification_expires_at = excluded.email_verification_expires_at,
                    password_reset_token = excluded.password_reset_token,
                    password_reset_expires_at = excluded.password_reset_expires_at,
                    created_at = excluded.created_at
                """,
                (
                    user.user_id,
                    user.email,
                    user.locale,
                    user.password_hash,
                    user.auth_provider,
                    int(user.email_verified),
                    user.email_verification_token,
                    user.email_verification_expires_at.isoformat() if user.email_verification_expires_at else None,
                    user.password_reset_token,
                    user.password_reset_expires_at.isoformat() if user.password_reset_expires_at else None,
                    user.created_at.isoformat(),
                ),
            )
            self._connection.commit()

    def get_user(self, user_id: str) -> Optional[User]:
        in_memory = super().get_user(user_id)
        if in_memory is not None:
            return in_memory

        with self._lock:
            row = self._connection.execute(
                """
                SELECT
                    user_id,
                    email,
                    locale,
                    password_hash,
                    auth_provider,
                    email_verified,
                    email_verification_token,
                    email_verification_expires_at,
                    password_reset_token,
                    password_reset_expires_at,
                    created_at
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        user = User(
            user_id=row["user_id"],
            email=row["email"],
            locale=row["locale"],
            password_hash=row["password_hash"],
            auth_provider=row["auth_provider"] or "guest",
            email_verified=bool(row["email_verified"]),
            email_verification_token=row["email_verification_token"],
            email_verification_expires_at=datetime.fromisoformat(row["email_verification_expires_at"])
            if row["email_verification_expires_at"]
            else None,
            password_reset_token=row["password_reset_token"],
            password_reset_expires_at=datetime.fromisoformat(row["password_reset_expires_at"])
            if row["password_reset_expires_at"]
            else None,
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        super().save_user(user)
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        in_memory = super().get_user_by_email(email)
        if in_memory is not None:
            return in_memory

        normalized = str(email).strip().lower()
        if not normalized:
            return None

        with self._lock:
            row = self._connection.execute(
                """
                SELECT
                    user_id,
                    email,
                    locale,
                    password_hash,
                    auth_provider,
                    email_verified,
                    email_verification_token,
                    email_verification_expires_at,
                    password_reset_token,
                    password_reset_expires_at,
                    created_at
                FROM users
                WHERE email = ?
                LIMIT 1
                """,
                (normalized,),
            ).fetchone()

        if row is None:
            return None

        user = User(
            user_id=row["user_id"],
            email=row["email"],
            locale=row["locale"],
            password_hash=row["password_hash"],
            auth_provider=row["auth_provider"] or "guest",
            email_verified=bool(row["email_verified"]),
            email_verification_token=row["email_verification_token"],
            email_verification_expires_at=datetime.fromisoformat(row["email_verification_expires_at"])
            if row["email_verification_expires_at"]
            else None,
            password_reset_token=row["password_reset_token"],
            password_reset_expires_at=datetime.fromisoformat(row["password_reset_expires_at"])
            if row["password_reset_expires_at"]
            else None,
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        super().save_user(user)
        return user

    def get_user_by_email_verification_token(self, token: str) -> Optional[User]:
        in_memory = super().get_user_by_email_verification_token(token)
        if in_memory is not None:
            return in_memory

        normalized = str(token).strip()
        if not normalized:
            return None

        with self._lock:
            row = self._connection.execute(
                """
                SELECT
                    user_id,
                    email,
                    locale,
                    password_hash,
                    auth_provider,
                    email_verified,
                    email_verification_token,
                    email_verification_expires_at,
                    password_reset_token,
                    password_reset_expires_at,
                    created_at
                FROM users
                WHERE email_verification_token = ?
                LIMIT 1
                """,
                (normalized,),
            ).fetchone()

        if row is None:
            return None

        user = User(
            user_id=row["user_id"],
            email=row["email"],
            locale=row["locale"],
            password_hash=row["password_hash"],
            auth_provider=row["auth_provider"] or "guest",
            email_verified=bool(row["email_verified"]),
            email_verification_token=row["email_verification_token"],
            email_verification_expires_at=datetime.fromisoformat(row["email_verification_expires_at"])
            if row["email_verification_expires_at"]
            else None,
            password_reset_token=row["password_reset_token"],
            password_reset_expires_at=datetime.fromisoformat(row["password_reset_expires_at"])
            if row["password_reset_expires_at"]
            else None,
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        super().save_user(user)
        return user

    def get_user_by_password_reset_token(self, token: str) -> Optional[User]:
        in_memory = super().get_user_by_password_reset_token(token)
        if in_memory is not None:
            return in_memory

        normalized = str(token).strip()
        if not normalized:
            return None

        with self._lock:
            row = self._connection.execute(
                """
                SELECT
                    user_id,
                    email,
                    locale,
                    password_hash,
                    auth_provider,
                    email_verified,
                    email_verification_token,
                    email_verification_expires_at,
                    password_reset_token,
                    password_reset_expires_at,
                    created_at
                FROM users
                WHERE password_reset_token = ?
                LIMIT 1
                """,
                (normalized,),
            ).fetchone()

        if row is None:
            return None

        user = User(
            user_id=row["user_id"],
            email=row["email"],
            locale=row["locale"],
            password_hash=row["password_hash"],
            auth_provider=row["auth_provider"] or "guest",
            email_verified=bool(row["email_verified"]),
            email_verification_token=row["email_verification_token"],
            email_verification_expires_at=datetime.fromisoformat(row["email_verification_expires_at"])
            if row["email_verification_expires_at"]
            else None,
            password_reset_token=row["password_reset_token"],
            password_reset_expires_at=datetime.fromisoformat(row["password_reset_expires_at"])
            if row["password_reset_expires_at"]
            else None,
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        super().save_user(user)
        return user

    def list_users(self, limit: int = 100) -> List[User]:
        safe_limit = max(1, min(int(limit), 500))
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT
                    user_id,
                    email,
                    locale,
                    password_hash,
                    auth_provider,
                    email_verified,
                    email_verification_token,
                    email_verification_expires_at,
                    password_reset_token,
                    password_reset_expires_at,
                    created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()

        users: List[User] = []
        for row in rows:
            user = User(
                user_id=row["user_id"],
                email=row["email"],
                locale=row["locale"],
                password_hash=row["password_hash"],
                auth_provider=row["auth_provider"] or "guest",
                email_verified=bool(row["email_verified"]),
                email_verification_token=row["email_verification_token"],
                email_verification_expires_at=datetime.fromisoformat(row["email_verification_expires_at"])
                if row["email_verification_expires_at"]
                else None,
                password_reset_token=row["password_reset_token"],
                password_reset_expires_at=datetime.fromisoformat(row["password_reset_expires_at"])
                if row["password_reset_expires_at"]
                else None,
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            super().save_user(user)
            users.append(user)

        if users:
            return users
        return super().list_users(limit=safe_limit)

    def add_submission(self, submission: AssessmentSubmission) -> None:
        super().add_submission(submission)
        encrypted_payload = self._encrypt_json(submission.responses)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO assessment_submissions_secure (submission_id, user_id, payload_encrypted, submitted_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    submission.submission_id,
                    submission.user_id,
                    encrypted_payload,
                    submission.submitted_at.isoformat(),
                ),
            )
            self._connection.commit()

    def list_submissions(self, user_id: str) -> List[AssessmentSubmission]:
        cached = super().list_submissions(user_id)
        if cached:
            return cached

        with self._lock:
            rows = self._connection.execute(
                """
                SELECT
                    submission_id,
                    user_id,
                    payload_encrypted,
                    submitted_at
                FROM assessment_submissions_secure
                WHERE user_id = ?
                ORDER BY submitted_at ASC
                """,
                (user_id,),
            ).fetchall()

        hydrated: List[AssessmentSubmission] = []
        for row in rows:
            submission = AssessmentSubmission(
                submission_id=row["submission_id"],
                user_id=row["user_id"],
                responses=self._decrypt_json(row["payload_encrypted"]),
                submitted_at=datetime.fromisoformat(row["submitted_at"]),
            )
            super().add_submission(submission)
            hydrated.append(submission)

        if hydrated:
            return hydrated

        # Legacy fallback for historical plaintext rows.
        with self._lock:
            legacy_rows = self._connection.execute(
                """
                SELECT
                    submission_id,
                    user_id,
                    responses_json,
                    submitted_at
                FROM assessment_submissions
                WHERE user_id = ?
                ORDER BY submitted_at ASC
                """,
                (user_id,),
            ).fetchall()

        migrated: List[AssessmentSubmission] = []
        for row in legacy_rows:
            submission = AssessmentSubmission(
                submission_id=row["submission_id"],
                user_id=row["user_id"],
                responses=json.loads(row["responses_json"]),
                submitted_at=datetime.fromisoformat(row["submitted_at"]),
            )
            migrated.append(submission)
            super().add_submission(submission)
            with self._lock:
                self._connection.execute(
                    """
                    INSERT OR REPLACE INTO assessment_submissions_secure (
                        submission_id,
                        user_id,
                        payload_encrypted,
                        submitted_at
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        submission.submission_id,
                        submission.user_id,
                        self._encrypt_json(submission.responses),
                        submission.submitted_at.isoformat(),
                    ),
                )
                self._connection.execute(
                    "DELETE FROM assessment_submissions WHERE submission_id = ?",
                    (submission.submission_id,),
                )
                self._connection.commit()

        return migrated

    def save_scores(self, user_id: str, scores: AssessmentScoreSet) -> None:
        super().save_scores(user_id, scores)
        encrypted_payload = self._encrypt_json(self._score_payload(scores))
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO assessment_scores_secure (
                    user_id,
                    payload_encrypted,
                    updated_at
                )
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    payload_encrypted = excluded.payload_encrypted,
                    updated_at = excluded.updated_at
                """,
                (
                    user_id,
                    encrypted_payload,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            self._connection.commit()

    def get_scores(self, user_id: str) -> Optional[AssessmentScoreSet]:
        in_memory = super().get_scores(user_id)
        if in_memory is not None:
            return in_memory

        with self._lock:
            row = self._connection.execute(
                """
                SELECT
                    user_id,
                    payload_encrypted
                FROM assessment_scores_secure
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is not None:
            payload = self._decrypt_json(row["payload_encrypted"])
            scores = self._hydrate_score_payload(payload)
            super().save_scores(user_id, scores)
            return scores

        # Legacy fallback for historical plaintext rows.
        with self._lock:
            legacy = self._connection.execute(
                """
                SELECT
                    phq9_score,
                    gad7_score,
                    pss10_score,
                    cssrs_positive,
                    scl90_global_index,
                    scl90_dimension_scores_json,
                    scl90_moderate_or_above
                FROM assessment_scores
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if legacy is None:
            return None

        scores = AssessmentScoreSet(
            phq9_score=int(legacy["phq9_score"]),
            gad7_score=int(legacy["gad7_score"]),
            pss10_score=int(legacy["pss10_score"]),
            cssrs_positive=bool(legacy["cssrs_positive"]),
            scl90_global_index=float(legacy["scl90_global_index"])
            if legacy["scl90_global_index"] is not None
            else None,
            scl90_dimension_scores=json.loads(legacy["scl90_dimension_scores_json"])
            if legacy["scl90_dimension_scores_json"]
            else None,
            scl90_moderate_or_above=bool(legacy["scl90_moderate_or_above"]),
        )
        super().save_scores(user_id, scores)
        with self._lock:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO assessment_scores_secure (user_id, payload_encrypted, updated_at)
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    self._encrypt_json(self._score_payload(scores)),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            self._connection.execute("DELETE FROM assessment_scores WHERE user_id = ?", (user_id,))
            self._connection.commit()

        return scores

    def save_triage(self, user_id: str, decision: TriageDecision) -> None:
        super().save_triage(user_id, decision)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO triage_decisions (
                    user_id,
                    channel,
                    reasons_json,
                    halt_coaching,
                    show_hotline,
                    dialogue_risk_level
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    channel = excluded.channel,
                    reasons_json = excluded.reasons_json,
                    halt_coaching = excluded.halt_coaching,
                    show_hotline = excluded.show_hotline,
                    dialogue_risk_level = excluded.dialogue_risk_level
                """,
                (
                    user_id,
                    decision.channel.value,
                    json.dumps(decision.reasons, ensure_ascii=False),
                    int(decision.halt_coaching),
                    int(decision.show_hotline),
                    decision.dialogue_risk_level.name.lower()
                    if decision.dialogue_risk_level is not None
                    else None,
                ),
            )
            self._connection.commit()

    def get_triage(self, user_id: str) -> Optional[TriageDecision]:
        in_memory = super().get_triage(user_id)
        if in_memory is not None:
            return in_memory

        with self._lock:
            row = self._connection.execute(
                """
                SELECT
                    user_id,
                    channel,
                    reasons_json,
                    halt_coaching,
                    show_hotline,
                    dialogue_risk_level
                FROM triage_decisions
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        risk = row["dialogue_risk_level"]
        dialogue_risk_level = RiskLevel[risk.upper()] if risk else None

        decision = TriageDecision(
            channel=TriageChannel(row["channel"]),
            reasons=list(json.loads(row["reasons_json"])),
            halt_coaching=bool(row["halt_coaching"]),
            show_hotline=bool(row["show_hotline"]),
            dialogue_risk_level=dialogue_risk_level,
        )
        super().save_triage(user_id, decision)
        return decision

    def save_schedule(self, user_id: str, schedule: ReassessmentSchedule) -> None:
        super().save_schedule(user_id, schedule)
        encoded_due_dates = {scale: due.isoformat() for scale, due in schedule.due_dates.items()}

        with self._lock:
            self._connection.execute(
                """
                INSERT INTO reassessment_schedules (user_id, due_dates_json)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    due_dates_json = excluded.due_dates_json
                """,
                (user_id, json.dumps(encoded_due_dates, ensure_ascii=False)),
            )
            self._connection.commit()

    def get_schedule(self, user_id: str) -> Optional[ReassessmentSchedule]:
        in_memory = super().get_schedule(user_id)
        if in_memory is not None:
            return in_memory

        with self._lock:
            row = self._connection.execute(
                "SELECT due_dates_json FROM reassessment_schedules WHERE user_id = ?",
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        due_dates_payload = json.loads(row["due_dates_json"])
        schedule = ReassessmentSchedule(
            due_dates={scale: date.fromisoformat(due) for scale, due in due_dates_payload.items()}
        )
        super().save_schedule(user_id, schedule)
        return schedule

    def save_test_result(self, result: TestResult) -> None:
        super().save_test_result(result)
        encrypted_payload = self._encrypt_json(
            {
                "answers": result.answers,
                "summary": result.summary,
            }
        )

        with self._lock:
            self._connection.execute(
                """
                INSERT INTO test_results_secure (
                    result_id,
                    user_id,
                    test_id,
                    payload_encrypted,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(result_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    test_id = excluded.test_id,
                    payload_encrypted = excluded.payload_encrypted,
                    created_at = excluded.created_at
                """,
                (
                    result.result_id,
                    result.user_id,
                    result.test_id,
                    encrypted_payload,
                    result.created_at.isoformat(),
                ),
            )
            self._connection.commit()

    def get_test_result(self, result_id: str) -> Optional[TestResult]:
        in_memory = super().get_test_result(result_id)
        if in_memory is not None:
            return in_memory

        with self._lock:
            row = self._connection.execute(
                """
                SELECT
                    result_id,
                    user_id,
                    test_id,
                    payload_encrypted,
                    created_at
                FROM test_results_secure
                WHERE result_id = ?
                """,
                (result_id,),
            ).fetchone()

        if row is not None:
            result = self._hydrate_secure_test_result(row)
            super().save_test_result(result)
            return result

        with self._lock:
            legacy = self._connection.execute(
                """
                SELECT
                    result_id,
                    user_id,
                    test_id,
                    answers_json,
                    summary_json,
                    created_at
                FROM test_results
                WHERE result_id = ?
                """,
                (result_id,),
            ).fetchone()

        if legacy is None:
            return None

        result = self._hydrate_test_result(legacy)
        super().save_test_result(result)
        with self._lock:
            self._connection.execute(
                """
                INSERT OR REPLACE INTO test_results_secure (
                    result_id,
                    user_id,
                    test_id,
                    payload_encrypted,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    result.result_id,
                    result.user_id,
                    result.test_id,
                    self._encrypt_json({"answers": result.answers, "summary": result.summary}),
                    result.created_at.isoformat(),
                ),
            )
            self._connection.execute("DELETE FROM test_results WHERE result_id = ?", (result_id,))
            self._connection.commit()
        return result

    def list_user_test_results(self, user_id: str) -> List[TestResult]:
        cached = super().list_user_test_results(user_id)
        if cached:
            return cached

        with self._lock:
            rows = self._connection.execute(
                """
                SELECT
                    result_id,
                    user_id,
                    test_id,
                    payload_encrypted,
                    created_at
                FROM test_results_secure
                WHERE user_id = ?
                ORDER BY created_at ASC
                """,
                (user_id,),
            ).fetchall()

        hydrated: List[TestResult] = []
        for row in rows:
            result = self._hydrate_secure_test_result(row)
            super().save_test_result(result)
            hydrated.append(result)

        if hydrated:
            return hydrated

        with self._lock:
            legacy_rows = self._connection.execute(
                """
                SELECT
                    result_id,
                    user_id,
                    test_id,
                    answers_json,
                    summary_json,
                    created_at
                FROM test_results
                WHERE user_id = ?
                ORDER BY created_at ASC
                """,
                (user_id,),
            ).fetchall()

        migrated: List[TestResult] = []
        for row in legacy_rows:
            result = self._hydrate_test_result(row)
            migrated.append(result)
            super().save_test_result(result)
            with self._lock:
                self._connection.execute(
                    """
                    INSERT OR REPLACE INTO test_results_secure (
                        result_id,
                        user_id,
                        test_id,
                        payload_encrypted,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        result.result_id,
                        result.user_id,
                        result.test_id,
                        self._encrypt_json({"answers": result.answers, "summary": result.summary}),
                        result.created_at.isoformat(),
                    ),
                )
                self._connection.execute("DELETE FROM test_results WHERE result_id = ?", (result.result_id,))
                self._connection.commit()

        return migrated

    def _hydrate_test_result(self, row: sqlite3.Row) -> TestResult:
        return TestResult(
            result_id=row["result_id"],
            user_id=row["user_id"],
            test_id=row["test_id"],
            answers=json.loads(row["answers_json"]),
            summary=json.loads(row["summary_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _hydrate_secure_test_result(self, row: sqlite3.Row) -> TestResult:
        payload = self._decrypt_json(row["payload_encrypted"])
        return TestResult(
            result_id=row["result_id"],
            user_id=row["user_id"],
            test_id=row["test_id"],
            answers=dict(payload.get("answers", {})),
            summary=dict(payload.get("summary", {})),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def save_coach_session(self, session: CoachSession) -> None:
        super().save_coach_session(session)
        encrypted_turns = self._encrypt_json(self._serialize_turns(session.turns))
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO coach_sessions_secure (
                    session_id,
                    user_id,
                    style_id,
                    started_at,
                    ended_at,
                    active,
                    halted_for_safety,
                    turns_encrypted
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    style_id = excluded.style_id,
                    started_at = excluded.started_at,
                    ended_at = excluded.ended_at,
                    active = excluded.active,
                    halted_for_safety = excluded.halted_for_safety,
                    turns_encrypted = excluded.turns_encrypted
                """,
                (
                    session.session_id,
                    session.user_id,
                    session.style_id,
                    session.started_at.isoformat(),
                    session.ended_at.isoformat() if session.ended_at else None,
                    int(session.active),
                    int(session.halted_for_safety),
                    encrypted_turns,
                ),
            )
            self._connection.commit()

    def get_coach_session(self, session_id: str) -> Optional[CoachSession]:
        in_memory = super().get_coach_session(session_id)
        if in_memory is not None:
            return in_memory

        with self._lock:
            row = self._connection.execute(
                """
                SELECT
                    session_id,
                    user_id,
                    style_id,
                    started_at,
                    ended_at,
                    active,
                    halted_for_safety,
                    turns_encrypted
                FROM coach_sessions_secure
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()

        if row is None:
            return None

        session = self._hydrate_secure_coach_session(row)
        super().save_coach_session(session)
        return session

    def list_user_coach_sessions(self, user_id: str) -> List[CoachSession]:
        cached = super().list_user_coach_sessions(user_id)
        if cached:
            return cached

        with self._lock:
            rows = self._connection.execute(
                """
                SELECT
                    session_id,
                    user_id,
                    style_id,
                    started_at,
                    ended_at,
                    active,
                    halted_for_safety,
                    turns_encrypted
                FROM coach_sessions_secure
                WHERE user_id = ?
                ORDER BY started_at ASC
                """,
                (user_id,),
            ).fetchall()

        hydrated: List[CoachSession] = []
        for row in rows:
            session = self._hydrate_secure_coach_session(row)
            super().save_coach_session(session)
            hydrated.append(session)

        return hydrated

    def _hydrate_secure_coach_session(self, row: sqlite3.Row) -> CoachSession:
        raw_turns = self._decrypt_json(row["turns_encrypted"])
        turns_payload = raw_turns if isinstance(raw_turns, list) else []
        return CoachSession(
            session_id=row["session_id"],
            user_id=row["user_id"],
            style_id=row["style_id"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
            active=bool(row["active"]),
            halted_for_safety=bool(row["halted_for_safety"]),
            turns=self._hydrate_turns(turns_payload),
        )

    def save_admin_session(self, session: AdminSession) -> None:
        super().save_admin_session(session)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO admin_sessions (session_id, username, created_at, expires_at, revoked)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    username = excluded.username,
                    created_at = excluded.created_at,
                    expires_at = excluded.expires_at,
                    revoked = excluded.revoked
                """,
                (
                    session.session_id,
                    session.username,
                    session.created_at.isoformat(),
                    session.expires_at.isoformat(),
                    int(session.revoked),
                ),
            )
            self._connection.commit()

    def get_admin_session(self, session_id: str) -> Optional[AdminSession]:
        in_memory = super().get_admin_session(session_id)
        if in_memory is not None:
            return in_memory

        with self._lock:
            row = self._connection.execute(
                """
                SELECT session_id, username, created_at, expires_at, revoked
                FROM admin_sessions
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()

        if row is None:
            return None

        session = AdminSession(
            session_id=row["session_id"],
            username=row["username"],
            created_at=datetime.fromisoformat(row["created_at"]),
            expires_at=datetime.fromisoformat(row["expires_at"]),
            revoked=bool(row["revoked"]),
        )
        super().save_admin_session(session)
        return session

    def revoke_admin_session(self, session_id: str) -> None:
        super().revoke_admin_session(session_id)
        with self._lock:
            self._connection.execute(
                "UPDATE admin_sessions SET revoked = 1 WHERE session_id = ?",
                (session_id,),
            )
            self._connection.commit()

    def save_api_audit_log(self, record: APIAuditLogRecord) -> None:
        super().save_api_audit_log(record)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO api_audit_logs (
                    request_id,
                    method,
                    path,
                    status_code,
                    duration_ms,
                    request_payload_json,
                    response_payload_json,
                    user_id,
                    client_ref,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.request_id,
                    record.method,
                    record.path,
                    int(record.status_code),
                    float(record.duration_ms),
                    json.dumps(record.request_payload, ensure_ascii=False),
                    json.dumps(record.response_payload, ensure_ascii=False),
                    record.user_id,
                    record.client_ref,
                    record.created_at.isoformat(),
                ),
            )
            self._connection.commit()

    def list_api_audit_logs(self) -> List[APIAuditLogRecord]:
        cached = super().list_api_audit_logs()
        if cached:
            return cached

        with self._lock:
            rows = self._connection.execute(
                """
                SELECT
                    request_id,
                    method,
                    path,
                    status_code,
                    duration_ms,
                    request_payload_json,
                    response_payload_json,
                    user_id,
                    client_ref,
                    created_at
                FROM api_audit_logs
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()

        hydrated: List[APIAuditLogRecord] = []
        for row in rows:
            record = APIAuditLogRecord(
                request_id=row["request_id"],
                method=row["method"],
                path=row["path"],
                status_code=int(row["status_code"]),
                duration_ms=float(row["duration_ms"]),
                request_payload=json.loads(row["request_payload_json"]),
                response_payload=json.loads(row["response_payload_json"]),
                user_id=row["user_id"],
                client_ref=row["client_ref"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
            super().save_api_audit_log(record)
            hydrated.append(record)

        return hydrated

    def erase_user_data(self, user_id: str) -> Dict[str, int]:
        with self._lock:
            persisted_counts = {
                "assessment_submissions": self._count_rows("assessment_submissions", user_id),
                "assessment_submissions_secure": self._count_rows("assessment_submissions_secure", user_id),
                "assessment_scores": self._count_rows("assessment_scores", user_id),
                "assessment_scores_secure": self._count_rows("assessment_scores_secure", user_id),
                "triage_decisions": self._count_rows("triage_decisions", user_id),
                "reassessment_schedules": self._count_rows("reassessment_schedules", user_id),
                "test_results": self._count_rows("test_results", user_id),
                "test_results_secure": self._count_rows("test_results_secure", user_id),
                "coach_sessions_secure": self._count_rows("coach_sessions_secure", user_id),
                "api_audit_logs": self._count_rows("api_audit_logs", user_id),
                "user": self._count_rows("users", user_id),
            }

            self._connection.execute("DELETE FROM assessment_submissions WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM assessment_submissions_secure WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM assessment_scores WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM assessment_scores_secure WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM triage_decisions WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM reassessment_schedules WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM test_results WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM test_results_secure WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM coach_sessions_secure WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM api_audit_logs WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self._connection.commit()

        in_memory_counts = super().erase_user_data(user_id)

        return {
            **in_memory_counts,
            "assessment_submissions": max(
                in_memory_counts.get("assessment_submissions", 0),
                max(
                    persisted_counts["assessment_submissions"],
                    persisted_counts["assessment_submissions_secure"],
                ),
            ),
            "assessment_scores": max(
                in_memory_counts.get("assessment_scores", 0),
                max(
                    persisted_counts["assessment_scores"],
                    persisted_counts["assessment_scores_secure"],
                ),
            ),
            "triage_decisions": max(
                in_memory_counts.get("triage_decisions", 0),
                persisted_counts["triage_decisions"],
            ),
            "reassessment_schedules": max(
                in_memory_counts.get("reassessment_schedules", 0),
                persisted_counts["reassessment_schedules"],
            ),
            "test_results": max(
                in_memory_counts.get("test_results", 0),
                max(
                    persisted_counts["test_results"],
                    persisted_counts["test_results_secure"],
                ),
            ),
            "coach_sessions": max(
                in_memory_counts.get("coach_sessions", 0),
                persisted_counts["coach_sessions_secure"],
            ),
            "api_audit_logs": max(
                in_memory_counts.get("api_audit_logs", 0),
                persisted_counts["api_audit_logs"],
            ),
            "user": max(in_memory_counts.get("user", 0), persisted_counts["user"]),
        }

    def _count_rows(self, table_name: str, user_id: str) -> int:
        row = self._connection.execute(
            f"SELECT COUNT(*) AS count FROM {table_name} WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return int(row["count"]) if row is not None else 0

    def close(self) -> None:
        with self._lock:
            self._connection.close()
