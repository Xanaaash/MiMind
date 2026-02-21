import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.scoring_service import score_single_scale, score_who5


class WHO5ScaleSupportTests(unittest.TestCase):
    def test_who5_scoring_and_severity(self) -> None:
        raw_score, score_100, severity, interpretation = score_who5([4, 4, 4, 4, 4])
        self.assertEqual(raw_score, 20)
        self.assertEqual(score_100, 80)
        self.assertEqual(severity, "minimal")
        self.assertIn("en-US", interpretation)
        self.assertIn("zh-CN", interpretation)

    def test_score_single_scale_shape(self) -> None:
        result = score_single_scale("who5", [2, 2, 2, 2, 2])
        self.assertEqual(result["scale_id"], "who5")
        self.assertEqual(result["score"], 40)
        self.assertIn("severity", result)
        self.assertIn("interpretation", result)


if __name__ == "__main__":
    unittest.main()
