from typing import Any, Dict, Optional, Tuple

from modules.safety.hotline.resolver import HotlineResolver
from modules.safety.service import SafetyRuntimeService
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import DialogueRiskSignal, RiskLevel


class SafetyAPI:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self._store = store or InMemoryStore()
        self._runtime = SafetyRuntimeService(self._store)
        self._hotline = HotlineResolver()

    @property
    def store(self) -> InMemoryStore:
        return self._store

    def post_assess_message(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            text = str(payload.get("text", "")).strip()
            if not text:
                raise ValueError("text is required")

            user = self._store.get_user(user_id)
            if user is None:
                raise ValueError("Unknown user_id")

            locale = str(payload.get("locale") or user.locale)
            override_signal = self._parse_override(payload.get("override_signal"))
            legal_policy_enabled = bool(payload.get("legal_policy_enabled", False))

            data = self._runtime.assess_and_respond(
                user_id=user_id,
                locale=locale,
                text=text,
                override_signal=override_signal,
                legal_policy_enabled=legal_policy_enabled,
            )
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def get_hotline_cache(self) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._hotline.local_cache_payload()}

    @staticmethod
    def _parse_override(payload: Any) -> Optional[DialogueRiskSignal]:
        if payload is None:
            return None
        if not isinstance(payload, dict):
            raise ValueError("override_signal must be an object")

        level_raw = str(payload.get("level", "")).strip().lower()
        mapping = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "extreme": RiskLevel.EXTREME,
        }
        if level_raw not in mapping:
            raise ValueError("Invalid override risk level")

        return DialogueRiskSignal(
            level=mapping[level_raw],
            text=str(payload.get("text", "")),
            is_joke=bool(payload.get("is_joke", False)),
        )
