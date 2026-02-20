from datetime import datetime, timedelta, timezone

from modules.storage.in_memory import InMemoryStore
from modules.tools.media_assets import MediaAssetURLBuilder


AUDIO_LIBRARY = {
    "rain": {
        "name": "Rainfall",
        "category": "white-noise",
        "duration_seconds": 0,
        "hosting": "embedded-web-audio",
        "asset_path": None,
    },
    "ocean": {
        "name": "Ocean Waves",
        "category": "white-noise",
        "duration_seconds": 0,
        "hosting": "embedded-web-audio",
        "asset_path": None,
    },
    "forest": {
        "name": "Forest Breeze",
        "category": "white-noise",
        "duration_seconds": 0,
        "hosting": "embedded-web-audio",
        "asset_path": None,
    },
    "campfire": {
        "name": "Campfire Crackle",
        "category": "white-noise",
        "duration_seconds": 0,
        "hosting": "embedded-web-audio",
        "asset_path": None,
    },
    "cafe": {
        "name": "Cafe Ambience",
        "category": "white-noise",
        "duration_seconds": 0,
        "hosting": "embedded-web-audio",
        "asset_path": None,
    },
}


class AudioToolService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._assets = MediaAssetURLBuilder()

    def list_tracks(self) -> dict:
        return {track_id: self._hydrate_track(track_id) for track_id in AUDIO_LIBRARY}

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
                "minutes": minutes,
                "occurred_at": started_at.isoformat(),
                "started_at": started_at.isoformat(),
                "ends_at": ends_at.isoformat(),
            },
        )

        return {
            "track": self._hydrate_track(track_id),
            "track_id": track_id,
            "duration_minutes": minutes,
            "ends_at": ends_at.isoformat(),
        }

    def _hydrate_track(self, track_id: str) -> dict:
        track = dict(AUDIO_LIBRARY[track_id])
        asset_path = track.pop("asset_path", None)
        track["stream_url"] = self._assets.build(asset_path) if asset_path else None
        track["asset_base_url"] = self._assets.base_url
        return track
