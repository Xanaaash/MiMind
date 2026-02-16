from typing import Any, Dict, Optional, Tuple

from modules.compliance.data_governance_service import DataGovernanceService
from modules.storage.in_memory import InMemoryStore


class DataGovernanceAPI:
    def __init__(self, store: Optional[InMemoryStore] = None) -> None:
        self._store = store or InMemoryStore()
        self._service = DataGovernanceService(self._store)

    def get_export(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._service.export_user_bundle(user_id=user_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}

    def post_erase(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        try:
            data = self._service.erase_user_bundle(user_id=user_id)
            return 200, {"data": data}
        except ValueError as error:
            return 400, {"error": str(error)}
