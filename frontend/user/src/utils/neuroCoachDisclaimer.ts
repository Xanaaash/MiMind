const COACH_DISCLAIMER_KEY = 'nd_coach_disclaimer_shown';

const NEURO_KEYWORDS = [
  'adhd', 'asd', '注意力', '多动', '自闭', '谱系',
  '高敏感', 'hsp', '感官', 'sensory', 'neurodiv',
  '社交面具', 'masking', 'catq', 'asrs', 'aq-10', 'aq10',
];

export function shouldInsertNeuroDisclaimer(userId: string, userMessage: string): boolean {
  const key = `${COACH_DISCLAIMER_KEY}_${userId}`;
  if (sessionStorage.getItem(key)) return false;

  const lower = userMessage.toLowerCase();
  return NEURO_KEYWORDS.some((kw) => lower.includes(kw));
}

export function markNeuroDisclaimerShown(userId: string): void {
  sessionStorage.setItem(`${COACH_DISCLAIMER_KEY}_${userId}`, '1');
}

export function getNeuroDisclaimerMessage(lang: string): string {
  if (lang.startsWith('zh')) {
    return '💡 温馨提示：以下讨论涉及神经多样性相关特质。MiMind 的评估和对话旨在帮助你探索个人认知与行为模式，绝非临床诊断。如果你认为这些特质已严重影响日常生活，建议寻求专业精神科医生的评估。';
  }
  return '💡 Heads up: The following discussion involves neurodiversity-related traits. MiMind assessments and conversations are designed to help you explore your cognitive and behavioral patterns — they are NOT clinical diagnoses. If you feel these traits significantly impact your daily life, we recommend seeking evaluation from a qualified professional.';
}
