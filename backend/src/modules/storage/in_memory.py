from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from modules.assessment.models import AssessmentScoreSet, AssessmentSubmission, ReassessmentSchedule
from modules.compliance.models import ConsentRecord
from modules.tests.models import TestResult
from modules.triage.models import TriageDecision
from modules.user.models import User


@dataclass
class InMemoryStore:
    users: Dict[str, User] = field(default_factory=dict)
    consents: Dict[str, ConsentRecord] = field(default_factory=dict)
    submissions: Dict[str, List[AssessmentSubmission]] = field(default_factory=dict)
    scores: Dict[str, AssessmentScoreSet] = field(default_factory=dict)
    triage_decisions: Dict[str, TriageDecision] = field(default_factory=dict)
    schedules: Dict[str, ReassessmentSchedule] = field(default_factory=dict)
    test_results: Dict[str, TestResult] = field(default_factory=dict)
    user_test_results: Dict[str, List[str]] = field(default_factory=dict)

    def save_user(self, user: User) -> None:
        self.users[user.user_id] = user

    def save_consent(self, consent: ConsentRecord) -> None:
        self.consents[consent.consent_id] = consent

    def add_submission(self, submission: AssessmentSubmission) -> None:
        self.submissions.setdefault(submission.user_id, []).append(submission)

    def save_scores(self, user_id: str, scores: AssessmentScoreSet) -> None:
        self.scores[user_id] = scores

    def save_triage(self, user_id: str, decision: TriageDecision) -> None:
        self.triage_decisions[user_id] = decision

    def save_schedule(self, user_id: str, schedule: ReassessmentSchedule) -> None:
        self.schedules[user_id] = schedule

    def save_test_result(self, result: TestResult) -> None:
        self.test_results[result.result_id] = result
        self.user_test_results.setdefault(result.user_id, []).append(result.result_id)

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_scores(self, user_id: str) -> Optional[AssessmentScoreSet]:
        return self.scores.get(user_id)

    def get_triage(self, user_id: str) -> Optional[TriageDecision]:
        return self.triage_decisions.get(user_id)

    def get_schedule(self, user_id: str) -> Optional[ReassessmentSchedule]:
        return self.schedules.get(user_id)

    def get_test_result(self, result_id: str) -> Optional[TestResult]:
        return self.test_results.get(result_id)

    def list_user_test_results(self, user_id: str) -> List[TestResult]:
        result_ids = self.user_test_results.get(user_id, [])
        return [self.test_results[result_id] for result_id in result_ids if result_id in self.test_results]
