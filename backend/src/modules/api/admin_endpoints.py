from typing import Any, Dict, Optional, Tuple

from modules.admin.service import AdminAuthService
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import TriageChannel, TriageDecision


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

    def get_users(self, session_id: Optional[str], limit: int = 100) -> Tuple[int, Dict[str, Any]]:
        session = self._service.get_valid_session(session_id=session_id)
        if session is None:
            return 401, {"error": "Admin session required"}

        safe_limit = max(1, min(int(limit), 500))
        users = self._store.list_users(limit=safe_limit)
        items = []
        for user in users:
            triage = self._store.get_triage(user.user_id)
            subscription = self._store.get_subscription(user.user_id)
            items.append(
                {
                    "user_id": user.user_id,
                    "email": user.email,
                    "locale": user.locale,
                    "auth_provider": user.auth_provider,
                    "email_verified": bool(user.email_verified),
                    "created_at": user.created_at.isoformat(),
                    "triage": triage.to_dict() if triage is not None else None,
                    "subscription": {
                        "plan_id": subscription.plan_id,
                        "status": subscription.status,
                        "ends_at": subscription.ends_at.isoformat() if subscription.ends_at else None,
                    }
                    if subscription is not None
                    else None,
                }
            )
        return 200, {"data": {"count": len(items), "items": items}}

    def post_user_triage_override(
        self,
        session_id: Optional[str],
        user_id: str,
        payload: Dict[str, Any],
    ) -> Tuple[int, Dict[str, Any]]:
        session = self._service.get_valid_session(session_id=session_id)
        if session is None:
            return 401, {"error": "Admin session required"}

        user = self._store.get_user(user_id)
        if user is None:
            return 404, {"error": "Unknown user_id"}

        channel_raw = str(payload.get("channel", "")).strip().lower()
        if channel_raw not in {item.value for item in TriageChannel}:
            return 400, {"error": "channel must be one of: green, yellow, red"}
        channel = TriageChannel(channel_raw)

        reasons_raw = payload.get("reasons")
        if isinstance(reasons_raw, list):
            reasons = [str(item).strip() for item in reasons_raw if str(item).strip()]
        elif reasons_raw is None:
            reasons = []
        else:
            reason_text = str(reasons_raw).strip()
            reasons = [reason_text] if reason_text else []

        default_halt = channel == TriageChannel.RED
        default_hotline = channel == TriageChannel.RED
        halt_coaching = bool(payload.get("halt_coaching", default_halt))
        show_hotline = bool(payload.get("show_hotline", default_hotline))

        decision = TriageDecision(
            channel=channel,
            reasons=reasons or ["admin-manual-override"],
            halt_coaching=halt_coaching,
            show_hotline=show_hotline,
        )
        self._store.save_triage(user_id, decision)
        return 200, {
            "data": {
                "user_id": user_id,
                "triage": decision.to_dict(),
                "updated_by": session.username,
            }
        }
