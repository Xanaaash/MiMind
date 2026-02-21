import i18n from '../i18n';

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
  const locale = lang.startsWith('zh') ? 'zh-CN' : 'en-US';
  return i18n.t('nd_disclaimer.coach_message', { lng: locale });
}
