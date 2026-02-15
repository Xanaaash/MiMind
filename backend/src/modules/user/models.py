from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class User:
    user_id: str
    email: str
    locale: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
