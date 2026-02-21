import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.admin_endpoints import AdminAPI
from modules.api.endpoints import OnboardingAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import TriageChannel


class AdminUserManagementContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding = OnboardingAPI(service=OnboardingService(self.store))
        self.admin = AdminAPI(store=self.store)

        self.user_green = self._register("admin-user-green@example.com")
        self.user_yellow = self._register("admin-user-yellow@example.com")
        self._assess_yellow(self.user_yellow)

        status, _, session_id = self.admin.post_login({"username": "admin", "password": "admin"})
        self.assertEqual(status, 200)
        self.assertIsNotNone(session_id)
        self.session_id = session_id

    def _register(self, email: str) -> str:
        status, body = self.onboarding.post_register(
            {
                "email": email,
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.assertEqual(status, 201)
        return body["data"]["user_id"]

    def _assess_yellow(self, user_id: str) -> None:
        status, _ = self.onboarding.post_assessment(
            user_id=user_id,
            payload={
                "responses": {
                    "phq9": [2] * 5 + [0] * 4,
                    "gad7": [0] * 7,
                    "pss10": [0] * 10,
                    "cssrs": {"q1": False, "q2": False},
                }
            },
        )
        self.assertEqual(status, 200)

    def test_get_users_requires_session(self) -> None:
        status, body = self.admin.get_users(session_id=None)
        self.assertEqual(status, 401)
        self.assertIn("Admin session required", body["error"])

    def test_get_users_contract(self) -> None:
        status, body = self.admin.get_users(session_id=self.session_id, limit=50)
        self.assertEqual(status, 200)
        data = body["data"]
        self.assertGreaterEqual(data["count"], 2)
        self.assertTrue(any(item["user_id"] == self.user_green for item in data["items"]))
        yellow_item = next(item for item in data["items"] if item["user_id"] == self.user_yellow)
        self.assertIsNotNone(yellow_item["triage"])
        self.assertEqual(yellow_item["triage"]["channel"], "yellow")

    def test_manual_triage_override_contract(self) -> None:
        status, body = self.admin.post_user_triage_override(
            session_id=self.session_id,
            user_id=self.user_green,
            payload={"channel": "red", "reasons": ["manual-review"]},
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["data"]["triage"]["channel"], "red")
        self.assertTrue(body["data"]["triage"]["halt_coaching"])
        self.assertTrue(body["data"]["triage"]["show_hotline"])

        triage = self.store.get_triage(self.user_green)
        self.assertIsNotNone(triage)
        self.assertEqual(triage.channel, TriageChannel.RED)


if __name__ == "__main__":
    unittest.main()
