import {
  getNeuroDisclaimerMessage,
  markNeuroDisclaimerShown,
  shouldInsertNeuroDisclaimer,
  type NeuroKeywordConfig,
} from '../../utils/neuroCoachDisclaimer';

describe('neuroCoachDisclaimer', () => {
  beforeEach(() => {
    sessionStorage.clear();
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

  it('returns localized disclaimer message', () => {
    expect(getNeuroDisclaimerMessage('zh-CN')).toContain('神经多样性');
    expect(getNeuroDisclaimerMessage('en-US')).toContain('Heads up');
  });
});
