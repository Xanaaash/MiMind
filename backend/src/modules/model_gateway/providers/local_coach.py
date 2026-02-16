import time

from modules.model_gateway.models import ModelGatewayRequest, ModelGatewayResponse, ModelTaskType


class LocalCoachProvider:
    def infer(self, request: ModelGatewayRequest) -> ModelGatewayResponse:
        if request.task_type != ModelTaskType.COACH_GENERATION:
            raise ValueError(f"LocalCoachProvider does not support task_type: {request.task_type}")

        start = time.perf_counter()
        style_id = str(request.metadata.get("style_id", "")).strip()
        user_message = request.text

        if style_id == "warm_guide":
            reply = (
                "I hear how important this is for you. "
                "Could you share one moment today that felt most emotionally intense?"
            )
        elif style_id == "rational_analysis":
            reply = (
                "Let's map this situation using CBT. "
                "What thought came first, and what action followed?"
            )
        else:
            reply = f"Let's keep exploring: {user_message[:120]}"

        latency = (time.perf_counter() - start) * 1000
        return ModelGatewayResponse(
            task_type=request.task_type,
            provider="local-heuristic-coach",
            risk_level=None,
            reasons=["local-coach-template"],
            latency_ms=latency,
            output_text=reply,
            raw={"style_id": style_id},
        )
