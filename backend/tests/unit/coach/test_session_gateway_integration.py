import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class CoachGatewayIntegrationUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.coach_api = CoachAPI(store=self.store)

        _, register_body = self.onboarding_api.post_register(
            {
                "email": "coach-gateway@example.com",
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

    def test_chat_includes_model_info_when_gateway_succeeds(self) -> None:
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
                "user_message": "I felt stressed after a long meeting.",
            },
        )
        self.assertEqual(chat_status, 200)
        self.assertEqual(chat_body["data"]["mode"], "coaching")
        self.assertIn("model", chat_body["data"])
        self.assertIn("provider", chat_body["data"]["model"])

    def test_chat_falls_back_when_gateway_fails(self) -> None:
        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.user_id,
            payload={
                "style_id": "rational_analysis",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        session_id = start_body["data"]["session"]["session_id"]

        class BrokenGateway:
            def run(self, *args, **kwargs):
                raise RuntimeError("provider outage")

        self.coach_api._service._model_gateway = BrokenGateway()  # type: ignore[attr-defined]

        chat_status, chat_body = self.coach_api.post_chat(
            session_id=session_id,
            payload={
                "user_message": "I felt stressed and want to understand my thoughts.",
            },
        )
        self.assertEqual(chat_status, 200)
        self.assertEqual(chat_body["data"]["mode"], "coaching")
        self.assertEqual(chat_body["data"]["model"]["provider"], "fallback-local-template")
        self.assertIn("error", chat_body["data"]["model"])


if __name__ == "__main__":
    unittest.main()
