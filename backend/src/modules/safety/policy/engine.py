from modules.safety.models import SafetyResponseAction
from modules.triage.models import RiskLevel


class SafetyPolicyEngine:
    def resolve(self, level: RiskLevel) -> SafetyResponseAction:
        if level == RiskLevel.LOW:
            return SafetyResponseAction(
                mode="monitor",
                pause_topic=False,
                stop_coaching=False,
                show_hotline=False,
                notify_ops=False,
                notify_emergency_contact=False,
                suggested_channel="green",
                message="I hear you. We can keep exploring this safely.",
            )

        if level == RiskLevel.MEDIUM:
            return SafetyResponseAction(
                mode="safety_pause",
                pause_topic=True,
                stop_coaching=False,
                show_hotline=True,
                notify_ops=False,
                notify_emergency_contact=False,
                suggested_channel="yellow",
                message="Let's pause and focus on your safety first, with support resources nearby.",
            )

        if level == RiskLevel.HIGH:
            return SafetyResponseAction(
                mode="crisis_stop",
                pause_topic=True,
                stop_coaching=True,
                show_hotline=True,
                notify_ops=True,
                notify_emergency_contact=False,
                suggested_channel="red",
                message="I need to stop normal coaching now and connect you to urgent support.",
            )

        return SafetyResponseAction(
            mode="extreme_emergency",
            pause_topic=True,
            stop_coaching=True,
            show_hotline=True,
            notify_ops=True,
            notify_emergency_contact=True,
            suggested_channel="red",
            message="This appears to be an immediate danger situation. Emergency support is required now.",
        )
