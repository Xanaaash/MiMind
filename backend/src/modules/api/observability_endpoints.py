from typing import Any, Dict, Optional, Tuple

from modules.observability.service import ModelObservabilityService
from modules.storage.in_memory import InMemoryStore


class ObservabilityAPI:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self._store = store or InMemoryStore()
        self._service = ModelObservabilityService(self._store)

    def get_model_invocations(
        self,
        limit: int = 50,
        task_type: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        try:
            safe_limit = int(limit)
            if safe_limit <= 0:
                raise ValueError("limit must be greater than 0")
            if safe_limit > 500:
                raise ValueError("limit must be <= 500")

            records = self._service.list_model_invocations(
                limit=safe_limit,
                task_type=task_type,
                provider=provider,
            )
            return 200, {"data": records}
        except ValueError as error:
            return 400, {"error": str(error)}

    def get_model_invocation_summary(
        self,
        limit: int = 200,
        task_type: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        try:
            safe_limit = int(limit)
            if safe_limit <= 0:
                raise ValueError("limit must be greater than 0")
            if safe_limit > 2000:
                raise ValueError("limit must be <= 2000")

            summary = self._service.summarize_model_invocations(
                limit=safe_limit,
                task_type=task_type,
                provider=provider,
            )
            return 200, {"data": summary}
        except ValueError as error:
            return 400, {"error": str(error)}
