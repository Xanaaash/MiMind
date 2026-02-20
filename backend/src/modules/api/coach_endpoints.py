from typing import Any, Dict, Optional, Tuple

from modules.coach.session_service import CoachSessionService
from modules.storage.in_memory import InMemoryStore


class CoachAPI:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self._store = store or InMemoryStore()
        self._service = CoachSessionService(self._store)

    @property
    def store(self) -> InMemoryStore:
        return self._store

    def post_start_session(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            style_id = str(payload.get("style_id", "")).strip()
            subscription_active = bool(payload.get("subscription_active", False))
            if not style_id:
                raise ValueError("style_id is required")

            data = self._service.start_session(
                user_id=user_id,
                style_id=style_id,
                subscription_active=subscription_active,
            )
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_chat(self, session_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            user_message = str(payload.get("user_message", "")).strip()
            if not user_message:
                raise ValueError("user_message is required")

            dialogue_risk = self._service.parse_dialogue_risk(payload.get("dialogue_risk"))
            data = self._service.chat(
                session_id=session_id,
                user_message=user_message,
                dialogue_risk=dialogue_risk,
            )
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_chat_stream(self, session_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        return self.post_chat(session_id=session_id, payload=payload)

    def post_end_session(self, session_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._service.end_session(session_id=session_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def get_session_history(self, user_id: str, limit: int = 20) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._service.list_session_history(user_id=user_id, limit=limit)
            return 200, {"data": data}
        except ValueError as error:
            return 404, {"error": str(error)}

    def get_session_summary(self, user_id: str, session_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._service.get_session_summary(user_id=user_id, session_id=session_id)
            return 200, {"data": data}
        except ValueError as error:
            return 404, {"error": str(error)}
