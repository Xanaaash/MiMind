import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.api.safety_endpoints import SafetyAPI
from modules.onboarding.service import OnboardingService
from modules.safety.detector_service import SafetyDetectorService
from modules.storage.in_memory import InMemoryStore


class CrisisRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.safety_api = SafetyAPI(store=self.store)
        self.coach_api = CoachAPI(store=self.store)
        self.detector = SafetyDetectorService()

        _, body = self.onboarding_api.post_register(
            {
                "email": "crisis-regression@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.user_id = body["data"]["user_id"]

    def test_high_risk_recall_regression_set(self) -> None:
        high_samples = [
            "I want to kill myself tonight",
            "I have a plan to end my life",
            "I will hurt myself right now",
        ]

        hits = 0
        for text in high_samples:
            result = self.detector.detect(text)
            if result.level.value >= 3:
                hits += 1

        recall = hits / len(high_samples)
        self.assertGreaterEqual(recall, 0.99)

    def test_joke_disclaimer_does_not_reduce_response(self) -> None:
        status, body = self.safety_api.post_assess_message(
            self.user_id,
            {
                "text": "I want to die, just kidding",
                "override_signal": {
                    "level": "high",
                    "text": "I want to die",
                    "is_joke": True,
                },
            },
        )
        self.assertEqual(status, 200)
        self.assertTrue(body["data"]["action"]["stop_coaching"])

    def test_dialogue_risk_overrides_green_scale_in_coach_flow(self) -> None:
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
        session_id = start_body["data"]["session"]["session_id"]

        chat_status, chat_body = self.coach_api.post_chat(
            session_id=session_id,
            payload={
                "user_message": "I will kill myself tonight",
            },
        )
        self.assertEqual(chat_status, 200)
        self.assertEqual(chat_body["data"]["mode"], "crisis")


if __name__ == "__main__":
    unittest.main()
