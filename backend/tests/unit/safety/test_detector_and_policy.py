import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.safety.detector_service import SafetyDetectorService
from modules.safety.policy.engine import SafetyPolicyEngine
from modules.triage.models import RiskLevel


class DetectorAndPolicyUnitTests(unittest.TestCase):
    def test_detector_flags_high_risk_keywords(self) -> None:
        detector = SafetyDetectorService()
        result = detector.detect("I want to kill myself tonight")
        self.assertIn(result.level, (RiskLevel.HIGH, RiskLevel.EXTREME))

    def test_policy_engine_covers_all_levels(self) -> None:
        engine = SafetyPolicyEngine()
        low = engine.resolve(RiskLevel.LOW)
        medium = engine.resolve(RiskLevel.MEDIUM)
        high = engine.resolve(RiskLevel.HIGH)
        extreme = engine.resolve(RiskLevel.EXTREME)

        self.assertEqual(low.mode, "monitor")
        self.assertEqual(medium.mode, "safety_pause")
        self.assertEqual(high.mode, "crisis_stop")
        self.assertEqual(extreme.mode, "extreme_emergency")

    def test_detector_fail_closed_when_internal_error(self) -> None:
        detector = SafetyDetectorService()

        class BrokenNLU:
            def classify(self, text: str):
                raise RuntimeError("nlu failure")

        detector._nlu = BrokenNLU()  # type: ignore[attr-defined]
        result = detector.detect("any message")
        self.assertEqual(result.level, RiskLevel.HIGH)
        self.assertTrue(result.fail_closed)


if __name__ == "__main__":
    unittest.main()
