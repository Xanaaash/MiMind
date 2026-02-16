import uuid

from modules.billing.catalog.service import BillingCatalogService
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import TriageChannel


class CheckoutService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._catalog = BillingCatalogService()

    def create_checkout(self, user_id: str, plan_id: str) -> dict:
        if self._store.get_user(user_id) is None:
            raise ValueError("Unknown user_id")

        plan = self._catalog.get_plan(plan_id)
        triage = self._store.get_triage(user_id)
        if plan_id == "coach":
            if triage is None or triage.channel != TriageChannel.GREEN:
                raise ValueError("Coach plan is only available for green channel users")

        return {
            "order_id": str(uuid.uuid4()),
            "user_id": user_id,
            "plan_id": plan.plan_id,
            "status": "pending_payment",
        }
