from __future__ import annotations

import hashlib
import hmac
import urllib.parse
from typing import Dict, Optional, Tuple

from modules.billing.domestic.config import DomesticBillingConfig


class DomesticPaymentGateway:
    CHANNEL_ALIPAY = "alipay"
    CHANNEL_WECHAT = "wechat_pay"

    def __init__(self, config: DomesticBillingConfig) -> None:
        self._config = config

    @staticmethod
    def normalize_channel(channel: str) -> str:
        normalized = str(channel).strip().lower()
        if normalized in {"wechat", "wechatpay", "wxpay"}:
            return DomesticPaymentGateway.CHANNEL_WECHAT
        return normalized

    def create_checkout(self, order_id: str, user_id: str, plan_id: str, payment_channel: str) -> dict:
        channel = self.normalize_channel(payment_channel)
        if channel not in {self.CHANNEL_ALIPAY, self.CHANNEL_WECHAT}:
            raise ValueError("payment_channel must be alipay or wechat_pay")

        query = urllib.parse.urlencode(
            {
                "out_trade_no": order_id,
                "user_id": user_id,
                "plan_id": plan_id,
            }
        )
        if channel == self.CHANNEL_ALIPAY:
            checkout_url = f"{self._config.alipay_gateway_url}?{query}"
        else:
            checkout_url = f"{self._config.wechat_gateway_url}?{query}"

        return {
            "payment_channel": channel,
            "checkout_url": checkout_url,
            "qr_code_url": checkout_url,
        }

    def verify_signature(self, payment_channel: str, payload: Dict[str, object], signature: str) -> None:
        channel = self.normalize_channel(payment_channel)
        if channel == self.CHANNEL_ALIPAY:
            secret = self._config.alipay_notify_secret
        elif channel == self.CHANNEL_WECHAT:
            secret = self._config.wechat_notify_secret
        else:
            raise ValueError("Unsupported domestic payment channel")

        if not secret:
            raise ValueError(f"{channel} notify secret is required")

        canonical = self._canonical_payload(payload)
        expected = hmac.new(
            secret.encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, str(signature).strip()):
            raise ValueError("Invalid domestic payment signature")

    def to_internal_event(self, payment_channel: str, payload: Dict[str, object]) -> Tuple[str, str, dict]:
        channel = self.normalize_channel(payment_channel)
        if channel == self.CHANNEL_ALIPAY:
            event_id = str(payload.get("notify_id", "")).strip() or str(payload.get("trade_no", "")).strip()
            trade_status = str(payload.get("trade_status", "")).strip().upper()
            event_type = "payment.succeeded" if trade_status in {"TRADE_SUCCESS", "TRADE_FINISHED"} else "payment.failed"
            user_id = str(payload.get("user_id", "")).strip() or str(payload.get("passback_params", "")).strip()
            plan_id = str(payload.get("plan_id", "")).strip() or str(payload.get("attach_plan_id", "")).strip()
        elif channel == self.CHANNEL_WECHAT:
            event_id = str(payload.get("id", "")).strip() or str(payload.get("transaction_id", "")).strip()
            trade_state = str(payload.get("trade_state", "")).strip().upper()
            event_type = "payment.succeeded" if trade_state == "SUCCESS" else "payment.failed"
            user_id = str(payload.get("user_id", "")).strip() or self._parse_attach_value(payload.get("attach"), "user_id")
            plan_id = str(payload.get("plan_id", "")).strip() or self._parse_attach_value(payload.get("attach"), "plan_id")
        else:
            raise ValueError("Unsupported domestic payment channel")

        return event_id, event_type, {"user_id": user_id, "plan_id": plan_id}

    @staticmethod
    def _canonical_payload(payload: Dict[str, object]) -> str:
        pairs = []
        for key in sorted(payload.keys()):
            value = payload[key]
            if value is None:
                continue
            pairs.append(f"{key}={value}")
        return "&".join(pairs)

    @staticmethod
    def _parse_attach_value(raw_attach: Optional[object], key: str) -> str:
        text = str(raw_attach or "").strip()
        if not text:
            return ""
        parsed = urllib.parse.parse_qs(text, keep_blank_values=True)
        values = parsed.get(key, [])
        return str(values[0]).strip() if values else ""
