from modules.safety.emergency.service import EmergencyService
from modules.safety.hotline.resolver import HotlineResolver
from modules.safety.models import SafetyDetectionResult
from modules.safety.ops_alert.service import OpsAlertService
from modules.safety.policy.engine import SafetyPolicyEngine
from modules.storage.in_memory import InMemoryStore


class SafetyInterruptionService:
    def __init__(self, store: InMemoryStore) -> None:
        self._policy = SafetyPolicyEngine()
        self._hotline = HotlineResolver()
        self._ops = OpsAlertService(store)
        self._emergency = EmergencyService()

    def handle(
        self,
        user_id: str,
        locale: str,
        detection: SafetyDetectionResult,
        legal_policy_enabled: bool = False,
    ) -> dict:
        action = self._policy.resolve(detection.level)
        hotline = self._hotline.resolve(locale) if action.show_hotline else None

        ops_event = None
        if action.notify_ops:
            ops_event = self._ops.notify(
                user_id=user_id,
                level=detection.level,
                reason=";".join(detection.reasons),
            )

        emergency_contact_notified = self._emergency.should_notify_emergency_contact(
            level=detection.level,
            legal_policy_enabled=legal_policy_enabled,
        )

        return {
            "detection": detection.to_dict(),
            "action": action.to_dict(),
            "hotline": hotline,
            "ops_event": ops_event,
            "emergency_contact_notified": emergency_contact_notified,
            "hotline_cache": self._hotline.local_cache_payload(),
        }
