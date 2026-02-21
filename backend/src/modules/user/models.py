from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class User:
    user_id: str
    email: str
    locale: str
    password_hash: Optional[str] = None
    auth_provider: str = "guest"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
