import json
import os
import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.billing_endpoints import BillingAPI
from modules.api.endpoints import OnboardingAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class BillingAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.billing_api = BillingAPI(store=self.store)

        self.green_user_id = self._register("green-billing@example.com")
        self.yellow_user_id = self._register("yellow-billing@example.com")

        self._assess_green(self.green_user_id)
        self._assess_yellow(self.yellow_user_id)

    def _register(self, email: str) -> str:
        status, body = self.onboarding_api.post_register(
            {
                "email": email,
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(status, 201)
        return body["data"]["user_id"]

    def _assess_green(self, user_id: str) -> None:
        self.onboarding_api.post_assessment(
            user_id=user_id,
            payload={
                "responses": {
                    "phq9": [0] * 9,
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )

    def _assess_yellow(self, user_id: str) -> None:
        self.onboarding_api.post_assessment(
            user_id=user_id,
            payload={
                "responses": {
                    "phq9": [2] * 5 + [0] * 4,  # total 10
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )

    def test_trial_checkout_webhook_and_entitlements(self) -> None:
        trial_status, trial_body = self.billing_api.post_start_trial(self.green_user_id)
        self.assertEqual(trial_status, 200)
        self.assertEqual(trial_body["data"]["plan_id"], "trial_base")

        coach_checkout_status, coach_checkout_body = self.billing_api.post_checkout(
            self.green_user_id,
            {"plan_id": "coach"},
        )
        self.assertEqual(coach_checkout_status, 200)
        self.assertEqual(coach_checkout_body["data"]["status"], "pending_payment")

        webhook_status, webhook_body = self.billing_api.post_webhook(
            {
                "event_id": "evt-contract-1",
                "event_type": "payment.succeeded",
                "payload": {"user_id": self.green_user_id, "plan_id": "coach"},
            }
        )
        self.assertEqual(webhook_status, 200)
        self.assertEqual(webhook_body["data"]["status"], "subscription_activated")

        dup_status, dup_body = self.billing_api.post_webhook(
            {
                "event_id": "evt-contract-1",
                "event_type": "payment.succeeded",
                "payload": {"user_id": self.green_user_id, "plan_id": "coach"},
            }
        )
        self.assertEqual(dup_status, 200)
        self.assertTrue(dup_body["data"]["duplicate"])

        ent_status, ent_body = self.billing_api.get_entitlements(self.green_user_id)
        self.assertEqual(ent_status, 200)
        self.assertTrue(ent_body["data"]["ai_coaching_enabled"])

        for _ in range(8):
            consume_status, _ = self.billing_api.post_consume_coach_session(self.green_user_id)
            self.assertEqual(consume_status, 200)

        ent2_status, ent2_body = self.billing_api.get_entitlements(self.green_user_id)
        self.assertEqual(ent2_status, 200)
        self.assertFalse(ent2_body["data"]["ai_coaching_enabled"])

    def test_yellow_user_cannot_checkout_coach_plan(self) -> None:
        checkout_status, checkout_body = self.billing_api.post_checkout(
            self.yellow_user_id,
            {"plan_id": "coach"},
        )
        self.assertEqual(checkout_status, 400)
        self.assertIn("green channel", checkout_body["error"])

    def test_stripe_event_shape_activates_subscription(self) -> None:
        webhook_status, webhook_body = self.billing_api.post_webhook(
            {
                "id": "evt-stripe-contract-1",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "metadata": {"user_id": self.green_user_id, "plan_id": "coach"},
                    }
                },
            }
        )

        self.assertEqual(webhook_status, 200)
        self.assertEqual(webhook_body["data"]["status"], "subscription_activated")
        self.assertEqual(webhook_body["data"]["provider_event_type"], "checkout.session.completed")

    def test_stripe_provider_requires_valid_signature(self) -> None:
        original_provider = os.environ.get("BILLING_PROVIDER")
        original_webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        try:
            os.environ["BILLING_PROVIDER"] = "stripe"
            os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_signature"
            stripe_api = BillingAPI(store=self.store)

            event = {
                "id": "evt-stripe-contract-2",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "metadata": {"user_id": self.green_user_id, "plan_id": "coach"},
                    }
                },
            }
            raw_body = json.dumps(event, separators=(",", ":")).encode("utf-8")
            webhook_status, webhook_body = stripe_api.post_webhook(
                event,
                raw_body=raw_body,
                stripe_signature="",
            )
            self.assertEqual(webhook_status, 400)
            self.assertIn("signature", webhook_body["error"].lower())
        finally:
            if original_provider is None:
                os.environ.pop("BILLING_PROVIDER", None)
            else:
                os.environ["BILLING_PROVIDER"] = original_provider

            if original_webhook_secret is None:
                os.environ.pop("STRIPE_WEBHOOK_SECRET", None)
            else:
                os.environ["STRIPE_WEBHOOK_SECRET"] = original_webhook_secret


if __name__ == "__main__":
    unittest.main()
