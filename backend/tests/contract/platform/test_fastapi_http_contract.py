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

    def test_user_auth_cookie_session_http(self) -> None:
        email = f"auth-http-{uuid4().hex[:8]}@example.com"
        register = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "StrongPass123",
                "locale": "en-US",
                "policy_version": "2026.02",
            },
        )
        self.assertEqual(register.status_code, 201)
        self.assertIn("mc_access_token", register.cookies)
        self.assertIn("mc_refresh_token", register.cookies)
        self.assertIn("email_verification", register.json())
        verification = register.json()["email_verification"]
        self.assertTrue(verification["required"])
        self.assertIn("token", verification)

        session = self.client.get("/api/auth/session")
        self.assertEqual(session.status_code, 200)
        self.assertTrue(session.json()["authenticated"])
        self.assertEqual(session.json()["email"], email)

        refresh = self.client.post("/api/auth/refresh")
        self.assertEqual(refresh.status_code, 200)
        self.assertTrue(refresh.json()["authenticated"])

        verify = self.client.post(
            "/api/auth/verify-email",
            json={"token": verification["token"]},
        )
        self.assertEqual(verify.status_code, 200)
        self.assertTrue(verify.json()["verified"])

        logout = self.client.post("/api/auth/logout")
        self.assertEqual(logout.status_code, 200)
        self.assertFalse(logout.json()["authenticated"])

        session_after_logout = self.client.get("/api/auth/session")
        self.assertEqual(session_after_logout.status_code, 401)

    def test_user_auth_password_reset_http(self) -> None:
        email = f"auth-reset-{uuid4().hex[:8]}@example.com"
        register = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "StrongPass123",
                "locale": "en-US",
                "policy_version": "2026.02",
            },
        )
        self.assertEqual(register.status_code, 201)

        forgot = self.client.post(
            "/api/auth/password/forgot",
            json={"email": email},
        )
        self.assertEqual(forgot.status_code, 200)
        self.assertTrue(forgot.json()["reset_requested"])

        verify_token = register.json()["email_verification"]["token"]
        verify = self.client.post("/api/auth/verify-email", json={"token": verify_token})
        self.assertEqual(verify.status_code, 200)

        from app import store  # local import to avoid circular in module load

        user = store.get_user_by_email(email)
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.password_reset_token)

        reset = self.client.post(
            "/api/auth/password/reset",
            json={"token": user.password_reset_token, "password": "NewPass123"},
        )
        self.assertEqual(reset.status_code, 200)
        self.assertTrue(reset.json()["reset"])

        login = self.client.post(
            "/api/auth/login",
            json={"email": email, "password": "NewPass123"},
        )
        self.assertEqual(login.status_code, 200)
        self.assertTrue(login.json()["authenticated"])

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

        with self.client.stream(
            "POST",
            f"/api/coach/{session_id}/chat/stream",
            json={"user_message": "Please help me with a small plan for today."},
        ) as stream_response:
            self.assertEqual(stream_response.status_code, 200)
            self.assertIn("text/event-stream", stream_response.headers.get("content-type", ""))
            stream_body = "".join(stream_response.iter_text())

        self.assertIn("event: meta", stream_body)
        self.assertIn("event: token", stream_body)
        self.assertIn("event: done", stream_body)

        end = self.client.post(f"/api/coach/{session_id}/end")
        self.assertEqual(end.status_code, 200)

        history = self.client.get(
            f"/api/coach/{user_id}/sessions",
            params={"limit": 10},
        )
        self.assertEqual(history.status_code, 200)
        history_data = history.json()
        self.assertGreaterEqual(history_data["count"], 1)
        self.assertEqual(history_data["items"][0]["session"]["session_id"], session_id)

        summary = self.client.get(f"/api/coach/{user_id}/sessions/{session_id}")
        self.assertEqual(summary.status_code, 200)
        summary_data = summary.json()
        self.assertEqual(summary_data["session"]["session_id"], session_id)
        self.assertIn("summary", summary_data)

        obs = self.client.get(
            "/api/observability/model-invocations",
            params={"limit": 10, "task_type": "coach_generation"},
        )
        self.assertEqual(obs.status_code, 200)
        data = obs.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(all(item["task_type"] == "coach_generation" for item in data))

        model_summary = self.client.get(
            "/api/observability/model-invocations/summary",
            params={"limit": 10, "task_type": "coach_generation"},
        )
        self.assertEqual(model_summary.status_code, 200)
        model_summary_data = model_summary.json()
        self.assertIn("totals", model_summary_data)
        self.assertIn("by_task_type", model_summary_data)
        self.assertGreaterEqual(model_summary_data["totals"]["total"], 1)

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

        breathing = self.client.post(
            f"/api/tools/breathing/{user_id}/complete",
            json={"cycles": 2},
        )
        self.assertEqual(breathing.status_code, 200)

        usage_stats = self.client.get(f"/api/tools/{user_id}/stats")
        self.assertEqual(usage_stats.status_code, 200)
        usage_payload = usage_stats.json()
        self.assertIn("week_usage_count", usage_payload)
        self.assertIn("total_duration_seconds", usage_payload)
        self.assertGreaterEqual(usage_payload["week_usage_count"], 1)

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

    def test_admin_auth_session_lifecycle_http(self) -> None:
        unauth_session = self.client.get("/api/admin/session")
        self.assertEqual(unauth_session.status_code, 401)

        invalid_login = self.client.post(
            "/api/admin/login",
            json={"username": "admin", "password": "wrong-password"},
        )
        self.assertEqual(invalid_login.status_code, 401)

        login = self.client.post(
            "/api/admin/login",
            json={"username": "admin", "password": "admin"},
        )
        self.assertEqual(login.status_code, 200)
        login_payload = login.json()
        self.assertTrue(login_payload["authenticated"])
        self.assertIn("auth_config", login_payload)
        self.assertIn("mc_admin_session", login.cookies)

        authed_session = self.client.get("/api/admin/session")
        self.assertEqual(authed_session.status_code, 200)
        self.assertTrue(authed_session.json()["authenticated"])
        self.assertEqual(authed_session.json()["username"], "admin")

        logout = self.client.post("/api/admin/logout")
        self.assertEqual(logout.status_code, 200)
        self.assertFalse(logout.json()["authenticated"])

        session_after_logout = self.client.get("/api/admin/session")
        self.assertEqual(session_after_logout.status_code, 401)

    def test_admin_user_management_and_compliance_http(self) -> None:
        unauth_users = self.client.get("/api/admin/users")
        self.assertEqual(unauth_users.status_code, 401)

        admin_login = self.client.post(
            "/api/admin/login",
            json={"username": "admin", "password": "admin"},
        )
        self.assertEqual(admin_login.status_code, 200)
        self.assertIn("mc_admin_session", admin_login.cookies)

        email = f"admin-users-{uuid4().hex[:8]}@example.com"
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

        users = self.client.get("/api/admin/users", params={"limit": 50})
        self.assertEqual(users.status_code, 200)
        users_payload = users.json()
        self.assertGreaterEqual(users_payload["count"], 1)
        matched = [item for item in users_payload["items"] if item["user_id"] == user_id]
        self.assertEqual(len(matched), 1)

        override = self.client.post(
            f"/api/admin/users/{user_id}/triage",
            json={"channel": "red", "reasons": ["admin-http-test"]},
        )
        self.assertEqual(override.status_code, 200)
        self.assertEqual(override.json()["triage"]["channel"], "red")
        self.assertTrue(override.json()["triage"]["halt_coaching"])

        export = self.client.get(f"/api/compliance/{user_id}/export")
        self.assertEqual(export.status_code, 200)
        self.assertEqual(export.json()["user_id"], user_id)

        erase = self.client.post(f"/api/compliance/{user_id}/erase")
        self.assertEqual(erase.status_code, 200)
        self.assertGreater(erase.json()["total_deleted"], 0)

        export_after_erase = self.client.get(f"/api/compliance/{user_id}/export")
        self.assertEqual(export_after_erase.status_code, 400)


if __name__ == "__main__":
    unittest.main()
