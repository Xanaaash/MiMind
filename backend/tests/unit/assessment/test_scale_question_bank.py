import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.catalog.question_bank import SCALE_QUESTION_BANKS, get_scale_question_bank
from modules.assessment.catalog.registry import CLINICAL_SCALE_DEFINITIONS


class ScaleQuestionBankTests(unittest.TestCase):
    def test_every_scale_definition_has_question_bank(self) -> None:
        self.assertEqual(set(CLINICAL_SCALE_DEFINITIONS.keys()), set(SCALE_QUESTION_BANKS.keys()))

    def test_phq9_questions_are_bilingual(self) -> None:
        bank = get_scale_question_bank("phq9")
        self.assertIn("zh-CN", bank["supported_locales"])
        self.assertEqual(len(bank["questions"]), 9)
        self.assertIn("en-US", bank["questions"][0]["text"])
        self.assertIn("zh-CN", bank["questions"][0]["text"])

    def test_unknown_scale_raises(self) -> None:
        with self.assertRaises(ValueError):
            get_scale_question_bank("unknown")


if __name__ == "__main__":
    unittest.main()
