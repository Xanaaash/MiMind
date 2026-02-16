from typing import Optional

from modules.safety.detector_service import SafetyDetectorService
from modules.safety.interruption_service import SafetyInterruptionService
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import DialogueRiskSignal


class SafetyRuntimeService:
    def __init__(self, store: InMemoryStore) -> None:
        self._detector = SafetyDetectorService()
        self._interruption = SafetyInterruptionService(store)

    def assess_and_respond(
        self,
        user_id: str,
        locale: str,
        text: str,
        override_signal: Optional[DialogueRiskSignal] = None,
        legal_policy_enabled: bool = False,
    ) -> dict:
        detection = self._detector.detect(text=text, override_signal=override_signal)
        return self._interruption.handle(
            user_id=user_id,
            locale=locale,
            detection=detection,
            legal_policy_enabled=legal_policy_enabled,
        )
