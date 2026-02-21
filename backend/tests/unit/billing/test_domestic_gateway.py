import hashlib
import hmac
import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.billing.domestic.config import DomesticBillingConfig
from modules.billing.domestic.gateway import DomesticPaymentGateway


class DomesticGatewayUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        config = DomesticBillingConfig(
            alipay_gateway_url="https://alipay.example/pay",
            alipay_notify_secret="ali_secret",
            wechat_gateway_url="https://wechat.example/pay",
            wechat_notify_secret="wx_secret",
        )
        self.gateway = DomesticPaymentGateway(config)

    @staticmethod
    def _sign(payload: dict, secret: str) -> str:
        canonical = "&".join(f"{k}={payload[k]}" for k in sorted(payload.keys()) if payload[k] is not None)
        return hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    def test_create_checkout_returns_qr_url(self) -> None:
        result = self.gateway.create_checkout(
            order_id="ord-1",
            user_id="u-1",
            plan_id="coach",
            payment_channel="wechat_pay",
        )
        self.assertEqual(result["payment_channel"], "wechat_pay")
        self.assertIn("out_trade_no=ord-1", result["checkout_url"])
        self.assertIn("qr_code_url", result)

    def test_verify_signature_accepts_valid_alipay_payload(self) -> None:
        payload = {"notify_id": "n-1", "trade_status": "TRADE_SUCCESS", "user_id": "u-1", "plan_id": "coach"}
        signature = self._sign(payload, "ali_secret")
        self.gateway.verify_signature("alipay", payload, signature)

    def test_to_internal_event_from_wechat_attach(self) -> None:
        event_id, event_type, payload = self.gateway.to_internal_event(
            "wechat_pay",
            {
                "id": "wx-event-1",
                "trade_state": "SUCCESS",
                "attach": "user_id=u-2&plan_id=base",
            },
        )
        self.assertEqual(event_id, "wx-event-1")
        self.assertEqual(event_type, "payment.succeeded")
        self.assertEqual(payload["user_id"], "u-2")
        self.assertEqual(payload["plan_id"], "base")


if __name__ == "__main__":
    unittest.main()
