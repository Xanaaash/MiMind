import json
import time

import httpx

from modules.model_gateway.config import ModelGatewayRoutingConfig
from modules.model_gateway.models import ModelGatewayRequest, ModelGatewayResponse, ModelTaskType


class OpenAIChatProvider:
    def __init__(self, config: ModelGatewayRoutingConfig) -> None:
        self._config = config

    def infer(self, request: ModelGatewayRequest) -> ModelGatewayResponse:
        if request.task_type != ModelTaskType.COACH_GENERATION:
            raise ValueError(f"OpenAIChatProvider does not support task_type: {request.task_type}")
        if not self._config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when coach provider is set to openai")

        start = time.perf_counter()

        system_prompt = str(request.metadata.get("system_prompt", "")).strip()
        style_prompt = request.metadata.get("style_prompt")
        context_prompt = request.metadata.get("context_prompt")

        style_text = ""
        if isinstance(style_prompt, dict):
            style_text = str(style_prompt.get("prompt", "")).strip()
        elif isinstance(style_prompt, str):
            style_text = style_prompt.strip()

        context_text = ""
        if isinstance(context_prompt, dict):
            context_text = json.dumps(context_prompt, ensure_ascii=True)
        elif isinstance(context_prompt, str):
            context_text = context_prompt

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if style_text:
            messages.append({"role": "system", "content": f"Style instruction: {style_text}"})
        if context_text:
            messages.append({"role": "system", "content": f"Context payload: {context_text}"})
        messages.append({"role": "user", "content": request.text})

        endpoint = f"{self._config.openai_base_url.rstrip('/')}/chat/completions"
        timeout = max(1.0, request.timeout_ms / 1000.0)

        response = httpx.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {self._config.openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self._config.openai_coach_model,
                "messages": messages,
                "temperature": 0.4,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()

        choices = payload.get("choices", [])
        if not choices:
            raise RuntimeError("OpenAI provider returned no choices")
        message = choices[0].get("message", {}) or {}
        content = str(message.get("content", "")).strip()
        if not content:
            raise RuntimeError("OpenAI provider returned empty content")

        latency = (time.perf_counter() - start) * 1000
        return ModelGatewayResponse(
            task_type=request.task_type,
            provider=f"openai:{self._config.openai_coach_model}",
            risk_level=None,
            reasons=["provider-openai"],
            latency_ms=latency,
            output_text=content,
            raw={
                "id": payload.get("id"),
                "finish_reason": choices[0].get("finish_reason"),
            },
        )
