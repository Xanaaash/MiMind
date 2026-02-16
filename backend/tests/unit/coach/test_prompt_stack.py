import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.memory.service import MemoryService
from modules.prompt.context.builder import build_context_prompt
from modules.prompt.styles.registry import get_style_prompt
from modules.prompt.system.prompt import get_system_prompt
from modules.storage.in_memory import InMemoryStore


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
        self.assertIn("empathic", warm["prompt"].lower())
        self.assertIn("cbt", rational["prompt"].lower())

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


if __name__ == "__main__":
    unittest.main()
