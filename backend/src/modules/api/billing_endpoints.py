from typing import Any, Dict, Optional, Tuple

from modules.billing.service import BillingService
from modules.entitlement.service import EntitlementService
from modules.storage.in_memory import InMemoryStore


class BillingAPI:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self._store = store or InMemoryStore()
        self._billing = BillingService(self._store)
        self._entitlement = EntitlementService()

    @property
    def store(self) -> InMemoryStore:
        return self._store

    def get_plans(self) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._billing.list_plans()}

    def post_start_trial(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._billing.start_trial(user_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_checkout(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            plan_id = str(payload.get("plan_id", "")).strip()
            if not plan_id:
                raise ValueError("plan_id is required")
            data = self._billing.create_checkout(user_id=user_id, plan_id=plan_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_webhook(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            event_id = str(payload.get("event_id", "")).strip()
            event_type = str(payload.get("event_type", "")).strip()
            event_payload = payload.get("payload", {})
            if not isinstance(event_payload, dict):
                raise ValueError("payload must be an object")
            data = self._billing.process_webhook(event_id=event_id, event_type=event_type, payload=event_payload)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_consume_coach_session(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._billing.consume_coach_session(user_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_run_maintenance(self) -> Tuple[int, Dict[str, Any]]:
        data = self._billing.run_maintenance()
        return 200, {"data": data}

    def get_subscription(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        subscription = self._billing.get_subscription(user_id)
        if subscription is None:
            return 404, {"error": "Subscription not found"}
        return 200, {"data": subscription}

    def get_entitlements(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        triage = self._store.get_triage(user_id)
        if triage is None:
            return 404, {"error": "Triage result not found"}

        subscription = self._billing.get_subscription(user_id)
        if subscription is None:
            plan_id = "free"
            ai_quota_remaining = 0
        else:
            plan_id = str(subscription["plan_id"])
            ai_quota_remaining = int(subscription["ai_quota_remaining"])

        data = self._entitlement.build_from_state(
            triage_decision=triage,
            plan_id=plan_id,
            ai_quota_remaining=ai_quota_remaining,
        )
        return 200, {"data": data}
