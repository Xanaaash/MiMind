from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class TriageChannel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class RiskLevel(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    EXTREME = 4


@dataclass
class DialogueRiskSignal:
    level: RiskLevel
    text: str
    is_joke: bool = False


@dataclass
class TriageDecision:
    channel: TriageChannel
    reasons: List[str] = field(default_factory=list)
    halt_coaching: bool = False
    show_hotline: bool = False
    dialogue_risk_level: Optional[RiskLevel] = None

    def to_dict(self) -> dict:
        return {
            "channel": self.channel.value,
            "reasons": list(self.reasons),
            "halt_coaching": self.halt_coaching,
            "show_hotline": self.show_hotline,
            "dialogue_risk_level": self.dialogue_risk_level.name.lower()
            if self.dialogue_risk_level is not None
            else None,
        }
