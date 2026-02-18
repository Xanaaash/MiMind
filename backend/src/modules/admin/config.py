import os
from dataclasses import dataclass


_DEFAULT_DEV_PASSWORD = "dev-admin-please-change"


@dataclass(frozen=True)
class AdminAuthConfig:
    username: str
    password: str
    session_ttl_hours: int


def load_admin_auth_config() -> AdminAuthConfig:
    configured_password = os.getenv("ADMIN_PASSWORD", "").strip()
    password = configured_password or _DEFAULT_DEV_PASSWORD

    ttl_raw = os.getenv("ADMIN_SESSION_TTL_HOURS", "8").strip()
    try:
        ttl = int(ttl_raw)
    except ValueError:
        ttl = 8
    ttl = min(max(ttl, 1), 72)

    return AdminAuthConfig(
        username="admin",
        password=password,
        session_ttl_hours=ttl,
    )


def using_dev_fallback_password(config: AdminAuthConfig) -> bool:
    return config.password == _DEFAULT_DEV_PASSWORD
