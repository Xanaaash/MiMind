from modules.triage.models import TriageChannel, TriageDecision


class EntitlementService:
    def build_from_triage(self, triage_decision: TriageDecision) -> dict:
        ai_enabled = triage_decision.channel == TriageChannel.GREEN
        return {
            "channel": triage_decision.channel.value,
            "ai_coaching_enabled": ai_enabled,
            "assessment_reports_enabled": True,
            "healing_tools_enabled": True,
            "suggest_medical_follow_up": triage_decision.channel != TriageChannel.GREEN,
        }
