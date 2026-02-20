import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

from modules.coach.access_guard import CoachAccessGuard
from modules.coach.models import CoachSession, CoachTurn
from modules.coach.summary_service import CoachSummaryService
from modules.memory.service import MemoryService
from modules.model_gateway.models import ModelTaskType
from modules.model_gateway.service import ModelGatewayService
from modules.prompt.context.builder import build_context_prompt
from modules.prompt.registry.runtime import get_prompt_registry
from modules.prompt.styles.registry import get_style_prompt
from modules.prompt.system.prompt import get_system_prompt
from modules.safety.service import SafetyRuntimeService
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import DialogueRiskSignal, RiskLevel
from modules.triage.triage_service import TriageService


class CoachSessionService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._access_guard = CoachAccessGuard(store)
        self._triage_service = TriageService()
        self._safety_runtime = SafetyRuntimeService(store)
        self._summary_service = CoachSummaryService()
        self._memory_service = MemoryService(store)
        self._model_gateway = ModelGatewayService(audit_store=store)

    def start_session(self, user_id: str, style_id: str, subscription_active: bool) -> dict:
        self._access_guard.ensure_session_access(user_id=user_id, subscription_active=subscription_active)

        subscription = self._store.get_subscription(user_id)
        if subscription is not None and subscription.plan_id == "coach":
            subscription.ai_used_in_cycle += 1

        style = get_style_prompt(style_id)
        context = build_context_prompt(self._store, user_id)
        prompt_pack_version = get_prompt_registry().get_active_version()

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
            "prompt_pack_version": prompt_pack_version,
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

        user = self._store.get_user(session.user_id)
        locale = user.locale if user else "en-US"
        safety = self._safety_runtime.assess_and_respond(
            user_id=session.user_id,
            locale=locale,
            text=user_message,
            override_signal=dialogue_risk,
            legal_policy_enabled=False,
        )

        level_map = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
            "extreme": RiskLevel.EXTREME,
        }
        detected_level = level_map.get(safety["detection"]["level"], RiskLevel.HIGH)
        effective_signal = DialogueRiskSignal(
            level=detected_level,
            text=user_message,
            is_joke=dialogue_risk.is_joke if dialogue_risk is not None else False,
        )
        triage = self._triage_service.evaluate(scores=scores, dialogue_risk=effective_signal)

        action = safety["action"]
        if action["stop_coaching"]:
            hotline = safety.get("hotline")
            hotline_text = f" {hotline['text']}" if hotline else ""
            crisis_text = f"{action['message']}{hotline_text}"
            session.turns.append(CoachTurn(role="coach", message=crisis_text))
            session.halted_for_safety = True
            session.active = False
            return {
                "mode": "crisis",
                "halted": True,
                "triage": triage.to_dict(),
                "coach_message": crisis_text,
                "safety": safety,
            }

        if action["pause_topic"]:
            safe_text = action["message"]
            session.turns.append(CoachTurn(role="coach", message=safe_text))
            return {
                "mode": "safety_pause",
                "halted": False,
                "triage": triage.to_dict(),
                "coach_message": safe_text,
                "safety": safety,
            }

        reply, model_info = self._generate_coach_reply(session=session, user_message=user_message)
        session.turns.append(CoachTurn(role="coach", message=reply))
        return {
            "mode": "coaching",
            "halted": False,
            "triage": triage.to_dict(),
            "coach_message": reply,
            "safety": safety,
            "model": model_info,
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

    def list_session_history(self, user_id: str, limit: int = 20) -> dict:
        if self._store.get_user(user_id) is None:
            raise ValueError("Unknown user_id")
        if limit <= 0:
            raise ValueError("limit must be greater than 0")

        sessions = sorted(
            self._store.list_user_coach_sessions(user_id),
            key=lambda session: session.started_at,
            reverse=True,
        )
        items = [self._serialize_session_history_item(session) for session in sessions[:limit]]
        return {
            "items": items,
            "count": len(items),
        }

    def get_session_summary(self, user_id: str, session_id: str) -> dict:
        if self._store.get_user(user_id) is None:
            raise ValueError("Unknown user_id")

        session = self._store.get_coach_session(session_id)
        if session is None or session.user_id != user_id:
            raise ValueError("Session not found")

        return self._serialize_session_history_item(session)

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

    def _generate_coach_reply(self, session: CoachSession, user_message: str) -> Tuple[str, dict]:
        user = self._store.get_user(session.user_id)
        locale = user.locale if user else "en-US"

        style_prompt = get_style_prompt(session.style_id)
        context_prompt = build_context_prompt(self._store, session.user_id)
        retrieval_error = None
        relevant_memories = []
        try:
            relevant_memories = self._memory_service.retrieve_relevant(
                user_id=session.user_id,
                query=user_message,
                limit=3,
            )
        except Exception as error:
            retrieval_error = str(error)

        if relevant_memories:
            context_prompt["relevant_memory_summaries"] = list(relevant_memories)

        try:
            response = self._model_gateway.run(
                task_type=ModelTaskType.COACH_GENERATION,
                text=user_message,
                locale=locale,
                timeout_ms=4000,
                metadata={
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "style_id": session.style_id,
                    "system_prompt": get_system_prompt(),
                    "style_prompt": style_prompt,
                    "context_prompt": context_prompt,
                    "relevant_memories": list(relevant_memories),
                },
            )
            if not response.output_text or not response.output_text.strip():
                raise ValueError("Gateway returned empty coach output_text")

            model_info = {
                "provider": response.provider,
                "trace_id": response.trace_id,
                "task_type": response.task_type,
                "latency_ms": round(response.latency_ms, 3),
                "relevant_memory_count": len(relevant_memories),
            }
            if retrieval_error:
                model_info["memory_retrieval_error"] = retrieval_error

            return response.output_text.strip(), model_info
        except Exception as error:
            fallback = self._fallback_coach_reply(style_id=session.style_id, user_message=user_message)
            model_info = {
                "provider": "fallback-local-template",
                "trace_id": None,
                "task_type": ModelTaskType.COACH_GENERATION,
                "latency_ms": 0.0,
                "error": str(error),
                "relevant_memory_count": len(relevant_memories),
            }
            if retrieval_error:
                model_info["memory_retrieval_error"] = retrieval_error

            return fallback, model_info

    @staticmethod
    def _fallback_coach_reply(style_id: str, user_message: str) -> str:
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

        if style_id == "deep_exploration":
            return (
                "Let's slow down and look beneath the surface. "
                "What familiar emotional pattern does this situation remind you of?"
            )

        if style_id == "mindfulness_guide":
            return (
                "Let's take one gentle pause together. "
                "What sensations do you notice in your body right now, without judging them?"
            )

        if style_id == "action_coach":
            return (
                "Let's turn this into one concrete step. "
                "What is the smallest action you can complete in the next 10 minutes?"
            )

        return f"Let's keep exploring: {user_message[:120]}"

    def _serialize_session_history_item(self, session: CoachSession) -> dict:
        return {
            "session": session.to_dict(),
            "summary": self._summary_service.build_summary(session),
            "last_user_message": self._last_turn_message(session, "user"),
            "last_coach_message": self._last_turn_message(session, "coach"),
        }

    @staticmethod
    def _last_turn_message(session: CoachSession, role: str) -> Optional[str]:
        for turn in reversed(session.turns):
            if turn.role == role:
                return turn.message
        return None
