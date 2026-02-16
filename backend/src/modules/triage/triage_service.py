from typing import Optional

from modules.assessment.models import AssessmentScoreSet
from modules.triage.models import DialogueRiskSignal, RiskLevel, TriageChannel, TriageDecision


class TriageService:
    def evaluate(self, scores: AssessmentScoreSet, dialogue_risk: Optional[DialogueRiskSignal] = None) -> TriageDecision:
        # Constitution rule: dialogue risk takes priority over scale outcomes.
        if dialogue_risk is not None:
            if dialogue_risk.level in (RiskLevel.HIGH, RiskLevel.EXTREME):
                return TriageDecision(
                    channel=TriageChannel.RED,
                    reasons=["dialogue-high-risk"],
                    halt_coaching=True,
                    show_hotline=True,
                    dialogue_risk_level=dialogue_risk.level,
                )
            if dialogue_risk.level == RiskLevel.MEDIUM:
                return TriageDecision(
                    channel=TriageChannel.YELLOW,
                    reasons=["dialogue-medium-risk"],
                    halt_coaching=False,
                    show_hotline=True,
                    dialogue_risk_level=dialogue_risk.level,
                )

        if scores.cssrs_positive:
            return TriageDecision(
                channel=TriageChannel.RED,
                reasons=["cssrs-positive"],
                halt_coaching=True,
                show_hotline=True,
            )

        if scores.phq9_score >= 20:
            return TriageDecision(
                channel=TriageChannel.RED,
                reasons=["phq9-severe"],
                halt_coaching=True,
                show_hotline=True,
            )

        if scores.phq9_score >= 10 or scores.gad7_score >= 10:
            return TriageDecision(
                channel=TriageChannel.YELLOW,
                reasons=["scale-moderate"],
                halt_coaching=False,
                show_hotline=False,
            )

        if scores.scl90_moderate_or_above:
            return TriageDecision(
                channel=TriageChannel.YELLOW,
                reasons=["scl90-elevated"],
                halt_coaching=False,
                show_hotline=False,
            )

        return TriageDecision(
            channel=TriageChannel.GREEN,
            reasons=["scale-low-risk"],
            halt_coaching=False,
            show_hotline=False,
        )
