from typing import Dict, Tuple


MBTI_KEYS: Dict[str, Tuple[str, str]] = {
    "ei": ("E", "I"),
    "sn": ("S", "N"),
    "tf": ("T", "F"),
    "jp": ("J", "P"),
}


def _require_numeric_map(answers: dict, required_keys, min_value: int, max_value: int) -> Dict[str, float]:
    if not isinstance(answers, dict):
        raise ValueError("answers must be an object")

    parsed: Dict[str, float] = {}
    for key in required_keys:
        if key not in answers:
            raise ValueError(f"Missing answer key: {key}")
        value = answers[key]
        if not isinstance(value, (int, float)):
            raise ValueError(f"Answer {key} must be numeric")
        numeric = float(value)
        if numeric < min_value or numeric > max_value:
            raise ValueError(f"Answer {key} must be between {min_value} and {max_value}")
        parsed[key] = numeric
    return parsed


def score_mbti(answers: dict) -> dict:
    parsed = _require_numeric_map(answers, MBTI_KEYS.keys(), -100, 100)

    type_code = ""
    strengths = {}
    for dimension, (positive_letter, negative_letter) in MBTI_KEYS.items():
        value = parsed[dimension]
        if value >= 0:
            type_code += positive_letter
            strengths[positive_letter] = round(abs(value), 2)
        else:
            type_code += negative_letter
            strengths[negative_letter] = round(abs(value), 2)

    return {
        "type": type_code,
        "dimension_strength": strengths,
    }


def score_16p(answers: dict) -> dict:
    parsed = _require_numeric_map(answers, list(MBTI_KEYS.keys()) + ["identity"], -100, 100)
    mbti_summary = score_mbti(parsed)

    identity_suffix = "-A" if parsed["identity"] >= 0 else "-T"
    return {
        "type": mbti_summary["type"] + identity_suffix,
        "dimension_strength": mbti_summary["dimension_strength"],
        "identity_score": round(parsed["identity"], 2),
    }


def score_big5(answers: dict) -> dict:
    parsed = _require_numeric_map(answers, ["O", "C", "E", "A", "N"], 0, 100)

    dominant = max(parsed.items(), key=lambda item: item[1])[0]
    lowest = min(parsed.items(), key=lambda item: item[1])[0]

    return {
        "scores": {k: round(v, 2) for k, v in parsed.items()},
        "dominant_trait": dominant,
        "lowest_trait": lowest,
    }


def _top_category_summary(answers: dict, categories) -> dict:
    parsed = _require_numeric_map(answers, categories, 0, 100)
    primary = max(parsed.items(), key=lambda item: item[1])[0]

    return {
        "scores": {k: round(v, 2) for k, v in parsed.items()},
        "primary_style": primary,
    }


def score_attachment(answers: dict) -> dict:
    return _top_category_summary(
        answers,
        ["secure", "anxious", "avoidant", "fearful"],
    )


def score_love_language(answers: dict) -> dict:
    return _top_category_summary(
        answers,
        ["words", "acts", "gifts", "time", "touch"],
    )


def score_test(scoring_type: str, answers: dict) -> dict:
    if scoring_type == "mbti":
        return score_mbti(answers)
    if scoring_type == "16p":
        return score_16p(answers)
    if scoring_type == "big5":
        return score_big5(answers)
    if scoring_type == "attachment":
        return score_attachment(answers)
    if scoring_type == "love_language":
        return score_love_language(answers)

    raise ValueError(f"Unsupported scoring_type: {scoring_type}")
