import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from modules.auth.config import UserAuthConfig, load_user_auth_config
from modules.auth.passwords import hash_password, validate_password_strength, verify_password
from modules.auth.tokens import decode_and_validate_jwt, encode_jwt
from modules.storage.in_memory import InMemoryStore
from modules.user.models import User


@dataclass(frozen=True)
class AuthTokenBundle:
    access_token: str
    refresh_token: str
    access_expires_at: datetime
    refresh_expires_at: datetime


class AuthService:
    def __init__(self, store: InMemoryStore, config: Optional[UserAuthConfig] = None) -> None:
        self._store = store
        self._config = config or load_user_auth_config()

    def register_user(self, email: str, locale: str, password: Optional[str] = None) -> User:
        normalized_email = str(email).strip().lower()
        if not normalized_email or "@" not in normalized_email:
            raise ValueError("A valid email is required")
        if not locale:
            raise ValueError("locale is required")
        if self._store.get_user_by_email(normalized_email) is not None:
            raise ValueError("Email already registered")

        auth_provider = "guest"
        password_hash = None
        email_verified = True
        email_verification_token = None
        email_verification_expires_at = None
        if password is not None:
            validate_password_strength(password)
            password_hash = hash_password(password)
            auth_provider = "password"
            email_verified = False
            email_verification_token = uuid.uuid4().hex
            email_verification_expires_at = datetime.now(timezone.utc) + timedelta(
                hours=self._config.email_verification_ttl_hours
            )

        user = User(
            user_id=str(uuid.uuid4()),
            email=normalized_email,
            locale=str(locale).strip(),
            password_hash=password_hash,
            auth_provider=auth_provider,
            email_verified=email_verified,
            email_verification_token=email_verification_token,
            email_verification_expires_at=email_verification_expires_at,
        )
        self._store.save_user(user)
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self._store.get_user_by_email(str(email).strip().lower())
        if user is None:
            raise ValueError("Invalid credentials")
        if not user.password_hash or user.auth_provider != "password":
            raise ValueError("Invalid credentials")
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        return user

    def issue_token_bundle(self, user: User) -> AuthTokenBundle:
        now = datetime.now(timezone.utc)
        access_expires_at = now + timedelta(minutes=self._config.access_token_ttl_minutes)
        refresh_expires_at = now + timedelta(hours=self._config.refresh_token_ttl_hours)

        access_token = encode_jwt(
            {
                "sub": user.user_id,
                "email": user.email,
                "token_type": "access",
                "jti": str(uuid.uuid4()),
                "iat": int(now.timestamp()),
                "exp": int(access_expires_at.timestamp()),
            },
            secret=self._config.jwt_secret,
        )
        refresh_token = encode_jwt(
            {
                "sub": user.user_id,
                "email": user.email,
                "token_type": "refresh",
                "jti": str(uuid.uuid4()),
                "iat": int(now.timestamp()),
                "exp": int(refresh_expires_at.timestamp()),
            },
            secret=self._config.jwt_secret,
        )
        return AuthTokenBundle(
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

    def get_user_from_access_token(self, token: str) -> User:
        payload = decode_and_validate_jwt(
            token=token,
            secret=self._config.jwt_secret,
            expected_token_type="access",
        )
        return self._resolve_user_from_payload(payload)

    def refresh_tokens(self, refresh_token: str) -> Tuple[User, AuthTokenBundle]:
        payload = decode_and_validate_jwt(
            token=refresh_token,
            secret=self._config.jwt_secret,
            expected_token_type="refresh",
        )
        user = self._resolve_user_from_payload(payload)
        return user, self.issue_token_bundle(user)

    def auth_payload(self, user: User, tokens: Optional[AuthTokenBundle] = None) -> dict:
        payload = {
            "authenticated": True,
            "user": self._serialize_user(user),
            "user_id": user.user_id,
            "email": user.email,
            "email_verified": user.email_verified,
        }
        if tokens is not None:
            payload["access_token"] = tokens.access_token
            payload["refresh_token"] = tokens.refresh_token
            payload["expires_at"] = tokens.access_expires_at.isoformat()
        return payload

    def verification_payload(self, user: User, include_token: bool = False) -> dict:
        required = user.auth_provider == "password"
        payload = {
            "required": required,
            "verified": bool(user.email_verified),
            "expires_at": user.email_verification_expires_at.isoformat()
            if user.email_verification_expires_at
            else None,
        }
        if include_token and user.email_verification_token:
            payload["token"] = user.email_verification_token
            payload["preview_link"] = f"/api/auth/verify-email?token={user.email_verification_token}"
        return payload

    def verify_email(self, token: str) -> User:
        normalized = str(token).strip()
        if not normalized:
            raise ValueError("Verification token is required")

        user = self._store.get_user_by_email_verification_token(normalized)
        if user is None:
            raise ValueError("Verification token is invalid")
        if user.auth_provider != "password":
            raise ValueError("Verification token is invalid")
        if user.email_verified:
            return user
        if user.email_verification_expires_at is not None and user.email_verification_expires_at <= datetime.now(
            timezone.utc
        ):
            raise ValueError("Verification token expired")

        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_expires_at = None
        self._store.save_user(user)
        return user

    def resend_verification(self, email: str) -> User:
        normalized = str(email).strip().lower()
        if not normalized:
            raise ValueError("email is required")

        user = self._store.get_user_by_email(normalized)
        if user is None:
            raise ValueError("User not found")
        if user.auth_provider != "password":
            raise ValueError("Email verification not required")
        if user.email_verified:
            return user

        user.email_verification_token = uuid.uuid4().hex
        user.email_verification_expires_at = datetime.now(timezone.utc) + timedelta(
            hours=self._config.email_verification_ttl_hours
        )
        self._store.save_user(user)
        return user

    @staticmethod
    def access_cookie_name() -> str:
        return "mc_access_token"

    @staticmethod
    def refresh_cookie_name() -> str:
        return "mc_refresh_token"

    @staticmethod
    def cookie_path() -> str:
        return "/"

    @staticmethod
    def cookie_samesite() -> str:
        return "lax"

    def cookie_secure(self) -> bool:
        return self._config.cookie_secure

    def access_cookie_max_age_seconds(self) -> int:
        return self._config.access_token_ttl_minutes * 60

    def refresh_cookie_max_age_seconds(self) -> int:
        return self._config.refresh_token_ttl_hours * 3600

    def _resolve_user_from_payload(self, payload: dict) -> User:
        user_id = str(payload.get("sub", "")).strip()
        if not user_id:
            raise ValueError("Token missing subject")

        user = self._store.get_user(user_id)
        if user is None:
            raise ValueError("Unknown user_id")
        return user

    @staticmethod
    def _serialize_user(user: User) -> dict:
        return {
            "user_id": user.user_id,
            "email": user.email,
            "locale": user.locale,
            "email_verified": user.email_verified,
            "created_at": user.created_at.isoformat(),
        }
