from modules.billing.catalog.service import BillingCatalogService
from modules.triage.models import TriageChannel, TriageDecision


class EntitlementService:
    def __init__(self) -> None:
        self._catalog = BillingCatalogService()

    def build_from_triage(self, triage_decision: TriageDecision) -> dict:
        # Backward-compatible default behavior before billing activation.
        return self.build_from_state(
            triage_decision=triage_decision,
            plan_id="base",
            ai_quota_remaining=0,
        )

    def build_from_state(self, triage_decision: TriageDecision, plan_id: str, ai_quota_remaining: int) -> dict:
        try:
            plan = self._catalog.get_plan(plan_id)
        except ValueError:
            plan = self._catalog.get_plan("free")

        ai_enabled = triage_decision.channel == TriageChannel.GREEN
        if plan.plan_id != "coach":
            ai_enabled = False
        if ai_quota_remaining <= 0:
            ai_enabled = False

        return {
            "channel": triage_decision.channel.value,
            "ai_coaching_enabled": ai_enabled,
            "assessment_reports_enabled": plan.reports_enabled,
            "healing_tools_enabled": plan.tools_enabled,
            "plan_id": plan.plan_id,
            "ai_quota_remaining": max(ai_quota_remaining, 0),
            "suggest_medical_follow_up": triage_decision.channel != TriageChannel.GREEN,
        }
