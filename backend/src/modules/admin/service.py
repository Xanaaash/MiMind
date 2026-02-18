import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from modules.admin.config import load_admin_auth_config, using_dev_fallback_password
from modules.admin.models import AdminSession
from modules.storage.in_memory import InMemoryStore


class AdminAuthService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._config = load_admin_auth_config()

    @property
    def username(self) -> str:
        return self._config.username

    def login(self, username: str, password: str) -> AdminSession:
        if username != self._config.username:
            raise ValueError("Invalid credentials")
        if password != self._config.password:
            raise ValueError("Invalid credentials")

        created_at = datetime.now(timezone.utc)
        expires_at = created_at + timedelta(hours=self._config.session_ttl_hours)
        session = AdminSession(
            session_id=secrets.token_urlsafe(32),
            username=self._config.username,
            created_at=created_at,
            expires_at=expires_at,
        )
        self._store.save_admin_session(session)
        return session

    def get_valid_session(self, session_id: Optional[str]) -> Optional[AdminSession]:
        if not session_id:
            return None

        session = self._store.get_admin_session(session_id)
        if session is None:
            return None

        now = datetime.now(timezone.utc)
        if not session.is_active(now):
            self._store.revoke_admin_session(session_id)
            return None

        return session

    def logout(self, session_id: Optional[str]) -> None:
        if not session_id:
            return
        self._store.revoke_admin_session(session_id)

    def session_payload(self, session: AdminSession) -> dict:
        return {
            "authenticated": True,
            "username": session.username,
            "expires_at": session.expires_at.isoformat(),
        }

    @staticmethod
    def cookie_name() -> str:
        return "mc_admin_session"

    @staticmethod
    def cookie_path() -> str:
        return "/"

    @staticmethod
    def cookie_samesite() -> str:
        return "lax"

    @staticmethod
    def cookie_secure() -> bool:
        return False

    def cookie_max_age_seconds(self) -> int:
        return self._config.session_ttl_hours * 3600

    def password_source_payload(self) -> dict:
        return {
            "username": self._config.username,
            "uses_dev_fallback_password": using_dev_fallback_password(self._config),
            "session_ttl_hours": self._config.session_ttl_hours,
        }
