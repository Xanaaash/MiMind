from modules.triage.models import RiskLevel


class EmergencyService:
    def should_notify_emergency_contact(self, level: RiskLevel, legal_policy_enabled: bool) -> bool:
        if not legal_policy_enabled:
            return False
        return level == RiskLevel.EXTREME
