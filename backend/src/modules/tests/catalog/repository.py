from typing import Dict

from modules.tests.definitions.catalog import CORE_TEST_DEFINITIONS
from modules.tests.models import TestDefinition


class TestCatalogRepository:
    def __init__(self) -> None:
        self._definitions: Dict[str, TestDefinition] = dict(CORE_TEST_DEFINITIONS)

    def list_tests(self) -> Dict[str, TestDefinition]:
        return dict(self._definitions)

    def get(self, test_id: str) -> TestDefinition:
        definition = self._definitions.get(test_id)
        if definition is None:
            raise ValueError(f"Unknown test_id: {test_id}")
        return definition
