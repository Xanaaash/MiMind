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

    def test_prompt_catalog_http(self) -> None:
        packs = self.client.get("/api/prompts/packs")
        self.assertEqual(packs.status_code, 200)
        payload = packs.json()
        self.assertIn("2026.02.0", payload)
        self.assertIn("2026.02.1", payload)

        active = self.client.get("/api/prompts/active")
        self.assertEqual(active.status_code, 200)
        active_payload = active.json()
        self.assertIn("active_version", active_payload)

    def test_observability_http_contract(self) -> None:
        email = f"obs-{uuid4().hex[:8]}@example.com"
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

        start = self.client.post(
            f"/api/coach/{user_id}/start",
            json={"style_id": "warm_guide", "subscription_active": True},
        )
        self.assertEqual(start.status_code, 200)
        session_id = start.json()["session"]["session_id"]

        chat = self.client.post(
            f"/api/coach/{session_id}/chat",
            json={"user_message": "I feel stressed before work meetings."},
        )
        self.assertEqual(chat.status_code, 200)

        obs = self.client.get(
            "/api/observability/model-invocations",
            params={"limit": 10, "task_type": "coach_generation"},
        )
        self.assertEqual(obs.status_code, 200)
        data = obs.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(all(item["task_type"] == "coach_generation" for item in data))

        summary = self.client.get(
            "/api/observability/model-invocations/summary",
            params={"limit": 10, "task_type": "coach_generation"},
        )
        self.assertEqual(summary.status_code, 200)
        summary_data = summary.json()
        self.assertIn("totals", summary_data)
        self.assertIn("by_task_type", summary_data)
        self.assertGreaterEqual(summary_data["totals"]["total"], 1)

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

        reassessment = self.client.get(f"/api/reassessment/{user_id}")
        self.assertEqual(reassessment.status_code, 200)
        self.assertIn("due_dates", reassessment.json())
        self.assertIn("phq9", reassessment.json()["due_dates"])

        entitlements = self.client.get(f"/api/billing/{user_id}/entitlements")
        self.assertEqual(entitlements.status_code, 200)
        self.assertEqual(entitlements.json()["plan_id"], "free")

    def test_interactive_tests_http_catalog_and_submit(self) -> None:
        email = f"tests-{uuid4().hex[:8]}@example.com"
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

        catalog = self.client.get("/api/tests/catalog")
        self.assertEqual(catalog.status_code, 200)
        catalog_payload = catalog.json()
        self.assertIn("eq", catalog_payload)
        self.assertIn("stress_coping", catalog_payload)
        self.assertIn("psych_age", catalog_payload)
        self.assertIn("required_answer_keys", catalog_payload["eq"])

        eq_schema = self.client.get("/api/tests/catalog/eq")
        self.assertEqual(eq_schema.status_code, 200)
        eq_payload = eq_schema.json()
        self.assertEqual(eq_payload["scoring_type"], "eq")
        self.assertEqual(eq_payload["category"], "social_emotional")

        submit = self.client.post(
            f"/api/tests/{user_id}/submit",
            json={
                "test_id": "eq",
                "answers": {
                    "self_awareness": 79,
                    "self_regulation": 75,
                    "empathy": 81,
                    "relationship_management": 72,
                },
            },
        )
        self.assertEqual(submit.status_code, 200)
        submit_payload = submit.json()
        self.assertIn("overall_score", submit_payload["summary"])

    def test_compliance_export_and_erase_http(self) -> None:
        email = f"compliance-{uuid4().hex[:8]}@example.com"
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
                    "pss10": [1] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )
        self.assertEqual(assessment.status_code, 200)

        submit = self.client.post(
            f"/api/tests/{user_id}/submit",
            json={
                "test_id": "eq",
                "answers": {
                    "self_awareness": 75,
                    "self_regulation": 70,
                    "empathy": 72,
                    "relationship_management": 74,
                },
            },
        )
        self.assertEqual(submit.status_code, 200)

        export = self.client.get(f"/api/compliance/{user_id}/export")
        self.assertEqual(export.status_code, 200)
        export_payload = export.json()
        self.assertEqual(export_payload["user_id"], user_id)
        self.assertIn("assessment", export_payload["data"])
        self.assertIn("tests", export_payload["data"])

        erase = self.client.post(f"/api/compliance/{user_id}/erase")
        self.assertEqual(erase.status_code, 200)
        self.assertGreater(erase.json()["total_deleted"], 0)

        export_after_erase = self.client.get(f"/api/compliance/{user_id}/export")
        self.assertEqual(export_after_erase.status_code, 400)


if __name__ == "__main__":
    unittest.main()
