from typing import Dict, Optional

from modules.model_gateway.config import ModelGatewayRoutingConfig, load_model_gateway_config
from modules.model_gateway.models import ModelGatewayRequest, ModelGatewayResponse, ModelTaskType
from modules.model_gateway.providers.base import ModelProvider
from modules.model_gateway.providers.local_coach import LocalCoachProvider
from modules.model_gateway.providers.local_safety import LocalSafetyProvider
from modules.model_gateway.providers.openai_chat import OpenAIChatProvider


class ModelGatewayService:
    def __init__(
        self,
        providers: Optional[Dict[str, ModelProvider]] = None,
        config: Optional[ModelGatewayRoutingConfig] = None,
    ) -> None:
        if providers is None:
            resolved = config or load_model_gateway_config()
            providers = self._build_default_providers(resolved)
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

    @staticmethod
    def _build_default_providers(config: ModelGatewayRoutingConfig) -> Dict[str, ModelProvider]:
        local_safety = LocalSafetyProvider()
        local_coach = LocalCoachProvider()
        openai_coach = OpenAIChatProvider(config)

        providers: Dict[str, ModelProvider] = {}
        providers[ModelTaskType.SAFETY_NLU_FAST] = ModelGatewayService._select_provider(
            task_type=ModelTaskType.SAFETY_NLU_FAST,
            provider_id=config.safety_nlu_provider,
            local_provider=local_safety,
            openai_provider=openai_coach,
        )
        providers[ModelTaskType.SAFETY_SEMANTIC_JUDGE] = ModelGatewayService._select_provider(
            task_type=ModelTaskType.SAFETY_SEMANTIC_JUDGE,
            provider_id=config.safety_semantic_provider,
            local_provider=local_safety,
            openai_provider=openai_coach,
        )
        providers[ModelTaskType.COACH_GENERATION] = ModelGatewayService._select_provider(
            task_type=ModelTaskType.COACH_GENERATION,
            provider_id=config.coach_generation_provider,
            local_provider=local_coach,
            openai_provider=openai_coach,
        )
        return providers

    @staticmethod
    def _select_provider(
        task_type: str,
        provider_id: str,
        local_provider: ModelProvider,
        openai_provider: ModelProvider,
    ) -> ModelProvider:
        if provider_id == "local":
            return local_provider

        if provider_id == "openai":
            if task_type != ModelTaskType.COACH_GENERATION:
                raise ValueError(
                    f"Provider 'openai' is not enabled for task_type '{task_type}' in this phase"
                )
            return openai_provider

        raise ValueError(f"Unknown provider '{provider_id}' for task_type '{task_type}'")
