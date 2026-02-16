from copy import deepcopy
from typing import Dict

SUPPORTED_LOCALES = ["en-US", "zh-CN"]


def _q(question_id: str, dimension_key: str, en: str, zh: str) -> Dict[str, object]:
    return {
        "question_id": question_id,
        "dimension_key": dimension_key,
        "text": {
            "en-US": en,
            "zh-CN": zh,
        },
    }


TEST_QUESTION_BANKS = {
    "mbti": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Choose the statement that is closer to your usual preference.",
            "zh-CN": "请选择更符合你日常偏好的描述。",
        },
        "questions": [
            _q("q1", "ei", "I gain energy from social interaction.", "我从社交互动中获得能量。"),
            _q("q2", "ei", "I prefer quiet time alone to recharge.", "我更倾向独处来恢复精力。"),
            _q("q3", "sn", "I focus on concrete facts and details.", "我更关注具体事实与细节。"),
            _q("q4", "sn", "I naturally look for patterns and possibilities.", "我更自然地寻找模式和可能性。"),
            _q("q5", "tf", "I decide mainly through logical analysis.", "我主要通过逻辑分析做决定。"),
            _q("q6", "tf", "I decide mainly by considering people and values.", "我主要考虑他人感受和价值来做决定。"),
            _q("q7", "jp", "I like planning and closure early.", "我喜欢提前规划并尽快定案。"),
            _q("q8", "jp", "I stay flexible and keep options open.", "我倾向保持灵活，保留选择空间。"),
        ],
    },
    "16p": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Rate each statement from strongly disagree to strongly agree.",
            "zh-CN": "请按“非常不同意”到“非常同意”进行评分。",
        },
        "questions": [
            _q("q1", "ei", "I feel comfortable initiating conversations with strangers.", "我会主动与陌生人开启交流。"),
            _q("q2", "sn", "I trust practical experience more than abstract theory.", "相比抽象理论，我更信任实践经验。"),
            _q("q3", "tf", "I prioritize fairness through consistent rules.", "我会通过一致规则来追求公平。"),
            _q("q4", "jp", "I feel better when my day follows a clear structure.", "当一天有清晰安排时我会更安心。"),
            _q("q5", "identity", "I usually feel confident in myself under pressure.", "在压力下我通常仍对自己有信心。"),
        ],
    },
    "big5": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Rate how accurately each statement describes you.",
            "zh-CN": "请评估每项描述对你的符合程度。",
        },
        "questions": [
            _q("q1", "O", "I enjoy trying novel ideas and experiences.", "我喜欢尝试新想法和新体验。"),
            _q("q2", "C", "I keep tasks organized and follow through.", "我会有条理地完成任务。"),
            _q("q3", "E", "I feel energized by being around many people.", "在人群中我会更有活力。"),
            _q("q4", "A", "I try to be considerate and cooperative.", "我会尽量体谅他人并合作。"),
            _q("q5", "N", "I am easily affected by stress or worry.", "我容易受到压力和担忧影响。"),
        ],
    },
    "attachment": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Rate each statement according to your close-relationship experience.",
            "zh-CN": "请根据你的亲密关系体验进行评分。",
        },
        "questions": [
            _q("q1", "secure", "I can rely on close others and feel safe.", "我能信任亲近的人并感到安全。"),
            _q("q2", "anxious", "I worry that people I care about may leave me.", "我会担心在意的人离开我。"),
            _q("q3", "avoidant", "I prefer keeping emotional distance in relationships.", "在关系中我倾向保持情感距离。"),
            _q("q4", "fearful", "I want closeness but fear being hurt.", "我渴望亲近又害怕受伤。"),
        ],
    },
    "love_language": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Rate how strongly each behavior makes you feel loved.",
            "zh-CN": "请评估每种行为让你感到被爱的程度。",
        },
        "questions": [
            _q("q1", "words", "Receiving sincere verbal appreciation.", "收到真诚的语言肯定。"),
            _q("q2", "acts", "Someone helping me with practical tasks.", "有人主动帮我处理实际事务。"),
            _q("q3", "gifts", "Receiving thoughtful gifts.", "收到有心意的礼物。"),
            _q("q4", "time", "Spending focused, quality time together.", "一起度过专注而高质量的时光。"),
            _q("q5", "touch", "Warm and respectful physical affection.", "温暖且尊重边界的肢体接触。"),
        ],
    },
    "stress_coping": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "When stressed, how often do you use each coping style?",
            "zh-CN": "当你有压力时，以下应对方式出现的频率如何？",
        },
        "questions": [
            _q("q1", "problem_focused", "I break the problem down and make a plan.", "我会拆解问题并制定计划。"),
            _q("q2", "emotion_focused", "I regulate emotions before handling the issue.", "我会先调节情绪再处理问题。"),
            _q("q3", "avoidance", "I postpone or avoid facing the stressor.", "我会拖延或回避压力源。"),
            _q("q4", "support_seeking", "I ask trusted people for help or perspective.", "我会向信任的人求助或寻求建议。"),
        ],
    },
    "eq": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Rate how often you demonstrate each emotional skill.",
            "zh-CN": "请评估你展现以下情绪能力的频率。",
        },
        "questions": [
            _q("q1", "self_awareness", "I can name what I am feeling in the moment.", "我能在当下辨识自己的情绪。"),
            _q("q2", "self_regulation", "I stay composed when emotions run high.", "情绪高涨时我仍能保持稳定。"),
            _q("q3", "empathy", "I notice emotional signals from others quickly.", "我能较快觉察他人的情绪信号。"),
            _q("q4", "relationship_management", "I handle difficult conversations constructively.", "我能建设性地处理困难对话。"),
        ],
    },
    "inner_child": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Reflect on how these inner states show up in your life.",
            "zh-CN": "请回顾这些“内在状态”在你生活中的出现程度。",
        },
        "questions": [
            _q("q1", "playful", "I allow myself curiosity and play.", "我允许自己保持好奇和玩心。"),
            _q("q2", "wounded", "I feel old emotional pain gets triggered easily.", "我容易被旧有情绪伤痛触发。"),
            _q("q3", "resilient", "I can recover and self-soothe after setbacks.", "受挫后我能够复原并安抚自己。"),
            _q("q4", "protective", "I set limits to protect vulnerable parts of me.", "我会设定边界来保护自己脆弱的部分。"),
        ],
    },
    "boundary": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Rate how clearly you communicate and maintain boundaries.",
            "zh-CN": "请评估你表达并维护边界的清晰程度。",
        },
        "questions": [
            _q("q1", "emotional", "I can say no when emotional demands overwhelm me.", "当情绪负担过重时，我能说“不”。"),
            _q("q2", "physical", "I clearly communicate my comfort with physical distance.", "我能清楚表达自己对身体距离的舒适边界。"),
            _q("q3", "digital", "I set limits on online availability and replies.", "我会设置线上可联系时间和回复边界。"),
            _q("q4", "work", "I protect rest time from unnecessary work intrusion.", "我会保护休息时间不被不必要工作侵占。"),
            _q("q5", "social", "I choose social commitments based on capacity, not pressure.", "我会基于精力而非压力来决定社交投入。"),
        ],
    },
    "psych_age": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Answer honestly based on your current life stage.",
            "zh-CN": "请结合你当前的人生阶段如实作答。",
        },
        "questions": [
            _q("q1", "chronological_age", "Enter your actual age in years.", "请输入你的实际年龄（岁）。"),
            _q("q2", "curiosity", "I remain eager to learn and explore new things.", "我仍保持学习与探索新事物的热情。"),
            _q("q3", "emotional_regulation", "I can manage emotional ups and downs effectively.", "我能较好管理情绪起伏。"),
            _q("q4", "social_energy", "I maintain steady energy for meaningful social connection.", "我能稳定投入有意义的社交连接。"),
        ],
    },
}


def get_test_question_bank(test_id: str) -> Dict[str, object]:
    bank = TEST_QUESTION_BANKS.get(test_id)
    if bank is None:
        raise ValueError(f"Unknown test_id: {test_id}")
    return deepcopy(bank)
