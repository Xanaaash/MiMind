from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class StripeBillingConfig:
    provider: str
    secret_key: str
    webhook_secret: str
    success_url: str
    cancel_url: str
    webhook_tolerance_seconds: int
    timeout_seconds: int
    plan_price_ids: Dict[str, str]

    @property
    def stripe_enabled(self) -> bool:
        return self.provider == "stripe"


def load_stripe_billing_config() -> StripeBillingConfig:
    provider = os.getenv("BILLING_PROVIDER", "local").strip().lower()
    if provider not in {"local", "stripe", "domestic"}:
        provider = "local"

    tolerance_raw = os.getenv("STRIPE_WEBHOOK_TOLERANCE_SECONDS", "300").strip()
    timeout_raw = os.getenv("STRIPE_TIMEOUT_SECONDS", "10").strip()
    try:
        tolerance = int(tolerance_raw)
    except ValueError:
        tolerance = 300
    tolerance = min(max(tolerance, 60), 3600)

    try:
        timeout = int(timeout_raw)
    except ValueError:
        timeout = 10
    timeout = min(max(timeout, 3), 60)

    return StripeBillingConfig(
        provider=provider,
        secret_key=os.getenv("STRIPE_SECRET_KEY", "").strip(),
        webhook_secret=os.getenv("STRIPE_WEBHOOK_SECRET", "").strip(),
        success_url=os.getenv("STRIPE_CHECKOUT_SUCCESS_URL", "https://example.com/billing/success").strip(),
        cancel_url=os.getenv("STRIPE_CHECKOUT_CANCEL_URL", "https://example.com/billing/cancel").strip(),
        webhook_tolerance_seconds=tolerance,
        timeout_seconds=timeout,
        plan_price_ids={
            "base": os.getenv("STRIPE_PRICE_ID_BASE", "").strip(),
            "coach": os.getenv("STRIPE_PRICE_ID_COACH", "").strip(),
        },
    )
