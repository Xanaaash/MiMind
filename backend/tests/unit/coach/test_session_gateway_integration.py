import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.memory.service import MemoryService
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore
from modules.tests.models import TestResult


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
        memory = MemoryService(self.store)
        memory.index_summary(self.user_id, "Work stress peaks before presentations.")
        memory.index_summary(self.user_id, "I calm down when I breathe slowly.")

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
        self.assertGreaterEqual(chat_body["data"]["model"]["relevant_memory_count"], 1)

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

    def test_chat_continues_when_memory_retrieval_fails(self) -> None:
        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.user_id,
            payload={
                "style_id": "warm_guide",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        session_id = start_body["data"]["session"]["session_id"]

        class BrokenMemoryService:
            def retrieve_relevant(self, user_id: str, query: str, limit: int = 3):
                raise RuntimeError("memory retrieval down")

        self.coach_api._service._memory_service = BrokenMemoryService()  # type: ignore[attr-defined]

        chat_status, chat_body = self.coach_api.post_chat(
            session_id=session_id,
            payload={
                "user_message": "I am worried about work stress again.",
            },
        )
        self.assertEqual(chat_status, 200)
        self.assertEqual(chat_body["data"]["mode"], "coaching")
        self.assertIn("memory_retrieval_error", chat_body["data"]["model"])

    def test_start_session_appends_neuro_adaptation_to_system_prompt(self) -> None:
        self.store.save_test_result(
            TestResult(
                result_id="asrs-high-1",
                user_id=self.user_id,
                test_id="asrs",
                answers={"q1": 4},
                summary={"total": 17, "maxTotal": 24, "level": "high"},
            )
        )

        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.user_id,
            payload={
                "style_id": "action_coach",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        prompt_stack = start_body["data"]["prompt_stack"]
        self.assertIn("additional neurodiversity adaptation guidance", prompt_stack["system"].lower())
        self.assertEqual(prompt_stack["context"]["neurodiversity_scores"]["asrs"]["level"], "high")

    def test_start_session_appends_asd_adaptation_to_system_prompt(self) -> None:
        self.store.save_test_result(
            TestResult(
                result_id="aq10-high-1",
                user_id=self.user_id,
                test_id="aq10",
                answers={"q1": 3},
                summary={"total": 7, "maxTotal": 10, "level": "high"},
            )
        )

        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.user_id,
            payload={
                "style_id": "action_coach",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        prompt_stack = start_body["data"]["prompt_stack"]
        self.assertIn("asd-adapted coaching guidance", prompt_stack["system"].lower())
        self.assertEqual(prompt_stack["context"]["neurodiversity_scores"]["aq10"]["level"], "high")


if __name__ == "__main__":
    unittest.main()
