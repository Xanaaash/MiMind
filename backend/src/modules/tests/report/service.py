from typing import Dict

from modules.tests.models import TestDefinition, TestResult


FORBIDDEN_REPORT_PHRASES = [
    "you have depression",
    "you are diagnosed",
    "prescription",
    "take medication",
]


def _assert_non_diagnostic(text: str) -> None:
    lowered = text.lower()
    for phrase in FORBIDDEN_REPORT_PHRASES:
        if phrase in lowered:
            raise ValueError(f"Forbidden diagnostic phrase found: {phrase}")


class TestReportService:
    def build_report(self, definition: TestDefinition, result: TestResult, subscription_active: bool) -> Dict[str, object]:
        preview_text = (
            f"{definition.display_name}: This profile highlights your current tendencies for reflection and growth."
        )
        _assert_non_diagnostic(preview_text)

        if not subscription_active:
            return {
                "is_locked": True,
                "preview": preview_text,
                "subscribe_hint": "Subscribe to unlock full interpretation and personalized suggestions.",
            }

        full_report = {
            "is_locked": False,
            "title": definition.display_name,
            "theory_reference": definition.theory_reference,
            "summary": result.summary,
            "reflection_prompts": [
                "Which pattern in this report feels most familiar this week?",
                "What is one small experiment you can try based on this profile?",
            ],
        }

        _assert_non_diagnostic(str(full_report))
        return full_report
