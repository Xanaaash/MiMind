import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.observability.models import APIAuditLogRecord
from modules.api.coach_endpoints import CoachAPI
from modules.api.endpoints import OnboardingAPI
from modules.api.observability_endpoints import ObservabilityAPI
from modules.api.safety_endpoints import SafetyAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class ModelInvocationObservabilityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.coach_api = CoachAPI(store=self.store)
        self.safety_api = SafetyAPI(store=self.store)
        self.observability_api = ObservabilityAPI(store=self.store)

        _, register_body = self.onboarding_api.post_register(
            {
                "email": "obs@example.com",
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

    def test_invocation_records_contract_and_filters(self) -> None:
        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.user_id,
            payload={
                "style_id": "warm_guide",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        session_id = start_body["data"]["session"]["session_id"]

        chat_status, _ = self.coach_api.post_chat(
            session_id=session_id,
            payload={"user_message": "I feel stressed before my weekly meeting."},
        )
        self.assertEqual(chat_status, 200)

        safety_status, _ = self.safety_api.post_assess_message(
            self.user_id,
            {"text": "I feel hopeless and can't go on."},
        )
        self.assertEqual(safety_status, 200)

        list_status, list_body = self.observability_api.get_model_invocations(limit=20)
        self.assertEqual(list_status, 200)
        data = list_body["data"]
        self.assertGreaterEqual(len(data), 3)
        self.assertIn("trace_id", data[0])
        self.assertIn("task_type", data[0])
        self.assertIn("provider", data[0])
        self.assertIn("estimated_cost_usd", data[0])

        filter_status, filter_body = self.observability_api.get_model_invocations(
            limit=20,
            task_type="coach_generation",
        )
        self.assertEqual(filter_status, 200)
        filtered = filter_body["data"]
        self.assertGreaterEqual(len(filtered), 1)
        self.assertTrue(all(item["task_type"] == "coach_generation" for item in filtered))

    def test_empty_observability_contract(self) -> None:
        fresh = ObservabilityAPI(store=InMemoryStore())
        status, body = fresh.get_model_invocations(limit=10)
        self.assertEqual(status, 200)
        self.assertEqual(body["data"], [])

    def test_summary_contract(self) -> None:
        start_status, start_body = self.coach_api.post_start_session(
            user_id=self.user_id,
            payload={
                "style_id": "warm_guide",
                "subscription_active": True,
            },
        )
        self.assertEqual(start_status, 200)
        session_id = start_body["data"]["session"]["session_id"]
        self.coach_api.post_chat(
            session_id=session_id,
            payload={"user_message": "I feel stressed before work meetings."},
        )

        status, body = self.observability_api.get_model_invocation_summary(limit=50)
        self.assertEqual(status, 200)
        data = body["data"]
        self.assertIn("totals", data)
        self.assertIn("by_task_type", data)
        self.assertIn("by_provider", data)
        self.assertGreaterEqual(data["totals"]["total"], 1)

        filtered_status, filtered_body = self.observability_api.get_model_invocation_summary(
            limit=50,
            task_type="coach_generation",
        )
        self.assertEqual(filtered_status, 200)
        self.assertGreaterEqual(filtered_body["data"]["totals"]["total"], 1)

    def test_api_audit_log_contract(self) -> None:
        self.store.save_api_audit_log(
            APIAuditLogRecord(
                request_id="audit-1",
                method="POST",
                path="/api/register",
                status_code=200,
                duration_ms=10.2,
                request_payload={"body": {"email": "te***@example.com", "password": "se***et"}},
                response_payload={"user_id": "u-1"},
                user_id="u-1",
                client_ref="127.0.0.1",
            )
        )
        self.store.save_api_audit_log(
            APIAuditLogRecord(
                request_id="audit-2",
                method="GET",
                path="/api/health",
                status_code=200,
                duration_ms=2.5,
                request_payload={},
                response_payload={"status": "ok"},
                client_ref="127.0.0.1",
            )
        )

        status, body = self.observability_api.get_api_audit_logs(limit=10, method="POST")
        self.assertEqual(status, 200)
        data = body["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["request_id"], "audit-1")
        self.assertEqual(data[0]["path"], "/api/register")


if __name__ == "__main__":
    unittest.main()
