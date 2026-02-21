import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.catalog.question_bank import get_scale_question_bank
from modules.assessment.catalog.scales import CDRISC10, ISI7, PHQ15, SWLS5, UCLA3, WHO5
from modules.assessment.scoring_service import score_single_scale


class ExtendedScaleSupportTests(unittest.TestCase):
    def test_extended_scales_have_bilingual_question_banks(self) -> None:
        for scale_id, expected_count in [
            (WHO5, 5),
            (ISI7, 7),
            (SWLS5, 5),
            (UCLA3, 3),
            (CDRISC10, 10),
            (PHQ15, 15),
        ]:
            bank = get_scale_question_bank(scale_id)
            self.assertEqual(len(bank["questions"]), expected_count)
            self.assertIn("en-US", bank["questions"][0]["text"])
            self.assertIn("zh-CN", bank["questions"][0]["text"])

    def test_extended_scales_can_be_scored(self) -> None:
        self.assertEqual(score_single_scale(WHO5, [5, 4, 3, 4, 4])["score"], 80)
        self.assertEqual(score_single_scale(ISI7, [2, 2, 1, 2, 1, 2, 2])["severity"], "subthreshold")
        self.assertEqual(score_single_scale(SWLS5, [4, 4, 3, 4, 4])["score"], 24)
        self.assertEqual(score_single_scale(UCLA3, [2, 1, 2])["score"], 5)
        self.assertEqual(score_single_scale(CDRISC10, [3] * 10)["score"], 30)
        self.assertEqual(score_single_scale(PHQ15, [1] * 15)["severity"], "severe")


if __name__ == "__main__":
    unittest.main()
