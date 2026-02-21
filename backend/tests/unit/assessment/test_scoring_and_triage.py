import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.scoring_service import score_submission
from modules.triage.models import TriageChannel
from modules.triage.triage_service import TriageService


class ScoringAndTriageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.triage = TriageService()

    def _base_responses(self) -> dict:
        return {
            "phq9": [0] * 9,
            "gad7": [0] * 7,
            "pss10": [0] * 10,
            "cssrs": {"q1": False, "q2": False, "q3": False},
        }

    def test_scoring_calculates_expected_values(self) -> None:
        responses = {
            "phq9": [1] * 9,
            "gad7": [2] * 7,
            "pss10": [0, 1, 2, 3, 4, 0, 1, 2, 3, 4],
            "cssrs": {"q1": False, "q2": True},
        }
        scores = score_submission(responses)

        self.assertEqual(scores.phq9_score, 9)
        self.assertEqual(scores.gad7_score, 14)
        self.assertEqual(scores.pss10_score, 16)
        self.assertTrue(scores.cssrs_positive)

    def test_invalid_score_payload_raises(self) -> None:
        responses = self._base_responses()
        responses["phq9"] = [1, 2]

        with self.assertRaises(ValueError):
            score_submission(responses)

    def test_triage_green(self) -> None:
        scores = score_submission(self._base_responses())
        decision = self.triage.evaluate(scores)
        self.assertEqual(decision.channel, TriageChannel.GREEN)

    def test_triage_yellow_when_phq_or_gad_moderate(self) -> None:
        responses = self._base_responses()
        responses["phq9"] = [2] * 5 + [0] * 4  # total 10

        scores = score_submission(responses)
        decision = self.triage.evaluate(scores)
        self.assertEqual(decision.channel, TriageChannel.YELLOW)

    def test_triage_red_when_phq_severe(self) -> None:
        responses = self._base_responses()
        responses["phq9"] = [3] * 7 + [0, 0]  # total 21

        scores = score_submission(responses)
        decision = self.triage.evaluate(scores)
        self.assertEqual(decision.channel, TriageChannel.RED)
        self.assertTrue(decision.halt_coaching)

    def test_triage_red_when_cssrs_positive(self) -> None:
        responses = self._base_responses()
        responses["cssrs"] = {"q1": True, "q2": False}

        scores = score_submission(responses)
        decision = self.triage.evaluate(scores)
        self.assertEqual(decision.channel, TriageChannel.RED)

    def test_triage_ignores_neurodiversity_only_high_scores(self) -> None:
        responses = self._base_responses()
        responses["asrs"] = [3] * 18
        responses["aq10"] = [1] * 10
        responses["hsp"] = [4] * 12
        responses["catq"] = [7] * 25

        scores = score_submission(responses)
        decision = self.triage.evaluate(scores)
        self.assertEqual(decision.channel, TriageChannel.GREEN)

    def test_triage_uses_core_thresholds_when_neurodiversity_payload_is_present(self) -> None:
        responses = self._base_responses()
        responses["asrs"] = [3] * 18
        responses["aq10"] = [1] * 10
        responses["phq9"] = [3] * 7 + [0, 0]  # total 21

        scores = score_submission(responses)
        decision = self.triage.evaluate(scores)
        self.assertEqual(decision.channel, TriageChannel.RED)


if __name__ == "__main__":
    unittest.main()
