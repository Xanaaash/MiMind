from dataclasses import dataclass
from typing import Dict, List

from modules.assessment.catalog.scales import CSSRS, GAD7, PHQ9, PSS10, SCL90, WHO5


@dataclass
class ClinicalScaleDefinition:
    scale_id: str
    display_name: str
    item_count: int
    cadence_days: int
    required_for_triage: bool
    theory_reference: str
    supported_input: List[str]

    def to_dict(self) -> dict:
        return {
            "scale_id": self.scale_id,
            "display_name": self.display_name,
            "item_count": self.item_count,
            "cadence_days": self.cadence_days,
            "required_for_triage": self.required_for_triage,
            "theory_reference": self.theory_reference,
            "supported_input": list(self.supported_input),
        }


CLINICAL_SCALE_DEFINITIONS: Dict[str, ClinicalScaleDefinition] = {
    PHQ9: ClinicalScaleDefinition(
        scale_id=PHQ9,
        display_name="PHQ-9 Depression Screening",
        item_count=9,
        cadence_days=30,
        required_for_triage=True,
        theory_reference="Patient Health Questionnaire-9",
        supported_input=["likert_0_3_list"],
    ),
    GAD7: ClinicalScaleDefinition(
        scale_id=GAD7,
        display_name="GAD-7 Anxiety Screening",
        item_count=7,
        cadence_days=30,
        required_for_triage=True,
        theory_reference="Generalized Anxiety Disorder-7",
        supported_input=["likert_0_3_list"],
    ),
    PSS10: ClinicalScaleDefinition(
        scale_id=PSS10,
        display_name="PSS-10 Perceived Stress",
        item_count=10,
        cadence_days=30,
        required_for_triage=True,
        theory_reference="Perceived Stress Scale-10",
        supported_input=["likert_0_4_list"],
    ),
    CSSRS: ClinicalScaleDefinition(
        scale_id=CSSRS,
        display_name="C-SSRS Screener",
        item_count=6,
        cadence_days=30,
        required_for_triage=True,
        theory_reference="Columbia-Suicide Severity Rating Scale (Screener)",
        supported_input=["boolean_list", "boolean_map"],
    ),
    SCL90: ClinicalScaleDefinition(
        scale_id=SCL90,
        display_name="SCL-90-R Broad Symptom Screening",
        item_count=90,
        cadence_days=90,
        required_for_triage=False,
        theory_reference="Symptom Checklist-90-Revised",
        supported_input=["likert_0_4_list_90", "dimension_score_map"],
    ),
    WHO5: ClinicalScaleDefinition(
        scale_id=WHO5,
        display_name="WHO-5 Well-Being Index",
        item_count=5,
        cadence_days=30,
        required_for_triage=False,
        theory_reference="WHO-5 World Health Organization Well-Being Index",
        supported_input=["likert_0_5_list"],
    ),
}
