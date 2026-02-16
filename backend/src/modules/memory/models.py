from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from uuid import uuid4


@dataclass
class MemoryVectorRecord:
    user_id: str
    text: str
    embedding: List[float]
    memory_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "memory_id": self.memory_id,
            "user_id": self.user_id,
            "text": self.text,
            "embedding": list(self.embedding),
            "created_at": self.created_at.isoformat(),
        }
