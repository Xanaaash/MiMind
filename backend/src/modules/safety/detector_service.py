from typing import Optional

from modules.model_gateway.models import ModelTaskType
from modules.model_gateway.service import ModelGatewayService
from modules.safety.models import SafetyDetectionResult
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import DialogueRiskSignal, RiskLevel


class SafetyDetectorService:
    def __init__(self, gateway: Optional[ModelGatewayService] = None, store: Optional[InMemoryStore] = None) -> None:
        self._gateway = gateway or ModelGatewayService(audit_store=store)

    def detect(self, text: str, override_signal: Optional[DialogueRiskSignal] = None) -> SafetyDetectionResult:
        try:
            nlu_result = self._gateway.run(
                task_type=ModelTaskType.SAFETY_NLU_FAST,
                text=text,
                timeout_ms=100,
                metadata={"component": "safety_detector"},
            )
            nlu_level = nlu_result.risk_level or RiskLevel.LOW

            if nlu_level in (RiskLevel.HIGH, RiskLevel.EXTREME):
                level = nlu_level
                reasons = list(nlu_result.reasons)
                semantic_latency_ms = 0.0
                source = "nlu-short-circuit"
            else:
                semantic_result = self._gateway.run(
                    task_type=ModelTaskType.SAFETY_SEMANTIC_JUDGE,
                    text=text,
                    timeout_ms=2000,
                    metadata={"component": "safety_detector"},
                )
                semantic_level = semantic_result.risk_level or RiskLevel.LOW

                level = max(nlu_level, semantic_level)
                reasons = list(nlu_result.reasons) + list(semantic_result.reasons)
                semantic_latency_ms = semantic_result.latency_ms
                source = "nlu+semantic"

            if override_signal is not None and override_signal.level > level:
                level = override_signal.level
                reasons.append("override-signal")

            # Constitution rule: do not trust "just joking" to suppress safety response.
            if override_signal is not None and override_signal.is_joke and override_signal.level >= RiskLevel.HIGH:
                level = override_signal.level
                reasons.append("joke-disclaimer-ignored")

            return SafetyDetectionResult(
                level=level,
                source=source,
                reasons=reasons,
                nlu_latency_ms=nlu_result.latency_ms,
                semantic_latency_ms=semantic_latency_ms,
            )
        except Exception as error:
            return SafetyDetectionResult(
                level=RiskLevel.HIGH,
                source="fail-closed",
                reasons=[f"detector-error:{error}"],
                fail_closed=True,
            )
