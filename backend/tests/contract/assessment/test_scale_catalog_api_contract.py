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

    def test_score_scale_contract_for_all_supported_scales(self) -> None:
        cases = [
            (
                {
                    "scale_id": "gad7",
                    "answers": [1] * 7,
                },
                ("score", 7),
            ),
            (
                {
                    "scale_id": "pss10",
                    "answers": [2] * 10,
                },
                ("score", 20),
            ),
            (
                {
                    "scale_id": "cssrs",
                    "answers": {"q1": False, "q2": True},
                },
                ("positive", True),
            ),
            (
                {
                    "scale_id": "scl90",
                    "answers": [2] * 90,
                },
                ("global_index", 2.0),
            ),
            (
                {
                    "scale_id": "scl90",
                    "answers": {
                        "somatization": 1,
                        "obsessive_compulsive": 1,
                        "interpersonal_sensitivity": 1,
                        "depression": 2,
                        "anxiety": 2,
                        "hostility": 1,
                        "phobic_anxiety": 1,
                        "paranoid_ideation": 1,
                        "psychoticism": 1,
                    },
                },
                ("moderate_or_above", False),
            ),
        ]

        for payload, (expected_key, expected_value) in cases:
            status, body = self.api.post_score_scale(payload)
            self.assertEqual(status, 200)
            self.assertEqual(body["data"][expected_key], expected_value)


if __name__ == "__main__":
    unittest.main()
