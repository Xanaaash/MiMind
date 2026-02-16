import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.endpoints import OnboardingAPI
from modules.api.tools_endpoints import HealingToolsAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore


class JournalRiskForwardingSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.onboarding_api = OnboardingAPI(service=OnboardingService(self.store))
        self.tools_api = HealingToolsAPI(store=self.store)

        _, body = self.onboarding_api.post_register(
            {
                "email": "journal-risk@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        self.user_id = body["data"]["user_id"]

    def test_high_risk_journal_entry_forwards_signal(self) -> None:
        status, body = self.tools_api.post_journal_entry(
            self.user_id,
            {
                "mood": "hopeless",
                "energy": 2,
                "note": "I want to kill myself tonight",
            },
        )

        self.assertEqual(status, 200)
        self.assertIsNotNone(body["data"]["risk_signal"])
        self.assertEqual(body["data"]["risk_signal"]["risk_level"], "high")

        events = self.store.tool_events.get(self.user_id, [])
        risk_events = [event for event in events if event.get("tool") == "journal-risk"]
        self.assertGreaterEqual(len(risk_events), 1)


if __name__ == "__main__":
    unittest.main()
