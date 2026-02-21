from dataclasses import dataclass
from typing import Dict, List


@dataclass
class ProfessionalScaleReference:
    citation: str
    source_url: str

    def to_dict(self) -> dict:
        return {
            "citation": self.citation,
            "source_url": self.source_url,
        }


@dataclass
class ProfessionalScaleDefinition:
    scale_id: str
    names: Dict[str, str]
    item_count: int
    use_cases: Dict[str, str]
    scoring_logic: Dict[str, str]
    disclaimer: Dict[str, str]
    references: List[ProfessionalScaleReference]
    interactive_available: bool

    def to_dict(self) -> dict:
        return {
            "scale_id": self.scale_id,
            "names": dict(self.names),
            "item_count": self.item_count,
            "use_cases": dict(self.use_cases),
            "scoring_logic": dict(self.scoring_logic),
            "disclaimer": dict(self.disclaimer),
            "references": [item.to_dict() for item in self.references],
            "interactive_available": self.interactive_available,
        }


PROFESSIONAL_SCALE_LIBRARY: Dict[str, ProfessionalScaleDefinition] = {
    "who5": ProfessionalScaleDefinition(
        scale_id="who5",
        names={
            "en-US": "WHO-5 Well-Being Index",
            "zh-CN": "WHO-5 主观幸福感指数",
        },
        item_count=5,
        use_cases={
            "en-US": "Quick check of subjective well-being and emotional recovery trend over the past two weeks.",
            "zh-CN": "用于快速评估近两周主观幸福感与情绪恢复趋势。",
        },
        scoring_logic={
            "en-US": "Sum five items (0-5 each), then multiply total by 4 to get a 0-100 well-being score.",
            "zh-CN": "5 题各按 0-5 计分，原始总分乘以 4，得到 0-100 的幸福感得分。",
        },
        disclaimer={
            "en-US": "Screening only, not a medical diagnosis. If persistent distress exists, seek licensed professionals.",
            "zh-CN": "仅用于初筛，不构成医疗诊断。如持续困扰，建议咨询持证专业人士。",
        },
        references=[
            ProfessionalScaleReference(
                citation="Topp CW, et al. The WHO-5 Well-Being Index: a systematic review of the literature.",
                source_url="https://pubmed.ncbi.nlm.nih.gov/23629982/",
            ),
        ],
        interactive_available=True,
    ),
    "isi7": ProfessionalScaleDefinition(
        scale_id="isi7",
        names={
            "en-US": "Insomnia Severity Index (ISI-7)",
            "zh-CN": "ISI-7 失眠严重度指数",
        },
        item_count=7,
        use_cases={
            "en-US": "Assess perceived insomnia severity and daytime impact over the recent period.",
            "zh-CN": "评估近期失眠主观严重度及日间功能影响。",
        },
        scoring_logic={
            "en-US": "Seven items scored 0-4, total 0-28; higher scores indicate more severe insomnia symptoms.",
            "zh-CN": "7 题各按 0-4 计分，总分 0-28，分数越高表示失眠困扰越明显。",
        },
        disclaimer={
            "en-US": "Educational and screening use only. Not for independent medical diagnosis or treatment decisions.",
            "zh-CN": "仅用于教育与筛查，不可独立用于医疗诊断或治疗决策。",
        },
        references=[
            ProfessionalScaleReference(
                citation="Bastien CH, et al. Validation of the Insomnia Severity Index as an outcome measure.",
                source_url="https://pubmed.ncbi.nlm.nih.gov/11780815/",
            ),
        ],
        interactive_available=False,
    ),
    "ucla3": ProfessionalScaleDefinition(
        scale_id="ucla3",
        names={
            "en-US": "UCLA Loneliness Scale (3-item)",
            "zh-CN": "UCLA 孤独感量表（3题短版）",
        },
        item_count=3,
        use_cases={
            "en-US": "Rapid screening of loneliness risk in general population or primary care contexts.",
            "zh-CN": "用于一般人群或初级场景中的孤独感风险快速筛查。",
        },
        scoring_logic={
            "en-US": "Three items scored 1-3, total 3-9; higher scores indicate stronger loneliness tendency.",
            "zh-CN": "3 题各按 1-3 计分，总分 3-9，分数越高表示孤独感倾向越高。",
        },
        disclaimer={
            "en-US": "This is a non-diagnostic social well-being screener and should be interpreted with context.",
            "zh-CN": "该量表为非诊断性社会福祉筛查工具，需结合情境解读。",
        },
        references=[
            ProfessionalScaleReference(
                citation="Hughes ME, et al. A short scale for measuring loneliness in large surveys.",
                source_url="https://pubmed.ncbi.nlm.nih.gov/18504506/",
            ),
        ],
        interactive_available=False,
    ),
    "swls5": ProfessionalScaleDefinition(
        scale_id="swls5",
        names={
            "en-US": "Satisfaction With Life Scale (SWLS)",
            "zh-CN": "生活满意度量表（SWLS）",
        },
        item_count=5,
        use_cases={
            "en-US": "Track global life satisfaction as a complement to symptom-focused assessments.",
            "zh-CN": "用于补充症状量表，追踪整体生活满意度变化。",
        },
        scoring_logic={
            "en-US": "Five items scored 1-7, total 5-35; higher scores reflect greater life satisfaction.",
            "zh-CN": "5 题各按 1-7 计分，总分 5-35，分数越高表示生活满意度越高。",
        },
        disclaimer={
            "en-US": "Not a diagnosis tool. Use as a self-reflection indicator with longitudinal context.",
            "zh-CN": "不用于临床诊断。建议作为长期自我观察指标解读。",
        },
        references=[
            ProfessionalScaleReference(
                citation="Diener E, et al. The Satisfaction With Life Scale.",
                source_url="https://pubmed.ncbi.nlm.nih.gov/16367493/",
            ),
        ],
        interactive_available=False,
    ),
    "rses10": ProfessionalScaleDefinition(
        scale_id="rses10",
        names={
            "en-US": "Rosenberg Self-Esteem Scale (RSES)",
            "zh-CN": "罗森伯格自尊量表（RSES）",
        },
        item_count=10,
        use_cases={
            "en-US": "Measure global self-esteem level and monitor confidence-related change over time.",
            "zh-CN": "用于评估总体自尊水平，并追踪信心相关变化。",
        },
        scoring_logic={
            "en-US": "Ten items scored on a 4-point scale with reverse items; total 10-40 after recoding.",
            "zh-CN": "10 题采用 4 点计分并含反向题，反向换算后总分 10-40。",
        },
        disclaimer={
            "en-US": "Provides educational self-esteem insight and is not a substitute for clinical evaluation.",
            "zh-CN": "用于教育性自我洞察，不能替代临床评估。",
        },
        references=[
            ProfessionalScaleReference(
                citation="Rosenberg M. Society and the adolescent self-image.",
                source_url="https://psycnet.apa.org/record/1966-35026-000",
            ),
        ],
        interactive_available=False,
    ),
    "auditc3": ProfessionalScaleDefinition(
        scale_id="auditc3",
        names={
            "en-US": "AUDIT-C Alcohol Use Screen",
            "zh-CN": "AUDIT-C 酒精使用筛查",
        },
        item_count=3,
        use_cases={
            "en-US": "Brief screening for potentially risky alcohol consumption patterns.",
            "zh-CN": "用于快速筛查潜在风险性饮酒模式。",
        },
        scoring_logic={
            "en-US": "Three items scored 0-4, total 0-12; higher scores indicate greater alcohol-use risk.",
            "zh-CN": "3 题各按 0-4 计分，总分 0-12，分数越高提示饮酒风险越高。",
        },
        disclaimer={
            "en-US": "Screening support only. Positive screens should be followed by professional assessment.",
            "zh-CN": "仅作筛查支持。阳性结果需由专业人员进一步评估。",
        },
        references=[
            ProfessionalScaleReference(
                citation="Bush K, et al. The AUDIT Alcohol Consumption Questions (AUDIT-C).",
                source_url="https://pubmed.ncbi.nlm.nih.gov/9230213/",
            ),
        ],
        interactive_available=False,
    ),
}


def list_professional_scales() -> dict:
    return {scale_id: definition.to_dict() for scale_id, definition in PROFESSIONAL_SCALE_LIBRARY.items()}
