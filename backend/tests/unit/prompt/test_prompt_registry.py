import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.prompt.registry.runtime import get_prompt_registry, reset_prompt_registry_for_tests
from modules.prompt.registry.service import PromptRegistryService
from modules.prompt.styles.registry import get_style_prompt
from modules.prompt.system.prompt import get_system_prompt


class PromptRegistryUnitTests(unittest.TestCase):
    def tearDown(self) -> None:
        reset_prompt_registry_for_tests()

    def test_registry_list_and_activate(self) -> None:
        service = PromptRegistryService()
        packs = service.list_packs()
        self.assertIn("2026.02.0", packs)
        self.assertIn("2026.02.1", packs)

        active_before = service.get_active_version()
        self.assertEqual(active_before, "2026.02.1")

        service.activate("2026.02.0")
        self.assertEqual(service.get_active_version(), "2026.02.0")

    def test_registry_unknown_version_raises(self) -> None:
        service = PromptRegistryService()
        with self.assertRaises(ValueError):
            service.activate("2099.01.0")

    def test_runtime_accessors_follow_active_version(self) -> None:
        registry = get_prompt_registry()
        registry.activate("2026.02.0")
        style_old = get_style_prompt("warm_guide")
        self.assertIn("avoid directive language", style_old["prompt"])
        deep_old = get_style_prompt("deep_exploration")
        self.assertIn("pattern", deep_old["prompt"].lower())

        registry.activate("2026.02.1")
        style_new = get_style_prompt("warm_guide")
        self.assertIn("gentle next-step question", style_new["prompt"])
        mindful_new = get_style_prompt("mindfulness_guide")
        action_new = get_style_prompt("action_coach")
        self.assertIn("ground", mindful_new["prompt"].lower())
        self.assertIn("step", action_new["prompt"].lower())

        system_prompt = get_system_prompt().lower()
        self.assertIn("never provide clinical diagnosis", system_prompt)
        self.assertIn("stop normal coaching flow", system_prompt)

    def test_invalid_default_version_falls_back_to_latest(self) -> None:
        service = PromptRegistryService(default_active_version="1999.01.0")
        self.assertEqual(service.get_active_version(), "2026.02.1")


if __name__ == "__main__":
    unittest.main()
