from typing import Optional

from modules.safety.models import SafetyDetectionResult
from modules.safety.nlu.classifier import NLUClassifier
from modules.safety.semantic.evaluator import SemanticRiskEvaluator
from modules.triage.models import DialogueRiskSignal, RiskLevel


class SafetyDetectorService:
    def __init__(self) -> None:
        self._nlu = NLUClassifier()
        self._semantic = SemanticRiskEvaluator()

    def detect(self, text: str, override_signal: Optional[DialogueRiskSignal] = None) -> SafetyDetectionResult:
        try:
            nlu_result = self._nlu.classify(text)

            if nlu_result.level in (RiskLevel.HIGH, RiskLevel.EXTREME):
                level = nlu_result.level
                reasons = list(nlu_result.reasons)
                semantic_latency_ms = 0.0
                source = "nlu-short-circuit"
            else:
                semantic_result = self._semantic.evaluate(text)
                level = max(nlu_result.level, semantic_result.level)
                reasons = list(nlu_result.reasons) + list(semantic_result.reasons)
                semantic_latency_ms = semantic_result.semantic_latency_ms
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
                nlu_latency_ms=nlu_result.nlu_latency_ms,
                semantic_latency_ms=semantic_latency_ms,
            )
        except Exception as error:
            return SafetyDetectionResult(
                level=RiskLevel.HIGH,
                source="fail-closed",
                reasons=[f"detector-error:{error}"],
                fail_closed=True,
            )
