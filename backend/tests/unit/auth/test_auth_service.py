import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.auth.service import AuthService
from modules.storage.in_memory import InMemoryStore


class AuthServiceUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.service = AuthService(self.store)

    def test_register_with_password_hashes_credentials(self) -> None:
        user = self.service.register_user(
            email="auth-user@example.com",
            locale="en-US",
            password="StrongPass123",
        )
        self.assertEqual(user.auth_provider, "password")
        self.assertIsNotNone(user.password_hash)
        self.assertNotEqual(user.password_hash, "StrongPass123")
        self.assertFalse(user.email_verified)
        self.assertIsNotNone(user.email_verification_token)

    def test_verify_email_marks_user_verified(self) -> None:
        user = self.service.register_user(
            email="verify@example.com",
            locale="en-US",
            password="StrongPass123",
        )
        self.assertIsNotNone(user.email_verification_token)

        verified = self.service.verify_email(user.email_verification_token or "")
        self.assertTrue(verified.email_verified)
        self.assertIsNone(verified.email_verification_token)

    def test_resend_verification_rotates_token(self) -> None:
        user = self.service.register_user(
            email="resend@example.com",
            locale="en-US",
            password="StrongPass123",
        )
        original = user.email_verification_token
        resent = self.service.resend_verification("resend@example.com")
        self.assertFalse(resent.email_verified)
        self.assertNotEqual(original, resent.email_verification_token)

    def test_authenticate_rejects_wrong_password(self) -> None:
        self.service.register_user(
            email="auth-user@example.com",
            locale="en-US",
            password="StrongPass123",
        )
        with self.assertRaises(ValueError):
            self.service.authenticate("auth-user@example.com", "wrong-pass")

    def test_refresh_rotates_access_and_refresh_tokens(self) -> None:
        user = self.service.register_user(
            email="auth-user@example.com",
            locale="en-US",
            password="StrongPass123",
        )
        first = self.service.issue_token_bundle(user)
        refreshed_user, second = self.service.refresh_tokens(first.refresh_token)

        self.assertEqual(refreshed_user.user_id, user.user_id)
        self.assertNotEqual(first.access_token, second.access_token)
        self.assertNotEqual(first.refresh_token, second.refresh_token)

    def test_guest_user_cannot_password_login(self) -> None:
        self.service.register_user(
            email="guest-only@example.com",
            locale="en-US",
            password=None,
        )
        with self.assertRaises(ValueError):
            self.service.authenticate("guest-only@example.com", "any-pass")

    def test_request_password_reset_generates_token_for_password_user(self) -> None:
        user = self.service.register_user(
            email="reset-user@example.com",
            locale="en-US",
            password="StrongPass123",
        )
        self.assertIsNone(user.password_reset_token)

        self.service.request_password_reset("reset-user@example.com")
        refreshed = self.store.get_user_by_email("reset-user@example.com")
        self.assertIsNotNone(refreshed)
        self.assertIsNotNone(refreshed.password_reset_token)
        self.assertIsNotNone(refreshed.password_reset_expires_at)

    def test_reset_password_rehashes_and_clears_reset_token(self) -> None:
        self.service.register_user(
            email="reset-final@example.com",
            locale="en-US",
            password="StrongPass123",
        )
        self.service.request_password_reset("reset-final@example.com")
        target = self.store.get_user_by_email("reset-final@example.com")
        self.assertIsNotNone(target)
        token = target.password_reset_token
        original_hash = target.password_hash

        self.service.reset_password(token=token or "", password="NewPass123")
        updated = self.store.get_user_by_email("reset-final@example.com")
        self.assertIsNotNone(updated)
        self.assertNotEqual(original_hash, updated.password_hash)
        self.assertIsNone(updated.password_reset_token)
        self.assertIsNone(updated.password_reset_expires_at)


if __name__ == "__main__":
    unittest.main()
