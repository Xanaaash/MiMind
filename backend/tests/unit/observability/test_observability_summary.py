import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.observability.service import ModelObservabilityService
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class ObservabilitySummaryUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.obs = ModelObservabilityService(self.store)

    def _seed_records(self) -> None:
        onboarding = OnboardingAPI(service=OnboardingService(self.store))
        coach = CoachAPI(store=self.store)

        _, register = onboarding.post_register(
            {
                "email": "summary@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        user_id = register["data"]["user_id"]
        onboarding.post_assessment(
            user_id=user_id,
            payload={
                "responses": {
                    "phq9": [0] * 9,
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )
        _, start = coach.post_start_session(
            user_id=user_id,
            payload={"style_id": "warm_guide", "subscription_active": True},
        )
        session_id = start["data"]["session"]["session_id"]
        coach.post_chat(session_id=session_id, payload={"user_message": "I feel stressed about work."})

    def test_summary_zero_safe(self) -> None:
        summary = self.obs.summarize_model_invocations()
        self.assertEqual(summary["totals"]["total"], 0)
        self.assertEqual(summary["totals"]["success_rate"], 0.0)
        self.assertEqual(summary["totals"]["p95_latency_ms"], 0.0)

    def test_summary_aggregate_fields(self) -> None:
        self._seed_records()
        summary = self.obs.summarize_model_invocations(limit=50)
        totals = summary["totals"]
        self.assertGreaterEqual(totals["total"], 1)
        self.assertGreaterEqual(totals["success"], 1)
        self.assertIn("coach_generation", summary["by_task_type"])
        self.assertGreaterEqual(totals["avg_latency_ms"], 0.0)
        self.assertGreaterEqual(totals["p95_latency_ms"], 0.0)

    def test_summary_filter_by_task(self) -> None:
        self._seed_records()
        summary = self.obs.summarize_model_invocations(limit=50, task_type="coach_generation")
        self.assertGreaterEqual(summary["totals"]["total"], 1)
        self.assertTrue(all(key == "coach_generation" for key in summary["by_task_type"].keys()))


if __name__ == "__main__":
    unittest.main()
