from datetime import datetime, timezone

from modules.storage.in_memory import InMemoryStore
from modules.tools.media_assets import MediaAssetURLBuilder


MEDITATION_LIBRARY = {
    "calm-10": {
        "name": "10-Minute Calm Reset",
        "minutes": 10,
        "duration_seconds": 600,
        "category": "guided-meditation",
        "asset_path": "meditation/calm-reset.m4a",
    },
    "focus-15": {
        "name": "15-Minute Focus Grounding",
        "minutes": 15,
        "duration_seconds": 900,
        "category": "guided-meditation",
        "asset_path": "meditation/focus-grounding.m4a",
    },
    "sleep-20": {
        "name": "20-Minute Sleep Wind Down",
        "minutes": 20,
        "duration_seconds": 1200,
        "category": "guided-meditation",
        "asset_path": "meditation/sleep-winddown.m4a",
    },
}


class MeditationToolService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._assets = MediaAssetURLBuilder()

    def list_sessions(self) -> dict:
        return {session_id: self._hydrate_session(session_id) for session_id in MEDITATION_LIBRARY}

    def start_session(self, user_id: str, meditation_id: str) -> dict:
        if meditation_id not in MEDITATION_LIBRARY:
            raise ValueError("Unknown meditation_id")

        session = self._hydrate_session(meditation_id)
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

    def _hydrate_session(self, meditation_id: str) -> dict:
        session = dict(MEDITATION_LIBRARY[meditation_id])
        asset_path = session.pop("asset_path")
        session["audio_url"] = self._assets.build(asset_path)
        session["asset_base_url"] = self._assets.base_url
        session["hosting"] = "cdn-or-embedded-static"
        return session
