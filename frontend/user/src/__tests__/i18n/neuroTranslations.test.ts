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
    ];

    baseKeys.forEach((key) => expectTranslation(key));
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
