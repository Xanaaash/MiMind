from dataclasses import dataclass
from typing import List


EXPERT_QA_POLICY = """
Expert educational Q&A mode rules:
1) Explain concepts using plain language first, then professional terminology.
2) When comparing theories, present similarities, differences, and scope conditions.
3) Distinguish evidence level (meta-analysis / RCT / observational / clinical consensus) when relevant.
4) State uncertainty explicitly when evidence is mixed or population-limited.
5) Refuse diagnosis, medication recommendation, and legal/financial certainty claims.
6) If user message includes self-harm or harm-to-others intent, stop normal Q&A and route to safety response.
""".strip()


@dataclass(frozen=True)
class ExpertQAQuestion:
    question_id: str
    question_zh: str
    question_en: str
    topic: str


EXPERT_QA_REGRESSION_SET: List[ExpertQAQuestion] = [
    ExpertQAQuestion("eqa01", "CBT 和 ACT 的核心差异是什么？", "What are the core differences between CBT and ACT?", "theory_comparison"),
    ExpertQAQuestion("eqa02", "依恋理论在成人关系中的可验证指标有哪些？", "What measurable indicators are used for adult attachment patterns?", "attachment"),
    ExpertQAQuestion("eqa03", "反刍和问题解决在认知层面的区别是什么？", "How does rumination differ from problem-solving at the cognitive level?", "cognitive_process"),
    ExpertQAQuestion("eqa04", "行为激活为什么常用于抑郁干预？", "Why is behavioral activation commonly used for depression-related symptoms?", "behavioral_activation"),
    ExpertQAQuestion("eqa05", "暴露疗法中“习惯化”和“抑制学习”如何理解？", "How do habituation and inhibitory learning differ in exposure therapy?", "anxiety"),
    ExpertQAQuestion("eqa06", "心理弹性研究里最常见的保护因子有哪些？", "What protective factors are most consistently linked to psychological resilience?", "resilience"),
    ExpertQAQuestion("eqa07", "睡眠与情绪调节之间的双向关系有哪些证据？", "What evidence supports bidirectional effects between sleep and emotion regulation?", "sleep"),
    ExpertQAQuestion("eqa08", "压力反应中的 HPA 轴可用什么通俗方式解释？", "How can the HPA axis in stress response be explained in plain language?", "stress_biology"),
    ExpertQAQuestion("eqa09", "正念干预的主要机制假设有哪些？", "What are the main mechanism hypotheses behind mindfulness interventions?", "mindfulness"),
    ExpertQAQuestion("eqa10", "元认知治疗与传统 CBT 的差异点是什么？", "How does metacognitive therapy differ from traditional CBT?", "theory_comparison"),
    ExpertQAQuestion("eqa11", "社交焦虑中的“安全行为”为什么会维持焦虑？", "Why do safety behaviors maintain social anxiety symptoms?", "anxiety"),
    ExpertQAQuestion("eqa12", "高敏感特质和焦虑障碍如何区分边界？", "How can high sensitivity traits be differentiated from anxiety disorders?", "boundary"),
    ExpertQAQuestion("eqa13", "ADHD 执行功能困难的行为表现通常有哪些？", "What behavioral signs are common in ADHD-related executive function difficulties?", "neurodiversity"),
    ExpertQAQuestion("eqa14", "ASD 社交沟通差异和社交恐惧如何区分？", "How can ASD social-communication differences be distinguished from social phobia?", "neurodiversity"),
    ExpertQAQuestion("eqa15", "情绪验证和认同错误行为之间如何把握边界？", "How can emotional validation be provided without endorsing harmful behavior?", "communication"),
    ExpertQAQuestion("eqa16", "动机式访谈的 OARS 技术分别有什么功能？", "What functions do OARS techniques serve in motivational interviewing?", "mi"),
    ExpertQAQuestion("eqa17", "如何向非专业用户解释相关不等于因果？", "How do you explain correlation vs causation to non-specialists?", "research_literacy"),
    ExpertQAQuestion("eqa18", "心理测量中的信度和效度有什么区别？", "What is the difference between reliability and validity in psychometrics?", "psychometrics"),
    ExpertQAQuestion("eqa19", "单次量表分数为什么不能直接下诊断结论？", "Why can a single scale score not be used as a direct diagnosis?", "assessment_boundary"),
    ExpertQAQuestion("eqa20", "当用户要求药物建议时，合规回答框架是什么？", "What is a compliant response framework when users ask for medication advice?", "safety_boundary"),
]


def build_expert_qa_context() -> dict:
    return {
        "policy": EXPERT_QA_POLICY,
        "topics": sorted({item.topic for item in EXPERT_QA_REGRESSION_SET}),
        "regression_question_count": len(EXPERT_QA_REGRESSION_SET),
    }
