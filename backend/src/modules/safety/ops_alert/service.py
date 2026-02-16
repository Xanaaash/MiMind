from datetime import datetime, timezone

from modules.storage.in_memory import InMemoryStore
from modules.triage.models import RiskLevel


class OpsAlertService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def notify(self, user_id: str, level: RiskLevel, reason: str) -> dict:
        event = {
            "tool": "ops-alert",
            "user_id": user_id,
            "risk_level": level.name.lower(),
            "reason": reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._store.save_tool_event(user_id, event)
        return event
