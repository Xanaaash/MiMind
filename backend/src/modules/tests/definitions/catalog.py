from modules.tests.models import TestDefinition


CORE_TEST_DEFINITIONS = {
    "mbti": TestDefinition(
        test_id="mbti",
        display_name="MBTI Jungian Dimensions",
        version="1.0",
        theory_reference="Jungian type theory",
        scoring_type="mbti",
    ),
    "16p": TestDefinition(
        test_id="16p",
        display_name="16Personalities Style",
        version="1.0",
        theory_reference="Myers-Briggs inspired personality dimensions",
        scoring_type="16p",
    ),
    "big5": TestDefinition(
        test_id="big5",
        display_name="Big Five OCEAN",
        version="1.0",
        theory_reference="Five-factor model (OCEAN)",
        scoring_type="big5",
    ),
    "attachment": TestDefinition(
        test_id="attachment",
        display_name="Attachment Style",
        version="1.0",
        theory_reference="Attachment theory (Bowlby / Ainsworth)",
        scoring_type="attachment",
    ),
    "love_language": TestDefinition(
        test_id="love_language",
        display_name="Love Language",
        version="1.0",
        theory_reference="Five love languages framework",
        scoring_type="love_language",
    ),
}
