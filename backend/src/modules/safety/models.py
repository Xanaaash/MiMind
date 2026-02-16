from dataclasses import dataclass, field
from typing import List

from modules.triage.models import RiskLevel


@dataclass
class SafetyDetectionResult:
    level: RiskLevel
    source: str
    reasons: List[str] = field(default_factory=list)
    nlu_latency_ms: float = 0.0
    semantic_latency_ms: float = 0.0
    fail_closed: bool = False

    def to_dict(self) -> dict:
        return {
            "level": self.level.name.lower(),
            "source": self.source,
            "reasons": list(self.reasons),
            "nlu_latency_ms": round(self.nlu_latency_ms, 3),
            "semantic_latency_ms": round(self.semantic_latency_ms, 3),
            "fail_closed": self.fail_closed,
        }


@dataclass
class SafetyResponseAction:
    mode: str
    pause_topic: bool
    stop_coaching: bool
    show_hotline: bool
    notify_ops: bool
    notify_emergency_contact: bool
    suggested_channel: str
    message: str

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "pause_topic": self.pause_topic,
            "stop_coaching": self.stop_coaching,
            "show_hotline": self.show_hotline,
            "notify_ops": self.notify_ops,
            "notify_emergency_contact": self.notify_emergency_contact,
            "suggested_channel": self.suggested_channel,
            "message": self.message,
        }
