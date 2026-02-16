import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.billing_endpoints import BillingAPI
from modules.api.endpoints import OnboardingAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class CoachChannelRestrictionSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.billing_api = BillingAPI(store=self.store)

        self.yellow_user_id = self._register("safety-yellow@example.com")
        self.red_user_id = self._register("safety-red@example.com")

        self._assess_yellow(self.yellow_user_id)
        self._assess_red(self.red_user_id)

    def _register(self, email: str) -> str:
        _, body = self.onboarding_api.post_register(
            {
                "email": email,
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        return body["data"]["user_id"]

    def _assess_yellow(self, user_id: str) -> None:
        self.onboarding_api.post_assessment(
            user_id=user_id,
            payload={
                "responses": {
                    "phq9": [2] * 5 + [0] * 4,
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )

    def _assess_red(self, user_id: str) -> None:
        self.onboarding_api.post_assessment(
            user_id=user_id,
            payload={
                "responses": {
                    "phq9": [3] * 7 + [0, 0],
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )

    def test_coach_checkout_blocked_for_yellow_and_red(self) -> None:
        y_status, _ = self.billing_api.post_checkout(self.yellow_user_id, {"plan_id": "coach"})
        r_status, _ = self.billing_api.post_checkout(self.red_user_id, {"plan_id": "coach"})
        self.assertEqual(y_status, 400)
        self.assertEqual(r_status, 400)

    def test_coach_webhook_activation_blocked_for_non_green(self) -> None:
        y_status, y_body = self.billing_api.post_webhook(
            {
                "event_id": "evt-safe-y",
                "event_type": "payment.succeeded",
                "payload": {"user_id": self.yellow_user_id, "plan_id": "coach"},
            }
        )
        r_status, r_body = self.billing_api.post_webhook(
            {
                "event_id": "evt-safe-r",
                "event_type": "payment.succeeded",
                "payload": {"user_id": self.red_user_id, "plan_id": "coach"},
            }
        )

        self.assertEqual(y_status, 200)
        self.assertEqual(r_status, 200)
        self.assertEqual(y_body["data"]["status"], "blocked_non_green")
        self.assertEqual(r_body["data"]["status"], "blocked_non_green")


if __name__ == "__main__":
    unittest.main()
