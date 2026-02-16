import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.tests.scoring.service import score_test


class InteractiveScoringTests(unittest.TestCase):
    def test_mbti_scoring_returns_type(self) -> None:
        summary = score_test(
            "mbti",
            {
                "ei": 55,
                "sn": -20,
                "tf": 10,
                "jp": -15,
            },
        )
        self.assertEqual(summary["type"], "ENTP")

    def test_16p_scoring_adds_identity_suffix(self) -> None:
        summary = score_test(
            "16p",
            {
                "ei": 30,
                "sn": -10,
                "tf": -40,
                "jp": -5,
                "identity": -12,
            },
        )
        self.assertEqual(summary["type"], "ENFP-T")

    def test_big5_scoring_identifies_dominant_trait(self) -> None:
        summary = score_test(
            "big5",
            {
                "O": 80,
                "C": 62,
                "E": 48,
                "A": 71,
                "N": 33,
            },
        )
        self.assertEqual(summary["dominant_trait"], "O")
        self.assertEqual(summary["lowest_trait"], "N")

    def test_attachment_and_love_language_primary_style(self) -> None:
        attachment = score_test(
            "attachment",
            {
                "secure": 75,
                "anxious": 50,
                "avoidant": 30,
                "fearful": 40,
            },
        )
        love = score_test(
            "love_language",
            {
                "words": 20,
                "acts": 88,
                "gifts": 10,
                "time": 76,
                "touch": 54,
            },
        )
        self.assertEqual(attachment["primary_style"], "secure")
        self.assertEqual(love["primary_style"], "acts")

    def test_stress_coping_primary_style(self) -> None:
        summary = score_test(
            "stress_coping",
            {
                "problem_focused": 72,
                "emotion_focused": 41,
                "avoidance": 20,
                "support_seeking": 64,
            },
        )
        self.assertEqual(summary["primary_style"], "problem_focused")

    def test_eq_scoring_level(self) -> None:
        summary = score_test(
            "eq",
            {
                "self_awareness": 80,
                "self_regulation": 76,
                "empathy": 82,
                "relationship_management": 74,
            },
        )
        self.assertEqual(summary["overall_score"], 78.0)
        self.assertEqual(summary["level"], "high")

    def test_inner_child_primary_profile(self) -> None:
        summary = score_test(
            "inner_child",
            {
                "playful": 52,
                "wounded": 61,
                "resilient": 74,
                "protective": 30,
            },
        )
        self.assertEqual(summary["primary_profile"], "resilient")

    def test_boundary_profile(self) -> None:
        summary = score_test(
            "boundary",
            {
                "emotional": 58,
                "physical": 61,
                "digital": 55,
                "work": 60,
                "social": 56,
            },
        )
        self.assertEqual(summary["boundary_profile"], "developing")
        self.assertEqual(summary["average_score"], 58.0)

    def test_psych_age_scoring(self) -> None:
        summary = score_test(
            "psych_age",
            {
                "chronological_age": 34,
                "curiosity": 70,
                "emotional_regulation": 62,
                "social_energy": 68,
            },
        )
        self.assertEqual(summary["psychological_age"], 33)
        self.assertEqual(summary["age_band"], "balanced")

    def test_psych_age_requires_valid_age_range(self) -> None:
        with self.assertRaises(ValueError):
            score_test(
                "psych_age",
                {
                    "chronological_age": 9,
                    "curiosity": 70,
                    "emotional_regulation": 62,
                    "social_energy": 68,
                },
            )

    def test_unknown_scoring_type_raises(self) -> None:
        with self.assertRaises(ValueError):
            score_test("unknown", {"a": 1})


if __name__ == "__main__":
    unittest.main()
