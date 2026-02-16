from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from uuid import uuid4

from modules.triage.models import RiskLevel


class ModelTaskType:
    SAFETY_NLU_FAST = "safety_nlu_fast"
    SAFETY_SEMANTIC_JUDGE = "safety_semantic_judge"


@dataclass
class ModelGatewayRequest:
    task_type: str
    text: str
    locale: str = "en-US"
    timeout_ms: int = 2000
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelGatewayResponse:
    task_type: str
    provider: str
    risk_level: Optional[RiskLevel]
    reasons: List[str]
    latency_ms: float
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task_type": self.task_type,
            "provider": self.provider,
            "risk_level": self.risk_level.name.lower() if self.risk_level else None,
            "reasons": list(self.reasons),
            "latency_ms": round(self.latency_ms, 3),
            "trace_id": self.trace_id,
            "raw": dict(self.raw),
        }
