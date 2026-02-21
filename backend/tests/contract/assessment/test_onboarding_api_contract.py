import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.endpoints import OnboardingAPI


class OnboardingAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = OnboardingAPI()

    def _base_responses(self) -> dict:
        return {
            "phq9": [0] * 9,
            "gad7": [0] * 7,
            "pss10": [0] * 10,
            "cssrs": {"q1": False, "q2": False, "q3": False},
        }

    def test_register_contract_returns_user_and_consent(self) -> None:
        status, body = self.api.post_register(
            {
                "email": "user@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )

        self.assertEqual(status, 201)
        self.assertIn("data", body)
        self.assertIn("user_id", body["data"])
        self.assertIn("consent_id", body["data"])

    def test_assessment_contract_returns_scores_triage_and_due_dates(self) -> None:
        register_status, register_body = self.api.post_register(
            {
                "email": "user2@example.com",
                "locale": "zh-CN",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(register_status, 201)
        user_id = register_body["data"]["user_id"]

        status, body = self.api.post_assessment(
            user_id=user_id,
            payload={
                "responses": self._base_responses(),
            },
        )

        self.assertEqual(status, 200)
        self.assertIn("scores", body["data"])
        self.assertIn("triage", body["data"])
        self.assertIn("reassessment_due", body["data"])

    def test_reassessment_schedule_contract_returns_due_dates(self) -> None:
        register_status, register_body = self.api.post_register(
            {
                "email": "user3@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(register_status, 201)
        user_id = register_body["data"]["user_id"]

        assessment_status, _ = self.api.post_assessment(
            user_id=user_id,
            payload={"responses": self._base_responses()},
        )
        self.assertEqual(assessment_status, 200)

        schedule_status, schedule_body = self.api.get_reassessment_schedule(user_id)
        self.assertEqual(schedule_status, 200)
        self.assertIn("due_dates", schedule_body["data"])
        self.assertIn("phq9", schedule_body["data"]["due_dates"])

    def test_entitlement_contract_blocks_ai_for_non_green(self) -> None:
        _, register_body = self.api.post_register(
            {
                "email": "risk@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        user_id = register_body["data"]["user_id"]

        risky = self._base_responses()
        risky["phq9"] = [2] * 5 + [0] * 4  # total 10 -> yellow
        status, _ = self.api.post_assessment(user_id=user_id, payload={"responses": risky})
        self.assertEqual(status, 200)

        ent_status, ent_body = self.api.get_entitlements(user_id)
        self.assertEqual(ent_status, 200)
        self.assertFalse(ent_body["data"]["ai_coaching_enabled"])
        self.assertEqual(ent_body["data"]["channel"], "yellow")

    def test_neurodiversity_payload_does_not_trigger_triage_without_core_threshold(self) -> None:
        _, register_body = self.api.post_register(
            {
                "email": "neuro@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        user_id = register_body["data"]["user_id"]

        responses = self._base_responses()
        responses["asrs"] = [3] * 18
        responses["aq10"] = [1] * 10
        responses["hsp"] = [4] * 12
        responses["catq"] = [7] * 25

        status, body = self.api.post_assessment(
            user_id=user_id,
            payload={"responses": responses},
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["data"]["triage"]["channel"], "green")


if __name__ == "__main__":
    unittest.main()
