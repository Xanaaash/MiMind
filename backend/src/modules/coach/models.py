from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class CoachTurn:
    role: str
    message: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CoachSession:
    session_id: str
    user_id: str
    style_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    active: bool = True
    halted_for_safety: bool = False
    turns: List[CoachTurn] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "style_id": self.style_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "active": self.active,
            "halted_for_safety": self.halted_for_safety,
            "turn_count": len(self.turns),
        }
