from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Dict


@dataclass
class AssessmentSubmission:
    submission_id: str
    user_id: str
    responses: Dict[str, Any]
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AssessmentScoreSet:
    phq9_score: int
    gad7_score: int
    pss10_score: int
    cssrs_positive: bool

    def to_dict(self) -> dict:
        return {
            "phq9_score": self.phq9_score,
            "gad7_score": self.gad7_score,
            "pss10_score": self.pss10_score,
            "cssrs_positive": self.cssrs_positive,
        }


@dataclass
class ReassessmentSchedule:
    due_dates: Dict[str, date]

    def to_dict(self) -> dict:
        return {scale: due.isoformat() for scale, due in self.due_dates.items()}
