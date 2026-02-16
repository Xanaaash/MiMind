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

    def test_unknown_scoring_type_raises(self) -> None:
        with self.assertRaises(ValueError):
            score_test("unknown", {"a": 1})


if __name__ == "__main__":
    unittest.main()
