import {
  getNeuroDisclaimerKeywordConfig,
  getNeuroDisclaimerMessage,
  loadNeuroDisclaimerKeywordConfig,
  markNeuroDisclaimerShown,
  resetNeuroDisclaimerKeywordConfig,
  setNeuroDisclaimerKeywordConfig,
  shouldInsertNeuroDisclaimer,
  type NeuroKeywordConfig,
} from '../../utils/neuroCoachDisclaimer';

describe('neuroCoachDisclaimer', () => {
  beforeEach(() => {
    sessionStorage.clear();
    resetNeuroDisclaimerKeywordConfig();
  });

  it('detects neuro keywords and inserts disclaimer once per user session', () => {
    const userId = 'u-disclaimer-1';
    expect(shouldInsertNeuroDisclaimer(userId, 'I have ADHD and masking fatigue')).toBe(true);

    markNeuroDisclaimerShown(userId);
    expect(shouldInsertNeuroDisclaimer(userId, 'ADHD still mentioned')).toBe(false);
  });

  it('supports locale-aware keyword matching', () => {
    const userId = 'u-disclaimer-2';
    expect(
      shouldInsertNeuroDisclaimer(userId, '我最近在社交面具上很累', {
        lang: 'zh-CN',
      })
    ).toBe(true);
  });

  it('supports custom keyword overrides', () => {
    const userId = 'u-disclaimer-3';
    const config: NeuroKeywordConfig = {
      common: ['dopamine crash'],
      'en-US': [],
      'zh-CN': [],
    };

    expect(
      shouldInsertNeuroDisclaimer(userId, 'Today I feel a dopamine crash after work', {
        lang: 'en-US',
        keywordConfig: config,
      })
    ).toBe(true);
  });

  it('loads runtime keyword config from external source', async () => {
    let requestedUrl = '';
    let requestedInit: RequestInit | undefined;

    const loaded = await loadNeuroDisclaimerKeywordConfig('/config/custom-neuro.json', async (input, init) => {
      requestedUrl = input;
      requestedInit = init;
      return {
        ok: true,
        json: async () => ({
          common: ['dopamine debt'],
          'en-US': [],
          'zh-CN': [],
        }),
      };
    });

    expect(loaded).toBe(true);
    expect(requestedUrl).toBe('/config/custom-neuro.json');
    expect(requestedInit).toMatchObject({ cache: 'no-store' });
    expect(shouldInsertNeuroDisclaimer('u-disclaimer-4', 'dopamine debt hit me again', { lang: 'en-US' })).toBe(true);
    expect(shouldInsertNeuroDisclaimer('u-disclaimer-5', 'ADHD keeps affecting me', { lang: 'en-US' })).toBe(false);
  });

  it('keeps existing runtime config when external loading fails', async () => {
    setNeuroDisclaimerKeywordConfig({
      common: ['focus wobble'],
      'en-US': [],
      'zh-CN': [],
    });
    expect(shouldInsertNeuroDisclaimer('u-disclaimer-6', 'focus wobble happened today', { lang: 'en-US' })).toBe(true);

    const loaded = await loadNeuroDisclaimerKeywordConfig('/config/bad-neuro.json', async () => ({
      ok: false,
      json: async () => ({}),
    }));

    expect(loaded).toBe(false);
    expect(shouldInsertNeuroDisclaimer('u-disclaimer-7', 'focus wobble happened again', { lang: 'en-US' })).toBe(true);
  });

  it('supports runtime config set/get/reset helpers', () => {
    setNeuroDisclaimerKeywordConfig({
      common: ['overload'],
      'en-US': ['meltdown'],
      'zh-CN': ['zh-crash-token'],
    });
    expect(getNeuroDisclaimerKeywordConfig()).toEqual({
      common: ['overload'],
      'en-US': ['meltdown'],
      'zh-CN': ['zh-crash-token'],
    });

    resetNeuroDisclaimerKeywordConfig();
    expect(getNeuroDisclaimerKeywordConfig()).toBeUndefined();
  });

  it('returns localized disclaimer message', () => {
    expect(getNeuroDisclaimerMessage('zh-CN')).toContain('神经多样性');
    expect(getNeuroDisclaimerMessage('en-US')).toContain('Heads up');
  });
});
