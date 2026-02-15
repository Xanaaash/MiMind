from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ConsentRecord:
    consent_id: str
    user_id: str
    policy_version: str
    accepted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
