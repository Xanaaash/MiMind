import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.endpoints import OnboardingAPI
from modules.api.safety_endpoints import SafetyAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class SafetyAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.safety_api = SafetyAPI(store=self.store)

        _, body = self.onboarding_api.post_register(
            {
                "email": "safety-contract@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.user_id = body["data"]["user_id"]

    def test_medium_and_high_risk_contract(self) -> None:
        medium_status, medium_body = self.safety_api.post_assess_message(
            self.user_id,
            {
                "text": "I feel hopeless and can't go on.",
            },
        )
        self.assertEqual(medium_status, 200)
        self.assertEqual(medium_body["data"]["action"]["mode"], "safety_pause")
        self.assertTrue(medium_body["data"]["action"]["show_hotline"])

        high_status, high_body = self.safety_api.post_assess_message(
            self.user_id,
            {
                "text": "I will kill myself tonight",
            },
        )
        self.assertEqual(high_status, 200)
        self.assertTrue(high_body["data"]["action"]["stop_coaching"])
        self.assertIsNotNone(high_body["data"]["ops_event"])

    def test_hotline_cache_contract(self) -> None:
        status, body = self.safety_api.get_hotline_cache()
        self.assertEqual(status, 200)
        self.assertIn("en-US", body["data"])
        self.assertIn("default", body["data"])


if __name__ == "__main__":
    unittest.main()
