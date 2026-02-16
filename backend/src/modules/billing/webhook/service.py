from datetime import datetime, timedelta, timezone

from modules.billing.catalog.service import BillingCatalogService
from modules.billing.models import SubscriptionRecord
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import TriageChannel


class WebhookService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._catalog = BillingCatalogService()

    def process_event(self, event_id: str, event_type: str, payload: dict) -> dict:
        if not event_id:
            raise ValueError("event_id is required")

        if self._store.is_webhook_processed(event_id):
            return {
                "duplicate": True,
                "event_id": event_id,
                "status": "ignored",
            }

        user_id = str(payload.get("user_id", "")).strip()
        plan_id = str(payload.get("plan_id", "")).strip()
        now = datetime.now(timezone.utc)

        if event_type == "payment.succeeded":
            if not user_id or not plan_id:
                raise ValueError("payment.succeeded requires user_id and plan_id")

            plan = self._catalog.get_plan(plan_id)
            triage = self._store.get_triage(user_id)
            if plan.plan_id == "coach" and (triage is None or triage.channel != TriageChannel.GREEN):
                self._store.mark_webhook_processed(event_id)
                return {
                    "duplicate": False,
                    "event_id": event_id,
                    "status": "blocked_non_green",
                }

            subscription = SubscriptionRecord(
                user_id=user_id,
                plan_id=plan.plan_id,
                status="active",
                started_at=now,
                ends_at=None,
                trial=False,
                ai_quota_monthly=plan.ai_sessions_per_month,
                ai_used_in_cycle=0,
                cycle_reset_at=now + timedelta(days=30),
            )
            self._store.save_subscription(subscription)
            outcome = "subscription_activated"
        elif event_type == "payment.failed":
            outcome = "payment_failed"
        else:
            outcome = "event_recorded"

        self._store.mark_webhook_processed(event_id)
        return {
            "duplicate": False,
            "event_id": event_id,
            "status": outcome,
        }
