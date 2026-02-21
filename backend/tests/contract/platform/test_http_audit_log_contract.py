import unittest
from uuid import uuid4

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from fastapi.testclient import TestClient

from app import app


class HTTPAuditLogContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_register_request_is_recorded_with_masked_email(self) -> None:
        email = f"audit-{uuid4().hex[:8]}@example.com"
        register = self.client.post(
            "/api/register",
            json={
                "email": email,
                "locale": "en-US",
                "policy_version": "2026.02",
            },
        )
        self.assertEqual(register.status_code, 200)

        logs = self.client.get(
            "/api/observability/http-audit",
            params={
                "path": "/api/register",
                "method": "POST",
                "limit": 5,
            },
        )
        self.assertEqual(logs.status_code, 200)
        data = logs.json()
        self.assertGreaterEqual(len(data), 1)

        payload = data[0]["request_payload"]["body"]
        self.assertIn("email", payload)
        self.assertNotEqual(payload["email"], email)
        self.assertIn("***@", payload["email"])
        self.assertEqual(data[0]["path"], "/api/register")

    def test_admin_login_request_masks_password(self) -> None:
        login = self.client.post(
            "/api/admin/login",
            json={
                "username": "admin",
                "password": "admin",
            },
        )
        self.assertEqual(login.status_code, 200)

        logs = self.client.get(
            "/api/observability/http-audit",
            params={
                "path": "/api/admin/login",
                "method": "POST",
                "limit": 5,
            },
        )
        self.assertEqual(logs.status_code, 200)
        data = logs.json()
        self.assertGreaterEqual(len(data), 1)

        payload = data[0]["request_payload"]["body"]
        self.assertIn("password", payload)
        self.assertNotEqual(payload["password"], "admin")
        self.assertEqual(data[0]["path"], "/api/admin/login")


if __name__ == "__main__":
    unittest.main()
