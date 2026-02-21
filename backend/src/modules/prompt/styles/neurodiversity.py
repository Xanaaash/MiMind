from typing import List, Optional


NEURODIVERSITY_DISCLAIMER_CONTEXT = """
Neurodiversity note:
- These are trait-exploration signals from self-report questionnaires.
- They are not clinical diagnoses and should not be framed as medical certainty.
- If traits significantly impair daily functioning, suggest professional evaluation.
""".strip()


ADHD_HIGH_CONTEXT = """
ADHD-adapted coaching guidance:
- Keep responses short and chunked, ideally 2-4 clear steps.
- Favor action-coaching structure with concrete, time-boxed next actions.
- Before suggestions, affirm effort and reduce shame-based framing.
- Watch for rejection sensitivity cues (RSD): validate first, then reframe collaboratively.
""".strip()

ASD_HIGH_CONTEXT = """
ASD-adapted coaching guidance:
- Use clear, literal, and structured language with minimal metaphor.
- Prefer systematic analysis: break interpersonal events into concrete steps.
- Replace broad emotional prompts with specific, answerable questions.
- Offer social script breakdowns for difficult scenarios (opening, response, boundary).
""".strip()


def build_neurodiversity_prompt_fragments(neurodiversity_scores: Optional[dict]) -> List[str]:
    if not isinstance(neurodiversity_scores, dict) or not neurodiversity_scores:
        return []

    fragments = [NEURODIVERSITY_DISCLAIMER_CONTEXT]
    asrs = neurodiversity_scores.get("asrs")
    if isinstance(asrs, dict) and str(asrs.get("level", "")).strip().lower() == "high":
        fragments.append(ADHD_HIGH_CONTEXT)
    aq10 = neurodiversity_scores.get("aq10")
    if isinstance(aq10, dict) and str(aq10.get("level", "")).strip().lower() == "high":
        fragments.append(ASD_HIGH_CONTEXT)

    return fragments
