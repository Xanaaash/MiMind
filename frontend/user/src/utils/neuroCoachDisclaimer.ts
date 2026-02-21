import i18n from '../i18n';

const COACH_DISCLAIMER_KEY = 'nd_coach_disclaimer_shown';

type SupportedLocale = 'zh-CN' | 'en-US';

export type NeuroKeywordConfig = Partial<Record<SupportedLocale | 'common', string[]>>;

const DEFAULT_NEURO_KEYWORDS: Record<SupportedLocale | 'common', string[]> = {
  common: ['adhd', 'asd', 'hsp', 'neurodiv', 'catq', 'asrs', 'aq-10', 'aq10', 'masking', 'sensory'],
  'zh-CN': ['注意力', '多动', '自闭', '谱系', '高敏感', '感官', '社交面具'],
  'en-US': ['attention', 'hyperactivity', 'autism', 'spectrum', 'high sensitivity', 'camouflage'],
};

type NeuroDisclaimerOptions = {
  lang?: string;
  keywordConfig?: NeuroKeywordConfig;
};

function normalizeLocale(lang?: string): SupportedLocale {
  return (lang ?? '').toLowerCase().startsWith('zh') ? 'zh-CN' : 'en-US';
}

function mergeKeywordConfig(override?: NeuroKeywordConfig): Record<SupportedLocale | 'common', string[]> {
  return {
    common: override?.common ?? DEFAULT_NEURO_KEYWORDS.common,
    'zh-CN': override?.['zh-CN'] ?? DEFAULT_NEURO_KEYWORDS['zh-CN'],
    'en-US': override?.['en-US'] ?? DEFAULT_NEURO_KEYWORDS['en-US'],
  };
}

function resolveKeywordPool(lang?: string, override?: NeuroKeywordConfig): string[] {
  const locale = normalizeLocale(lang);
  const fallbackLocale: SupportedLocale = locale === 'zh-CN' ? 'en-US' : 'zh-CN';
  const config = mergeKeywordConfig(override);
  return Array.from(new Set([...config.common, ...config[locale], ...config[fallbackLocale]])).map((item) =>
    item.toLowerCase()
  );
}

export function shouldInsertNeuroDisclaimer(
  userId: string,
  userMessage: string,
  options?: NeuroDisclaimerOptions
): boolean {
  const key = `${COACH_DISCLAIMER_KEY}_${userId}`;
  if (sessionStorage.getItem(key)) return false;

  const lower = userMessage.toLowerCase();
  const keywords = resolveKeywordPool(options?.lang, options?.keywordConfig);
  return keywords.some((kw) => lower.includes(kw));
}

export function markNeuroDisclaimerShown(userId: string): void {
  sessionStorage.setItem(`${COACH_DISCLAIMER_KEY}_${userId}`, '1');
}

export function getNeuroDisclaimerMessage(lang: string): string {
  const locale = lang.startsWith('zh') ? 'zh-CN' : 'en-US';
  return i18n.t('nd_disclaimer.coach_message', { lng: locale });
}
