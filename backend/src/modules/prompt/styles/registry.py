STYLE_PROMPTS = {
    "warm_guide": {
        "name": "Warm Guide",
        "prompt": "Use empathic reflections, validate feelings, and avoid directive language.",
    },
    "rational_analysis": {
        "name": "Rational Analysis",
        "prompt": "Use structured CBT-style questioning and focus on thought-behavior links.",
    },
}


def get_style_prompt(style_id: str) -> dict:
    style = STYLE_PROMPTS.get(style_id)
    if style is None:
        raise ValueError(f"Unsupported style_id: {style_id}")
    return dict(style)
