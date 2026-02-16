import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from fastapi.testclient import TestClient

from app import app


class FastAPIScaleEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_scales_catalog_http(self) -> None:
        response = self.client.get("/api/scales/catalog")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("scl90", payload)
        self.assertIn("question_bank", payload["phq9"])
        self.assertEqual(len(payload["scl90"]["question_bank"]["questions"]), 90)

    def test_single_scale_score_http(self) -> None:
        response = self.client.post(
            "/api/scales/score",
            json={
                "scale_id": "scl90",
                "answers": [2] * 90,
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["global_index"], 2.0)

    def test_cssrs_scale_score_http(self) -> None:
        response = self.client.post(
            "/api/scales/score",
            json={
                "scale_id": "cssrs",
                "answers": {"q1": False, "q2": True},
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["positive"])


if __name__ == "__main__":
    unittest.main()
