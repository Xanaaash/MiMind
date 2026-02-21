import os
from dataclasses import dataclass


_DEFAULT_DEV_JWT_SECRET = "mimind-dev-user-jwt-secret"


@dataclass(frozen=True)
class UserAuthConfig:
    jwt_secret: str
    access_token_ttl_minutes: int
    refresh_token_ttl_hours: int
    email_verification_ttl_hours: int
    password_reset_ttl_minutes: int
    cookie_secure: bool


def _parse_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_user_auth_config() -> UserAuthConfig:
    configured_secret = os.getenv("AUTH_JWT_SECRET", "").strip()
    jwt_secret = configured_secret or _DEFAULT_DEV_JWT_SECRET

    access_raw = os.getenv("AUTH_ACCESS_TTL_MINUTES", "15").strip()
    refresh_raw = os.getenv("AUTH_REFRESH_TTL_HOURS", "168").strip()
    verify_raw = os.getenv("AUTH_EMAIL_VERIFICATION_TTL_HOURS", "24").strip()
    reset_raw = os.getenv("AUTH_PASSWORD_RESET_TTL_MINUTES", "30").strip()

    try:
        access_ttl = int(access_raw)
    except ValueError:
        access_ttl = 15
    access_ttl = min(max(access_ttl, 5), 120)

    try:
        refresh_ttl = int(refresh_raw)
    except ValueError:
        refresh_ttl = 168
    refresh_ttl = min(max(refresh_ttl, 24), 24 * 30)

    try:
        verify_ttl = int(verify_raw)
    except ValueError:
        verify_ttl = 24
    verify_ttl = min(max(verify_ttl, 1), 24 * 7)

    try:
        reset_ttl = int(reset_raw)
    except ValueError:
        reset_ttl = 30
    reset_ttl = min(max(reset_ttl, 5), 24 * 60)

    cookie_secure = _parse_bool(os.getenv("AUTH_COOKIE_SECURE", "false"))
    return UserAuthConfig(
        jwt_secret=jwt_secret,
        access_token_ttl_minutes=access_ttl,
        refresh_token_ttl_hours=refresh_ttl,
        email_verification_ttl_hours=verify_ttl,
        password_reset_ttl_minutes=reset_ttl,
        cookie_secure=cookie_secure,
    )


def using_dev_jwt_secret(config: UserAuthConfig) -> bool:
    return config.jwt_secret == _DEFAULT_DEV_JWT_SECRET
