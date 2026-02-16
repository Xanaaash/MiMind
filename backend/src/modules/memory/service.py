from typing import List

from modules.storage.in_memory import InMemoryStore


class MemoryService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def index_summary(self, user_id: str, summary: str) -> None:
        if not summary.strip():
            return
        self._store.save_memory_summary(user_id, summary.strip())

    def retrieve_recent(self, user_id: str, limit: int = 3) -> List[str]:
        items = self._store.list_memory_summaries(user_id)
        if limit <= 0:
            return []
        return items[-limit:]
