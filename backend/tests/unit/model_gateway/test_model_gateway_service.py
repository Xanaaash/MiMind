import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.model_gateway.models import ModelGatewayRequest, ModelTaskType
from modules.model_gateway.service import ModelGatewayService
from modules.triage.models import RiskLevel


class ModelGatewayServiceUnitTests(unittest.TestCase):
    def test_gateway_routes_safety_tasks(self) -> None:
        gateway = ModelGatewayService()

        nlu = gateway.run(ModelTaskType.SAFETY_NLU_FAST, "I feel stressed and anxious")
        self.assertEqual(nlu.task_type, ModelTaskType.SAFETY_NLU_FAST)
        self.assertEqual(nlu.risk_level, RiskLevel.LOW)
        self.assertGreaterEqual(nlu.latency_ms, 0.0)
        self.assertTrue(nlu.provider.startswith("local-heuristic"))

        semantic = gateway.run(ModelTaskType.SAFETY_SEMANTIC_JUDGE, "I can't handle this and nothing matters")
        self.assertEqual(semantic.task_type, ModelTaskType.SAFETY_SEMANTIC_JUDGE)
        self.assertIn(semantic.risk_level, (RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.EXTREME))
        self.assertGreaterEqual(semantic.latency_ms, 0.0)

    def test_gateway_unsupported_task_raises(self) -> None:
        gateway = ModelGatewayService()
        with self.assertRaises(ValueError):
            gateway.run("unsupported_task", "hello")

    def test_gateway_provider_error_bubbles_to_caller(self) -> None:
        class BrokenProvider:
            def infer(self, request: ModelGatewayRequest):
                raise RuntimeError("provider failed")

        gateway = ModelGatewayService(
            providers={
                ModelTaskType.SAFETY_NLU_FAST: BrokenProvider(),
            }
        )

        with self.assertRaises(RuntimeError):
            gateway.run(ModelTaskType.SAFETY_NLU_FAST, "hello")


if __name__ == "__main__":
    unittest.main()
