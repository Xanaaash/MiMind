import { describe, expect, it } from 'vitest';

import zhCN from '../../../public/locales/zh-CN.json';
import enUS from '../../../public/locales/en-US.json';
import {
  SCALE_INTRO_KEYS,
  SCALE_NAME_KEYS,
  TEST_INTRO_KEYS,
  TEST_NAME_KEYS,
} from '../../utils/assessmentCopy';

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

describe('assessment/test bilingual translations', () => {
  it('covers all mapped scale/test name and intro keys', () => {
    const mappedKeys = [
      ...Object.values(SCALE_NAME_KEYS),
      ...Object.values(SCALE_INTRO_KEYS),
      ...Object.values(TEST_NAME_KEYS),
      ...Object.values(TEST_INTRO_KEYS),
      'scales.intro.generic',
      'tests.intro.generic',
    ];
    Array.from(new Set(mappedKeys)).forEach((key) => expectTranslation(key));
  });

  it('covers result severity and structured summary labels', () => {
    [
      'scales.severity_label.minimal',
      'scales.severity_label.none',
      'scales.severity_label.mild',
      'scales.severity_label.moderate',
      'scales.severity_label.moderately severe',
      'scales.severity_label.severe',
      'scales.severity_label.unknown',
      'tests.summary_label.type',
      'tests.summary_label.dimension_strength',
      'tests.summary_label.identity_score',
      'tests.summary_label.scores',
      'tests.summary_label.dominant_trait',
      'tests.summary_label.lowest_trait',
      'tests.summary_label.primary_style',
      'tests.summary_label.overall_score',
      'tests.summary_label.level',
      'tests.summary_label.primary_profile',
      'tests.summary_label.boundary_profile',
      'tests.summary_label.average_score',
      'tests.summary_label.psychological_age',
      'tests.summary_label.age_band',
      'tests.summary_label.inputs',
      'tests.value_label.high',
      'tests.value_label.developing',
      'tests.value_label.emerging',
      'tests.value_label.healthy',
      'tests.value_label.fragile',
      'tests.value_label.youthful',
      'tests.value_label.balanced',
      'tests.value_label.mature',
      'tests.value_label.mixed',
      'tests.value_label.medium',
      'tests.share_card.generic_subtitle',
      'tests.share_card.footer_line1',
      'tests.share_card.footer_line2',
      'tests.share_card.mbti_subtitle',
      'tests.share_card.mbti_type_label',
      'tests.share_card.big5_subtitle',
      'tests.share_card.big5_dominant_label',
      'tests.share_card.trait_o',
      'tests.share_card.trait_c',
      'tests.share_card.trait_e',
      'tests.share_card.trait_a',
      'tests.share_card.trait_n',
    ].forEach((key) => expectTranslation(key));
  });
});
