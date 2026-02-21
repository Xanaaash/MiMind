import { describe, expect, it } from 'vitest';

import zhCN from '../../../public/locales/zh-CN.json';
import enUS from '../../../public/locales/en-US.json';
import { NEURO_SCALES } from '../../data/neuroScales';

type LocaleResource = Record<string, unknown>;

function getByPath(resource: LocaleResource, path: string): unknown {
  return path.split('.').reduce<unknown>((current, key) => {
    if (typeof current !== 'object' || current === null || !(key in current)) {
      return undefined;
    }
    return (current as Record<string, unknown>)[key];
  }, resource);
}

function expectTranslation(path: string): void {
  const zhValue = getByPath(zhCN as LocaleResource, path);
  const enValue = getByPath(enUS as LocaleResource, path);

  expect(zhValue, `missing zh-CN translation: ${path}`).toBeTypeOf('string');
  expect(enValue, `missing en-US translation: ${path}`).toBeTypeOf('string');
  expect(String(zhValue).trim().length, `empty zh-CN translation: ${path}`).toBeGreaterThan(0);
  expect(String(enValue).trim().length, `empty en-US translation: ${path}`).toBeGreaterThan(0);
}

describe('neurodiversity translations', () => {
  it('contains bilingual report and disclaimer copy', () => {
    const baseKeys = [
      'neuro.title',
      'neuro.intro',
      'neuro.result_title',
      'neuro.dimension_chart',
      'neuro.dimension_detail',
      'neuro.interpretation',
      'neuro.share_title',
      'neuro.share_subtitle',
      'neuro.share_download',
      'neuro.share_native',
      'neuro.share_preset_xiaohongshu',
      'neuro.share_preset_instagram',
      'neuro.share_preset_tiktok',
      'neuro.retake',
      'neuro.back_to_hub',
      'neuro.level_low',
      'neuro.level_moderate',
      'neuro.level_high',
      'nd_disclaimer.title',
      'nd_disclaimer.legal_review_badge',
      'nd_disclaimer.legal_review_note',
      'nd_disclaimer.p1',
      'nd_disclaimer.p2',
      'nd_disclaimer.seek_help',
      'nd_disclaimer.accept',
      'nd_disclaimer.decline',
      'nd_disclaimer.banner_title',
      'nd_disclaimer.banner_body',
      'nd_disclaimer.coach_message',
      'legal.back_home',
      'legal.privacy.title',
      'legal.privacy.subtitle',
      'legal.privacy.updated_at',
      'legal.terms.title',
      'legal.terms.subtitle',
      'legal.terms.updated_at',
      'neuro_share.card_title',
      'neuro_share.score_label',
      'neuro_share.insight_label',
      'neuro_share.footer',
      'neuro_share.fallback.title',
    ];

    baseKeys.forEach((key) => expectTranslation(key));
  });

  it('includes bilingual legal sections and neuro share archetype structures', () => {
    const locales: Array<[string, LocaleResource]> = [
      ['zh-CN', zhCN as LocaleResource],
      ['en-US', enUS as LocaleResource],
    ];

    locales.forEach(([locale, resource]) => {
      const privacySections = getByPath(resource, 'legal.privacy.sections');
      const termsSections = getByPath(resource, 'legal.terms.sections');
      const fallbackTags = getByPath(resource, 'neuro_share.fallback.tags');

      expect(Array.isArray(privacySections), `${locale} legal.privacy.sections should be array`).toBe(true);
      expect(Array.isArray(termsSections), `${locale} legal.terms.sections should be array`).toBe(true);
      expect(Array.isArray(fallbackTags), `${locale} neuro_share.fallback.tags should be array`).toBe(true);

      (privacySections as Array<Record<string, unknown>>).forEach((section, idx) => {
        expect(typeof section.heading, `${locale} legal privacy heading ${idx}`).toBe('string');
        expect(typeof section.body, `${locale} legal privacy body ${idx}`).toBe('string');
      });
      (termsSections as Array<Record<string, unknown>>).forEach((section, idx) => {
        expect(typeof section.heading, `${locale} legal terms heading ${idx}`).toBe('string');
        expect(typeof section.body, `${locale} legal terms body ${idx}`).toBe('string');
      });
      (fallbackTags as Array<unknown>).forEach((tag, idx) => {
        expect(typeof tag, `${locale} neuro_share fallback tag ${idx}`).toBe('string');
      });

      ['asrs', 'aq10', 'hsp', 'catq'].forEach((scaleId) => {
        ['low', 'moderate', 'high'].forEach((level) => {
          const basePath = `neuro_share.archetypes.${scaleId}.${level}`;
          const title = getByPath(resource, `${basePath}.title`);
          const tags = getByPath(resource, `${basePath}.tags`);
          expect(typeof title, `${locale} ${basePath}.title`).toBe('string');
          expect(Array.isArray(tags), `${locale} ${basePath}.tags`).toBe(true);
          (tags as Array<unknown>).forEach((tag, idx) => {
            expect(typeof tag, `${locale} ${basePath}.tags[${idx}]`).toBe('string');
          });
        });
      });
    });
  });

  it('covers each neuro scale question, labels, and summary copy in zh-CN/en-US', () => {
    NEURO_SCALES.forEach((scale) => {
      expectTranslation(scale.nameKey);
      expectTranslation(scale.descKey);

      scale.dimensions.forEach((dimension) => {
        expectTranslation(dimension.nameKey);
      });

      expect(scale.answerLabels['zh-CN']).toBeDefined();
      expect(scale.answerLabels['en-US']).toBeDefined();
      expect(scale.answerLabels['zh-CN'].length).toBe(scale.answerLabels['en-US'].length);

      scale.answerLabels['zh-CN'].forEach((label) => {
        expect(label.trim().length).toBeGreaterThan(0);
      });
      scale.answerLabels['en-US'].forEach((label) => {
        expect(label.trim().length).toBeGreaterThan(0);
      });

      scale.questions.forEach((question) => {
        const zhText = question.text['zh-CN'];
        const enText = question.text['en-US'];
        expect(typeof zhText).toBe('string');
        expect(typeof enText).toBe('string');
        expect((zhText ?? '').trim().length).toBeGreaterThan(0);
        expect((enText ?? '').trim().length).toBeGreaterThan(0);
      });

      const maxAnswerValue = scale.answerLabels['zh-CN'].length - 1;
      const lowAnswers = Array.from({ length: scale.itemCount }, () => 0);
      const moderateAnswers = Array.from({ length: scale.itemCount }, () => Math.floor(maxAnswerValue / 2));
      const highAnswers = Array.from({ length: scale.itemCount }, () => maxAnswerValue);

      [lowAnswers, moderateAnswers, highAnswers].forEach((answers) => {
        const result = scale.score(answers);
        expectTranslation(result.levelKey);
        expectTranslation(result.summaryKey);
      });
    });
  });
});
