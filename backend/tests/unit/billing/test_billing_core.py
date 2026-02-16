import unittest
from datetime import datetime, timedelta, timezone

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.endpoints import OnboardingAPI
from modules.billing.service import BillingService
from modules.entitlement.service import EntitlementService
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class BillingCoreUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.billing = BillingService(self.store)
        self.entitlement = EntitlementService()

        _, body = self.onboarding_api.post_register(
            {
                "email": "billing-unit@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.user_id = body["data"]["user_id"]

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

    def test_webhook_idempotency(self) -> None:
        first = self.billing.process_webhook(
            event_id="evt_1",
            event_type="payment.succeeded",
            payload={"user_id": self.user_id, "plan_id": "base"},
        )
        second = self.billing.process_webhook(
            event_id="evt_1",
            event_type="payment.succeeded",
            payload={"user_id": self.user_id, "plan_id": "base"},
        )

        self.assertFalse(first["duplicate"])
        self.assertTrue(second["duplicate"])

    def test_quota_consumption_and_reset(self) -> None:
        self.billing.process_webhook(
            event_id="evt_2",
            event_type="payment.succeeded",
            payload={"user_id": self.user_id, "plan_id": "coach"},
        )

        for _ in range(3):
            self.billing.consume_coach_session(self.user_id)

        subscription = self.billing.get_subscription(self.user_id)
        self.assertEqual(subscription["ai_used_in_cycle"], 3)

        # Force cycle reset timestamp to the past, then run reset.
        raw = self.store.get_subscription(self.user_id)
        raw.cycle_reset_at = datetime.now(timezone.utc) - timedelta(days=1)
        self.billing.run_maintenance()

        after = self.billing.get_subscription(self.user_id)
        self.assertEqual(after["ai_used_in_cycle"], 0)

    def test_entitlement_matrix_for_plan_and_quota(self) -> None:
        triage = self.store.get_triage(self.user_id)

        free_ent = self.entitlement.build_from_state(triage, plan_id="free", ai_quota_remaining=0)
        coach_ent = self.entitlement.build_from_state(triage, plan_id="coach", ai_quota_remaining=2)
        exhausted_ent = self.entitlement.build_from_state(triage, plan_id="coach", ai_quota_remaining=0)

        self.assertFalse(free_ent["ai_coaching_enabled"])
        self.assertTrue(coach_ent["ai_coaching_enabled"])
        self.assertFalse(exhausted_ent["ai_coaching_enabled"])


if __name__ == "__main__":
    unittest.main()
