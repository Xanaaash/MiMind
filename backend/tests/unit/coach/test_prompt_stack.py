import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.memory.service import MemoryService
from modules.prompt.context.builder import build_context_prompt
from modules.prompt.styles.registry import get_style_prompt
from modules.prompt.system.prompt import get_system_prompt
from modules.storage.in_memory import InMemoryStore
from modules.tests.models import TestResult


class PromptStackUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = InMemoryStore()

    def test_system_prompt_contains_non_overridable_redlines(self) -> None:
        system_prompt = get_system_prompt().lower()
        self.assertIn("never provide clinical diagnosis", system_prompt)
        self.assertIn("never provide medication", system_prompt)
        self.assertIn("stop normal coaching flow", system_prompt)

    def test_style_prompt_registry_returns_expected_styles(self) -> None:
        warm = get_style_prompt("warm_guide")
        rational = get_style_prompt("rational_analysis")
        deep = get_style_prompt("deep_exploration")
        mindful = get_style_prompt("mindfulness_guide")
        action = get_style_prompt("action_coach")
        self.assertIn("empathic", warm["prompt"].lower())
        self.assertIn("cbt", rational["prompt"].lower())
        self.assertIn("pattern", deep["prompt"].lower())
        self.assertIn("ground", mindful["prompt"].lower())
        self.assertIn("step", action["prompt"].lower())

    def test_context_prompt_includes_recent_memory(self) -> None:
        from modules.user.models import User

        self.store.save_user(User(user_id="u1", email="u1@example.com", locale="en-US"))
        memory = MemoryService(self.store)
        memory.index_summary("u1", "summary-1")
        memory.index_summary("u1", "summary-2")
        memory.index_summary("u1", "summary-3")
        memory.index_summary("u1", "summary-4")

        context = build_context_prompt(self.store, "u1")
        self.assertEqual(context["memory_summaries"], ["summary-2", "summary-3", "summary-4"])

    def test_context_prompt_adds_adhd_adaptation_fragment_for_high_asrs(self) -> None:
        from modules.user.models import User

        self.store.save_user(User(user_id="u1", email="u1@example.com", locale="en-US"))
        self.store.save_test_result(
            TestResult(
                result_id="asrs-high-1",
                user_id="u1",
                test_id="asrs",
                answers={"q1": 4},
                summary={
                    "total": 18,
                    "maxTotal": 24,
                    "level": "high",
                },
            )
        )

        context = build_context_prompt(self.store, "u1")
        self.assertEqual(context["neurodiversity_scores"]["asrs"]["level"], "high")
        fragments = context["neurodiversity_prompt_fragments"]
        self.assertIsInstance(fragments, list)
        self.assertTrue(any("not clinical diagnoses" in item.lower() for item in fragments))
        self.assertTrue(any("adhd-adapted coaching guidance" in item.lower() for item in fragments))

    def test_context_prompt_adds_asd_adaptation_fragment_for_high_aq10(self) -> None:
        from modules.user.models import User

        self.store.save_user(User(user_id="u1", email="u1@example.com", locale="en-US"))
        self.store.save_test_result(
            TestResult(
                result_id="aq10-high-1",
                user_id="u1",
                test_id="aq10",
                answers={"q1": 3},
                summary={
                    "total": 7,
                    "maxTotal": 10,
                    "level": "high",
                },
            )
        )

        context = build_context_prompt(self.store, "u1")
        self.assertEqual(context["neurodiversity_scores"]["aq10"]["level"], "high")
        fragments = context["neurodiversity_prompt_fragments"]
        self.assertIsInstance(fragments, list)
        self.assertTrue(any("asd-adapted coaching guidance" in item.lower() for item in fragments))

    def test_context_prompt_adds_hsp_adaptation_fragment_for_high_hsp(self) -> None:
        from modules.user.models import User

        self.store.save_user(User(user_id="u1", email="u1@example.com", locale="en-US"))
        self.store.save_test_result(
            TestResult(
                result_id="hsp-high-1",
                user_id="u1",
                test_id="hsp",
                answers={"q1": 6},
                summary={
                    "total": 5.2,
                    "maxTotal": 7,
                    "level": "high",
                },
            )
        )

        context = build_context_prompt(self.store, "u1")
        self.assertEqual(context["neurodiversity_scores"]["hsp"]["level"], "high")
        fragments = context["neurodiversity_prompt_fragments"]
        self.assertIsInstance(fragments, list)
        self.assertTrue(any("hsp-adapted coaching guidance" in item.lower() for item in fragments))


if __name__ == "__main__":
    unittest.main()
