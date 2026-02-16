import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.compliance.data_governance_service import DataGovernanceService
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore
from modules.tests.service import InteractiveTestsService


class DataGovernanceServiceUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        onboarding = OnboardingService(self.store)

        registration = onboarding.register(
            email="governance@example.com",
            locale="en-US",
            policy_version="2026.02",
        )
        self.user_id = registration["user_id"]

        onboarding.submit_assessment(
            user_id=self.user_id,
            responses={
                "phq9": [0] * 9,
                "gad7": [0] * 7,
                "pss10": [1] * 10,
                "cssrs": {"q1": False, "q2": False},
            },
        )

        tests_service = InteractiveTestsService(self.store)
        tests_service.submit_test(
            user_id=self.user_id,
            test_id="eq",
            answers={
                "self_awareness": 75,
                "self_regulation": 70,
                "empathy": 72,
                "relationship_management": 74,
            },
        )

        self.service = DataGovernanceService(self.store)

    def test_export_contains_assessment_and_test_sections(self) -> None:
        bundle = self.service.export_user_bundle(self.user_id)
        self.assertEqual(bundle["user_id"], self.user_id)
        self.assertIn("generated_at", bundle)
        self.assertIn("assessment", bundle["data"])
        self.assertIn("tests", bundle["data"])
        self.assertEqual(len(bundle["data"]["assessment"]["submissions"]), 1)
        self.assertEqual(len(bundle["data"]["tests"]["results"]), 1)

    def test_erase_is_idempotent(self) -> None:
        first = self.service.erase_user_bundle(self.user_id)
        self.assertGreater(first["total_deleted"], 0)

        second = self.service.erase_user_bundle(self.user_id)
        self.assertEqual(second["total_deleted"], 0)

    def test_export_unknown_user_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.service.export_user_bundle("missing")


if __name__ == "__main__":
    unittest.main()
