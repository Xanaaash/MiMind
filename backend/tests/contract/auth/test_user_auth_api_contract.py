import unittest
from uuid import uuid4

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.auth_endpoints import UserAuthAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class UserAuthAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        onboarding = OnboardingService(self.store)
        self.api = UserAuthAPI(store=self.store, onboarding_service=onboarding)

    def test_register_login_session_refresh_logout_contract(self) -> None:
        email = f"auth-{uuid4().hex[:8]}@example.com"
        register_status, register_body, register_tokens = self.api.post_register(
            {
                "email": email,
                "password": "StrongPass123",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(register_status, 201)
        self.assertIsNotNone(register_tokens)
        self.assertTrue(register_body["data"]["authenticated"])
        self.assertEqual(register_body["data"]["email"], email)
        self.assertFalse(register_body["data"]["email_verified"])
        verification = register_body["data"]["email_verification"]
        self.assertTrue(verification["required"])
        self.assertFalse(verification["verified"])
        self.assertIn("token", verification)

        session_status, session_body = self.api.get_session(register_tokens.access_token)  # type: ignore[union-attr]
        self.assertEqual(session_status, 200)
        self.assertTrue(session_body["data"]["authenticated"])
        self.assertEqual(session_body["data"]["email"], email)

        refresh_status, refresh_body, refresh_tokens = self.api.post_refresh(register_tokens.refresh_token)  # type: ignore[union-attr]
        self.assertEqual(refresh_status, 200)
        self.assertIsNotNone(refresh_tokens)
        self.assertTrue(refresh_body["data"]["authenticated"])
        self.assertEqual(refresh_body["data"]["email"], email)
        self.assertNotEqual(register_tokens.access_token, refresh_tokens.access_token)  # type: ignore[union-attr]

        logout_status, logout_body = self.api.post_logout()
        self.assertEqual(logout_status, 200)
        self.assertFalse(logout_body["data"]["authenticated"])

        verify_status, verify_body = self.api.post_verify_email({"token": verification["token"]})
        self.assertEqual(verify_status, 200)
        self.assertTrue(verify_body["data"]["verified"])
        self.assertEqual(verify_body["data"]["email"], email)

    def test_duplicate_email_registration_returns_409(self) -> None:
        email = f"dup-{uuid4().hex[:8]}@example.com"
        first_status, _, _ = self.api.post_register(
            {
                "email": email,
                "password": "StrongPass123",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(first_status, 201)

        second_status, second_body, _ = self.api.post_register(
            {
                "email": email,
                "password": "StrongPass123",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(second_status, 409)
        self.assertIn("Email already registered", second_body["error"])

    def test_invalid_login_returns_401(self) -> None:
        email = f"login-{uuid4().hex[:8]}@example.com"
        self.api.post_register(
            {
                "email": email,
                "password": "StrongPass123",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )

        status, body, tokens = self.api.post_login({"email": email, "password": "wrong"})
        self.assertEqual(status, 401)
        self.assertIsNone(tokens)
        self.assertIn("Invalid credentials", body["error"])

    def test_legacy_user_without_password_cannot_login(self) -> None:
        onboarding = OnboardingService(self.store)
        email = f"legacy-{uuid4().hex[:8]}@example.com"
        onboarding.register(
            email=email,
            locale="en-US",
            policy_version="2026.02",
        )

        status, body, tokens = self.api.post_login(
            {"email": email, "password": "StrongPass123"}
        )
        self.assertEqual(status, 401)
        self.assertIsNone(tokens)
        self.assertIn("Invalid credentials", body["error"])

    def test_resend_verification_contract(self) -> None:
        email = f"verify-{uuid4().hex[:8]}@example.com"
        self.api.post_register(
            {
                "email": email,
                "password": "StrongPass123",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )

        status, body = self.api.post_resend_verification({"email": email})
        self.assertEqual(status, 200)
        self.assertEqual(body["data"]["email"], email)
        self.assertTrue(body["data"]["email_verification"]["required"])
        self.assertIn("token", body["data"]["email_verification"])


if __name__ == "__main__":
    unittest.main()
