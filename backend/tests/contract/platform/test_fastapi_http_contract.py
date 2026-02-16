import unittest
from uuid import uuid4

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from fastapi.testclient import TestClient

from app import app


class FastAPIHTTPContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_healthz(self) -> None:
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_register_and_assessment_flow(self) -> None:
        email = f"api-{uuid4().hex[:8]}@example.com"

        register = self.client.post(
            "/api/register",
            json={
                "email": email,
                "locale": "en-US",
                "policy_version": "2026.02",
            },
        )
        self.assertEqual(register.status_code, 200)
        user_id = register.json()["user_id"]

        assessment = self.client.post(
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
        self.assertEqual(assessment.status_code, 200)
        self.assertEqual(assessment.json()["triage"]["channel"], "green")

        entitlements = self.client.get(f"/api/billing/{user_id}/entitlements")
        self.assertEqual(entitlements.status_code, 200)
        self.assertEqual(entitlements.json()["plan_id"], "free")


if __name__ == "__main__":
    unittest.main()
