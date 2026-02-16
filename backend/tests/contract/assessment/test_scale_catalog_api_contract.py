import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.scales_endpoints import ClinicalScalesAPI


class ScaleCatalogAPIContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = ClinicalScalesAPI()

    def test_catalog_contains_core_and_extended_scales(self) -> None:
        status, body = self.api.get_catalog()
        self.assertEqual(status, 200)

        data = body["data"]
        self.assertIn("phq9", data)
        self.assertIn("gad7", data)
        self.assertIn("cssrs", data)
        self.assertIn("scl90", data)
        self.assertEqual(data["scl90"]["cadence_days"], 90)

    def test_score_scale_contract(self) -> None:
        status, body = self.api.post_score_scale(
            {
                "scale_id": "phq9",
                "answers": [1] * 9,
            }
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["data"]["score"], 9)


if __name__ == "__main__":
    unittest.main()
