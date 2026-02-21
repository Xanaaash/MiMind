import uuid

from modules.billing.catalog.service import BillingCatalogService
from modules.billing.domestic.config import load_domestic_billing_config
from modules.billing.domestic.gateway import DomesticPaymentGateway
from modules.billing.stripe.config import load_stripe_billing_config
from modules.billing.stripe.gateway import StripeGateway
from modules.storage.in_memory import InMemoryStore
from modules.triage.models import TriageChannel


class CheckoutService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._catalog = BillingCatalogService()
        self._stripe_config = load_stripe_billing_config()
        self._domestic_config = load_domestic_billing_config()
        self._stripe_gateway = StripeGateway(self._stripe_config)
        self._domestic_gateway = DomesticPaymentGateway(self._domestic_config)

    def create_checkout(self, user_id: str, plan_id: str, payment_channel: str = "") -> dict:
        user = self._store.get_user(user_id)
        if user is None:
            raise ValueError("Unknown user_id")

        plan = self._catalog.get_plan(plan_id)
        triage = self._store.get_triage(user_id)
        if plan_id == "coach":
            if triage is None or triage.channel != TriageChannel.GREEN:
                raise ValueError("Coach plan is only available for green channel users")

        if self._stripe_config.stripe_enabled:
            session = self._stripe_gateway.create_checkout_session(
                user_id=user_id,
                plan_id=plan.plan_id,
                email=user.email,
            )
            return {
                "order_id": str(session.get("id", "")),
                "user_id": user_id,
                "plan_id": plan.plan_id,
                "status": "pending_payment",
                "checkout_provider": "stripe",
                "checkout_session_id": str(session.get("id", "")),
                "checkout_url": str(session.get("url", "")),
            }

        if self._stripe_config.provider == "domestic":
            order_id = str(uuid.uuid4())
            channel_payload = self._domestic_gateway.create_checkout(
                order_id=order_id,
                user_id=user_id,
                plan_id=plan.plan_id,
                payment_channel=payment_channel,
            )
            return {
                "order_id": order_id,
                "user_id": user_id,
                "plan_id": plan.plan_id,
                "status": "pending_payment",
                "checkout_provider": "domestic",
                **channel_payload,
            }

        return {
            "order_id": str(uuid.uuid4()),
            "user_id": user_id,
            "plan_id": plan.plan_id,
            "status": "pending_payment",
            "checkout_provider": "local",
        }
