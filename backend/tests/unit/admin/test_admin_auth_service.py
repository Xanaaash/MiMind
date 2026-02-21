import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.admin.service import AdminAuthService
from modules.storage.in_memory import InMemoryStore


class AdminAuthServiceUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()

    def test_login_persists_session_and_returns_payload(self) -> None:
        with patch.dict(os.environ, {"ADMIN_PASSWORD": "test-admin-pass", "ADMIN_SESSION_TTL_HOURS": "12"}):
            service = AdminAuthService(self.store)
            session = service.login(username="admin", password="test-admin-pass")

            self.assertTrue(session.session_id)
            persisted = self.store.get_admin_session(session.session_id)
            self.assertIsNotNone(persisted)
            self.assertEqual(persisted.username, "admin")  # type: ignore[union-attr]

            payload = service.session_payload(session)
            self.assertTrue(payload["authenticated"])
            self.assertEqual(payload["username"], "admin")
            self.assertIn("expires_at", payload)
            self.assertEqual(service.cookie_max_age_seconds(), 12 * 3600)

    def test_login_rejects_invalid_credentials(self) -> None:
        with patch.dict(os.environ, {"ADMIN_PASSWORD": "secret-pass"}):
            service = AdminAuthService(self.store)

            with self.assertRaisesRegex(ValueError, "Invalid credentials"):
                service.login(username="admin", password="wrong-pass")

            with self.assertRaisesRegex(ValueError, "Invalid credentials"):
                service.login(username="wrong-admin", password="secret-pass")

    def test_get_valid_session_revokes_expired_session(self) -> None:
        with patch.dict(os.environ, {"ADMIN_PASSWORD": "test-admin-pass"}):
            service = AdminAuthService(self.store)
            session = service.login(username="admin", password="test-admin-pass")

            expired = datetime.now(timezone.utc) - timedelta(minutes=1)
            persisted = self.store.get_admin_session(session.session_id)
            self.assertIsNotNone(persisted)
            persisted.expires_at = expired  # type: ignore[union-attr]

            restored = service.get_valid_session(session.session_id)
            self.assertIsNone(restored)
            self.assertTrue(self.store.get_admin_session(session.session_id).revoked)  # type: ignore[union-attr]

    def test_logout_revokes_session(self) -> None:
        with patch.dict(os.environ, {"ADMIN_PASSWORD": "test-admin-pass"}):
            service = AdminAuthService(self.store)
            session = service.login(username="admin", password="test-admin-pass")

            self.assertIsNotNone(service.get_valid_session(session.session_id))
            service.logout(session.session_id)
            self.assertIsNone(service.get_valid_session(session.session_id))

    def test_password_source_payload_reports_fallback_usage(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            fallback_service = AdminAuthService(self.store)
            fallback = fallback_service.password_source_payload()
            self.assertTrue(fallback["uses_dev_fallback_password"])

        with patch.dict(os.environ, {"ADMIN_PASSWORD": "custom-secure-pass"}):
            configured_service = AdminAuthService(self.store)
            configured = configured_service.password_source_payload()
            self.assertFalse(configured["uses_dev_fallback_password"])
            self.assertEqual(configured["username"], "admin")


if __name__ == "__main__":
    unittest.main()
