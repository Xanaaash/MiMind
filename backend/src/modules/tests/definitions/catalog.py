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
    "stress_coping": TestDefinition(
        test_id="stress_coping",
        display_name="Stress Coping Style",
        version="1.0",
        theory_reference="Lazarus and Folkman coping model",
        scoring_type="stress_coping",
    ),
    "eq": TestDefinition(
        test_id="eq",
        display_name="Emotional Intelligence (EQ)",
        version="1.0",
        theory_reference="Emotional intelligence model (Goleman)",
        scoring_type="eq",
    ),
    "inner_child": TestDefinition(
        test_id="inner_child",
        display_name="Inner Child Profile",
        version="1.0",
        theory_reference="Inner child framework in trauma-informed therapy",
        scoring_type="inner_child",
    ),
    "boundary": TestDefinition(
        test_id="boundary",
        display_name="Interpersonal Boundary",
        version="1.0",
        theory_reference="Boundary setting theory in relational psychology",
        scoring_type="boundary",
    ),
    "psych_age": TestDefinition(
        test_id="psych_age",
        display_name="Psychological Age",
        version="1.0",
        theory_reference="Developmental and personality trait composites",
        scoring_type="psych_age",
    ),
}
