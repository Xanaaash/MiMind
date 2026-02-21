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
            response["email_verification"] = self._auth.verification_payload(user, include_token=True)
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
            payload = self._auth.auth_payload(user, tokens=tokens)
            payload["email_verification"] = self._auth.verification_payload(user)
            return 200, {"data": payload}, tokens
        except ValueError as error:
            status = 401 if str(error) == "Invalid credentials" else 400
            return status, {"error": str(error)}, None

    def get_session(self, access_token: Optional[str]) -> Tuple[int, Dict[str, Any]]:
        try:
            if not access_token:
                raise ValueError("User session required")
            user = self._auth.get_user_from_access_token(access_token)
            payload = self._auth.auth_payload(user)
            payload["email_verification"] = self._auth.verification_payload(user)
            return 200, {"data": payload}
        except ValueError:
            return 401, {"error": "User session required"}

    def post_refresh(self, refresh_token: Optional[str]) -> Tuple[int, Dict[str, Any], Optional[AuthTokenBundle]]:
        try:
            if not refresh_token:
                raise ValueError("Refresh token required")
            user, tokens = self._auth.refresh_tokens(refresh_token)
            payload = self._auth.auth_payload(user, tokens=tokens)
            payload["email_verification"] = self._auth.verification_payload(user)
            return 200, {"data": payload}, tokens
        except ValueError as error:
            message = str(error)
            auth_errors = {
                "Refresh token required",
                "Token expired",
                "Invalid token signature",
                "Invalid token format",
                "Invalid token type",
                "Token missing subject",
                "Unknown user_id",
            }
            status = 401 if message in auth_errors else 400
            return status, {"error": message}, None

    @staticmethod
    def post_logout() -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": {"authenticated": False}}

    def post_verify_email(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            token = str(payload.get("token", "")).strip()
            if not token:
                raise ValueError("token is required")
            user = self._auth.verify_email(token)
            return 200, {
                "data": {
                    "verified": bool(user.email_verified),
                    "email": user.email,
                    "user_id": user.user_id,
                }
            }
        except ValueError as error:
            message = str(error)
            status = 400 if message in {"token is required", "Verification token expired"} else 404
            return status, {"error": message}

    def post_resend_verification(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            email = str(payload.get("email", "")).strip()
            if not email:
                raise ValueError("email is required")
            user = self._auth.resend_verification(email)
            return 200, {
                "data": {
                    "email": user.email,
                    "user_id": user.user_id,
                    "email_verification": self._auth.verification_payload(user, include_token=True),
                }
            }
        except ValueError as error:
            message = str(error)
            status = 400 if message in {"email is required", "Email verification not required"} else 404
            return status, {"error": message}

    def post_forgot_password(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            email = str(payload.get("email", "")).strip()
            if not email:
                raise ValueError("email is required")
            self._auth.request_password_reset(email=email)
            return 200, {"data": {"reset_requested": True}}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_reset_password(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            token = str(payload.get("token", "")).strip()
            password = str(payload.get("password", ""))
            if not token:
                raise ValueError("token is required")
            if not password:
                raise ValueError("password is required")
            self._auth.reset_password(token=token, password=password)
            return 200, {"data": {"reset": True}}
        except ValueError as error:
            message = str(error)
            status = 404 if message == "Password reset token is invalid" else 400
            return status, {"error": message}
