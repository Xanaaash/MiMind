from datetime import datetime, timezone

from modules.storage.in_memory import InMemoryStore


MEDITATION_LIBRARY = {
    "calm-10": {"name": "10-Minute Calm Reset", "minutes": 10},
    "focus-15": {"name": "15-Minute Focus Grounding", "minutes": 15},
    "sleep-20": {"name": "20-Minute Sleep Wind Down", "minutes": 20},
}


class MeditationToolService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def list_sessions(self) -> dict:
        return dict(MEDITATION_LIBRARY)

    def start_session(self, user_id: str, meditation_id: str) -> dict:
        if meditation_id not in MEDITATION_LIBRARY:
            raise ValueError("Unknown meditation_id")

        session = dict(MEDITATION_LIBRARY[meditation_id])
        started_at = datetime.now(timezone.utc)
        self._store.save_tool_event(
            user_id,
            {
                "tool": "meditation",
                "meditation_id": meditation_id,
                "minutes": session["minutes"],
                "started_at": started_at.isoformat(),
            },
        )

        return {
            "meditation_id": meditation_id,
            "session": session,
        }
