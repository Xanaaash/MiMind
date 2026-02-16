from modules.assessment.catalog.registry import CLINICAL_SCALE_DEFINITIONS
from modules.assessment.catalog.question_bank import get_scale_question_bank


class ClinicalScaleCatalogService:
    def list_scales(self) -> dict:
        return {scale_id: self._build_catalog_item(scale_id) for scale_id in CLINICAL_SCALE_DEFINITIONS}

    def get_scale(self, scale_id: str) -> dict:
        return self._build_catalog_item(scale_id)

    def _build_catalog_item(self, scale_id: str) -> dict:
        definition = CLINICAL_SCALE_DEFINITIONS.get(scale_id)
        if definition is None:
            raise ValueError(f"Unknown scale_id: {scale_id}")

        item = definition.to_dict()
        item["question_bank"] = get_scale_question_bank(scale_id)
        return item
