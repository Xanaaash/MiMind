import uuid

from modules.compliance.models import ConsentRecord
from modules.storage.in_memory import InMemoryStore


class ComplianceService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def capture_consent(self, user_id: str, policy_version: str) -> ConsentRecord:
        if not user_id:
            raise ValueError("user_id is required")
        if not policy_version:
            raise ValueError("policy_version is required")

        consent = ConsentRecord(
            consent_id=str(uuid.uuid4()),
            user_id=user_id,
            policy_version=policy_version,
        )
        self._store.save_consent(consent)
        return consent
