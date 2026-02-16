from modules.tests.models import TestResult


class PairingService:
    def build_pairing_report(self, left: TestResult, right: TestResult) -> dict:
        if left.test_id != right.test_id:
            return {
                "compatibility_score": 50,
                "compatibility_level": "mixed",
                "notes": "Different test frameworks were compared; treat this as exploratory feedback.",
            }

        left_key = self._primary_label(left)
        right_key = self._primary_label(right)

        if left_key and right_key and left_key == right_key:
            return {
                "compatibility_score": 86,
                "compatibility_level": "high",
                "notes": "You share similar psychological patterns in this test.",
            }

        if left_key and right_key and left_key[:1] == right_key[:1]:
            return {
                "compatibility_score": 70,
                "compatibility_level": "medium",
                "notes": "You overlap in one major trait while differing elsewhere.",
            }

        return {
            "compatibility_score": 58,
            "compatibility_level": "developing",
            "notes": "Differences may be complementary if discussed with curiosity.",
        }

    @staticmethod
    def _primary_label(result: TestResult) -> str:
        for key in ("type", "primary_style", "dominant_trait"):
            if key in result.summary:
                return str(result.summary[key])
        return ""
