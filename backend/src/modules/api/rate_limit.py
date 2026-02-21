import os
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Deque, Dict, Optional, Tuple

from fastapi import Request

from modules.auth.config import load_user_auth_config
from modules.auth.tokens import decode_and_validate_jwt


def _parse_bool(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(raw: str, default: int, *, minimum: int, maximum: int) -> int:
    try:
        value = int(raw.strip())
    except ValueError:
        value = default
    return min(max(value, minimum), maximum)


@dataclass(frozen=True)
class RateLimitConfig:
    enabled: bool
    window_seconds: int
    ip_requests: int
    user_requests: int

    @staticmethod
    def from_env() -> "RateLimitConfig":
        enabled = _parse_bool(os.getenv("RATE_LIMIT_ENABLED", "true"))
        window_seconds = _parse_int(
            os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"),
            60,
            minimum=10,
            maximum=3600,
        )
        ip_requests = _parse_int(
            os.getenv("RATE_LIMIT_IP_REQUESTS", "120"),
            120,
            minimum=10,
            maximum=10000,
        )
        user_requests = _parse_int(
            os.getenv("RATE_LIMIT_USER_REQUESTS", "240"),
            240,
            minimum=10,
            maximum=10000,
        )
        return RateLimitConfig(
            enabled=enabled,
            window_seconds=window_seconds,
            ip_requests=ip_requests,
            user_requests=user_requests,
        )


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after_seconds: int
    scope: str


class APIRateLimiter:
    def __init__(
        self,
        config: RateLimitConfig,
        *,
        time_source: Optional[Callable[[], float]] = None,
    ) -> None:
        self._config = config
        self._time_source = time_source or time.time
        self._events: Dict[str, Deque[float]] = {}
        self._lock = threading.Lock()
        self._jwt_secret = load_user_auth_config().jwt_secret

    @property
    def enabled(self) -> bool:
        return self._config.enabled

    def evaluate(self, request: Request) -> RateLimitResult:
        if not self._config.enabled:
            return RateLimitResult(allowed=True, limit=0, remaining=0, retry_after_seconds=0, scope="disabled")

        scope, bucket_id, limit = self._resolve_bucket(request)
        now = self._time_source()
        window_start = now - self._config.window_seconds
        storage_key = f"{scope}:{bucket_id}"

        with self._lock:
            bucket = self._events.setdefault(storage_key, deque())
            while bucket and bucket[0] <= window_start:
                bucket.popleft()

            if len(bucket) >= limit:
                oldest = bucket[0]
                retry_after = max(1, int(oldest + self._config.window_seconds - now) + 1)
                return RateLimitResult(
                    allowed=False,
                    limit=limit,
                    remaining=0,
                    retry_after_seconds=retry_after,
                    scope=scope,
                )

            bucket.append(now)
            remaining = max(limit - len(bucket), 0)
            return RateLimitResult(
                allowed=True,
                limit=limit,
                remaining=remaining,
                retry_after_seconds=0,
                scope=scope,
            )

    def _resolve_bucket(self, request: Request) -> Tuple[str, str, int]:
        user_id = self._extract_user_id(request)
        if user_id:
            return "user", user_id, self._config.user_requests

        client_host = "anonymous"
        if request.client and request.client.host:
            client_host = request.client.host
        return "ip", client_host, self._config.ip_requests

    def _extract_user_id(self, request: Request) -> Optional[str]:
        user_header = request.headers.get("x-user-id", "").strip()
        if user_header:
            return user_header[:128]

        authorization = request.headers.get("authorization", "").strip()
        if not authorization.lower().startswith("bearer "):
            return None

        token = authorization[7:].strip()
        if not token:
            return None

        try:
            payload = decode_and_validate_jwt(
                token,
                self._jwt_secret,
                expected_token_type="access",
            )
        except ValueError:
            return None

        subject = payload.get("sub")
        if isinstance(subject, str) and subject:
            return subject[:128]
        return None
