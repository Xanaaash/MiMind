import unittest

from backend.tests.bootstrap import configure_import_path

configure_import_path()

from modules.api.endpoints import OnboardingAPI
from modules.api.tests_endpoints import InteractiveTestsAPI
from modules.onboarding.service import OnboardingService
from modules.storage.in_memory import InMemoryStore
from modules.tests.report.service import FORBIDDEN_REPORT_PHRASES


class ReportLanguageSafetyTests(unittest.TestCase):
    def test_report_does_not_include_diagnostic_language(self) -> None:
        store = InMemoryStore()
        onboarding_api = OnboardingAPI(service=OnboardingService(store))
        tests_api = InteractiveTestsAPI(store=store)

        _, register_body = onboarding_api.post_register(
            {
                "email": "safe-report@example.com",
                "locale": "en-US",
                "policy_version": "2026.02",
            }
        )
        user_id = register_body["data"]["user_id"]

        _, submit_body = tests_api.post_submit(
            user_id=user_id,
            payload={
                "test_id": "big5",
                "answers": {
                    "O": 82,
                    "C": 67,
                    "E": 51,
                    "A": 74,
                    "N": 29,
                },
            },
        )

        result_id = submit_body["data"]["result_id"]
        report_status, report_body = tests_api.get_report(
            user_id=user_id,
            result_id=result_id,
            subscription_active=True,
        )

        self.assertEqual(report_status, 200)
        report_text = str(report_body["data"]).lower()
        for phrase in FORBIDDEN_REPORT_PHRASES:
            self.assertNotIn(phrase, report_text)


if __name__ == "__main__":
    unittest.main()
