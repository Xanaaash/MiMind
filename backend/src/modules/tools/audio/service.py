from datetime import datetime, timedelta, timezone

from modules.storage.in_memory import InMemoryStore


AUDIO_LIBRARY = {
    "rain": {"name": "Rainfall", "category": "white-noise"},
    "forest": {"name": "Forest Breeze", "category": "ambient"},
    "waves": {"name": "Ocean Waves", "category": "ambient"},
}


class AudioToolService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def list_tracks(self) -> dict:
        return dict(AUDIO_LIBRARY)

    def start_playback(self, user_id: str, track_id: str, minutes: int) -> dict:
        if track_id not in AUDIO_LIBRARY:
            raise ValueError("Unknown track_id")
        if minutes <= 0 or minutes > 180:
            raise ValueError("minutes must be between 1 and 180")

        started_at = datetime.now(timezone.utc)
        ends_at = started_at + timedelta(minutes=minutes)

        self._store.save_tool_event(
            user_id,
            {
                "tool": "audio",
                "track_id": track_id,
                "started_at": started_at.isoformat(),
                "ends_at": ends_at.isoformat(),
            },
        )

        return {
            "track": AUDIO_LIBRARY[track_id],
            "track_id": track_id,
            "duration_minutes": minutes,
            "ends_at": ends_at.isoformat(),
        }
