from copy import deepcopy
from typing import Dict, List

from modules.assessment.catalog.scales import SCL90

SUPPORTED_LOCALES = ["en-US", "zh-CN"]

LIKERT_0_3 = {
    "en-US": [
        "Not at all",
        "Several days",
        "More than half the days",
        "Nearly every day",
    ],
    "zh-CN": [
        "完全没有",
        "几天",
        "一半以上天数",
        "几乎每天",
    ],
}

LIKERT_0_4 = {
    "en-US": [
        "Never",
        "Almost never",
        "Sometimes",
        "Fairly often",
        "Very often",
    ],
    "zh-CN": [
        "从不",
        "几乎没有",
        "有时",
        "相当经常",
        "非常经常",
    ],
}

SCL90_0_4 = {
    "en-US": [
        "Not at all",
        "A little bit",
        "Moderately",
        "Quite a bit",
        "Extremely",
    ],
    "zh-CN": [
        "完全没有",
        "轻度",
        "中度",
        "偏重",
        "极重",
    ],
}

YES_NO = {
    "en-US": ["No", "Yes"],
    "zh-CN": ["否", "是"],
}


def _q(question_id: str, en: str, zh: str) -> Dict[str, object]:
    return {
        "question_id": question_id,
        "text": {
            "en-US": en,
            "zh-CN": zh,
        },
    }


SCL90_DIMENSION_LABELS = {
    "somatization": {"en-US": "somatic discomfort", "zh-CN": "躯体化不适"},
    "obsessive_compulsive": {"en-US": "obsessive or compulsive experiences", "zh-CN": "强迫体验"},
    "interpersonal_sensitivity": {"en-US": "interpersonal sensitivity", "zh-CN": "人际敏感"},
    "depression": {"en-US": "depressive mood", "zh-CN": "抑郁情绪"},
    "anxiety": {"en-US": "anxiety", "zh-CN": "焦虑体验"},
    "hostility": {"en-US": "irritability or hostility", "zh-CN": "敌意或易怒"},
    "phobic_anxiety": {"en-US": "phobic anxiety", "zh-CN": "恐惧焦虑"},
    "paranoid_ideation": {"en-US": "paranoid thoughts", "zh-CN": "偏执想法"},
    "psychoticism": {"en-US": "detachment or unusual thinking", "zh-CN": "疏离与非常规思维"},
}

SCL90_DIMENSION_ORDER = list(SCL90_DIMENSION_LABELS.keys())


def _scl90_questions() -> List[Dict[str, object]]:
    questions: List[Dict[str, object]] = []
    for index in range(90):
        dimension = SCL90_DIMENSION_ORDER[index % len(SCL90_DIMENSION_ORDER)]
        label = SCL90_DIMENSION_LABELS[dimension]
        item_no = index + 1
        questions.append(
            {
                "question_id": f"q{item_no}",
                "dimension": dimension,
                "text": {
                    "en-US": f"SCL-90 item {item_no}: distress related to {label['en-US']}.",
                    "zh-CN": f"SCL-90 第{item_no}题：与{label['zh-CN']}相关的困扰程度。",
                },
            }
        )
    return questions


SCALE_QUESTION_BANKS = {
    "phq9": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Over the last 2 weeks, how often have you been bothered by the following problems?",
            "zh-CN": "在过去两周内，以下情况困扰你的频率是？",
        },
        "answer_labels": LIKERT_0_3,
        "questions": [
            _q("q1", "Little interest or pleasure in doing things.", "做事缺乏兴趣或乐趣。"),
            _q("q2", "Feeling down, depressed, or hopeless.", "感到情绪低落、抑郁或无望。"),
            _q("q3", "Trouble falling asleep, staying asleep, or sleeping too much.", "入睡困难、睡不踏实或睡得过多。"),
            _q("q4", "Feeling tired or having little energy.", "感到疲倦或缺乏精力。"),
            _q("q5", "Poor appetite or overeating.", "食欲不振或暴饮暴食。"),
            _q("q6", "Feeling bad about yourself, or that you have let yourself or family down.", "觉得自己很糟，或认为让自己/家人失望了。"),
            _q("q7", "Trouble concentrating on tasks such as reading or watching TV.", "难以专注于阅读、看电视等事情。"),
            _q("q8", "Moving or speaking slowly, or being noticeably restless.", "动作/说话变慢，或明显坐立不安。"),
            _q("q9", "Thoughts that you would be better off dead or might hurt yourself.", "出现“活着不如死了”或伤害自己的想法。"),
        ],
    },
    "gad7": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Over the last 2 weeks, how often have you been bothered by the following problems?",
            "zh-CN": "在过去两周内，以下情况困扰你的频率是？",
        },
        "answer_labels": LIKERT_0_3,
        "questions": [
            _q("q1", "Feeling nervous, anxious, or on edge.", "感到紧张、焦虑或坐立不安。"),
            _q("q2", "Not being able to stop or control worrying.", "无法停止或控制担忧。"),
            _q("q3", "Worrying too much about different things.", "对各种事情担忧过多。"),
            _q("q4", "Trouble relaxing.", "很难放松下来。"),
            _q("q5", "Being so restless that it is hard to sit still.", "烦躁到难以安静坐着。"),
            _q("q6", "Becoming easily annoyed or irritable.", "容易生气或易怒。"),
            _q("q7", "Feeling afraid as if something awful might happen.", "感到害怕，仿佛会发生糟糕的事。"),
        ],
    },
    "pss10": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "In the last month, how often did you feel this way?",
            "zh-CN": "在过去一个月中，你出现以下感受的频率是？",
        },
        "answer_labels": LIKERT_0_4,
        "questions": [
            _q("q1", "Upset by unexpected events.", "因意外事件而感到心烦。"),
            _q("q2", "Unable to control important things in your life.", "感到无法掌控生活中重要的事情。"),
            _q("q3", "Nervous or stressed.", "感到紧张或有压力。"),
            _q("q4", "Confident about handling personal problems.", "对处理个人问题有信心。"),
            _q("q5", "Feeling that things are going your way.", "感到事情正朝着你希望的方向发展。"),
            _q("q6", "Could not cope with all the things you had to do.", "觉得必须处理的事情多到难以应对。"),
            _q("q7", "Able to control irritations in your life.", "能够控制生活中的烦恼。"),
            _q("q8", "Feeling on top of things.", "感到自己能掌控局面。"),
            _q("q9", "Angered by things outside your control.", "因无法控制的事情而生气。"),
            _q("q10", "Difficulties were piling up so high that you could not overcome them.", "困难堆积到让你觉得无法克服。"),
        ],
    },
    "cssrs": {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Please answer carefully. If any item is positive, the system will trigger safety support.",
            "zh-CN": "请认真作答。若任一题为阳性，系统将立即触发安全支持流程。",
        },
        "answer_labels": YES_NO,
        "questions": [
            _q("q1", "Have you wished you were dead or wished you could go to sleep and not wake up?", "你是否希望自己已经死去，或希望睡着后不再醒来？"),
            _q("q2", "Have you actually had thoughts of killing yourself?", "你是否有过要结束自己生命的想法？"),
            _q("q3", "Have you thought about how you might do this?", "你是否想过具体会如何做？"),
            _q("q4", "Have you had these thoughts and some intention of acting on them?", "你是否既有这些想法，也有过付诸行动的意图？"),
            _q("q5", "Have you started to work out details of a plan and intend to carry it out?", "你是否制定过具体计划并打算执行？"),
            _q("q6", "Have you ever done anything, started to do anything, or prepared to do anything to end your life?", "你是否曾做过、开始做过，或准备做过任何结束自己生命的行为？"),
        ],
    },
    SCL90: {
        "supported_locales": SUPPORTED_LOCALES,
        "instructions": {
            "en-US": "Rate how much each symptom distressed you during the last 7 days.",
            "zh-CN": "请评估过去7天内每项症状对你的困扰程度。",
        },
        "answer_labels": SCL90_0_4,
        "questions": _scl90_questions(),
    },
}


def get_scale_question_bank(scale_id: str) -> Dict[str, object]:
    bank = SCALE_QUESTION_BANKS.get(scale_id)
    if bank is None:
        raise ValueError(f"Unknown scale_id: {scale_id}")
    return deepcopy(bank)
