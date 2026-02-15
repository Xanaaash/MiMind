import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.scoring_service import score_submission
from modules.triage.models import DialogueRiskSignal, RiskLevel, TriageChannel
from modules.triage.triage_service import TriageService


class DialoguePrioritySafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.triage = TriageService()

    def _green_scores(self):
        responses = {
            "phq9": [0] * 9,
            "gad7": [0] * 7,
            "pss10": [0] * 10,
            "cssrs": {"q1": False, "q2": False},
        }
        return score_submission(responses)

    def test_dialogue_high_risk_overrides_green_scale(self) -> None:
        scores = self._green_scores()

        decision = self.triage.evaluate(
            scores,
            dialogue_risk=DialogueRiskSignal(
                level=RiskLevel.HIGH,
                text="I have a plan to hurt myself tonight",
                is_joke=False,
            ),
        )

        self.assertEqual(decision.channel, TriageChannel.RED)
        self.assertTrue(decision.halt_coaching)
        self.assertTrue(decision.show_hotline)

    def test_joke_disclaimer_does_not_bypass_safety_response(self) -> None:
        scores = self._green_scores()

        decision = self.triage.evaluate(
            scores,
            dialogue_risk=DialogueRiskSignal(
                level=RiskLevel.HIGH,
                text="Just kidding, but I want to die",
                is_joke=True,
            ),
        )

        self.assertEqual(decision.channel, TriageChannel.RED)
        self.assertTrue(decision.halt_coaching)


if __name__ == "__main__":
    unittest.main()
