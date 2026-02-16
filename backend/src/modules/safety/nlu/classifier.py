import time

from modules.safety.models import SafetyDetectionResult
from modules.triage.models import RiskLevel


HIGH_KEYWORDS = [
    "kill myself",
    "suicide",
    "end my life",
    "hurt myself",
    "hurt someone",
    "kill them",
]

MEDIUM_KEYWORDS = [
    "hopeless",
    "can't go on",
    "no reason to live",
    "worthless",
]

LOW_KEYWORDS = [
    "stressed",
    "anxious",
    "sad",
    "tired",
]


class NLUClassifier:
    def classify(self, text: str) -> SafetyDetectionResult:
        start = time.perf_counter()
        normalized = text.lower()

        for keyword in HIGH_KEYWORDS:
            if keyword in normalized:
                latency = (time.perf_counter() - start) * 1000
                return SafetyDetectionResult(
                    level=RiskLevel.HIGH,
                    source="nlu",
                    reasons=[f"high-keyword:{keyword}"],
                    nlu_latency_ms=latency,
                )

        for keyword in MEDIUM_KEYWORDS:
            if keyword in normalized:
                latency = (time.perf_counter() - start) * 1000
                return SafetyDetectionResult(
                    level=RiskLevel.MEDIUM,
                    source="nlu",
                    reasons=[f"medium-keyword:{keyword}"],
                    nlu_latency_ms=latency,
                )

        for keyword in LOW_KEYWORDS:
            if keyword in normalized:
                latency = (time.perf_counter() - start) * 1000
                return SafetyDetectionResult(
                    level=RiskLevel.LOW,
                    source="nlu",
                    reasons=[f"low-keyword:{keyword}"],
                    nlu_latency_ms=latency,
                )

        latency = (time.perf_counter() - start) * 1000
        return SafetyDetectionResult(
            level=RiskLevel.LOW,
            source="nlu",
            reasons=["no-risk-keyword"],
            nlu_latency_ms=latency,
        )
