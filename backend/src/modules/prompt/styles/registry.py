from modules.prompt.registry.runtime import get_prompt_registry


def get_style_prompt(style_id: str) -> dict:
    return get_prompt_registry().get_style_prompt(style_id=style_id)
