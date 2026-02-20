import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.scoring_service import score_submission
from modules.safety.emergency.service import EmergencyService
from modules.safety.hotline.resolver import FALLBACK_HOTLINE, HOTLINE_BY_LOCALE, HotlineResolver
from modules.safety.nlu.classifier import NLUClassifier
from modules.safety.policy.engine import SafetyPolicyEngine
from modules.safety.semantic.evaluator import SemanticRiskEvaluator
from modules.triage.models import DialogueRiskSignal, RiskLevel, TriageChannel
from modules.triage.triage_service import TriageService


class CrisisRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = SafetyPolicyEngine()
        self.hotline = HotlineResolver()
        self.emergency = EmergencyService()
        self.nlu = NLUClassifier()
        self.semantic = SemanticRiskEvaluator()
        self.triage = TriageService()

    @staticmethod
    def _green_scores():
        responses = {
            "phq9": [0] * 9,
            "gad7": [0] * 7,
            "pss10": [0] * 10,
            "cssrs": {"q1": False, "q2": False},
        }
        return score_submission(responses)

    def test_four_level_policy_regression(self) -> None:
        low = self.policy.resolve(RiskLevel.LOW)
        medium = self.policy.resolve(RiskLevel.MEDIUM)
        high = self.policy.resolve(RiskLevel.HIGH)
        extreme = self.policy.resolve(RiskLevel.EXTREME)

        self.assertEqual(low.mode, "monitor")
        self.assertFalse(low.stop_coaching)
        self.assertFalse(low.show_hotline)

        self.assertEqual(medium.mode, "safety_pause")
        self.assertFalse(medium.stop_coaching)
        self.assertTrue(medium.show_hotline)

        self.assertEqual(high.mode, "crisis_stop")
        self.assertTrue(high.stop_coaching)
        self.assertTrue(high.notify_ops)
        self.assertFalse(high.notify_emergency_contact)

        self.assertEqual(extreme.mode, "extreme_emergency")
        self.assertTrue(extreme.stop_coaching)
        self.assertTrue(extreme.notify_ops)
        self.assertTrue(extreme.notify_emergency_contact)

    def test_hotline_locale_resolution_and_fallback(self) -> None:
        self.assertEqual(self.hotline.resolve("en-US"), HOTLINE_BY_LOCALE["en-US"])
        self.assertEqual(self.hotline.resolve("zh-CN"), HOTLINE_BY_LOCALE["zh-CN"])
        self.assertEqual(self.hotline.resolve("fr-FR"), FALLBACK_HOTLINE)

        cache = self.hotline.local_cache_payload()
        self.assertIn("default", cache)
        self.assertEqual(cache["default"], FALLBACK_HOTLINE)

    def test_emergency_contact_requires_extreme_and_legal_policy(self) -> None:
        self.assertFalse(
            self.emergency.should_notify_emergency_contact(RiskLevel.EXTREME, legal_policy_enabled=False)
        )
        self.assertFalse(
            self.emergency.should_notify_emergency_contact(RiskLevel.HIGH, legal_policy_enabled=True)
        )
        self.assertTrue(
            self.emergency.should_notify_emergency_contact(RiskLevel.EXTREME, legal_policy_enabled=True)
        )

    def test_dialogue_high_risk_overrides_green_scale(self) -> None:
        decision = self.triage.evaluate(
            self._green_scores(),
            dialogue_risk=DialogueRiskSignal(
                level=RiskLevel.HIGH,
                text="I want to hurt myself tonight",
                is_joke=False,
            ),
        )
        self.assertEqual(decision.channel, TriageChannel.RED)
        self.assertTrue(decision.halt_coaching)
        self.assertTrue(decision.show_hotline)

    def test_joke_disclaimer_still_results_in_red_channel(self) -> None:
        decision = self.triage.evaluate(
            self._green_scores(),
            dialogue_risk=DialogueRiskSignal(
                level=RiskLevel.HIGH,
                text="I want to die, just kidding",
                is_joke=True,
            ),
        )
        self.assertEqual(decision.channel, TriageChannel.RED)
        self.assertTrue(decision.halt_coaching)
        self.assertEqual(decision.dialogue_risk_level, RiskLevel.HIGH)

    def test_nlu_high_keyword_recall_regression_set(self) -> None:
        high_samples = [
            "I want to kill myself tonight",
            "I have decided to end my life soon",
            "I will hurt myself right now",
        ]

        hits = sum(1 for text in high_samples if self.nlu.classify(text).level.value >= RiskLevel.HIGH.value)
        self.assertGreaterEqual(hits / len(high_samples), 0.99)

    def test_semantic_extreme_when_high_intent_has_immediacy(self) -> None:
        result = self.semantic.evaluate("I want to die right now, tonight")
        self.assertEqual(result.level, RiskLevel.EXTREME)


if __name__ == "__main__":
    unittest.main()
