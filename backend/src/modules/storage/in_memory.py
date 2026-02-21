from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from modules.admin.models import AdminSession
from modules.assessment.models import AssessmentScoreSet, AssessmentSubmission, ReassessmentSchedule
from modules.billing.models import RenewalReminderRecord, SubscriptionRecord
from modules.coach.models import CoachSession
from modules.compliance.models import ConsentRecord
from modules.journal.models import JournalEntry
from modules.memory.models import MemoryVectorRecord
from modules.observability.models import APIAuditLogRecord, ModelInvocationRecord
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
    api_audit_logs: List[APIAuditLogRecord] = field(default_factory=list)
    subscriptions: Dict[str, SubscriptionRecord] = field(default_factory=dict)
    renewal_reminders: Dict[str, List[RenewalReminderRecord]] = field(default_factory=dict)
    processed_webhooks: set = field(default_factory=set)
    admin_sessions: Dict[str, AdminSession] = field(default_factory=dict)

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
        session_ids = self.user_coach_sessions.setdefault(session.user_id, [])
        if session.session_id not in session_ids:
            session_ids.append(session.session_id)

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

    def save_api_audit_log(self, record: APIAuditLogRecord) -> None:
        self.api_audit_logs.append(record)

    def save_subscription(self, subscription: SubscriptionRecord) -> None:
        self.subscriptions[subscription.user_id] = subscription

    def save_renewal_reminder(self, reminder: RenewalReminderRecord) -> None:
        self.renewal_reminders.setdefault(reminder.user_id, []).append(reminder)

    def save_admin_session(self, session: AdminSession) -> None:
        self.admin_sessions[session.session_id] = session

    def mark_webhook_processed(self, event_id: str) -> None:
        self.processed_webhooks.add(event_id)

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def list_users(self, limit: int = 100) -> List[User]:
        safe_limit = max(1, min(int(limit), 500))
        items = sorted(self.users.values(), key=lambda item: item.created_at, reverse=True)
        return items[:safe_limit]

    def get_user_by_email(self, email: str) -> Optional[User]:
        normalized = str(email).strip().lower()
        if not normalized:
            return None
        for user in self.users.values():
            if user.email.lower() == normalized:
                return user
        return None

    def get_user_by_email_verification_token(self, token: str) -> Optional[User]:
        normalized = str(token).strip()
        if not normalized:
            return None
        for user in self.users.values():
            if user.email_verification_token == normalized:
                return user
        return None

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

    def list_submissions(self, user_id: str) -> List[AssessmentSubmission]:
        return list(self.submissions.get(user_id, []))

    def list_user_consents(self, user_id: str) -> List[ConsentRecord]:
        return [consent for consent in self.consents.values() if consent.user_id == user_id]

    def get_coach_session(self, session_id: str) -> Optional[CoachSession]:
        return self.coach_sessions.get(session_id)

    def list_user_coach_sessions(self, user_id: str) -> List[CoachSession]:
        session_ids = self.user_coach_sessions.get(user_id, [])
        return [self.coach_sessions[session_id] for session_id in session_ids if session_id in self.coach_sessions]

    def list_memory_summaries(self, user_id: str) -> List[str]:
        return list(self.memory_summaries.get(user_id, []))

    def list_memory_vectors(self, user_id: str) -> List[MemoryVectorRecord]:
        return list(self.memory_vectors.get(user_id, []))

    def list_journal_entries(self, user_id: str) -> List[JournalEntry]:
        return list(self.journal_entries.get(user_id, []))

    def list_tool_events(self, user_id: str) -> List[dict]:
        return list(self.tool_events.get(user_id, []))

    def get_subscription(self, user_id: str) -> Optional[SubscriptionRecord]:
        return self.subscriptions.get(user_id)

    def list_renewal_reminders(self, user_id: str) -> List[RenewalReminderRecord]:
        return list(self.renewal_reminders.get(user_id, []))

    def get_admin_session(self, session_id: str) -> Optional[AdminSession]:
        return self.admin_sessions.get(session_id)

    def revoke_admin_session(self, session_id: str) -> None:
        session = self.admin_sessions.get(session_id)
        if session is not None:
            session.revoked = True

    def list_model_invocations(self) -> List[ModelInvocationRecord]:
        return list(self.model_invocations)

    def list_api_audit_logs(self) -> List[APIAuditLogRecord]:
        return list(self.api_audit_logs)

    def is_webhook_processed(self, event_id: str) -> bool:
        return event_id in self.processed_webhooks

    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        user = self.get_user(user_id)
        if user is None:
            raise ValueError("Unknown user_id")

        scores = self.get_scores(user_id)
        triage = self.get_triage(user_id)
        schedule = self.get_schedule(user_id)
        subscription = self.get_subscription(user_id)

        return {
            "user": {
                "user_id": user.user_id,
                "email": user.email,
                "locale": user.locale,
                "created_at": user.created_at.isoformat(),
            },
            "consents": [
                {
                    "consent_id": consent.consent_id,
                    "policy_version": consent.policy_version,
                    "accepted_at": consent.accepted_at.isoformat(),
                }
                for consent in self.list_user_consents(user_id)
            ],
            "assessment": {
                "submissions": [
                    {
                        "submission_id": submission.submission_id,
                        "responses": dict(submission.responses),
                        "submitted_at": submission.submitted_at.isoformat(),
                    }
                    for submission in self.list_submissions(user_id)
                ],
                "scores": scores.to_dict() if scores is not None else None,
                "triage": triage.to_dict() if triage is not None else None,
                "reassessment_due": schedule.to_dict() if schedule is not None else None,
            },
            "tests": {
                "results": [result.to_dict() for result in self.list_user_test_results(user_id)],
            },
            "coach": {
                "sessions": [session.to_dict() for session in self.list_user_coach_sessions(user_id)],
            },
            "tools": {
                "journal_entries": [entry.to_dict() for entry in self.list_journal_entries(user_id)],
                "tool_events": self.list_tool_events(user_id),
            },
            "memory": {
                "summaries": self.list_memory_summaries(user_id),
                "vectors": [
                    {
                        "memory_id": vector.memory_id,
                        "text_preview": vector.text[:80],
                        "embedding_dimensions": len(vector.embedding),
                        "created_at": vector.created_at.isoformat(),
                    }
                    for vector in self.list_memory_vectors(user_id)
                ],
            },
            "billing": {
                "subscription": {
                    "plan_id": subscription.plan_id,
                    "status": subscription.status,
                    "started_at": subscription.started_at.isoformat(),
                    "ends_at": subscription.ends_at.isoformat() if subscription.ends_at else None,
                    "trial": subscription.trial,
                    "ai_quota_monthly": subscription.ai_quota_monthly,
                    "ai_used_in_cycle": subscription.ai_used_in_cycle,
                    "cycle_reset_at": subscription.cycle_reset_at.isoformat(),
                }
                if subscription is not None
                else None,
                "renewal_reminders": [
                    {
                        "reminder_id": item.reminder_id,
                        "plan_id": item.plan_id,
                        "due_at": item.due_at.isoformat(),
                        "reminder_at": item.reminder_at.isoformat(),
                        "days_remaining": item.days_remaining,
                    }
                    for item in self.list_renewal_reminders(user_id)
                ],
            },
        }

    def erase_user_data(self, user_id: str) -> Dict[str, int]:
        removed_consents = 0
        consent_ids_to_remove = [consent_id for consent_id, consent in self.consents.items() if consent.user_id == user_id]
        for consent_id in consent_ids_to_remove:
            self.consents.pop(consent_id, None)
            removed_consents += 1

        removed_submissions = len(self.submissions.pop(user_id, []))

        removed_scores = 1 if self.scores.pop(user_id, None) is not None else 0
        removed_triage = 1 if self.triage_decisions.pop(user_id, None) is not None else 0
        removed_schedule = 1 if self.schedules.pop(user_id, None) is not None else 0

        removed_test_results = 0
        for result_id in self.user_test_results.pop(user_id, []):
            if self.test_results.pop(result_id, None) is not None:
                removed_test_results += 1

        removed_coach_sessions = 0
        for session_id in self.user_coach_sessions.pop(user_id, []):
            if self.coach_sessions.pop(session_id, None) is not None:
                removed_coach_sessions += 1

        removed_journal_entries = len(self.journal_entries.pop(user_id, []))
        removed_tool_events = len(self.tool_events.pop(user_id, []))
        removed_memory_summaries = len(self.memory_summaries.pop(user_id, []))
        removed_memory_vectors = len(self.memory_vectors.pop(user_id, []))
        removed_api_audit_logs = 0
        retained_api_logs: List[APIAuditLogRecord] = []
        for record in self.api_audit_logs:
            if record.user_id == user_id:
                removed_api_audit_logs += 1
            else:
                retained_api_logs.append(record)
        self.api_audit_logs = retained_api_logs
        removed_subscription = 1 if self.subscriptions.pop(user_id, None) is not None else 0
        removed_renewal_reminders = len(self.renewal_reminders.pop(user_id, []))
        removed_user = 1 if self.users.pop(user_id, None) is not None else 0

        return {
            "user": removed_user,
            "consents": removed_consents,
            "assessment_submissions": removed_submissions,
            "assessment_scores": removed_scores,
            "triage_decisions": removed_triage,
            "reassessment_schedules": removed_schedule,
            "test_results": removed_test_results,
            "coach_sessions": removed_coach_sessions,
            "journal_entries": removed_journal_entries,
            "tool_events": removed_tool_events,
            "memory_summaries": removed_memory_summaries,
            "memory_vectors": removed_memory_vectors,
            "api_audit_logs": removed_api_audit_logs,
            "subscriptions": removed_subscription,
            "renewal_reminders": removed_renewal_reminders,
        }
