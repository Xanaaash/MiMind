from typing import Any, Dict, Optional, Tuple

from modules.onboarding.service import OnboardingService


class OnboardingAPI:
    def __init__(self, service: Optional[OnboardingService] = None) -> None:
        self._service = service or OnboardingService()

    def post_register(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            for field in ("email", "locale", "policy_version"):
                if not payload.get(field):
                    raise ValueError(f"{field} is required")

            data = self._service.register(
                email=str(payload["email"]),
                locale=str(payload["locale"]),
                policy_version=str(payload["policy_version"]),
            )
            return 201, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_assessment(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            responses = payload.get("responses")
            if not isinstance(responses, dict):
                raise ValueError("responses is required")

            dialogue_risk_payload = payload.get("dialogue_risk")
            dialogue_risk = self._service.parse_dialogue_risk(dialogue_risk_payload)
            data = self._service.submit_assessment(
                user_id=user_id,
                responses=responses,
                dialogue_risk=dialogue_risk,
            )
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def get_entitlements(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._service.get_entitlements(user_id)
            return 200, {"data": data}
        except ValueError as error:
            return 404, {"error": str(error)}
