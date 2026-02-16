import math
from typing import Dict, Optional
from uuid import uuid4

from modules.model_gateway.config import ModelGatewayRoutingConfig, load_model_gateway_config
from modules.model_gateway.models import ModelGatewayRequest, ModelGatewayResponse, ModelTaskType
from modules.model_gateway.providers.base import ModelProvider
from modules.model_gateway.providers.local_coach import LocalCoachProvider
from modules.model_gateway.providers.local_safety import LocalSafetyProvider
from modules.model_gateway.providers.openai_chat import OpenAIChatProvider
from modules.observability.models import ModelInvocationRecord
from modules.storage.in_memory import InMemoryStore


class ModelGatewayService:
    def __init__(
        self,
        providers: Optional[Dict[str, ModelProvider]] = None,
        config: Optional[ModelGatewayRoutingConfig] = None,
        audit_store: Optional[InMemoryStore] = None,
    ) -> None:
        if providers is None:
            resolved = config or load_model_gateway_config()
            providers = self._build_default_providers(resolved)
        self._providers = dict(providers)
        self._audit_store = audit_store

    def infer(self, request: ModelGatewayRequest) -> ModelGatewayResponse:
        provider = self._providers.get(request.task_type)
        if provider is None:
            self._record_failure(
                request=request,
                provider_name="unresolved",
                error=ValueError(f"Unsupported model task_type: {request.task_type}"),
            )
            raise ValueError(f"Unsupported model task_type: {request.task_type}")

        try:
            response = provider.infer(request)
        except Exception as error:
            self._record_failure(
                request=request,
                provider_name=provider.__class__.__name__,
                error=error,
            )
            raise

        self._record_success(request=request, response=response)
        return response

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

    def _record_success(self, request: ModelGatewayRequest, response: ModelGatewayResponse) -> None:
        if self._audit_store is None:
            return
        try:
            input_chars = len(request.text)
            output_chars = len(response.output_text or "")
            self._audit_store.save_model_invocation(
                ModelInvocationRecord(
                    trace_id=response.trace_id,
                    task_type=request.task_type,
                    provider=response.provider,
                    success=True,
                    latency_ms=response.latency_ms,
                    estimated_cost_usd=self._estimate_cost_usd(
                        task_type=request.task_type,
                        provider=response.provider,
                        input_chars=input_chars,
                        output_chars=output_chars,
                    ),
                    input_chars=input_chars,
                    output_chars=output_chars,
                    metadata=self._sanitize_metadata(request.metadata),
                )
            )
        except Exception:
            # Auditing must never break runtime behavior.
            return

    def _record_failure(self, request: ModelGatewayRequest, provider_name: str, error: Exception) -> None:
        if self._audit_store is None:
            return
        try:
            input_chars = len(request.text)
            self._audit_store.save_model_invocation(
                ModelInvocationRecord(
                    trace_id=f"error-{uuid4()}",
                    task_type=request.task_type,
                    provider=provider_name,
                    success=False,
                    latency_ms=0.0,
                    estimated_cost_usd=0.0,
                    input_chars=input_chars,
                    output_chars=0,
                    metadata=self._sanitize_metadata(request.metadata),
                    error=str(error),
                )
            )
        except Exception:
            return

    @staticmethod
    def _sanitize_metadata(metadata: dict) -> dict:
        keep = {"component", "session_id", "user_id", "style_id"}
        sanitized: Dict[str, str] = {}
        for key in keep:
            if key in metadata and metadata[key] is not None:
                sanitized[key] = str(metadata[key])
        return sanitized

    @staticmethod
    def _estimate_cost_usd(task_type: str, provider: str, input_chars: int, output_chars: int) -> float:
        if provider.startswith("local-"):
            return 0.0
        if provider.startswith("openai:") and task_type == ModelTaskType.COACH_GENERATION:
            input_tokens = math.ceil(max(0, input_chars) / 4)
            output_tokens = math.ceil(max(0, output_chars) / 4)
            return (input_tokens * 0.15 / 1_000_000) + (output_tokens * 0.6 / 1_000_000)
        return 0.0
