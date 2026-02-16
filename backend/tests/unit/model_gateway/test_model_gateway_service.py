import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.model_gateway.config import ModelGatewayRoutingConfig
from modules.model_gateway.models import ModelGatewayRequest, ModelTaskType
from modules.model_gateway.service import ModelGatewayService
from modules.storage.in_memory import InMemoryStore
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

    def test_gateway_routes_coach_generation_to_local_provider_by_default(self) -> None:
        gateway = ModelGatewayService()
        result = gateway.run(
            ModelTaskType.COACH_GENERATION,
            "I had a stressful day",
            metadata={"style_id": "warm_guide"},
        )
        self.assertEqual(result.task_type, ModelTaskType.COACH_GENERATION)
        self.assertEqual(result.risk_level, None)
        self.assertTrue(bool(result.output_text))
        self.assertIn("local-heuristic-coach", result.provider)

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

    def test_gateway_persists_success_audit_record(self) -> None:
        store = InMemoryStore()
        gateway = ModelGatewayService(audit_store=store)

        result = gateway.run(
            ModelTaskType.COACH_GENERATION,
            "I had a difficult day at work",
            metadata={"user_id": "u1", "session_id": "s1"},
        )
        self.assertTrue(bool(result.trace_id))

        records = store.list_model_invocations()
        self.assertEqual(len(records), 1)
        self.assertTrue(records[0].success)
        self.assertEqual(records[0].task_type, ModelTaskType.COACH_GENERATION)
        self.assertEqual(records[0].metadata.get("user_id"), "u1")

    def test_gateway_persists_failure_audit_record(self) -> None:
        class BrokenProvider:
            def infer(self, request: ModelGatewayRequest):
                raise RuntimeError("provider down")

        store = InMemoryStore()
        gateway = ModelGatewayService(
            providers={ModelTaskType.SAFETY_NLU_FAST: BrokenProvider()},
            audit_store=store,
        )
        with self.assertRaises(RuntimeError):
            gateway.run(ModelTaskType.SAFETY_NLU_FAST, "hello")

        records = store.list_model_invocations()
        self.assertEqual(len(records), 1)
        self.assertFalse(records[0].success)
        self.assertIn("provider down", str(records[0].error))

    def test_openai_coach_provider_without_api_key_fails_clearly(self) -> None:
        gateway = ModelGatewayService(
            config=ModelGatewayRoutingConfig(
                coach_generation_provider="openai",
                openai_api_key="",
            )
        )

        with self.assertRaises(ValueError):
            gateway.run(ModelTaskType.COACH_GENERATION, "hello")

    def test_unknown_provider_in_config_raises(self) -> None:
        with self.assertRaises(ValueError):
            ModelGatewayService(
                config=ModelGatewayRoutingConfig(
                    safety_nlu_provider="local",
                    safety_semantic_provider="local",
                    coach_generation_provider="mystery",
                )
            )


if __name__ == "__main__":
    unittest.main()
