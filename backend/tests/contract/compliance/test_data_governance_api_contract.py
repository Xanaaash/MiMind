import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.compliance_endpoints import DataGovernanceAPI
from modules.api.endpoints import OnboardingAPI
from modules.api.tests_endpoints import InteractiveTestsAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class DataGovernanceAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.tests_api = InteractiveTestsAPI(store=self.store)
        self.governance_api = DataGovernanceAPI(store=self.store)

        status, body = self.onboarding_api.post_register(
            {
                "email": "contract-governance@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(status, 201)
        self.user_id = body["data"]["user_id"]

        status, _ = self.onboarding_api.post_assessment(
            self.user_id,
            {
                "responses": {
                    "phq9": [0] * 9,
                    "gad7": [0] * 7,
                    "pss10": [1] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )
        self.assertEqual(status, 200)

        status, _ = self.tests_api.post_submit(
            user_id=self.user_id,
            payload={
                "test_id": "eq",
                "answers": {
                    "self_awareness": 75,
                    "self_regulation": 70,
                    "empathy": 72,
                    "relationship_management": 74,
                },
            },
        )
        self.assertEqual(status, 200)

    def test_export_contract(self) -> None:
        status, body = self.governance_api.get_export(self.user_id)
        self.assertEqual(status, 200)

        data = body["data"]
        self.assertEqual(data["user_id"], self.user_id)
        self.assertIn("generated_at", data)
        self.assertIn("assessment", data["data"])
        self.assertIn("tests", data["data"])

    def test_erase_contract_is_idempotent(self) -> None:
        first_status, first_body = self.governance_api.post_erase(self.user_id)
        self.assertEqual(first_status, 200)
        self.assertGreater(first_body["data"]["total_deleted"], 0)

        second_status, second_body = self.governance_api.post_erase(self.user_id)
        self.assertEqual(second_status, 200)
        self.assertEqual(second_body["data"]["total_deleted"], 0)

    def test_export_unknown_user_contract(self) -> None:
        status, body = self.governance_api.get_export("missing")
        self.assertEqual(status, 400)
        self.assertIn("Unknown user_id", body["error"])


if __name__ == "__main__":
    unittest.main()
