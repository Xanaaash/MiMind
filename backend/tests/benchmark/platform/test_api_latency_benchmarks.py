import time
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from web_app import app


class PlatformLatencyBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def _register_user(self) -> str:
        email = f"perf-{uuid4().hex}@example.com"
        response = self.client.post(
            "/api/register",
            json={
                "email": email,
                "locale": "en-US",
                "policy_version": "2026.02",
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["user_id"]

    def _submit_green_assessment(self, user_id: str) -> None:
        response = self.client.post(
            f"/api/assessment/{user_id}",
            json={
                "responses": {
                    "phq9": [0] * 9,
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_first_screen_load_under_2s(self) -> None:
        start = time.perf_counter()
        response = self.client.get("/")
        elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_ms, 2000.0)

    def test_assessment_submit_under_1s(self) -> None:
        user_id = self._register_user()

        start = time.perf_counter()
        response = self.client.post(
            f"/api/assessment/{user_id}",
            json={
                "responses": {
                    "phq9": [0] * 9,
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed_ms, 1000.0)

    def test_coach_response_under_3s(self) -> None:
        user_id = self._register_user()
        self._submit_green_assessment(user_id)

        start_response = self.client.post(
            f"/api/coach/{user_id}/start",
            json={"style_id": "warm_guide", "subscription_active": True},
        )
        self.assertEqual(start_response.status_code, 200)
        session_id = start_response.json()["session"]["session_id"]

        start = time.perf_counter()
        chat_response = self.client.post(
            f"/api/coach/{session_id}/chat",
            json={"user_message": "I feel stressed about work and want to plan tomorrow."},
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        self.assertEqual(chat_response.status_code, 200)
        self.assertEqual(chat_response.json()["mode"], "coaching")
        self.assertLess(elapsed_ms, 3000.0)


if __name__ == "__main__":
    unittest.main()
