from __future__ import annotations

import json
import os
import sqlite3
from datetime import date, datetime
from threading import Lock
from typing import Any, Dict, List, Optional

from modules.admin.models import AdminSession
from modules.assessment.models import AssessmentScoreSet, AssessmentSubmission, ReassessmentSchedule
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

    def save_user(self, user: User) -> None:
        super().save_user(user)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO users (user_id, email, locale, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    email = excluded.email,
                    locale = excluded.locale,
                    created_at = excluded.created_at
                """,
                (user.user_id, user.email, user.locale, user.created_at.isoformat()),
            )
            self._connection.commit()

    def get_user(self, user_id: str) -> Optional[User]:
        in_memory = super().get_user(user_id)
        if in_memory is not None:
            return in_memory

        with self._lock:
            row = self._connection.execute(
                "SELECT user_id, email, locale, created_at FROM users WHERE user_id = ?",
                (user_id,),
            ).fetchone()

        if row is None:
            return None

        user = User(
            user_id=row["user_id"],
            email=row["email"],
            locale=row["locale"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        super().save_user(user)
        return user

    def add_submission(self, submission: AssessmentSubmission) -> None:
        super().add_submission(submission)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO assessment_submissions (submission_id, user_id, responses_json, submitted_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    submission.submission_id,
                    submission.user_id,
                    json.dumps(submission.responses, ensure_ascii=False),
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
                    responses_json,
                    submitted_at
                FROM assessment_submissions
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
                responses=json.loads(row["responses_json"]),
                submitted_at=datetime.fromisoformat(row["submitted_at"]),
            )
            super().add_submission(submission)
            hydrated.append(submission)

        return hydrated

    def save_scores(self, user_id: str, scores: AssessmentScoreSet) -> None:
        super().save_scores(user_id, scores)
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO assessment_scores (
                    user_id,
                    phq9_score,
                    gad7_score,
                    pss10_score,
                    cssrs_positive,
                    scl90_global_index,
                    scl90_dimension_scores_json,
                    scl90_moderate_or_above
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    phq9_score = excluded.phq9_score,
                    gad7_score = excluded.gad7_score,
                    pss10_score = excluded.pss10_score,
                    cssrs_positive = excluded.cssrs_positive,
                    scl90_global_index = excluded.scl90_global_index,
                    scl90_dimension_scores_json = excluded.scl90_dimension_scores_json,
                    scl90_moderate_or_above = excluded.scl90_moderate_or_above
                """,
                (
                    user_id,
                    scores.phq9_score,
                    scores.gad7_score,
                    scores.pss10_score,
                    int(scores.cssrs_positive),
                    scores.scl90_global_index,
                    json.dumps(scores.scl90_dimension_scores, ensure_ascii=False)
                    if scores.scl90_dimension_scores is not None
                    else None,
                    int(scores.scl90_moderate_or_above),
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

        if row is None:
            return None

        scores = AssessmentScoreSet(
            phq9_score=int(row["phq9_score"]),
            gad7_score=int(row["gad7_score"]),
            pss10_score=int(row["pss10_score"]),
            cssrs_positive=bool(row["cssrs_positive"]),
            scl90_global_index=float(row["scl90_global_index"])
            if row["scl90_global_index"] is not None
            else None,
            scl90_dimension_scores=json.loads(row["scl90_dimension_scores_json"])
            if row["scl90_dimension_scores_json"]
            else None,
            scl90_moderate_or_above=bool(row["scl90_moderate_or_above"]),
        )
        super().save_scores(user_id, scores)
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

        with self._lock:
            self._connection.execute(
                """
                INSERT INTO test_results (
                    result_id,
                    user_id,
                    test_id,
                    answers_json,
                    summary_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(result_id) DO UPDATE SET
                    user_id = excluded.user_id,
                    test_id = excluded.test_id,
                    answers_json = excluded.answers_json,
                    summary_json = excluded.summary_json,
                    created_at = excluded.created_at
                """,
                (
                    result.result_id,
                    result.user_id,
                    result.test_id,
                    json.dumps(result.answers, ensure_ascii=False),
                    json.dumps(result.summary, ensure_ascii=False),
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
                    answers_json,
                    summary_json,
                    created_at
                FROM test_results
                WHERE result_id = ?
                """,
                (result_id,),
            ).fetchone()

        if row is None:
            return None

        result = self._hydrate_test_result(row)
        super().save_test_result(result)
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
                    answers_json,
                    summary_json,
                    created_at
                FROM test_results
                WHERE user_id = ?
                ORDER BY created_at ASC
                """,
                (user_id,),
            ).fetchall()

        hydrated: List[TestResult] = []
        for row in rows:
            result = self._hydrate_test_result(row)
            super().save_test_result(result)
            hydrated.append(result)

        return hydrated

    def _hydrate_test_result(self, row: sqlite3.Row) -> TestResult:
        return TestResult(
            result_id=row["result_id"],
            user_id=row["user_id"],
            test_id=row["test_id"],
            answers=json.loads(row["answers_json"]),
            summary=json.loads(row["summary_json"]),
            created_at=datetime.fromisoformat(row["created_at"]),
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

    def erase_user_data(self, user_id: str) -> Dict[str, int]:
        with self._lock:
            persisted_counts = {
                "assessment_submissions": self._count_rows("assessment_submissions", user_id),
                "assessment_scores": self._count_rows("assessment_scores", user_id),
                "triage_decisions": self._count_rows("triage_decisions", user_id),
                "reassessment_schedules": self._count_rows("reassessment_schedules", user_id),
                "test_results": self._count_rows("test_results", user_id),
                "user": self._count_rows("users", user_id),
            }

            self._connection.execute("DELETE FROM assessment_submissions WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM assessment_scores WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM triage_decisions WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM reassessment_schedules WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM test_results WHERE user_id = ?", (user_id,))
            self._connection.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            self._connection.commit()

        in_memory_counts = super().erase_user_data(user_id)

        return {
            **in_memory_counts,
            "assessment_submissions": max(
                in_memory_counts.get("assessment_submissions", 0),
                persisted_counts["assessment_submissions"],
            ),
            "assessment_scores": max(
                in_memory_counts.get("assessment_scores", 0),
                persisted_counts["assessment_scores"],
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
                persisted_counts["test_results"],
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
