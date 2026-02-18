from typing import Any, Dict, Optional, Tuple

from modules.admin.service import AdminAuthService
from modules.storage.in_memory import InMemoryStore


class AdminAPI:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self._store = store or InMemoryStore()
        self._service = AdminAuthService(self._store)

    @property
    def service(self) -> AdminAuthService:
        return self._service

    def post_login(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any], Optional[str]]:
        try:
            username = str(payload.get("username", "")).strip()
            password = str(payload.get("password", ""))
            if not username or not password:
                raise ValueError("username and password are required")

            session = self._service.login(username=username, password=password)
            data = self._service.session_payload(session)
            data["auth_config"] = self._service.password_source_payload()
            return 200, {"data": data}, session.session_id
        except ValueError as error:
            message = str(error)
            status = 401 if message == "Invalid credentials" else 400
            return status, {"error": message}, None

    def post_logout(self, session_id: Optional[str]) -> Tuple[int, Dict[str, Any]]:
        self._service.logout(session_id=session_id)
        return 200, {"data": {"authenticated": False}}

    def get_session(self, session_id: Optional[str]) -> Tuple[int, Dict[str, Any]]:
        session = self._service.get_valid_session(session_id=session_id)
        if session is None:
            return 401, {"error": "Admin session required"}
        return 200, {"data": self._service.session_payload(session)}

    def get_users(self, session_id: Optional[str]) -> Tuple[int, Dict[str, Any]]:
        session = self._service.get_valid_session(session_id=session_id)
        if session is None:
            return 401, {"error": "Admin session required"}

        return 501, {
            "error": {
                "status": "not_implemented",
                "message": "User management UI/API is deferred in this phase.",
                "next_step": "Implement list/filter/detail actions in next feature cycle.",
            }
        }
