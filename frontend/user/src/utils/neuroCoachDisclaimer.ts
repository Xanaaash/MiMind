import i18n from '../i18n';

const COACH_DISCLAIMER_KEY = 'nd_coach_disclaimer_shown';
export const DEFAULT_NEURO_KEYWORD_CONFIG_URL = '/config/neuro-disclaimer-keywords.json';

type SupportedLocale = 'zh-CN' | 'en-US';
type KeywordBucket = SupportedLocale | 'common';
type KeywordConfigResponse = Pick<Response, 'ok' | 'json'>;
type KeywordConfigFetcher = (input: string, init?: RequestInit) => Promise<KeywordConfigResponse>;

export type NeuroKeywordConfig = Partial<Record<KeywordBucket, string[]>>;

const KEYWORD_BUCKETS: KeywordBucket[] = ['common', 'zh-CN', 'en-US'];

const DEFAULT_NEURO_KEYWORDS: Record<KeywordBucket, string[]> = {
  common: ['adhd', 'asd', 'hsp', 'neurodiv', 'catq', 'asrs', 'aq-10', 'aq10', 'masking', 'sensory'],
  'zh-CN': ['注意力', '多动', '自闭', '谱系', '高敏感', '感官', '社交面具'],
  'en-US': ['attention', 'hyperactivity', 'autism', 'spectrum', 'high sensitivity', 'camouflage'],
};

let runtimeNeuroKeywordConfig: NeuroKeywordConfig | undefined;

type NeuroDisclaimerOptions = {
  lang?: string;
  keywordConfig?: NeuroKeywordConfig;
};

function normalizeLocale(lang?: string): SupportedLocale {
  return (lang ?? '').toLowerCase().startsWith('zh') ? 'zh-CN' : 'en-US';
}

function normalizeKeywordList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is string => typeof item === 'string')
    .map((item) => item.trim())
    .filter(Boolean);
}

function normalizeKeywordConfig(value: unknown): NeuroKeywordConfig | undefined {
  if (!value || typeof value !== 'object') return undefined;

  const normalized: NeuroKeywordConfig = {};
  for (const bucket of KEYWORD_BUCKETS) {
    const raw = (value as Record<string, unknown>)[bucket];
    if (raw === undefined) continue;
    if (!Array.isArray(raw)) continue;
    normalized[bucket] = normalizeKeywordList(raw);
  }

  return Object.keys(normalized).length > 0 ? normalized : undefined;
}

function mergeKeywordConfig(...overrides: Array<NeuroKeywordConfig | undefined>): Record<KeywordBucket, string[]> {
  const merged: Record<KeywordBucket, string[]> = {
    common: [...DEFAULT_NEURO_KEYWORDS.common],
    'zh-CN': [...DEFAULT_NEURO_KEYWORDS['zh-CN']],
    'en-US': [...DEFAULT_NEURO_KEYWORDS['en-US']],
  };

  for (const override of overrides) {
    if (!override) continue;
    for (const bucket of KEYWORD_BUCKETS) {
      if (override[bucket] !== undefined) {
        merged[bucket] = [...(override[bucket] ?? [])];
      }
    }
  }

  return merged;
}

function resolveKeywordPool(lang?: string, override?: NeuroKeywordConfig): string[] {
  const locale = normalizeLocale(lang);
  const fallbackLocale: SupportedLocale = locale === 'zh-CN' ? 'en-US' : 'zh-CN';
  const config = mergeKeywordConfig(runtimeNeuroKeywordConfig, override);

  return Array.from(new Set([...config.common, ...config[locale], ...config[fallbackLocale]])).map((item) =>
    item.toLowerCase()
  );
}

export function getNeuroDisclaimerKeywordConfig(): NeuroKeywordConfig | undefined {
  if (!runtimeNeuroKeywordConfig) return undefined;

  return {
    common: runtimeNeuroKeywordConfig.common ? [...runtimeNeuroKeywordConfig.common] : undefined,
    'zh-CN': runtimeNeuroKeywordConfig['zh-CN'] ? [...runtimeNeuroKeywordConfig['zh-CN']] : undefined,
    'en-US': runtimeNeuroKeywordConfig['en-US'] ? [...runtimeNeuroKeywordConfig['en-US']] : undefined,
  };
}

export function setNeuroDisclaimerKeywordConfig(config?: NeuroKeywordConfig): void {
  runtimeNeuroKeywordConfig = normalizeKeywordConfig(config);
}

export function resetNeuroDisclaimerKeywordConfig(): void {
  runtimeNeuroKeywordConfig = undefined;
}

export async function loadNeuroDisclaimerKeywordConfig(
  url = DEFAULT_NEURO_KEYWORD_CONFIG_URL,
  fetcher: KeywordConfigFetcher = fetch
): Promise<boolean> {
  try {
    const response = await fetcher(url, { cache: 'no-store' });
    if (!response.ok) return false;

    const payload = await response.json();
    const normalized = normalizeKeywordConfig(payload);
    if (!normalized) return false;

    runtimeNeuroKeywordConfig = normalized;
    return true;
  } catch {
    return false;
  }
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
