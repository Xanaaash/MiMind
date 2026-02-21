import unittest

from fastapi.testclient import TestClient

from backend.tests.bootstrap import configure_import_path

configure_import_path()

import app as app_module
from modules.api.rate_limit import APIRateLimiter, RateLimitConfig


class _Clock:
    def __init__(self) -> None:
        self.value = 0.0

    def now(self) -> float:
        return self.value


class APIRateLimitContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original = app_module.api_rate_limiter
        self.client = TestClient(app_module.app)

    def tearDown(self) -> None:
        app_module.api_rate_limiter = self._original

    def test_ip_rate_limit_returns_429_and_retry_after(self) -> None:
        clock = _Clock()
        app_module.api_rate_limiter = APIRateLimiter(
            config=RateLimitConfig(enabled=True, window_seconds=60, ip_requests=2, user_requests=2),
            time_source=clock.now,
        )

        first = self.client.get("/api/prompts/packs")
        second = self.client.get("/api/prompts/packs")
        blocked = self.client.get("/api/prompts/packs")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(blocked.json()["error"], "Rate limit exceeded")
        self.assertEqual(blocked.headers.get("x-ratelimit-scope"), "ip")
        self.assertEqual(blocked.headers.get("x-ratelimit-remaining"), "0")
        self.assertIsNotNone(blocked.headers.get("retry-after"))

    def test_user_scope_is_prioritized_over_ip_scope(self) -> None:
        clock = _Clock()
        app_module.api_rate_limiter = APIRateLimiter(
            config=RateLimitConfig(enabled=True, window_seconds=60, ip_requests=1, user_requests=2),
            time_source=clock.now,
        )

        headers_a = {"X-User-Id": "user-a"}
        headers_b = {"X-User-Id": "user-b"}

        first = self.client.get("/api/prompts/packs", headers=headers_a)
        second = self.client.get("/api/prompts/packs", headers=headers_a)
        third = self.client.get("/api/prompts/packs", headers=headers_a)
        other_user = self.client.get("/api/prompts/packs", headers=headers_b)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(third.status_code, 429)
        self.assertEqual(third.headers.get("x-ratelimit-scope"), "user")
        self.assertEqual(other_user.status_code, 200)


if __name__ == "__main__":
    unittest.main()
