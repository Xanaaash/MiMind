from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional


@dataclass
class SubscriptionRecord:
    user_id: str
    plan_id: str
    status: str = "active"
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ends_at: Optional[datetime] = None
    trial: bool = False
    ai_quota_monthly: int = 0
    ai_used_in_cycle: int = 0
    cycle_reset_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30))
    renewal_reminder_sent_at: Optional[datetime] = None

    def quota_remaining(self) -> int:
        return max(self.ai_quota_monthly - self.ai_used_in_cycle, 0)


@dataclass
class BillingPlan:
    plan_id: str
    display_name: str
    reports_enabled: bool
    tools_enabled: bool
    ai_sessions_per_month: int
    trial_days: int = 0


@dataclass
class RenewalReminderRecord:
    reminder_id: str
    user_id: str
    plan_id: str
    due_at: datetime
    reminder_at: datetime
    days_remaining: int
