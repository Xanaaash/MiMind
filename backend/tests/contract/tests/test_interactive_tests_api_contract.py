import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.endpoints import OnboardingAPI
from modules.api.tests_endpoints import InteractiveTestsAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class InteractiveTestsAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.tests_api = InteractiveTestsAPI(store=self.store)

        status, body = self.onboarding_api.post_register(
            {
                "email": "tests@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(status, 201)
        self.user_id = body["data"]["user_id"]

    def test_catalog_contract_contains_theory_metadata(self) -> None:
        status, body = self.tests_api.get_catalog()
        self.assertEqual(status, 200)
        self.assertIn("mbti", body["data"])
        self.assertIn("theory_reference", body["data"]["mbti"])
        self.assertIn("eq", body["data"])
        self.assertIn("inner_child", body["data"])
        self.assertIn("boundary", body["data"])
        self.assertIn("psych_age", body["data"])

    def test_submit_report_share_and_pairing_contract(self) -> None:
        submit_status, submit_body = self.tests_api.post_submit(
            user_id=self.user_id,
            payload={
                "test_id": "mbti",
                "answers": {
                    "ei": 60,
                    "sn": -10,
                    "tf": 25,
                    "jp": -30,
                },
            },
        )
        self.assertEqual(submit_status, 200)
        result_id = submit_body["data"]["result_id"]

        locked_status, locked_body = self.tests_api.get_report(
            user_id=self.user_id,
            result_id=result_id,
            subscription_active=False,
        )
        self.assertEqual(locked_status, 200)
        self.assertTrue(locked_body["data"]["is_locked"])

        full_status, full_body = self.tests_api.get_report(
            user_id=self.user_id,
            result_id=result_id,
            subscription_active=True,
        )
        self.assertEqual(full_status, 200)
        self.assertFalse(full_body["data"]["is_locked"])
        self.assertIn("summary", full_body["data"])

        share_status, share_body = self.tests_api.post_share_card(user_id=self.user_id, result_id=result_id)
        self.assertEqual(share_status, 200)
        self.assertEqual(share_body["data"]["format"], "vertical")

        submit_status_2, submit_body_2 = self.tests_api.post_submit(
            user_id=self.user_id,
            payload={
                "test_id": "mbti",
                "answers": {
                    "ei": 50,
                    "sn": -5,
                    "tf": 20,
                    "jp": -10,
                },
            },
        )
        self.assertEqual(submit_status_2, 200)
        result_id_2 = submit_body_2["data"]["result_id"]

        pairing_status, pairing_body = self.tests_api.post_pairing(
            {
                "left_result_id": result_id,
                "right_result_id": result_id_2,
            }
        )
        self.assertEqual(pairing_status, 200)
        self.assertIn("compatibility_score", pairing_body["data"])

    def test_submit_new_test_types_contract(self) -> None:
        cases = [
            (
                "stress_coping",
                {
                    "problem_focused": 70,
                    "emotion_focused": 40,
                    "avoidance": 20,
                    "support_seeking": 60,
                },
                "primary_style",
            ),
            (
                "eq",
                {
                    "self_awareness": 80,
                    "self_regulation": 75,
                    "empathy": 70,
                    "relationship_management": 72,
                },
                "overall_score",
            ),
            (
                "inner_child",
                {
                    "playful": 45,
                    "wounded": 50,
                    "resilient": 78,
                    "protective": 40,
                },
                "primary_profile",
            ),
            (
                "boundary",
                {
                    "emotional": 62,
                    "physical": 65,
                    "digital": 55,
                    "work": 60,
                    "social": 64,
                },
                "boundary_profile",
            ),
            (
                "psych_age",
                {
                    "chronological_age": 31,
                    "curiosity": 68,
                    "emotional_regulation": 62,
                    "social_energy": 70,
                },
                "psychological_age",
            ),
        ]

        for test_id, answers, expected_key in cases:
            status, body = self.tests_api.post_submit(
                user_id=self.user_id,
                payload={
                    "test_id": test_id,
                    "answers": answers,
                },
            )
            self.assertEqual(status, 200)
            self.assertIn(expected_key, body["data"]["summary"])


if __name__ == "__main__":
    unittest.main()
