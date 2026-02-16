from typing import Dict, Optional

from modules.model_gateway.models import ModelGatewayRequest, ModelGatewayResponse, ModelTaskType
from modules.model_gateway.providers.base import ModelProvider
from modules.model_gateway.providers.local_safety import LocalSafetyProvider


class ModelGatewayService:
    def __init__(self, providers: Optional[Dict[str, ModelProvider]] = None) -> None:
        if providers is None:
            local_safety = LocalSafetyProvider()
            providers = {
                ModelTaskType.SAFETY_NLU_FAST: local_safety,
                ModelTaskType.SAFETY_SEMANTIC_JUDGE: local_safety,
            }
        self._providers = dict(providers)

    def infer(self, request: ModelGatewayRequest) -> ModelGatewayResponse:
        provider = self._providers.get(request.task_type)
        if provider is None:
            raise ValueError(f"Unsupported model task_type: {request.task_type}")
        return provider.infer(request)

    def run(
        self,
        task_type: str,
        text: str,
        locale: str = "en-US",
        timeout_ms: int = 2000,
        metadata: Optional[dict] = None,
    ) -> ModelGatewayResponse:
        request = ModelGatewayRequest(
            task_type=task_type,
            text=text,
            locale=locale,
            timeout_ms=timeout_ms,
            metadata=metadata or {},
        )
        return self.infer(request)
