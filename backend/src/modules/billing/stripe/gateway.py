from __future__ import annotations

import hashlib
import hmac
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Tuple

from modules.billing.stripe.config import StripeBillingConfig


class StripeGateway:
    def __init__(self, config: StripeBillingConfig) -> None:
        self._config = config

    def create_checkout_session(self, user_id: str, plan_id: str, email: str) -> dict:
        if not self._config.secret_key:
            raise ValueError("STRIPE_SECRET_KEY is required when BILLING_PROVIDER=stripe")

        price_id = self._config.plan_price_ids.get(plan_id, "")
        if not price_id:
            raise ValueError(f"Missing Stripe price id for plan: {plan_id}")

        form = {
            "mode": "subscription",
            "success_url": self._config.success_url,
            "cancel_url": self._config.cancel_url,
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
            "client_reference_id": user_id,
            "metadata[user_id]": user_id,
            "metadata[plan_id]": plan_id,
        }
        if email:
            form["customer_email"] = email

        encoded = urllib.parse.urlencode(form).encode("utf-8")
        request = urllib.request.Request(
            "https://api.stripe.com/v1/checkout/sessions",
            data=encoded,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._config.secret_key}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self._config.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detail = ""
            try:
                body = error.read().decode("utf-8", errors="ignore")
                parsed = json.loads(body) if body else {}
                detail = str(parsed.get("error", {}).get("message", "")).strip()
            except Exception:
                detail = ""
            if detail:
                raise ValueError(f"Stripe checkout request failed: {detail}") from error
            raise ValueError("Stripe checkout request failed") from error
        except urllib.error.URLError as error:
            raise ValueError("Stripe checkout request failed") from error

        session_id = str(payload.get("id", "")).strip()
        if not session_id:
            raise ValueError("Stripe checkout request failed")

        return payload

    def verify_webhook_signature(self, raw_body: bytes, signature_header: str) -> None:
        if not self._config.webhook_secret:
            raise ValueError("STRIPE_WEBHOOK_SECRET is required when BILLING_PROVIDER=stripe")
        if not raw_body:
            raise ValueError("Stripe webhook body is required")
        timestamp, signatures = self._parse_signature_header(signature_header)
        if not timestamp or not signatures:
            raise ValueError("Invalid Stripe signature")

        now = int(time.time())
        if abs(now - timestamp) > self._config.webhook_tolerance_seconds:
            raise ValueError("Stripe signature timestamp outside tolerance")

        signed_payload = f"{timestamp}.".encode("utf-8") + raw_body
        expected = hmac.new(
            self._config.webhook_secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()
        if not any(hmac.compare_digest(expected, candidate) for candidate in signatures):
            raise ValueError("Invalid Stripe signature")

    @staticmethod
    def _parse_signature_header(signature_header: str) -> Tuple[int, list]:
        timestamp = 0
        signatures = []
        for pair in str(signature_header).split(","):
            key, _, value = pair.partition("=")
            k = key.strip()
            v = value.strip()
            if not k or not v:
                continue
            if k == "t":
                try:
                    timestamp = int(v)
                except ValueError:
                    timestamp = 0
            elif k == "v1":
                signatures.append(v)
        return timestamp, signatures

    @staticmethod
    def event_to_internal(event: Dict[str, object]) -> Tuple[str, str, dict]:
        event_id = str(event.get("id", "")).strip()
        event_type = str(event.get("type", "")).strip()
        data = event.get("data", {})
        data_object = data.get("object", {}) if isinstance(data, dict) else {}
        metadata = data_object.get("metadata", {}) if isinstance(data_object, dict) else {}

        payload = {
            "user_id": str(metadata.get("user_id", "")).strip()
            or str(data_object.get("client_reference_id", "")).strip(),
            "plan_id": str(metadata.get("plan_id", "")).strip(),
        }

        if event_type == "checkout.session.completed":
            mapped = "payment.succeeded"
        elif event_type in {"checkout.session.expired", "invoice.payment_failed"}:
            mapped = "payment.failed"
        else:
            mapped = "stripe.event.received"

        return event_id, mapped, payload
