from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from modules.billing.models import RenewalReminderRecord, SubscriptionRecord
from modules.storage.in_memory import InMemoryStore


class RenewalService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def downgrade_expired_subscriptions(self, now: Optional[datetime] = None) -> int:
        now = now or datetime.now(timezone.utc)
        downgraded = 0
        for user_id, subscription in list(self._store.subscriptions.items()):
            if not self._is_paid_active_subscription(subscription):
                continue
            if subscription.ends_at is None or subscription.ends_at > now:
                continue

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
            downgraded += 1
        return downgraded

    def enqueue_renewal_reminders(self, now: Optional[datetime] = None, window_days: int = 3) -> int:
        now = now or datetime.now(timezone.utc)
        if window_days < 1:
            window_days = 1

        created = 0
        for subscription in list(self._store.subscriptions.values()):
            if not self._is_paid_active_subscription(subscription):
                continue
            if subscription.ends_at is None or subscription.ends_at <= now:
                continue

            days_remaining = (subscription.ends_at.date() - now.date()).days
            if days_remaining < 0 or days_remaining > window_days:
                continue

            sent_at = subscription.renewal_reminder_sent_at
            if sent_at is not None and sent_at.date() == now.date():
                continue

            reminder = RenewalReminderRecord(
                reminder_id=str(uuid.uuid4()),
                user_id=subscription.user_id,
                plan_id=subscription.plan_id,
                due_at=subscription.ends_at,
                reminder_at=now,
                days_remaining=days_remaining,
            )
            self._store.save_renewal_reminder(reminder)
            subscription.renewal_reminder_sent_at = now
            self._store.save_subscription(subscription)
            created += 1

        return created

    @staticmethod
    def _is_paid_active_subscription(subscription: SubscriptionRecord) -> bool:
        if subscription.status != "active":
            return False
        if subscription.trial:
            return False
        return subscription.plan_id in {"base", "coach"}
