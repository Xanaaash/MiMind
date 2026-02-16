from typing import Any, Dict, Optional, Tuple

from modules.storage.in_memory import InMemoryStore
from modules.tests.service import InteractiveTestsService


class InteractiveTestsAPI:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self._store = store or InMemoryStore()
        self._service = InteractiveTestsService(self._store)

    @property
    def store(self) -> InMemoryStore:
        return self._store

    def get_catalog(self) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._service.list_catalog()}

    def get_catalog_item(self, test_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            return 200, {"data": self._service.get_catalog_item(test_id)}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_submit(self, user_id: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            test_id = str(payload.get("test_id", "")).strip()
            answers = payload.get("answers")
            if not test_id:
                raise ValueError("test_id is required")
            if not isinstance(answers, dict):
                raise ValueError("answers is required")

            data = self._service.submit_test(user_id=user_id, test_id=test_id, answers=answers)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def get_report(self, user_id: str, result_id: str, subscription_active: bool) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._service.get_report(
                user_id=user_id,
                result_id=result_id,
                subscription_active=subscription_active,
            )
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_share_card(self, user_id: str, result_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._service.get_share_card(user_id=user_id, result_id=result_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_pairing(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            left_result_id = str(payload.get("left_result_id", "")).strip()
            right_result_id = str(payload.get("right_result_id", "")).strip()
            if not left_result_id or not right_result_id:
                raise ValueError("left_result_id and right_result_id are required")

            data = self._service.get_pairing_report(left_result_id=left_result_id, right_result_id=right_result_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}
