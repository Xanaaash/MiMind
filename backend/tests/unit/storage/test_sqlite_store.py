import tempfile
import unittest
import sqlite3
from datetime import date, datetime, timezone

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.models import AssessmentScoreSet, AssessmentSubmission, ReassessmentSchedule
from modules.coach.models import CoachSession, CoachTurn
from modules.observability.models import APIAuditLogRecord
from modules.storage.sqlite_store import SQLiteStore
from modules.tests.models import TestResult
from modules.triage.models import RiskLevel, TriageChannel, TriageDecision
from modules.user.models import User


class SQLiteStorePersistenceTests(unittest.TestCase):
    def test_schema_migrations_recorded_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = f"{temp_dir}/mimind.db"

            store = SQLiteStore(db_path=db_path)
            store.close()

            reopened = SQLiteStore(db_path=db_path)
            reopened.close()

            connection = sqlite3.connect(db_path)
            try:
                rows = connection.execute(
                    """
                    SELECT version, name
                    FROM schema_migrations
                    ORDER BY version ASC
                    """
                ).fetchall()
            finally:
                connection.close()

            versions = [int(version) for version, _ in rows]
            self.assertEqual(versions, [1, 2, 3, 4, 5])
            self.assertEqual(rows[0][1], "baseline_schema")
            self.assertEqual(rows[1][1], "api_audit_logs")
            self.assertEqual(rows[2][1], "user_password_auth_fields")
            self.assertEqual(rows[3][1], "auth_and_audit_compatibility_backfill")
            self.assertEqual(rows[4][1], "encrypted_sensitive_storage")

    def test_api_audit_logs_persist_across_store_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = f"{temp_dir}/mimind.db"

            store_one = SQLiteStore(db_path=db_path)
            store_one.save_api_audit_log(
                APIAuditLogRecord(
                    request_id="req-1",
                    method="POST",
                    path="/api/register",
                    status_code=200,
                    duration_ms=12.3,
                    request_payload={"body": {"email": "te***@example.com"}},
                    response_payload={"user_id": "u-audit"},
                    user_id="u-audit",
                    client_ref="127.0.0.1",
                )
            )
            store_one.close()

            store_two = SQLiteStore(db_path=db_path)
            logs = store_two.list_api_audit_logs()
            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0].request_id, "req-1")
            self.assertEqual(logs[0].path, "/api/register")
            self.assertEqual(logs[0].user_id, "u-audit")
            store_two.close()

    def test_scale_artifacts_persist_across_store_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = f"{temp_dir}/mimind.db"

            store_one = SQLiteStore(db_path=db_path)
            user = User(user_id="u-scale", email="scale@example.com", locale="en-US")
            store_one.save_user(user)
            store_one.save_scores(
                "u-scale",
                AssessmentScoreSet(
                    phq9_score=3,
                    gad7_score=4,
                    pss10_score=12,
                    cssrs_positive=False,
                    scl90_global_index=1.2,
                    scl90_dimension_scores={"depression": 1.5},
                    scl90_moderate_or_above=False,
                ),
            )
            store_one.save_triage(
                "u-scale",
                TriageDecision(
                    channel=TriageChannel.YELLOW,
                    reasons=["moderate_symptoms"],
                    halt_coaching=False,
                    show_hotline=False,
                    dialogue_risk_level=RiskLevel.MEDIUM,
                ),
            )
            store_one.save_schedule(
                "u-scale",
                ReassessmentSchedule(
                    due_dates={
                        "phq9": date(2026, 3, 1),
                        "gad7": date(2026, 3, 1),
                    }
                ),
            )
            store_one.close()

            store_two = SQLiteStore(db_path=db_path)
            restored_user = store_two.get_user("u-scale")
            self.assertIsNotNone(restored_user)
            self.assertEqual(restored_user.email, "scale@example.com")

            restored_scores = store_two.get_scores("u-scale")
            self.assertIsNotNone(restored_scores)
            self.assertEqual(restored_scores.phq9_score, 3)
            self.assertEqual(restored_scores.scl90_dimension_scores["depression"], 1.5)

            restored_triage = store_two.get_triage("u-scale")
            self.assertIsNotNone(restored_triage)
            self.assertEqual(restored_triage.channel, TriageChannel.YELLOW)
            self.assertEqual(restored_triage.dialogue_risk_level, RiskLevel.MEDIUM)

            restored_schedule = store_two.get_schedule("u-scale")
            self.assertIsNotNone(restored_schedule)
            self.assertEqual(restored_schedule.due_dates["phq9"], date(2026, 3, 1))
            store_two.close()

    def test_test_results_persist_across_store_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = f"{temp_dir}/mimind.db"

            store_one = SQLiteStore(db_path=db_path)
            result = TestResult(
                result_id="r-1",
                user_id="u-test",
                test_id="eq",
                answers={
                    "self_awareness": 70,
                    "self_regulation": 72,
                    "empathy": 74,
                    "relationship_management": 76,
                },
                summary={"overall_score": 73.0, "level": "high"},
            )
            store_one.save_test_result(result)
            store_one.close()

            store_two = SQLiteStore(db_path=db_path)
            restored = store_two.get_test_result("r-1")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.test_id, "eq")
            self.assertEqual(restored.summary["overall_score"], 73.0)

            user_results = store_two.list_user_test_results("u-test")
            self.assertEqual(len(user_results), 1)
            self.assertEqual(user_results[0].result_id, "r-1")
            store_two.close()

    def test_coach_sessions_persist_across_store_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = f"{temp_dir}/mimind.db"

            store_one = SQLiteStore(db_path=db_path)
            session = CoachSession(
                session_id="s-1",
                user_id="u-coach",
                style_id="warm_guide",
                turns=[
                    CoachTurn(role="user", message="sensitive-coach-message"),
                    CoachTurn(role="coach", message="supportive reply"),
                ],
            )
            store_one.save_coach_session(session)
            store_one.close()

            store_two = SQLiteStore(db_path=db_path)
            restored = store_two.get_coach_session("s-1")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.user_id, "u-coach")
            self.assertEqual(len(restored.turns), 2)
            self.assertEqual(restored.turns[0].message, "sensitive-coach-message")

            history = store_two.list_user_coach_sessions("u-coach")
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0].session_id, "s-1")
            store_two.close()

    def test_sensitive_payloads_are_encrypted_at_rest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = f"{temp_dir}/mimind.db"

            store = SQLiteStore(db_path=db_path)
            store.add_submission(
                AssessmentSubmission(
                    submission_id="sub-secure",
                    user_id="u-secure",
                    responses={"notes": "plaintext-marker-submission"},
                )
            )
            store.save_scores(
                "u-secure",
                AssessmentScoreSet(
                    phq9_score=1,
                    gad7_score=2,
                    pss10_score=3,
                    cssrs_positive=False,
                    scl90_dimension_scores={"marker": 1.0},
                    scl90_moderate_or_above=False,
                ),
            )
            store.save_test_result(
                TestResult(
                    result_id="r-secure",
                    user_id="u-secure",
                    test_id="eq",
                    answers={"marker": "plaintext-marker-test"},
                    summary={"marker": "plaintext-marker-summary"},
                )
            )
            store.save_coach_session(
                CoachSession(
                    session_id="s-secure",
                    user_id="u-secure",
                    style_id="warm_guide",
                    turns=[CoachTurn(role="user", message="plaintext-marker-coach")],
                )
            )
            store.close()

            connection = sqlite3.connect(db_path)
            try:
                submission_cipher = connection.execute(
                    "SELECT payload_encrypted FROM assessment_submissions_secure WHERE submission_id = ?",
                    ("sub-secure",),
                ).fetchone()[0]
                score_cipher = connection.execute(
                    "SELECT payload_encrypted FROM assessment_scores_secure WHERE user_id = ?",
                    ("u-secure",),
                ).fetchone()[0]
                test_cipher = connection.execute(
                    "SELECT payload_encrypted FROM test_results_secure WHERE result_id = ?",
                    ("r-secure",),
                ).fetchone()[0]
                coach_cipher = connection.execute(
                    "SELECT turns_encrypted FROM coach_sessions_secure WHERE session_id = ?",
                    ("s-secure",),
                ).fetchone()[0]
            finally:
                connection.close()

            self.assertNotIn("plaintext-marker-submission", submission_cipher)
            self.assertNotIn("plaintext-marker-test", test_cipher)
            self.assertNotIn("plaintext-marker-summary", test_cipher)
            self.assertNotIn("plaintext-marker-coach", coach_cipher)
            self.assertTrue(str(score_cipher).startswith("enc:v1:"))

    def test_erase_user_data_removes_persisted_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = f"{temp_dir}/mimind.db"

            store = SQLiteStore(db_path=db_path)
            store.save_user(User(user_id="u-erase", email="erase@example.com", locale="en-US"))
            store.add_submission(
                AssessmentSubmission(
                    submission_id="sub-1",
                    user_id="u-erase",
                    responses={"phq9": [1] * 9},
                    submitted_at=datetime.now(timezone.utc),
                )
            )
            store.save_scores(
                "u-erase",
                AssessmentScoreSet(
                    phq9_score=9,
                    gad7_score=7,
                    pss10_score=10,
                    cssrs_positive=False,
                ),
            )
            store.save_triage(
                "u-erase",
                TriageDecision(channel=TriageChannel.GREEN, reasons=["baseline_green"]),
            )
            store.save_schedule(
                "u-erase",
                ReassessmentSchedule(due_dates={"phq9": date(2026, 3, 1)}),
            )
            store.save_test_result(
                TestResult(
                    result_id="r-erase",
                    user_id="u-erase",
                    test_id="eq",
                    answers={
                        "self_awareness": 70,
                        "self_regulation": 72,
                        "empathy": 74,
                        "relationship_management": 76,
                    },
                    summary={"overall_score": 73.0, "level": "high"},
                )
            )
            store.save_api_audit_log(
                APIAuditLogRecord(
                    request_id="req-erase",
                    method="POST",
                    path="/api/assessment/u-erase",
                    status_code=200,
                    duration_ms=8.5,
                    request_payload={"body": {"phq9": [1] * 9}},
                    response_payload={"triage": {"channel": "green"}},
                    user_id="u-erase",
                    client_ref="127.0.0.1",
                )
            )

            deleted = store.erase_user_data("u-erase")
            self.assertEqual(deleted["user"], 1)
            self.assertEqual(deleted["assessment_submissions"], 1)
            self.assertEqual(deleted["assessment_scores"], 1)
            self.assertEqual(deleted["test_results"], 1)
            self.assertEqual(deleted["api_audit_logs"], 1)
            self.assertEqual(deleted["coach_sessions"], 0)

            store.close()

            restored = SQLiteStore(db_path=db_path)
            self.assertIsNone(restored.get_user("u-erase"))
            self.assertEqual(restored.list_submissions("u-erase"), [])
            self.assertIsNone(restored.get_scores("u-erase"))
            self.assertIsNone(restored.get_test_result("r-erase"))
            self.assertEqual(sum(restored.erase_user_data("u-erase").values()), 0)
            restored.close()


if __name__ == "__main__":
    unittest.main()
