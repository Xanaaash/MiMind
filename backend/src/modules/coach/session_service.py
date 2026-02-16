import uuid
from datetime import datetime, timezone
from typing import Optional

from modules.coach.access_guard import CoachAccessGuard
from modules.coach.models import CoachSession, CoachTurn
from modules.coach.summary_service import CoachSummaryService
from modules.memory.service import MemoryService
from modules.prompt.context.builder import build_context_prompt
from modules.prompt.styles.registry import get_style_prompt
from modules.prompt.system.prompt import get_system_prompt
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import DialogueRiskSignal, RiskLevel
from modules.triage.triage_service import TriageService


class CoachSessionService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._access_guard = CoachAccessGuard(store)
        self._triage_service = TriageService()
        self._summary_service = CoachSummaryService()
        self._memory_service = MemoryService(store)

    def start_session(self, user_id: str, style_id: str, subscription_active: bool) -> dict:
        self._access_guard.ensure_session_access(user_id=user_id, subscription_active=subscription_active)

        subscription = self._store.get_subscription(user_id)
        if subscription is not None and subscription.plan_id == "coach":
            subscription.ai_used_in_cycle += 1

        style = get_style_prompt(style_id)
        context = build_context_prompt(self._store, user_id)

        session = CoachSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            style_id=style_id,
        )
        self._store.save_coach_session(session)

        return {
            "session": session.to_dict(),
            "prompt_stack": {
                "system": get_system_prompt(),
                "style": style,
                "context": context,
            },
        }

    def chat(self, session_id: str, user_message: str, dialogue_risk: Optional[DialogueRiskSignal]) -> dict:
        session = self._store.get_coach_session(session_id)
        if session is None:
            raise ValueError("Session not found")
        if not session.active:
            raise ValueError("Session is not active")

        user_message = str(user_message).strip()
        if not user_message:
            raise ValueError("user_message is required")

        session.turns.append(CoachTurn(role="user", message=user_message))

        scores = self._store.get_scores(session.user_id)
        if scores is None:
            raise ValueError("Assessment scores required before coaching")

        triage = self._triage_service.evaluate(scores=scores, dialogue_risk=dialogue_risk)
        if triage.dialogue_risk_level in (RiskLevel.HIGH, RiskLevel.EXTREME):
            crisis_text = (
                "I hear that this may be a high-risk moment. I need to pause normal coaching now. "
                "Please contact local crisis support immediately."
            )
            session.turns.append(CoachTurn(role="coach", message=crisis_text))
            session.halted_for_safety = True
            session.active = False
            return {
                "mode": "crisis",
                "halted": True,
                "triage": triage.to_dict(),
                "coach_message": crisis_text,
            }

        if triage.dialogue_risk_level == RiskLevel.MEDIUM:
            safe_text = (
                "I want to slow down and focus on your safety first. "
                "If you can, consider reaching out to a trusted person or local support resource."
            )
            session.turns.append(CoachTurn(role="coach", message=safe_text))
            return {
                "mode": "safety_pause",
                "halted": False,
                "triage": triage.to_dict(),
                "coach_message": safe_text,
            }

        reply = self._generate_coach_reply(style_id=session.style_id, user_message=user_message)
        session.turns.append(CoachTurn(role="coach", message=reply))
        return {
            "mode": "coaching",
            "halted": False,
            "triage": triage.to_dict(),
            "coach_message": reply,
        }

    def end_session(self, session_id: str) -> dict:
        session = self._store.get_coach_session(session_id)
        if session is None:
            raise ValueError("Session not found")

        session.active = False
        session.ended_at = datetime.now(timezone.utc)

        summary = self._summary_service.build_summary(session)
        self._memory_service.index_summary(session.user_id, summary)

        return {
            "session": session.to_dict(),
            "summary": summary,
            "memory_items": self._memory_service.retrieve_recent(session.user_id, limit=3),
        }

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

    @staticmethod
    def _generate_coach_reply(style_id: str, user_message: str) -> str:
        if style_id == "warm_guide":
            return (
                "I hear how important this is for you. "
                "Could you share one moment today that felt most emotionally intense?"
            )

        if style_id == "rational_analysis":
            return (
                "Let's map this situation using CBT. "
                "What thought came first, and what action followed?"
            )

        return f"Let's keep exploring: {user_message[:120]}"
