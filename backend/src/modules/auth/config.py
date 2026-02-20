import os
from dataclasses import dataclass


_DEFAULT_DEV_JWT_SECRET = "mindcoach-dev-user-jwt-secret"


@dataclass(frozen=True)
class UserAuthConfig:
    jwt_secret: str
    access_token_ttl_minutes: int
    refresh_token_ttl_hours: int
    cookie_secure: bool


def _parse_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_user_auth_config() -> UserAuthConfig:
    configured_secret = os.getenv("AUTH_JWT_SECRET", "").strip()
    jwt_secret = configured_secret or _DEFAULT_DEV_JWT_SECRET

    access_raw = os.getenv("AUTH_ACCESS_TTL_MINUTES", "15").strip()
    refresh_raw = os.getenv("AUTH_REFRESH_TTL_HOURS", "168").strip()

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

    cookie_secure = _parse_bool(os.getenv("AUTH_COOKIE_SECURE", "false"))
    return UserAuthConfig(
        jwt_secret=jwt_secret,
        access_token_ttl_minutes=access_ttl,
        refresh_token_ttl_hours=refresh_ttl,
        cookie_secure=cookie_secure,
    )


def using_dev_jwt_secret(config: UserAuthConfig) -> bool:
    return config.jwt_secret == _DEFAULT_DEV_JWT_SECRET
