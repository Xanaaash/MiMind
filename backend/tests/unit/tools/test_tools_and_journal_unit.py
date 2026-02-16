import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.journal.context_adapter import build_journal_context_summary
from modules.journal.service import JournalService
from modules.storage.in_memory import InMemoryStore
from modules.tools.breathing.service import BreathingToolService
from modules.user.models import User


class ToolsAndJournalUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()
        self.user_id = "tool-user"
        self.store.save_user(User(user_id=self.user_id, email="tool@example.com", locale="en-US"))

    def test_breathing_pattern_has_expected_duration(self) -> None:
        service = BreathingToolService(self.store)
        pattern = service.complete_session(user_id=self.user_id, cycles=3)
        self.assertEqual(pattern["total_seconds"], 57)
        self.assertEqual(len(pattern["steps"]), 9)

    def test_journal_trend_calculation(self) -> None:
        journal = JournalService(self.store)
        journal.add_entry(self.user_id, mood="calm", energy=7, note="A steady day")
        journal.add_entry(self.user_id, mood="stressed", energy=4, note="Work pressure")

        trend = journal.trend(self.user_id, days=7)
        self.assertEqual(trend["entry_count"], 2)
        self.assertEqual(trend["average_energy"], 5.5)

    def test_journal_context_adapter_uses_recent_entries(self) -> None:
        journal = JournalService(self.store)
        journal.add_entry(self.user_id, mood="hopeful", energy=8, note="Better today")

        summary = build_journal_context_summary(self.store, self.user_id)
        self.assertEqual(summary["entry_count"], 1)
        self.assertEqual(summary["latest_mood"], "hopeful")
        self.assertEqual(summary["average_energy"], 8.0)


if __name__ == "__main__":
    unittest.main()
