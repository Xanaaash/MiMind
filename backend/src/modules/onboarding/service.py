import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from modules.assessment.models import AssessmentSubmission
from modules.assessment.schedule_service import build_reassessment_schedule
from modules.assessment.scoring_service import score_submission
from modules.auth.service import AuthService
from modules.compliance.service import ComplianceService
from modules.entitlement.service import EntitlementService
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import DialogueRiskSignal, RiskLevel
from modules.triage.triage_service import TriageService


class OnboardingService:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self.store = store or InMemoryStore()
        self.auth_service = AuthService(self.store)
        self.compliance_service = ComplianceService(self.store)
        self.triage_service = TriageService()
        self.entitlement_service = EntitlementService()

    def register(self, email: str, locale: str, policy_version: str) -> dict:
        user = self.auth_service.register_user(email=email, locale=locale)
        consent = self.compliance_service.capture_consent(user_id=user.user_id, policy_version=policy_version)

        return {
            "user_id": user.user_id,
            "email": user.email,
            "locale": user.locale,
            "consent_id": consent.consent_id,
            "policy_version": consent.policy_version,
            "created_at": user.created_at.isoformat(),
        }

    def submit_assessment(
        self,
        user_id: str,
        responses: Dict[str, Any],
        dialogue_risk: Optional[DialogueRiskSignal] = None,
    ) -> dict:
        if self.store.get_user(user_id) is None:
            raise ValueError("Unknown user_id")

        scores = score_submission(responses)

        submission = AssessmentSubmission(
            submission_id=str(uuid.uuid4()),
            user_id=user_id,
            responses=responses,
            submitted_at=datetime.now(timezone.utc),
        )
        self.store.add_submission(submission)
        self.store.save_scores(user_id, scores)

        triage = self.triage_service.evaluate(scores, dialogue_risk=dialogue_risk)
        self.store.save_triage(user_id, triage)

        schedule = build_reassessment_schedule(start_date=submission.submitted_at.date())
        self.store.save_schedule(user_id, schedule)

        return {
            "submission_id": submission.submission_id,
            "scores": scores.to_dict(),
            "triage": triage.to_dict(),
            "reassessment_due": schedule.to_dict(),
        }

    def get_entitlements(self, user_id: str) -> dict:
        triage = self.store.get_triage(user_id)
        if triage is None:
            raise ValueError("Triage result not found for user")
        return self.entitlement_service.build_from_triage(triage)

    @staticmethod
    def parse_dialogue_risk(payload: Optional[dict]) -> Optional[DialogueRiskSignal]:
        if payload is None:
            return None

        level_raw = str(payload.get("level", "")).strip().lower()
        mapping = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "extreme": RiskLevel.EXTREME,
        }
        if level_raw not in mapping:
            raise ValueError("Invalid dialogue risk level")

        return DialogueRiskSignal(
            level=mapping[level_raw],
            text=str(payload.get("text", "")),
            is_joke=bool(payload.get("is_joke", False)),
        )
