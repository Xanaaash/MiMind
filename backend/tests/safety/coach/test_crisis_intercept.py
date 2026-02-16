import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class CoachCrisisSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.coach_api = CoachAPI(store=self.store)

        _, register_body = self.onboarding_api.post_register(
            {
                "email": "safety@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.user_id = register_body["data"]["user_id"]

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
        self.session_id = start_body["data"]["session"]["session_id"]

    def test_high_risk_with_joke_disclaimer_still_halts_session(self) -> None:
        chat_status, chat_body = self.coach_api.post_chat(
            session_id=self.session_id,
            payload={
                "user_message": "I want to die, just kidding",
                "dialogue_risk": {
                    "level": "high",
                    "text": "I want to die tonight",
                    "is_joke": True,
                },
            },
        )

        self.assertEqual(chat_status, 200)
        self.assertEqual(chat_body["data"]["mode"], "crisis")
        self.assertTrue(chat_body["data"]["halted"])

        second_chat_status, second_chat_body = self.coach_api.post_chat(
            session_id=self.session_id,
            payload={"user_message": "Can we continue?"},
        )
        self.assertEqual(second_chat_status, 400)
        self.assertIn("not active", second_chat_body["error"])

    def test_medium_risk_triggers_safety_pause_without_halt(self) -> None:
        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.user_id,
            payload={
                "style_id": "warm_guide",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        session_id = start_body["data"]["session"]["session_id"]

        chat_status, chat_body = self.coach_api.post_chat(
            session_id=session_id,
            payload={
                "user_message": "I feel unsafe lately.",
                "dialogue_risk": {
                    "level": "medium",
                    "text": "I feel unsafe",
                    "is_joke": False,
                },
            },
        )

        self.assertEqual(chat_status, 200)
        self.assertEqual(chat_body["data"]["mode"], "safety_pause")
        self.assertFalse(chat_body["data"]["halted"])


if __name__ == "__main__":
    unittest.main()
