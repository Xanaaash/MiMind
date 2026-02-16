import os
from typing import Optional

from modules.prompt.registry.service import PromptRegistryService

_REGISTRY: Optional[PromptRegistryService] = None


def get_prompt_registry() -> PromptRegistryService:
    global _REGISTRY
    if _REGISTRY is None:
        default_version = os.getenv("MINDCOACH_PROMPT_PACK", "").strip() or None
        _REGISTRY = PromptRegistryService(default_active_version=default_version)
    return _REGISTRY


def reset_prompt_registry_for_tests() -> None:
    global _REGISTRY
    _REGISTRY = None
