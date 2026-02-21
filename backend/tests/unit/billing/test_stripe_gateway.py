import hashlib
import hmac
import time
import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.billing.stripe.config import StripeBillingConfig
from modules.billing.stripe.gateway import StripeGateway


class StripeGatewayUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = StripeBillingConfig(
            provider="stripe",
            secret_key="sk_test_123",
            webhook_secret="whsec_test_123",
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            webhook_tolerance_seconds=300,
            timeout_seconds=10,
            plan_price_ids={"base": "price_base", "coach": "price_coach"},
        )
        self.gateway = StripeGateway(self.config)

    def test_event_to_internal_checkout_completed(self) -> None:
        event = {
            "id": "evt_123",
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"user_id": "u-1", "plan_id": "coach"},
                    "client_reference_id": "u-fallback",
                }
            },
        }
        event_id, event_type, payload = self.gateway.event_to_internal(event)
        self.assertEqual(event_id, "evt_123")
        self.assertEqual(event_type, "payment.succeeded")
        self.assertEqual(payload["user_id"], "u-1")
        self.assertEqual(payload["plan_id"], "coach")

    def test_verify_webhook_signature_accepts_valid_header(self) -> None:
        raw_body = b'{"id":"evt_1"}'
        timestamp = int(time.time())
        signed = f"{timestamp}.".encode("utf-8") + raw_body
        signature = hmac.new(
            self.config.webhook_secret.encode("utf-8"),
            signed,
            hashlib.sha256,
        ).hexdigest()

        self.gateway.verify_webhook_signature(raw_body, f"t={timestamp},v1={signature}")

    def test_verify_webhook_signature_rejects_invalid_header(self) -> None:
        with self.assertRaises(ValueError):
            self.gateway.verify_webhook_signature(b"{}", "t=1,v1=invalid")


if __name__ == "__main__":
    unittest.main()
