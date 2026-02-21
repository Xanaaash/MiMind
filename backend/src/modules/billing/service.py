from datetime import datetime
from typing import Optional

from modules.billing.catalog.service import BillingCatalogService
from modules.billing.checkout.service import CheckoutService
from modules.billing.quota.service import QuotaService
from modules.billing.trial.service import TrialService
from modules.billing.webhook.service import WebhookService
from modules.storage.in_memory import InMemoryStore


class BillingService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._catalog = BillingCatalogService()
        self._checkout = CheckoutService(store)
        self._trial = TrialService(store)
        self._quota = QuotaService(store)
        self._webhook = WebhookService(store)

    def list_plans(self) -> dict:
        catalog = self._catalog.list_plans()
        return {
            plan_id: {
                "display_name": plan.display_name,
                "reports_enabled": plan.reports_enabled,
                "tools_enabled": plan.tools_enabled,
                "ai_sessions_per_month": plan.ai_sessions_per_month,
                "trial_days": plan.trial_days,
            }
            for plan_id, plan in catalog.items()
        }

    def start_trial(self, user_id: str) -> dict:
        subscription = self._trial.start_base_trial(user_id)
        return self._subscription_to_dict(subscription)

    def create_checkout(self, user_id: str, plan_id: str, payment_channel: str = "") -> dict:
        return self._checkout.create_checkout(user_id=user_id, plan_id=plan_id, payment_channel=payment_channel)

    def process_webhook(self, event_id: str, event_type: str, payload: dict) -> dict:
        return self._webhook.process_event(event_id=event_id, event_type=event_type, payload=payload)

    def consume_coach_session(self, user_id: str) -> dict:
        return self._quota.consume_coach_session(user_id)

    def run_maintenance(self, now: Optional[datetime] = None) -> dict:
        expired_trials = self._trial.expire_trials(now=now)
        reset_quotas = self._quota.reset_monthly_quotas(now=now)
        return {
            "expired_trials": expired_trials,
            "reset_quotas": reset_quotas,
        }

    def get_subscription(self, user_id: str) -> Optional[dict]:
        subscription = self._store.get_subscription(user_id)
        if subscription is None:
            return None
        return self._subscription_to_dict(subscription)

    @staticmethod
    def _subscription_to_dict(subscription) -> dict:
        return {
            "user_id": subscription.user_id,
            "plan_id": subscription.plan_id,
            "status": subscription.status,
            "trial": subscription.trial,
            "started_at": subscription.started_at.isoformat(),
            "ends_at": subscription.ends_at.isoformat() if subscription.ends_at else None,
            "ai_quota_monthly": subscription.ai_quota_monthly,
            "ai_used_in_cycle": subscription.ai_used_in_cycle,
            "ai_quota_remaining": subscription.quota_remaining(),
            "cycle_reset_at": subscription.cycle_reset_at.isoformat(),
        }
