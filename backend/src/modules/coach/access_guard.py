from modules.storage.in_memory import InMemoryStore
from modules.triage.models import TriageChannel


class CoachAccessGuard:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def ensure_session_access(self, user_id: str, subscription_active: bool) -> None:
        triage = self._store.get_triage(user_id)
        if triage is None:
            raise ValueError("Triage result required before starting coaching")

        if triage.channel != TriageChannel.GREEN:
            raise ValueError("AI coaching is only available for green channel users")

        subscription = self._store.get_subscription(user_id)
        if subscription is not None:
            if subscription.status != "active" or subscription.plan_id != "coach":
                raise ValueError("Active coach subscription is required")
            if subscription.quota_remaining() <= 0:
                raise ValueError("Monthly AI session quota exhausted")
            return

        if not subscription_active:
            raise ValueError("Active coach subscription is required")
