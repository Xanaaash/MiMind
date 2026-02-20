import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.journal.context_adapter import build_journal_context_summary
from modules.journal.service import JournalService
from modules.storage.in_memory import InMemoryStore
from modules.tools.audio.service import AudioToolService
from modules.tools.breathing.service import BreathingToolService
from modules.tools.meditation.service import MeditationToolService
from modules.tools.stats.service import ToolUsageStatsService
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

    def test_tool_usage_stats_aggregates_usage_and_duration(self) -> None:
        audio = AudioToolService(self.store)
        breathing = BreathingToolService(self.store)
        meditation = MeditationToolService(self.store)
        stats_service = ToolUsageStatsService(self.store)

        audio.start_playback(user_id=self.user_id, track_id="rain", minutes=5)
        breathing.complete_session(user_id=self.user_id, cycles=2)
        meditation.start_session(user_id=self.user_id, meditation_id="calm-10")

        stats = stats_service.get_usage_stats(self.user_id)
        self.assertEqual(stats["week_usage_count"], 3)
        self.assertEqual(stats["total_usage_count"], 3)
        self.assertEqual(stats["total_duration_seconds"], 938)

    def test_audio_library_exposes_hosting_metadata(self) -> None:
        audio = AudioToolService(self.store)
        library = audio.list_tracks()

        self.assertIn("campfire", library)
        self.assertEqual(library["rain"]["hosting"], "embedded-web-audio")
        self.assertIn("asset_base_url", library["rain"])
        self.assertIsNone(library["rain"]["stream_url"])

    def test_meditation_library_exposes_audio_urls(self) -> None:
        meditation = MeditationToolService(self.store)
        sessions = meditation.list_sessions()

        self.assertIn("calm-10", sessions)
        self.assertEqual(sessions["calm-10"]["duration_seconds"], 600)
        self.assertIn("/audio/meditation/calm-reset.m4a", sessions["calm-10"]["audio_url"])
        self.assertEqual(sessions["calm-10"]["hosting"], "cdn-or-embedded-static")


if __name__ == "__main__":
    unittest.main()
