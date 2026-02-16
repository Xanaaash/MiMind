import os
from dataclasses import dataclass


@dataclass
class ModelGatewayRoutingConfig:
    safety_nlu_provider: str = "local"
    safety_semantic_provider: str = "local"
    coach_generation_provider: str = "local"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_coach_model: str = "gpt-4o-mini"


def load_model_gateway_config() -> ModelGatewayRoutingConfig:
    return ModelGatewayRoutingConfig(
        safety_nlu_provider=os.getenv("MINDCOACH_PROVIDER_SAFETY_NLU", "local").strip().lower(),
        safety_semantic_provider=os.getenv("MINDCOACH_PROVIDER_SAFETY_SEMANTIC", "local").strip().lower(),
        coach_generation_provider=os.getenv("MINDCOACH_PROVIDER_COACH", "local").strip().lower(),
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip(),
        openai_coach_model=os.getenv("OPENAI_COACH_MODEL", "gpt-4o-mini").strip(),
    )
