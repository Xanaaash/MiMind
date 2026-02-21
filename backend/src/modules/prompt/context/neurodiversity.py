from __future__ import annotations

from typing import Dict, Optional

from modules.storage.in_memory import InMemoryStore
from modules.tests.models import TestResult


NEURO_TEST_IDS = {"asrs", "aq10", "hsp", "catq"}
VALID_LEVELS = {"low", "moderate", "high"}


def build_neurodiversity_scores(store: InMemoryStore, user_id: str) -> Optional[dict]:
    latest_by_test: Dict[str, dict] = {}
    for result in reversed(store.list_user_test_results(user_id)):
        test_id = str(result.test_id).strip().lower()
        if test_id not in NEURO_TEST_IDS:
            continue
        if test_id in latest_by_test:
            continue

        latest_by_test[test_id] = _build_score_payload(result, test_id)

    return latest_by_test or None


def _build_score_payload(result: TestResult, test_id: str) -> dict:
    summary = result.summary if isinstance(result.summary, dict) else {}
    total_score, max_score = _extract_total_scores(summary)
    level = _infer_level(test_id, summary, total_score, max_score) or "unknown"

    payload = {
        "level": level,
        "source_result_id": result.result_id,
        "captured_at": result.created_at.isoformat(),
    }
    if total_score is not None:
        payload["score"] = round(total_score, 3)
    if max_score is not None:
        payload["max_score"] = round(max_score, 3)
    return payload


def _infer_level(
    test_id: str,
    summary: dict,
    total_score: Optional[float],
    max_score: Optional[float],
) -> Optional[str]:
    explicit = _explicit_level(summary)
    if explicit:
        return explicit

    if test_id == "asrs":
        flagged = _number(summary, "flagged_count", "part_a_positive_count", "part_a_flagged")
        if flagged is not None:
            if flagged >= 4:
                return "high"
            if flagged >= 2:
                return "moderate"
            return "low"

        screener_positive = _bool(summary, "screener_positive", "high_trait")
        if screener_positive is not None:
            return "high" if screener_positive else "low"

        if total_score is not None:
            if total_score >= 14:
                return "high"
            if total_score >= 8:
                return "moderate"
            return "low"

    if test_id == "aq10":
        high_trait = _bool(summary, "high_trait")
        if high_trait is not None:
            return "high" if high_trait else "low"
        if total_score is not None:
            if total_score >= 6:
                return "high"
            if total_score >= 3:
                return "moderate"
            return "low"

    if test_id == "hsp":
        mean_score = _number(summary, "mean_score")
        if mean_score is not None:
            if mean_score >= 4.5:
                return "high"
            if mean_score >= 3:
                return "moderate"
            return "low"
        if total_score is not None and max_score == 7:
            if total_score >= 4.5:
                return "high"
            if total_score >= 3:
                return "moderate"
            return "low"

    if test_id == "catq" and total_score is not None:
        if total_score >= 95:
            return "high"
        if total_score >= 60:
            return "moderate"
        return "low"

    if total_score is None or max_score is None or max_score <= 0:
        return None

    ratio = total_score / max_score
    if ratio >= 0.65:
        return "high"
    if ratio >= 0.4:
        return "moderate"
    return "low"


def _extract_total_scores(summary: dict) -> tuple[Optional[float], Optional[float]]:
    total_score = _number(summary, "total", "total_score", "score", "mean_score")
    max_score = _number(summary, "maxTotal", "max_total", "max_score")
    return total_score, max_score


def _explicit_level(summary: dict) -> Optional[str]:
    value = summary.get("level")
    if not isinstance(value, str):
        return None
    level = value.strip().lower()
    if level in VALID_LEVELS:
        return level
    return None


def _number(summary: dict, *keys: str) -> Optional[float]:
    for key in keys:
        value = summary.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _bool(summary: dict, *keys: str) -> Optional[bool]:
    for key in keys:
        value = summary.get(key)
        if isinstance(value, bool):
            return value
    return None
