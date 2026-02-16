import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.prompt_endpoints import PromptRegistryAPI
from modules.prompt.registry.service import PromptRegistryService


class PromptRegistryAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = PromptRegistryService(default_active_version="2026.02.1")
        self.api = PromptRegistryAPI(registry=self.registry)

    def test_list_and_active_contract(self) -> None:
        list_status, list_body = self.api.get_packs()
        self.assertEqual(list_status, 200)
        self.assertIn("2026.02.0", list_body["data"])
        self.assertIn("2026.02.1", list_body["data"])

        active_status, active_body = self.api.get_active()
        self.assertEqual(active_status, 200)
        self.assertEqual(active_body["data"]["active_version"], "2026.02.1")

    def test_activate_contract(self) -> None:
        status, body = self.api.post_activate({"version": "2026.02.0"})
        self.assertEqual(status, 200)
        self.assertEqual(body["data"]["active_version"], "2026.02.0")

    def test_activate_invalid_version_contract(self) -> None:
        status, body = self.api.post_activate({"version": "invalid"})
        self.assertEqual(status, 400)
        self.assertIn("Unknown prompt version", body["error"])


if __name__ == "__main__":
    unittest.main()
