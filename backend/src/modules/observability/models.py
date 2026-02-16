from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass
class ModelInvocationRecord:
    trace_id: str
    task_type: str
    provider: str
    success: bool
    latency_ms: float
    estimated_cost_usd: float
    input_chars: int
    output_chars: int
    metadata: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "task_type": self.task_type,
            "provider": self.provider,
            "success": self.success,
            "latency_ms": round(self.latency_ms, 3),
            "estimated_cost_usd": round(self.estimated_cost_usd, 8),
            "input_chars": self.input_chars,
            "output_chars": self.output_chars,
            "metadata": dict(self.metadata),
            "error": self.error,
            "created_at": self.created_at.isoformat(),
        }
