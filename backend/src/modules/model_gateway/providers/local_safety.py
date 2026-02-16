from modules.model_gateway.models import ModelGatewayRequest, ModelGatewayResponse, ModelTaskType
from modules.safety.nlu.classifier import NLUClassifier
from modules.safety.semantic.evaluator import SemanticRiskEvaluator


class LocalSafetyProvider:
    def __init__(self) -> None:
        self._nlu = NLUClassifier()
        self._semantic = SemanticRiskEvaluator()

    def infer(self, request: ModelGatewayRequest) -> ModelGatewayResponse:
        if request.task_type == ModelTaskType.SAFETY_NLU_FAST:
            detection = self._nlu.classify(request.text)
            return ModelGatewayResponse(
                task_type=request.task_type,
                provider="local-heuristic-nlu",
                risk_level=detection.level,
                reasons=list(detection.reasons),
                latency_ms=detection.nlu_latency_ms,
                raw={
                    "source": detection.source,
                },
            )

        if request.task_type == ModelTaskType.SAFETY_SEMANTIC_JUDGE:
            detection = self._semantic.evaluate(request.text)
            return ModelGatewayResponse(
                task_type=request.task_type,
                provider="local-heuristic-semantic",
                risk_level=detection.level,
                reasons=list(detection.reasons),
                latency_ms=detection.semantic_latency_ms,
                raw={
                    "source": detection.source,
                },
            )

        raise ValueError(f"LocalSafetyProvider does not support task_type: {request.task_type}")
