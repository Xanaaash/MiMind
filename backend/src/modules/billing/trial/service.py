from datetime import datetime, timedelta, timezone
from typing import Optional

from modules.billing.catalog.service import BillingCatalogService
from modules.billing.models import SubscriptionRecord
from modules.storage.in_memory import InMemoryStore


class TrialService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._catalog = BillingCatalogService()

    def start_base_trial(self, user_id: str) -> SubscriptionRecord:
        if self._store.get_user(user_id) is None:
            raise ValueError("Unknown user_id")

        existing = self._store.get_subscription(user_id)
        if existing is not None and existing.status == "active":
            raise ValueError("Active subscription already exists")

        trial_plan = self._catalog.get_plan("trial_base")
        now = datetime.now(timezone.utc)
        trial = SubscriptionRecord(
            user_id=user_id,
            plan_id=trial_plan.plan_id,
            status="active",
            started_at=now,
            ends_at=now + timedelta(days=trial_plan.trial_days),
            trial=True,
            ai_quota_monthly=0,
            ai_used_in_cycle=0,
            cycle_reset_at=now + timedelta(days=30),
        )
        self._store.save_subscription(trial)
        return trial

    def expire_trials(self, now: Optional[datetime] = None) -> int:
        now = now or datetime.now(timezone.utc)
        expired_count = 0

        for user_id, subscription in list(self._store.subscriptions.items()):
            if subscription.trial and subscription.status == "active" and subscription.ends_at is not None:
                if subscription.ends_at <= now:
                    free = SubscriptionRecord(
                        user_id=user_id,
                        plan_id="free",
                        status="active",
                        started_at=now,
                        ends_at=None,
                        trial=False,
                        ai_quota_monthly=0,
                        ai_used_in_cycle=0,
                        cycle_reset_at=now + timedelta(days=30),
                    )
                    self._store.save_subscription(free)
                    expired_count += 1

        return expired_count
