from typing import Any, Dict, Optional, Tuple

from modules.auth.service import AuthService, AuthTokenBundle
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class UserAuthAPI:
    def __init__(
        self,
        store: Optional[InMemoryStore] = None,
        onboarding_service: Optional[OnboardingService] = None,
    ) -> None:
        self._store = store or InMemoryStore()
        self._auth = AuthService(self._store)
        self._onboarding = onboarding_service or OnboardingService(self._store)

    @property
    def service(self) -> AuthService:
        return self._auth

    def post_register(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any], Optional[AuthTokenBundle]]:
        try:
            for field in ("email", "password", "locale", "policy_version"):
                if not payload.get(field):
                    raise ValueError(f"{field} is required")

            data = self._onboarding.register(
                email=str(payload["email"]),
                locale=str(payload["locale"]),
                policy_version=str(payload["policy_version"]),
                password=str(payload["password"]),
            )
            user = self._store.get_user(data["user_id"])
            if user is None:
                raise ValueError("registration failed")

            tokens = self._auth.issue_token_bundle(user)
            response = self._auth.auth_payload(user, tokens=tokens)
            response["consent_id"] = data["consent_id"]
            response["policy_version"] = data["policy_version"]
            return 201, {"data": response}, tokens
        except ValueError as error:
            message = str(error)
            if message == "Email already registered":
                return 409, {"error": message}, None
            return 400, {"error": message}, None

    def post_login(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any], Optional[AuthTokenBundle]]:
        try:
            email = str(payload.get("email", "")).strip()
            password = str(payload.get("password", ""))
            if not email or not password:
                raise ValueError("email and password are required")

            user = self._auth.authenticate(email=email, password=password)
            tokens = self._auth.issue_token_bundle(user)
            return 200, {"data": self._auth.auth_payload(user, tokens=tokens)}, tokens
        except ValueError as error:
            status = 401 if str(error) == "Invalid credentials" else 400
            return status, {"error": str(error)}, None

    def get_session(self, access_token: Optional[str]) -> Tuple[int, Dict[str, Any]]:
        try:
            if not access_token:
                raise ValueError("User session required")
            user = self._auth.get_user_from_access_token(access_token)
            return 200, {"data": self._auth.auth_payload(user)}
        except ValueError:
            return 401, {"error": "User session required"}

    def post_refresh(self, refresh_token: Optional[str]) -> Tuple[int, Dict[str, Any], Optional[AuthTokenBundle]]:
        try:
            if not refresh_token:
                raise ValueError("Refresh token required")
            user, tokens = self._auth.refresh_tokens(refresh_token)
            return 200, {"data": self._auth.auth_payload(user, tokens=tokens)}, tokens
        except ValueError as error:
            message = str(error)
            status = 401 if message in {"Refresh token required", "Token expired", "Invalid token signature"} else 400
            return status, {"error": message}, None

    @staticmethod
    def post_logout() -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": {"authenticated": False}}
