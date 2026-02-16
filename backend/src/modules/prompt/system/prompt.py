from modules.prompt.registry.runtime import get_prompt_registry


def get_system_prompt() -> str:
    return get_prompt_registry().get_system_prompt()
