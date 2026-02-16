import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.tests.catalog.question_bank import TEST_QUESTION_BANKS, get_test_question_bank
from modules.tests.definitions.catalog import CORE_TEST_DEFINITIONS


class InteractiveTestQuestionBankTests(unittest.TestCase):
    def test_every_test_definition_has_question_bank(self) -> None:
        self.assertEqual(set(CORE_TEST_DEFINITIONS.keys()), set(TEST_QUESTION_BANKS.keys()))

    def test_eq_questions_are_bilingual(self) -> None:
        bank = get_test_question_bank("eq")
        self.assertEqual(len(bank["questions"]), 4)
        self.assertIn("zh-CN", bank["supported_locales"])
        self.assertIn("en-US", bank["questions"][0]["text"])
        self.assertIn("zh-CN", bank["questions"][0]["text"])

    def test_unknown_test_raises(self) -> None:
        with self.assertRaises(ValueError):
            get_test_question_bank("unknown")


if __name__ == "__main__":
    unittest.main()
