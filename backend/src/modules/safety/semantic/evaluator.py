import time

from modules.safety.models import SafetyDetectionResult
from modules.triage.models import RiskLevel


EXTREME_PATTERNS = [
    "tonight",
    "right now",
    "already prepared",
    "have a plan",
]

HIGH_PATTERNS = [
    "i want to die",
    "i will kill myself",
    "i want to hurt myself",
    "i want to hurt others",
]

MEDIUM_PATTERNS = [
    "nothing matters",
    "can't handle this",
    "i am breaking down",
]


class SemanticRiskEvaluator:
    def evaluate(self, text: str) -> SafetyDetectionResult:
        start = time.perf_counter()
        normalized = text.lower()

        # A simple heuristic evaluator used in prototype mode.
        if any(signal in normalized for signal in HIGH_PATTERNS) and any(
            marker in normalized for marker in EXTREME_PATTERNS
        ):
            latency = (time.perf_counter() - start) * 1000
            return SafetyDetectionResult(
                level=RiskLevel.EXTREME,
                source="semantic",
                reasons=["high-intent-with-immediacy"],
                semantic_latency_ms=latency,
            )

        if any(signal in normalized for signal in HIGH_PATTERNS):
            latency = (time.perf_counter() - start) * 1000
            return SafetyDetectionResult(
                level=RiskLevel.HIGH,
                source="semantic",
                reasons=["high-intent"],
                semantic_latency_ms=latency,
            )

        if any(signal in normalized for signal in MEDIUM_PATTERNS):
            latency = (time.perf_counter() - start) * 1000
            return SafetyDetectionResult(
                level=RiskLevel.MEDIUM,
                source="semantic",
                reasons=["moderate-distress"],
                semantic_latency_ms=latency,
            )

        latency = (time.perf_counter() - start) * 1000
        return SafetyDetectionResult(
            level=RiskLevel.LOW,
            source="semantic",
            reasons=["low-distress"],
            semantic_latency_ms=latency,
        )
