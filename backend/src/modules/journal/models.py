from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class JournalEntry:
    entry_id: str
    user_id: str
    mood: str
    energy: int
    note: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "user_id": self.user_id,
            "mood": self.mood,
            "energy": self.energy,
            "note": self.note,
            "created_at": self.created_at.isoformat(),
        }
