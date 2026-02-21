import math
from collections import defaultdict
from typing import Dict, List, Optional

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

    def summarize_model_invocations(
        self,
        limit: int = 200,
        task_type: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> dict:
        records = self._filtered_records(limit=limit, task_type=task_type, provider=provider)
        return {
            "totals": self._aggregate(records),
            "by_task_type": self._group_aggregate(records, key="task_type"),
            "by_provider": self._group_aggregate(records, key="provider"),
        }

    def list_api_audit_logs(
        self,
        limit: int = 100,
        method: Optional[str] = None,
        path: Optional[str] = None,
        status_code: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> List[dict]:
        items = self._store.list_api_audit_logs()
        ordered = sorted(items, key=lambda item: item.created_at, reverse=True)

        normalized_method = str(method).strip().upper() if method is not None else None
        normalized_path = str(path).strip() if path is not None else None
        normalized_user = str(user_id).strip() if user_id is not None else None

        if normalized_method:
            ordered = [item for item in ordered if item.method.upper() == normalized_method]
        if normalized_path:
            ordered = [item for item in ordered if item.path == normalized_path]
        if status_code is not None:
            ordered = [item for item in ordered if int(item.status_code) == int(status_code)]
        if normalized_user:
            ordered = [item for item in ordered if item.user_id == normalized_user]

        safe_limit = max(1, min(int(limit), 1000))
        return [item.to_dict() for item in ordered[:safe_limit]]

    def _filtered_records(
        self,
        limit: int,
        task_type: Optional[str],
        provider: Optional[str],
    ) -> List[object]:
        items = self._store.list_model_invocations()
        ordered = sorted(items, key=lambda item: item.created_at, reverse=True)

        normalized_task = str(task_type).strip() if task_type is not None else None
        normalized_provider = str(provider).strip() if provider is not None else None
        if normalized_task:
            ordered = [item for item in ordered if item.task_type == normalized_task]
        if normalized_provider:
            lowered = normalized_provider.lower()
            ordered = [item for item in ordered if lowered in item.provider.lower()]

        safe_limit = max(1, min(int(limit), 2000))
        return ordered[:safe_limit]

    @staticmethod
    def _aggregate(records: List[object]) -> dict:
        total = len(records)
        if total == 0:
            return {
                "total": 0,
                "success": 0,
                "failure": 0,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "estimated_cost_usd": 0.0,
            }

        success = sum(1 for item in records if bool(item.success))
        failure = total - success
        latencies = sorted(float(item.latency_ms) for item in records)
        avg_latency = sum(latencies) / total
        p95 = ModelObservabilityService._percentile(latencies, 95)
        estimated_cost = sum(float(item.estimated_cost_usd) for item in records)

        return {
            "total": total,
            "success": success,
            "failure": failure,
            "success_rate": round(success / total, 4),
            "avg_latency_ms": round(avg_latency, 3),
            "p95_latency_ms": round(p95, 3),
            "estimated_cost_usd": round(estimated_cost, 8),
        }

    @staticmethod
    def _group_aggregate(records: List[object], key: str) -> Dict[str, dict]:
        grouped: Dict[str, List[object]] = defaultdict(list)
        for item in records:
            group_value = str(getattr(item, key))
            grouped[group_value].append(item)
        return {
            group_name: ModelObservabilityService._aggregate(group_items)
            for group_name, group_items in sorted(grouped.items(), key=lambda item: item[0])
        }

    @staticmethod
    def _percentile(values: List[float], percentile: int) -> float:
        if not values:
            return 0.0
        if percentile <= 0:
            return values[0]
        if percentile >= 100:
            return values[-1]
        index = math.ceil((percentile / 100) * len(values)) - 1
        index = min(max(index, 0), len(values) - 1)
        return values[index]
