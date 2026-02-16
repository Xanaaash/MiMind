from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


@dataclass
class TestDefinition:
    test_id: str
    display_name: str
    version: str
    theory_reference: str
    scoring_type: str
    required_answer_keys: List[str]
    answer_range: str
    category: str

    def to_catalog_dict(self) -> dict:
        return {
            "display_name": self.display_name,
            "version": self.version,
            "theory_reference": self.theory_reference,
            "scoring_type": self.scoring_type,
            "required_answer_keys": list(self.required_answer_keys),
            "answer_range": self.answer_range,
            "category": self.category,
            "input_dimension_count": len(self.required_answer_keys),
        }


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
