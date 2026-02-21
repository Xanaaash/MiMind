from typing import Any, Dict, Optional, Tuple

from modules.assessment.catalog.professional_library import list_professional_scales
from modules.assessment.catalog.service import ClinicalScaleCatalogService
from modules.assessment.scoring_service import score_single_scale


class ClinicalScalesAPI:
    def __init__(self, catalog_service: Optional[ClinicalScaleCatalogService] = None) -> None:
        self._catalog = catalog_service or ClinicalScaleCatalogService()

    def get_catalog(self) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": self._catalog.list_scales()}

    def get_professional_library(self) -> Tuple[int, Dict[str, Any]]:
        return 200, {"data": list_professional_scales()}

    def post_score_scale(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            scale_id = str(payload.get("scale_id", "")).strip()
            answers = payload.get("answers")
            if not scale_id:
                raise ValueError("scale_id is required")
            if answers is None:
                raise ValueError("answers is required")

            score = score_single_scale(scale_id, answers)
            return 200, {"data": score}
        except ValueError as error:
            return 400, {"error": str(error)}
