from datetime import datetime, timedelta, timezone
from typing import Optional

from modules.storage.in_memory import InMemoryStore


class QuotaService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def consume_coach_session(self, user_id: str) -> dict:
        subscription = self._store.get_subscription(user_id)
        if subscription is None or subscription.status != "active":
            raise ValueError("Active subscription required")

        if subscription.plan_id != "coach":
            raise ValueError("Coach quota is only available on coach plan")

        if subscription.quota_remaining() <= 0:
            raise ValueError("Monthly AI session quota exhausted")

        subscription.ai_used_in_cycle += 1
        return {
            "plan_id": subscription.plan_id,
            "ai_quota_monthly": subscription.ai_quota_monthly,
            "ai_used_in_cycle": subscription.ai_used_in_cycle,
            "ai_quota_remaining": subscription.quota_remaining(),
        }

    def reset_monthly_quotas(self, now: Optional[datetime] = None) -> int:
        now = now or datetime.now(timezone.utc)
        reset_count = 0

        for subscription in self._store.subscriptions.values():
            if subscription.status != "active":
                continue
            if subscription.cycle_reset_at <= now:
                subscription.ai_used_in_cycle = 0
                subscription.cycle_reset_at = now + timedelta(days=30)
                reset_count += 1

        return reset_count
