import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.api.tools_endpoints import HealingToolsAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class HealingToolsAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.tools_api = HealingToolsAPI(store=self.store)
        self.coach_api = CoachAPI(store=self.store)

        status, body = self.onboarding_api.post_register(
            {
                "email": "healing@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(status, 201)
        self.user_id = body["data"]["user_id"]

    def test_tools_and_journal_contract(self) -> None:
        _, audio_body = self.tools_api.get_audio_library()
        self.assertIn("rain", audio_body["data"])

        audio_status, audio_start = self.tools_api.post_start_audio(
            self.user_id,
            {
                "track_id": "rain",
                "minutes": 15,
            },
        )
        self.assertEqual(audio_status, 200)
        self.assertEqual(audio_start["data"]["duration_minutes"], 15)

        breathing_status, breathing_body = self.tools_api.post_breathing_session(
            self.user_id,
            {
                "cycles": 4,
            },
        )
        self.assertEqual(breathing_status, 200)
        self.assertEqual(breathing_body["data"]["protocol"], "4-7-8")

        meditation_status, meditation_body = self.tools_api.post_start_meditation(
            self.user_id,
            {
                "meditation_id": "calm-10",
            },
        )
        self.assertEqual(meditation_status, 200)
        self.assertEqual(meditation_body["data"]["meditation_id"], "calm-10")

        journal_status, journal_body = self.tools_api.post_journal_entry(
            self.user_id,
            {
                "mood": "stressed",
                "energy": 4,
                "note": "Long day but manageable",
            },
        )
        self.assertEqual(journal_status, 200)
        self.assertIn("entry", journal_body["data"])

        trend_status, trend_body = self.tools_api.get_journal_trend(self.user_id, 7)
        self.assertEqual(trend_status, 200)
        self.assertEqual(trend_body["data"]["entry_count"], 1)

        stats_status, stats_body = self.tools_api.get_usage_stats(self.user_id)
        self.assertEqual(stats_status, 200)
        self.assertEqual(stats_body["data"]["week_usage_count"], 3)
        self.assertEqual(stats_body["data"]["total_usage_count"], 3)
        self.assertGreater(stats_body["data"]["total_duration_seconds"], 0)

    def test_journal_context_is_available_to_coach_prompt(self) -> None:
        self.tools_api.post_journal_entry(
            self.user_id,
            {
                "mood": "calm",
                "energy": 8,
                "note": "Nice evening walk",
            },
        )

        self.onboarding_api.post_assessment(
            user_id=self.user_id,
            payload={
                "responses": {
                    "phq9": [0] * 9,
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )

        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.user_id,
            payload={
                "style_id": "warm_guide",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        context = start_body["data"]["prompt_stack"]["context"]
        self.assertEqual(context["journal_summary"]["entry_count"], 1)


if __name__ == "__main__":
    unittest.main()
