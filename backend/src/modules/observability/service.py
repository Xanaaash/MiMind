from typing import List, Optional

from modules.storage.in_memory import InMemoryStore


class ModelObservabilityService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def list_model_invocations(
        self,
        limit: int = 50,
        task_type: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> List[dict]:
        items = self._store.list_model_invocations()
        ordered = sorted(items, key=lambda item: item.created_at, reverse=True)

        normalized_task = str(task_type).strip() if task_type is not None else None
        normalized_provider = str(provider).strip() if provider is not None else None

        if normalized_task:
            ordered = [item for item in ordered if item.task_type == normalized_task]
        if normalized_provider:
            lowered = normalized_provider.lower()
            ordered = [item for item in ordered if lowered in item.provider.lower()]

        safe_limit = max(1, min(int(limit), 500))
        return [item.to_dict() for item in ordered[:safe_limit]]
