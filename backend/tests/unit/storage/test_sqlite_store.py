import tempfile
import unittest
from datetime import date

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.models import AssessmentScoreSet, ReassessmentSchedule
from modules.storage.sqlite_store import SQLiteStore
from modules.tests.models import TestResult
from modules.triage.models import RiskLevel, TriageChannel, TriageDecision
from modules.user.models import User


class SQLiteStorePersistenceTests(unittest.TestCase):
    def test_scale_artifacts_persist_across_store_instances(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = f"{temp_dir}/mindcoach.db"

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
            db_path = f"{temp_dir}/mindcoach.db"

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


if __name__ == "__main__":
    unittest.main()
