from typing import Protocol

from modules.model_gateway.models import ModelGatewayRequest, ModelGatewayResponse


class ModelProvider(Protocol):
    def infer(self, request: ModelGatewayRequest) -> ModelGatewayResponse:
        ...
