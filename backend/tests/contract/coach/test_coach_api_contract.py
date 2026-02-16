import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class CoachAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.coach_api = CoachAPI(store=self.store)

        self.green_user_id = self._register_user("green@example.com")
        self.yellow_user_id = self._register_user("yellow@example.com")

        self._submit_assessment(self.green_user_id, phq_total=0)
        self._submit_assessment(self.yellow_user_id, phq_total=10)

    def _register_user(self, email: str) -> str:
        status, body = self.onboarding_api.post_register(
            {
                "email": email,
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(status, 201)
        return body["data"]["user_id"]

    def _submit_assessment(self, user_id: str, phq_total: int) -> None:
        phq_answers = [0] * 9
        for idx in range(min(9, phq_total // 2)):
            phq_answers[idx] = 2
        if phq_total % 2 == 1 and phq_total // 2 < 9:
            phq_answers[phq_total // 2] = 1

        status, _ = self.onboarding_api.post_assessment(
            user_id=user_id,
            payload={
                "responses": {
                    "phq9": phq_answers,
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )
        self.assertEqual(status, 200)

    def test_green_user_can_start_chat_and_end_session(self) -> None:
        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.green_user_id,
            payload={
                "style_id": "warm_guide",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        self.assertIn("prompt_stack", start_body["data"])
        self.assertIn("prompt_pack_version", start_body["data"])
        session_id = start_body["data"]["session"]["session_id"]

        chat_status, chat_body = self.coach_api.post_chat(
            session_id=session_id,
            payload={
                "user_message": "I felt stressed after work.",
            },
        )
        self.assertEqual(chat_status, 200)
        self.assertEqual(chat_body["data"]["mode"], "coaching")
        self.assertIn("model", chat_body["data"])
        self.assertIn("provider", chat_body["data"]["model"])
        self.assertIn("task_type", chat_body["data"]["model"])

        end_status, end_body = self.coach_api.post_end_session(session_id)
        self.assertEqual(end_status, 200)
        self.assertIn("summary", end_body["data"])
        self.assertGreaterEqual(len(end_body["data"]["memory_items"]), 1)

    def test_non_green_user_is_blocked(self) -> None:
        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.yellow_user_id,
            payload={
                "style_id": "rational_analysis",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 400)
        self.assertIn("only available for green channel", start_body["error"])


if __name__ == "__main__":
    unittest.main()
