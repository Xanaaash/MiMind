import uuid
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from modules.journal.models import JournalEntry
from modules.storage.in_memory import InMemoryStore


HIGH_RISK_KEYWORDS = ["kill myself", "end my life", "suicide", "self-harm"]
MEDIUM_RISK_KEYWORDS = ["hopeless", "can't go on", "worthless"]


class JournalService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def add_entry(self, user_id: str, mood: str, energy: int, note: str) -> dict:
        if not mood:
            raise ValueError("mood is required")
        if energy < 0 or energy > 10:
            raise ValueError("energy must be between 0 and 10")

        entry = JournalEntry(
            entry_id=str(uuid.uuid4()),
            user_id=user_id,
            mood=mood.strip().lower(),
            energy=energy,
            note=str(note).strip(),
            created_at=datetime.now(timezone.utc),
        )
        self._store.save_journal_entry(entry)

        risk_signal = self._detect_risk(entry)
        if risk_signal is not None:
            self._store.save_tool_event(
                user_id,
                {
                    "tool": "journal-risk",
                    "entry_id": entry.entry_id,
                    "risk_level": risk_signal["risk_level"],
                    "reason": risk_signal["reason"],
                },
            )

        return {
            "entry": entry.to_dict(),
            "risk_signal": risk_signal,
        }

    def list_entries(self, user_id: str) -> List[dict]:
        entries = self._store.list_journal_entries(user_id)
        return [entry.to_dict() for entry in entries]

    def trend(self, user_id: str, days: int) -> Dict[str, object]:
        if days <= 0 or days > 365:
            raise ValueError("days must be between 1 and 365")

        entries = self._store.list_journal_entries(user_id)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        filtered = [entry for entry in entries if entry.created_at >= cutoff]

        if not filtered:
            return {
                "days": days,
                "entry_count": 0,
                "average_energy": None,
                "mood_distribution": {},
            }

        average_energy = sum(entry.energy for entry in filtered) / len(filtered)
        mood_distribution = Counter(entry.mood for entry in filtered)

        return {
            "days": days,
            "entry_count": len(filtered),
            "average_energy": round(average_energy, 2),
            "mood_distribution": dict(mood_distribution),
        }

    @staticmethod
    def _detect_risk(entry: JournalEntry) -> Optional[Dict[str, str]]:
        text = f"{entry.mood} {entry.note}".lower()

        for keyword in HIGH_RISK_KEYWORDS:
            if keyword in text:
                return {
                    "risk_level": "high",
                    "reason": f"keyword:{keyword}",
                }

        for keyword in MEDIUM_RISK_KEYWORDS:
            if keyword in text:
                return {
                    "risk_level": "medium",
                    "reason": f"keyword:{keyword}",
                }

        return None
