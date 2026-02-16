from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class TestDefinition:
    test_id: str
    display_name: str
    version: str
    theory_reference: str
    scoring_type: str


@dataclass
class TestResult:
    result_id: str
    user_id: str
    test_id: str
    answers: Dict[str, Any]
    summary: Dict[str, Any]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "result_id": self.result_id,
            "user_id": self.user_id,
            "test_id": self.test_id,
            "answers": self.answers,
            "summary": self.summary,
            "created_at": self.created_at.isoformat(),
        }
