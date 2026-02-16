import uuid
from typing import Dict

from modules.cards.service import ShareCardService
from modules.storage.in_memory import InMemoryStore
from modules.tests.catalog.repository import TestCatalogRepository
from modules.tests.catalog.question_bank import get_test_question_bank
from modules.tests.models import TestResult
from modules.tests.pairing.service import PairingService
from modules.tests.report.service import TestReportService
from modules.tests.scoring.service import score_test


class InteractiveTestsService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store
        self._catalog = TestCatalogRepository()
        self._report_service = TestReportService()
        self._share_card_service = ShareCardService()
        self._pairing_service = PairingService()

    def list_catalog(self) -> Dict[str, dict]:
        return {test_id: self._build_catalog_item(test_id) for test_id in self._catalog.list_tests()}

    def get_catalog_item(self, test_id: str) -> dict:
        return self._build_catalog_item(test_id)

    def submit_test(self, user_id: str, test_id: str, answers: dict) -> dict:
        if self._store.get_user(user_id) is None:
            raise ValueError("Unknown user_id")

        definition = self._catalog.get(test_id)
        summary = score_test(definition.scoring_type, answers)

        result = TestResult(
            result_id=str(uuid.uuid4()),
            user_id=user_id,
            test_id=test_id,
            answers=answers,
            summary=summary,
        )
        self._store.save_test_result(result)
        return result.to_dict()

    def get_report(self, user_id: str, result_id: str, subscription_active: bool) -> dict:
        result = self._require_owned_result(user_id, result_id)
        definition = self._catalog.get(result.test_id)
        return self._report_service.build_report(definition, result, subscription_active)

    def get_share_card(self, user_id: str, result_id: str) -> dict:
        result = self._require_owned_result(user_id, result_id)
        definition = self._catalog.get(result.test_id)
        return self._share_card_service.build_share_card(definition, result)

    def get_pairing_report(self, left_result_id: str, right_result_id: str) -> dict:
        left = self._store.get_test_result(left_result_id)
        right = self._store.get_test_result(right_result_id)
        if left is None or right is None:
            raise ValueError("Both results must exist for pairing")
        return self._pairing_service.build_pairing_report(left, right)

    def _require_owned_result(self, user_id: str, result_id: str) -> TestResult:
        result = self._store.get_test_result(result_id)
        if result is None:
            raise ValueError("Result not found")
        if result.user_id != user_id:
            raise ValueError("Result does not belong to user")
        return result

    def _build_catalog_item(self, test_id: str) -> dict:
        definition = self._catalog.get(test_id)
        data = definition.to_catalog_dict()
        data["question_bank"] = get_test_question_bank(test_id)
        return data
