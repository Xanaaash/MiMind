import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.assessment.scoring_service import score_scl90, score_single_scale, score_submission
from modules.triage.models import TriageChannel
from modules.triage.triage_service import TriageService


class SCL90ScaleSupportTests(unittest.TestCase):
    def test_scl90_dimension_scoring(self) -> None:
        global_index, dimensions = score_scl90(
            {
                "somatization": 2,
                "obsessive_compulsive": 2,
                "interpersonal_sensitivity": 1,
                "depression": 3,
                "anxiety": 2,
                "hostility": 1,
                "phobic_anxiety": 0,
                "paranoid_ideation": 1,
                "psychoticism": 0,
            }
        )

        self.assertAlmostEqual(global_index, 1.333, places=3)
        self.assertIsNotNone(dimensions)
        self.assertIn("depression", dimensions)

    def test_scl90_list_scoring(self) -> None:
        global_index, dimensions = score_scl90([2] * 90)
        self.assertEqual(global_index, 2.0)
        self.assertIsNone(dimensions)

    def test_submission_carries_scl90_and_affects_triage(self) -> None:
        responses = {
            "phq9": [0] * 9,
            "gad7": [0] * 7,
            "pss10": [0] * 10,
            "cssrs": {"q1": False, "q2": False},
            "scl90": [3] * 90,
        }
        scores = score_submission(responses)
        self.assertTrue(scores.scl90_moderate_or_above)

        triage = TriageService().evaluate(scores)
        self.assertEqual(triage.channel, TriageChannel.YELLOW)

    def test_score_single_scale_api_shape(self) -> None:
        result = score_single_scale("scl90", [2] * 90)
        self.assertEqual(result["scale_id"], "scl90")
        self.assertTrue(result["moderate_or_above"])


if __name__ == "__main__":
    unittest.main()
