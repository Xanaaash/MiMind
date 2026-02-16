from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from modules.assessment.models import AssessmentScoreSet, AssessmentSubmission, ReassessmentSchedule
from modules.billing.models import SubscriptionRecord
from modules.coach.models import CoachSession
from modules.compliance.models import ConsentRecord
from modules.journal.models import JournalEntry
from modules.memory.models import MemoryVectorRecord
from modules.observability.models import ModelInvocationRecord
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
    coach_sessions: Dict[str, CoachSession] = field(default_factory=dict)
    user_coach_sessions: Dict[str, List[str]] = field(default_factory=dict)
    memory_summaries: Dict[str, List[str]] = field(default_factory=dict)
    memory_vectors: Dict[str, List[MemoryVectorRecord]] = field(default_factory=dict)
    journal_entries: Dict[str, List[JournalEntry]] = field(default_factory=dict)
    tool_events: Dict[str, List[dict]] = field(default_factory=dict)
    model_invocations: List[ModelInvocationRecord] = field(default_factory=list)
    subscriptions: Dict[str, SubscriptionRecord] = field(default_factory=dict)
    processed_webhooks: set = field(default_factory=set)

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

    def save_coach_session(self, session: CoachSession) -> None:
        self.coach_sessions[session.session_id] = session
        self.user_coach_sessions.setdefault(session.user_id, []).append(session.session_id)

    def save_memory_summary(self, user_id: str, summary: str) -> None:
        self.memory_summaries.setdefault(user_id, []).append(summary)

    def save_memory_vector(self, record: MemoryVectorRecord) -> None:
        self.memory_vectors.setdefault(record.user_id, []).append(record)

    def save_journal_entry(self, entry: JournalEntry) -> None:
        self.journal_entries.setdefault(entry.user_id, []).append(entry)

    def save_tool_event(self, user_id: str, event: dict) -> None:
        self.tool_events.setdefault(user_id, []).append(event)

    def save_model_invocation(self, record: ModelInvocationRecord) -> None:
        self.model_invocations.append(record)

    def save_subscription(self, subscription: SubscriptionRecord) -> None:
        self.subscriptions[subscription.user_id] = subscription

    def mark_webhook_processed(self, event_id: str) -> None:
        self.processed_webhooks.add(event_id)

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

    def get_coach_session(self, session_id: str) -> Optional[CoachSession]:
        return self.coach_sessions.get(session_id)

    def list_memory_summaries(self, user_id: str) -> List[str]:
        return list(self.memory_summaries.get(user_id, []))

    def list_memory_vectors(self, user_id: str) -> List[MemoryVectorRecord]:
        return list(self.memory_vectors.get(user_id, []))

    def list_journal_entries(self, user_id: str) -> List[JournalEntry]:
        return list(self.journal_entries.get(user_id, []))

    def get_subscription(self, user_id: str) -> Optional[SubscriptionRecord]:
        return self.subscriptions.get(user_id)

    def list_model_invocations(self) -> List[ModelInvocationRecord]:
        return list(self.model_invocations)

    def is_webhook_processed(self, event_id: str) -> bool:
        return event_id in self.processed_webhooks
