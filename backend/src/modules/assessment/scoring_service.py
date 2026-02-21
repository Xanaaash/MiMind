from typing import Any, Dict, Iterable, List, Optional, Tuple

from modules.assessment.catalog.scales import (
    CDRISC10,
    CSSRS,
    GAD7,
    ISI7,
    MANDATORY_SCALES,
    PHQ9,
    PHQ15,
    PSS10,
    QUESTION_COUNTS,
    SCL90,
    SCL90_DIMENSIONS,
    SWLS5,
    UCLA3,
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
    index_score = raw_score * 4
    if index_score >= 76:
        severity = "minimal"
    elif index_score >= 51:
        severity = "mild"
    elif index_score >= 29:
        severity = "moderate"
    else:
        severity = "severe"
    interpretation = {
        "en-US": "Lower WHO-5 index may indicate reduced emotional well-being and suggests follow-up screening.",
        "zh-CN": "WHO-5 指数较低可能提示幸福感下降，建议结合后续评估或支持。",
    }
    return raw_score, index_score, severity, interpretation


def score_isi7(answers: Iterable[int]) -> int:
    validated = _validate_likert_answers(ISI7, answers, QUESTION_COUNTS[ISI7], 0, 4)
    return sum(validated)


def score_swls5(answers: Iterable[int]) -> int:
    validated = _validate_likert_answers(SWLS5, answers, QUESTION_COUNTS[SWLS5], 0, 6)
    # UI stores 0..6. SWLS conventional scoring is 1..7.
    return sum(value + 1 for value in validated)


def score_ucla3(answers: Iterable[int]) -> int:
    validated = _validate_likert_answers(UCLA3, answers, QUESTION_COUNTS[UCLA3], 0, 2)
    return sum(validated)


def score_cdrisc10(answers: Iterable[int]) -> int:
    validated = _validate_likert_answers(CDRISC10, answers, QUESTION_COUNTS[CDRISC10], 0, 4)
    return sum(validated)


def score_phq15(answers: Iterable[int]) -> int:
    validated = _validate_likert_answers(PHQ15, answers, QUESTION_COUNTS[PHQ15], 0, 2)
    return sum(validated)


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
        raw_score, index_score, severity, interpretation = score_who5(answers)
        return {
            "scale_id": WHO5,
            "score": index_score,
            "raw_score": raw_score,
            "severity": severity,
            "interpretation": interpretation,
        }

    if scale_id == ISI7:
        score = score_isi7(answers)
        if score <= 7:
            severity = "none"
        elif score <= 14:
            severity = "subthreshold"
        elif score <= 21:
            severity = "moderate"
        else:
            severity = "severe"
        return {
            "scale_id": ISI7,
            "score": score,
            "severity": severity,
        }

    if scale_id == SWLS5:
        score = score_swls5(answers)
        return {
            "scale_id": SWLS5,
            "score": score,
            "interpretation": {
                "en-US": "Higher total generally indicates better global life satisfaction.",
                "zh-CN": "总分越高通常代表总体生活满意度越高。",
            },
        }

    if scale_id == UCLA3:
        score = score_ucla3(answers)
        return {
            "scale_id": UCLA3,
            "score": score,
            "severity": "elevated_loneliness" if score >= 4 else "low_to_moderate_loneliness",
        }

    if scale_id == CDRISC10:
        score = score_cdrisc10(answers)
        return {
            "scale_id": CDRISC10,
            "score": score,
            "interpretation": {
                "en-US": "Higher total suggests stronger perceived resilience resources.",
                "zh-CN": "总分越高通常代表主观心理韧性资源越强。",
            },
        }

    if scale_id == PHQ15:
        score = score_phq15(answers)
        if score >= 15:
            severity = "severe"
        elif score >= 10:
            severity = "moderate"
        elif score >= 5:
            severity = "mild"
        else:
            severity = "minimal"
        return {
            "scale_id": PHQ15,
            "score": score,
            "severity": severity,
            "interpretation": {
                "en-US": "Higher PHQ-15 totals indicate greater somatic symptom burden.",
                "zh-CN": "PHQ-15 分数越高通常提示躯体症状负担越高。",
            },
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
