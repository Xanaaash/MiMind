from typing import Any, Dict, Iterable, List, Optional, Tuple

from modules.assessment.catalog.scales import (
    CSSRS,
    GAD7,
    MANDATORY_SCALES,
    PHQ9,
    PSS10,
    QUESTION_COUNTS,
    SCL90,
    SCL90_DIMENSIONS,
    WHO5,
)
from modules.assessment.models import AssessmentScoreSet


def _validate_likert_answers(
    scale: str,
    answers: Iterable[int],
    expected_count: int,
    min_value: int,
    max_value: int,
) -> List[int]:
    casted = list(answers)
    if len(casted) != expected_count:
        raise ValueError(f"{scale} requires {expected_count} answers")

    for value in casted:
        if not isinstance(value, int):
            raise ValueError(f"{scale} answers must be integers")
        if value < min_value or value > max_value:
            raise ValueError(f"{scale} answers must be between {min_value} and {max_value}")

    return casted


def score_phq9(answers: Iterable[int]) -> int:
    validated = _validate_likert_answers(PHQ9, answers, QUESTION_COUNTS[PHQ9], 0, 3)
    return sum(validated)


def score_gad7(answers: Iterable[int]) -> int:
    validated = _validate_likert_answers(GAD7, answers, QUESTION_COUNTS[GAD7], 0, 3)
    return sum(validated)


def score_pss10(answers: Iterable[int]) -> int:
    validated = _validate_likert_answers(PSS10, answers, QUESTION_COUNTS[PSS10], 0, 4)

    # 1-indexed reverse-coded items in PSS-10: 4, 5, 7, 8
    reverse_indices = {3, 4, 6, 7}
    total = 0
    for idx, value in enumerate(validated):
        if idx in reverse_indices:
            total += 4 - value
        else:
            total += value
    return total


def score_cssrs(answers: Any) -> bool:
    if isinstance(answers, dict):
        values = list(answers.values())
    elif isinstance(answers, list):
        values = answers
    else:
        raise ValueError("cssrs answers must be a dict or a list")

    if not values:
        raise ValueError("cssrs answers must not be empty")

    for value in values:
        if not isinstance(value, bool):
            raise ValueError("cssrs answers must be booleans")

    return any(values)


def score_scl90(answers: Any) -> Tuple[float, Optional[Dict[str, float]]]:
    if isinstance(answers, list):
        validated = _validate_likert_answers(SCL90, answers, QUESTION_COUNTS[SCL90], 0, 4)
        global_index = round(sum(validated) / len(validated), 3)
        return global_index, None

    if not isinstance(answers, dict):
        raise ValueError("scl90 answers must be a list or a dict")

    if "dimensions" in answers and isinstance(answers["dimensions"], dict):
        dimensions = answers["dimensions"]
    else:
        dimensions = answers

    parsed: Dict[str, float] = {}
    for key in SCL90_DIMENSIONS:
        if key not in dimensions:
            raise ValueError(f"scl90 dimension '{key}' is required")

        value = dimensions[key]
        if not isinstance(value, (int, float)):
            raise ValueError(f"scl90 dimension '{key}' must be numeric")

        numeric = float(value)
        if numeric < 0 or numeric > 4:
            raise ValueError(f"scl90 dimension '{key}' must be between 0 and 4")
        parsed[key] = round(numeric, 3)

    global_index = round(sum(parsed.values()) / len(parsed), 3)
    return global_index, parsed


def score_who5(answers: Iterable[int]) -> Tuple[int, int, str, Dict[str, str]]:
    validated = _validate_likert_answers(WHO5, answers, QUESTION_COUNTS[WHO5], 0, 5)
    raw_score = sum(validated)
    score_100 = raw_score * 4

    if score_100 <= 28:
        severity = "severe"
        interpretation = {
            "en-US": "Current well-being appears low. Consider adding structured support and checking in with a professional if this pattern persists.",
            "zh-CN": "当前主观幸福感偏低。建议增加结构化支持，并在持续低迷时寻求专业支持。",
        }
    elif score_100 <= 50:
        severity = "moderate"
        interpretation = {
            "en-US": "Well-being is in a middle range. Daily recovery habits and regular mood tracking may help improve stability.",
            "zh-CN": "当前主观幸福感处于中间区间。建议通过日常恢复习惯和持续追踪来提升稳定性。",
        }
    else:
        severity = "minimal"
        interpretation = {
            "en-US": "Well-being is currently in a relatively healthy range. Keep protective routines and regular self-checks.",
            "zh-CN": "当前主观幸福感总体处于较健康区间。建议保持保护性习惯并定期自我检查。",
        }

    return raw_score, score_100, severity, interpretation


def score_single_scale(scale_id: str, answers: Any) -> dict:
    if scale_id == PHQ9:
        score = score_phq9(answers)
        return {"scale_id": PHQ9, "score": score}

    if scale_id == GAD7:
        score = score_gad7(answers)
        return {"scale_id": GAD7, "score": score}

    if scale_id == PSS10:
        score = score_pss10(answers)
        return {"scale_id": PSS10, "score": score}

    if scale_id == CSSRS:
        positive = score_cssrs(answers)
        return {"scale_id": CSSRS, "positive": positive}

    if scale_id == SCL90:
        global_index, dimensions = score_scl90(answers)
        return {
            "scale_id": SCL90,
            "global_index": global_index,
            "moderate_or_above": global_index >= 2.0,
            "dimension_scores": dimensions,
        }

    if scale_id == WHO5:
        raw_score, score_100, severity, interpretation = score_who5(answers)
        return {
            "scale_id": WHO5,
            "score": score_100,
            "raw_score": raw_score,
            "severity": severity,
            "interpretation": interpretation,
        }

    raise ValueError(f"Unsupported scale_id: {scale_id}")


def score_submission(responses: Dict[str, Any]) -> AssessmentScoreSet:
    missing = [scale for scale in MANDATORY_SCALES if scale not in responses]
    if missing:
        raise ValueError(f"Missing mandatory scales: {', '.join(missing)}")

    scl90_global_index: Optional[float] = None
    scl90_dimensions: Optional[Dict[str, float]] = None
    if SCL90 in responses:
        scl90_global_index, scl90_dimensions = score_scl90(responses[SCL90])

    return AssessmentScoreSet(
        phq9_score=score_phq9(responses[PHQ9]),
        gad7_score=score_gad7(responses[GAD7]),
        pss10_score=score_pss10(responses[PSS10]),
        cssrs_positive=score_cssrs(responses[CSSRS]),
        scl90_global_index=scl90_global_index,
        scl90_dimension_scores=scl90_dimensions,
        scl90_moderate_or_above=(scl90_global_index is not None and scl90_global_index >= 2.0),
    )
