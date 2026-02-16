from datetime import datetime, timezone
from typing import Any, Dict

from modules.storage.in_memory import InMemoryStore


class DataGovernanceService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def export_user_bundle(self, user_id: str) -> Dict[str, Any]:
        if not user_id:
            raise ValueError("user_id is required")

        payload = self._store.export_user_data(user_id)
        return {
            "user_id": user_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data": payload,
        }

    def erase_user_bundle(self, user_id: str) -> Dict[str, Any]:
        if not user_id:
            raise ValueError("user_id is required")

        existed_before = self._store.get_user(user_id) is not None
        deleted = self._store.erase_user_data(user_id)

        return {
            "user_id": user_id,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "existed_before": existed_before,
            "deleted": deleted,
            "total_deleted": int(sum(deleted.values())),
        }
