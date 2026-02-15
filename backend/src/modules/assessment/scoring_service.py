from typing import Any, Dict, Iterable, List

from modules.assessment.catalog.scales import CSSRS, GAD7, MANDATORY_SCALES, PHQ9, PSS10, QUESTION_COUNTS
from modules.assessment.models import AssessmentScoreSet


def _validate_likert_answers(scale: str, answers: Iterable[int], expected_count: int, min_value: int, max_value: int) -> List[int]:
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


def score_submission(responses: Dict[str, Any]) -> AssessmentScoreSet:
    missing = [scale for scale in MANDATORY_SCALES if scale not in responses]
    if missing:
        raise ValueError(f"Missing mandatory scales: {', '.join(missing)}")

    return AssessmentScoreSet(
        phq9_score=score_phq9(responses[PHQ9]),
        gad7_score=score_gad7(responses[GAD7]),
        pss10_score=score_pss10(responses[PSS10]),
        cssrs_positive=score_cssrs(responses[CSSRS]),
    )
