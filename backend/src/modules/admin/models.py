from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class AdminSession:
    session_id: str
    username: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    revoked: bool = False

    def is_active(self, now: datetime) -> bool:
        return not self.revoked and self.expires_at > now

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "username": self.username,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "revoked": self.revoked,
        }
