from dataclasses import dataclass
from typing import Dict, List

from modules.assessment.catalog.scales import (
    CDRISC10,
    CSSRS,
    GAD7,
    ISI7,
    PHQ9,
    PHQ15,
    PSS10,
    SCL90,
    SWLS5,
    UCLA3,
    WHO5,
)

STANDARD_DISCLAIMER = {
    "en-US": "Educational screening only. This is not a diagnosis. If safety risk exists, seek local emergency or professional support immediately.",
    "zh-CN": "仅用于心理教育与初步筛查，不构成诊断。如存在安全风险，请立即联系当地紧急服务或专业机构。",
}


@dataclass
class ClinicalScaleDefinition:
    scale_id: str
    display_name: str
    display_name_i18n: Dict[str, str]
    item_count: int
    cadence_days: int
    required_for_triage: bool
    theory_reference: str
    source_citation: str
    use_case_i18n: Dict[str, str]
    scoring_method: str
    disclaimer_i18n: Dict[str, str]
    supported_input: List[str]

    def to_dict(self) -> dict:
        return {
            "scale_id": self.scale_id,
            "display_name": self.display_name,
            "display_name_i18n": dict(self.display_name_i18n),
            "item_count": self.item_count,
            "cadence_days": self.cadence_days,
            "required_for_triage": self.required_for_triage,
            "theory_reference": self.theory_reference,
            "source_citation": self.source_citation,
            "use_case_i18n": dict(self.use_case_i18n),
            "scoring_method": self.scoring_method,
            "disclaimer_i18n": dict(self.disclaimer_i18n),
            "supported_input": list(self.supported_input),
        }


CLINICAL_SCALE_DEFINITIONS: Dict[str, ClinicalScaleDefinition] = {
    PHQ9: ClinicalScaleDefinition(
        scale_id=PHQ9,
        display_name="PHQ-9 Depression Screening",
        display_name_i18n={"en-US": "PHQ-9 Depression Screening", "zh-CN": "PHQ-9 抑郁筛查"},
        item_count=9,
        cadence_days=30,
        required_for_triage=True,
        theory_reference="Patient Health Questionnaire-9 (PHQ-9)",
        source_citation="Kroenke K, Spitzer RL, Williams JBW. J Gen Intern Med. 2001;16(9):606-613.",
        use_case_i18n={
            "en-US": "Screens depressive symptom severity during the past 2 weeks.",
            "zh-CN": "用于筛查过去两周抑郁相关症状的严重程度。",
        },
        scoring_method="0-3 each item, total 0-27; cutoffs commonly at 5/10/15/20.",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_3_list"],
    ),
    GAD7: ClinicalScaleDefinition(
        scale_id=GAD7,
        display_name="GAD-7 Anxiety Screening",
        display_name_i18n={"en-US": "GAD-7 Anxiety Screening", "zh-CN": "GAD-7 焦虑筛查"},
        item_count=7,
        cadence_days=30,
        required_for_triage=True,
        theory_reference="Generalized Anxiety Disorder-7 (GAD-7)",
        source_citation="Spitzer RL, Kroenke K, Williams JBW, Lowe B. Arch Intern Med. 2006;166(10):1092-1097.",
        use_case_i18n={
            "en-US": "Screens generalized anxiety symptom burden during the past 2 weeks.",
            "zh-CN": "用于筛查过去两周广泛性焦虑症状负担。",
        },
        scoring_method="0-3 each item, total 0-21; cutoffs commonly at 5/10/15.",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_3_list"],
    ),
    PSS10: ClinicalScaleDefinition(
        scale_id=PSS10,
        display_name="PSS-10 Perceived Stress",
        display_name_i18n={"en-US": "PSS-10 Perceived Stress", "zh-CN": "PSS-10 压力量表"},
        item_count=10,
        cadence_days=30,
        required_for_triage=True,
        theory_reference="Perceived Stress Scale-10 (PSS-10)",
        source_citation="Cohen S, Kamarck T, Mermelstein R. J Health Soc Behav. 1983;24(4):385-396.",
        use_case_i18n={
            "en-US": "Evaluates how unpredictable, uncontrollable, and overloaded life feels in the past month.",
            "zh-CN": "用于评估过去一个月中个体对不可预测、不可控与负荷过高的主观感受。",
        },
        scoring_method="0-4 each item; reverse-score items 4/5/7/8; total 0-40.",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_4_list"],
    ),
    CSSRS: ClinicalScaleDefinition(
        scale_id=CSSRS,
        display_name="C-SSRS Screener",
        display_name_i18n={"en-US": "C-SSRS Screener", "zh-CN": "C-SSRS 安全风险筛查"},
        item_count=6,
        cadence_days=30,
        required_for_triage=True,
        theory_reference="Columbia-Suicide Severity Rating Scale (Screener)",
        source_citation="Posner K, et al. Am J Psychiatry. 2011;168(12):1266-1277.",
        use_case_i18n={
            "en-US": "Rapidly detects suicidal ideation/behavior risk and triggers safety workflow.",
            "zh-CN": "用于快速识别自伤/自杀意念与行为风险并触发安全流程。",
        },
        scoring_method="Any positive item is treated as safety-positive and triggers risk protocol.",
        disclaimer_i18n={
            "en-US": "Safety triage only. Positive responses require immediate professional evaluation.",
            "zh-CN": "仅用于安全分流。若出现阳性结果，应立即转介专业评估与支持。",
        },
        supported_input=["boolean_list", "boolean_map"],
    ),
    SCL90: ClinicalScaleDefinition(
        scale_id=SCL90,
        display_name="SCL-90-R Broad Symptom Screening",
        display_name_i18n={"en-US": "SCL-90-R Broad Symptom Screening", "zh-CN": "SCL-90 广泛症状筛查"},
        item_count=90,
        cadence_days=90,
        required_for_triage=False,
        theory_reference="Symptom Checklist-90-Revised (SCL-90-R)",
        source_citation="Derogatis LR. SCL-90-R Manual. 1977/1994 editions.",
        use_case_i18n={
            "en-US": "Provides broad symptom-domain screening across multiple psychological distress dimensions.",
            "zh-CN": "用于跨多维心理症状的广泛筛查，观察总体困扰水平。",
        },
        scoring_method="0-4 each item; global index is average score of all items (or dimension means).",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_4_list_90", "dimension_score_map"],
    ),
    WHO5: ClinicalScaleDefinition(
        scale_id=WHO5,
        display_name="WHO-5 Well-Being Index",
        display_name_i18n={"en-US": "WHO-5 Well-Being Index", "zh-CN": "WHO-5 幸福感指数"},
        item_count=5,
        cadence_days=30,
        required_for_triage=False,
        theory_reference="WHO-5 Well-Being Index",
        source_citation="Topp CW, Ostergaard SD, Sondergaard S, Bech P. Psychother Psychosom. 2015;84(3):167-176.",
        use_case_i18n={
            "en-US": "Tracks positive emotional well-being and functioning over the recent two weeks.",
            "zh-CN": "用于追踪近两周积极情绪状态与功能感受。",
        },
        scoring_method="0-5 each item, raw 0-25, transformed index = raw*4 (0-100).",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_5_list"],
    ),
    ISI7: ClinicalScaleDefinition(
        scale_id=ISI7,
        display_name="Insomnia Severity Index (ISI-7)",
        display_name_i18n={"en-US": "Insomnia Severity Index (ISI-7)", "zh-CN": "ISI-7 失眠严重度指数"},
        item_count=7,
        cadence_days=30,
        required_for_triage=False,
        theory_reference="Insomnia Severity Index (ISI)",
        source_citation="Bastien CH, Vallieres A, Morin CM. Sleep Med. 2001;2(4):297-307.",
        use_case_i18n={
            "en-US": "Assesses perceived insomnia severity, sleep dissatisfaction, and daytime impact.",
            "zh-CN": "用于评估主观失眠严重度、睡眠满意度与白天功能影响。",
        },
        scoring_method="0-4 each item, total 0-28; cutoffs 0-7/8-14/15-21/22-28.",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_4_list"],
    ),
    SWLS5: ClinicalScaleDefinition(
        scale_id=SWLS5,
        display_name="Satisfaction With Life Scale (SWLS-5)",
        display_name_i18n={"en-US": "Satisfaction With Life Scale (SWLS-5)", "zh-CN": "SWLS-5 生活满意度量表"},
        item_count=5,
        cadence_days=60,
        required_for_triage=False,
        theory_reference="Satisfaction With Life Scale (SWLS)",
        source_citation="Diener E, Emmons RA, Larsen RJ, Griffin S. J Pers Assess. 1985;49(1):71-75.",
        use_case_i18n={
            "en-US": "Measures global cognitive evaluation of one's life satisfaction.",
            "zh-CN": "用于评估个体对整体生活状况的认知性满意度。",
        },
        scoring_method="1-7 each item (stored as 0-6 + 1), total 5-35; higher indicates greater life satisfaction.",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_6_list"],
    ),
    UCLA3: ClinicalScaleDefinition(
        scale_id=UCLA3,
        display_name="UCLA Loneliness Scale (3-item)",
        display_name_i18n={"en-US": "UCLA Loneliness Scale (3-item)", "zh-CN": "UCLA 孤独感量表（3题）"},
        item_count=3,
        cadence_days=60,
        required_for_triage=False,
        theory_reference="UCLA Loneliness Scale (3-item short form)",
        source_citation="Hughes ME, Waite LJ, Hawkley LC, Cacioppo JT. Res Aging. 2004;26(6):655-672.",
        use_case_i18n={
            "en-US": "Screens brief social disconnection and loneliness-related distress.",
            "zh-CN": "用于快速筛查社交疏离体验与孤独相关困扰。",
        },
        scoring_method="0-2 each item, total 0-6; higher indicates stronger loneliness signal.",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_2_list"],
    ),
    CDRISC10: ClinicalScaleDefinition(
        scale_id=CDRISC10,
        display_name="CD-RISC-10 Resilience Scale",
        display_name_i18n={"en-US": "CD-RISC-10 Resilience Scale", "zh-CN": "CD-RISC-10 心理韧性量表"},
        item_count=10,
        cadence_days=60,
        required_for_triage=False,
        theory_reference="Connor-Davidson Resilience Scale 10-item (CD-RISC-10)",
        source_citation="Campbell-Sills L, Stein MB. J Trauma Stress. 2007;20(6):1019-1028.",
        use_case_i18n={
            "en-US": "Measures perceived resilience and recovery capacity under stress.",
            "zh-CN": "用于评估个体在压力下的心理韧性与恢复能力。",
        },
        scoring_method="0-4 each item, total 0-40; higher indicates stronger resilience resources.",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_4_list"],
    ),
    PHQ15: ClinicalScaleDefinition(
        scale_id=PHQ15,
        display_name="PHQ-15 Somatic Symptom Scale",
        display_name_i18n={"en-US": "PHQ-15 Somatic Symptom Scale", "zh-CN": "PHQ-15 躯体症状量表"},
        item_count=15,
        cadence_days=45,
        required_for_triage=False,
        theory_reference="Patient Health Questionnaire-15 (PHQ-15)",
        source_citation="Kroenke K, Spitzer RL, Williams JBW. Psychosom Med. 2002;64(2):258-266.",
        use_case_i18n={
            "en-US": "Screens common somatic symptom burden and functional discomfort.",
            "zh-CN": "用于筛查常见躯体症状负担与相关功能不适。",
        },
        scoring_method="0-2 each item, total 0-30; typical cutoffs 5/10/15 for mild/moderate/severe.",
        disclaimer_i18n=STANDARD_DISCLAIMER,
        supported_input=["likert_0_2_list"],
    ),
}
