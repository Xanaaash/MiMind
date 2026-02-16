from typing import Dict

from modules.billing.models import BillingPlan


PLAN_CATALOG = {
    "free": BillingPlan(
        plan_id="free",
        display_name="Free",
        reports_enabled=False,
        tools_enabled=False,
        ai_sessions_per_month=0,
    ),
    "base": BillingPlan(
        plan_id="base",
        display_name="Base Subscription",
        reports_enabled=True,
        tools_enabled=True,
        ai_sessions_per_month=0,
    ),
    "coach": BillingPlan(
        plan_id="coach",
        display_name="Coach Subscription",
        reports_enabled=True,
        tools_enabled=True,
        ai_sessions_per_month=8,
    ),
    "trial_base": BillingPlan(
        plan_id="trial_base",
        display_name="Base Trial",
        reports_enabled=True,
        tools_enabled=True,
        ai_sessions_per_month=0,
        trial_days=7,
    ),
}


class BillingCatalogService:
    def list_plans(self) -> Dict[str, BillingPlan]:
        return dict(PLAN_CATALOG)

    def get_plan(self, plan_id: str) -> BillingPlan:
        plan = PLAN_CATALOG.get(plan_id)
        if plan is None:
            raise ValueError(f"Unknown plan_id: {plan_id}")
        return plan
