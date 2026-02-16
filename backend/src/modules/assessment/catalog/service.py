from modules.assessment.catalog.registry import CLINICAL_SCALE_DEFINITIONS


class ClinicalScaleCatalogService:
    def list_scales(self) -> dict:
        return {
            scale_id: definition.to_dict()
            for scale_id, definition in CLINICAL_SCALE_DEFINITIONS.items()
        }

    def get_scale(self, scale_id: str) -> dict:
        definition = CLINICAL_SCALE_DEFINITIONS.get(scale_id)
        if definition is None:
            raise ValueError(f"Unknown scale_id: {scale_id}")
        return definition.to_dict()
