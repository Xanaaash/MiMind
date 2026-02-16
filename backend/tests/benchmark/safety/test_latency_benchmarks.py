import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.safety.detector_service import SafetyDetectorService


class SafetyLatencyBenchmarkTests(unittest.TestCase):
    def test_nlu_latency_under_100ms(self) -> None:
        detector = SafetyDetectorService()
        result = detector.detect("I feel stressed about work and life")
        self.assertLess(result.nlu_latency_ms, 100.0)

    def test_semantic_latency_under_2s(self) -> None:
        detector = SafetyDetectorService()
        result = detector.detect("I can't handle this and nothing matters")
        self.assertLess(result.semantic_latency_ms, 2000.0)


if __name__ == "__main__":
    unittest.main()
