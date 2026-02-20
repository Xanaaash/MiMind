from typing import Any, Dict, Optional, Tuple

from modules.journal.service import JournalService
from modules.storage.in_memory import InMemoryStore
from modules.tools.audio.service import AudioToolService
from modules.tools.breathing.service import BreathingToolService
from modules.tools.meditation.service import MeditationToolService
from modules.tools.stats.service import ToolUsageStatsService


class HealingToolsAPI:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self._store = store or InMemoryStore()
        self._audio = AudioToolService(self._store)
        self._breathing = BreathingToolService(self._store)
        self._meditation = MeditationToolService(self._store)
        self._stats = ToolUsageStatsService(self._store)
        self._journal = JournalService(self._store)

    @property
    def store(self) -> InMemoryStore:
        return self._store

    def get_audio_library(self) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._audio.list_tracks()}

    def post_start_audio(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            track_id = str(payload.get("track_id", "")).strip()
            minutes = int(payload.get("minutes", 0))
            data = self._audio.start_playback(user_id=user_id, track_id=track_id, minutes=minutes)
            return 200, {"data": data}
        except (ValueError, TypeError) as error:
            return 400, {"error": str(error)}

    def post_breathing_session(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            cycles = int(payload.get("cycles", 0))
            data = self._breathing.complete_session(user_id=user_id, cycles=cycles)
            return 200, {"data": data}
        except (ValueError, TypeError) as error:
            return 400, {"error": str(error)}

    def get_meditation_library(self) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._meditation.list_sessions()}

    def post_start_meditation(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            meditation_id = str(payload.get("meditation_id", "")).strip()
            data = self._meditation.start_session(user_id=user_id, meditation_id=meditation_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_journal_entry(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            mood = str(payload.get("mood", "")).strip()
            energy = int(payload.get("energy", 0))
            note = str(payload.get("note", ""))
            data = self._journal.add_entry(user_id=user_id, mood=mood, energy=energy, note=note)
            return 200, {"data": data}
        except (ValueError, TypeError) as error:
            return 400, {"error": str(error)}

    def get_journal_entries(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._journal.list_entries(user_id)}

    def get_journal_trend(self, user_id: str, days: int) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._journal.trend(user_id=user_id, days=days)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def get_usage_stats(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._stats.get_usage_stats(user_id=user_id)}
