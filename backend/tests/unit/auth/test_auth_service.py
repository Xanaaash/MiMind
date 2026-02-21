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


if __name__ == "__main__":
    unittest.main()
