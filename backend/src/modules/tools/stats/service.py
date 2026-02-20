from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from modules.storage.in_memory import InMemoryStore


SUPPORTED_TOOL_TYPES = ("audio", "breathing", "meditation")


class ToolUsageStatsService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def get_usage_stats(self, user_id: str) -> dict:
        now = datetime.now(timezone.utc)
        week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)

        by_tool: Dict[str, dict] = {
            tool: {
                "week_usage_count": 0,
                "total_usage_count": 0,
                "total_duration_seconds": 0,
            }
            for tool in SUPPORTED_TOOL_TYPES
        }

        week_usage_count = 0
        total_usage_count = 0
        total_duration_seconds = 0

        for event in self._store.list_tool_events(user_id):
            tool = event.get("tool")
            if tool not in by_tool:
                continue

            duration_seconds = self._duration_seconds(event)
            occurred_at = self._event_timestamp(event)

            total_usage_count += 1
            total_duration_seconds += duration_seconds
            by_tool[tool]["total_usage_count"] += 1
            by_tool[tool]["total_duration_seconds"] += duration_seconds

            if occurred_at is not None and week_start <= occurred_at < week_end:
                week_usage_count += 1
                by_tool[tool]["week_usage_count"] += 1

        return {
            "week_start": week_start.date().isoformat(),
            "week_end": (week_end - timedelta(days=1)).date().isoformat(),
            "week_usage_count": week_usage_count,
            "total_usage_count": total_usage_count,
            "total_duration_seconds": total_duration_seconds,
            "by_tool": by_tool,
        }

    def _event_timestamp(self, event: dict) -> Optional[datetime]:
        for key in ("occurred_at", "completed_at", "started_at", "created_at"):
            value = event.get(key)
            parsed = self._parse_iso_datetime(value)
            if parsed is not None:
                return parsed
        return None

    def _duration_seconds(self, event: dict) -> int:
        total_seconds = event.get("total_seconds")
        if isinstance(total_seconds, (int, float)):
            return max(int(total_seconds), 0)

        minutes = event.get("minutes")
        if isinstance(minutes, (int, float)):
            return max(int(minutes * 60), 0)

        started_at = self._parse_iso_datetime(event.get("started_at"))
        ends_at = self._parse_iso_datetime(event.get("ends_at"))
        if started_at is not None and ends_at is not None and ends_at >= started_at:
            return int((ends_at - started_at).total_seconds())

        return 0

    @staticmethod
    def _parse_iso_datetime(value: object) -> Optional[datetime]:
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            dt = datetime.fromisoformat(value)
        except ValueError:
            return None
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
