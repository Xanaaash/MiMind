import { describe, expect, it } from 'vitest';

import zhCN from '../../../public/locales/zh-CN.json';
import enUS from '../../../public/locales/en-US.json';

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

describe('tools route translations', () => {
  it('contains bilingual keys for rescue and mindfulness hubs', () => {
    [
      'nav.rescue',
      'nav.mindfulness',
      'tools.rescue.title',
      'tools.rescue.subtitle',
      'tools.rescue.primary_action',
      'tools.rescue.minimal_hint',
      'tools.rescue.quick_pink_caption',
      'tools.rescue.quick_pink_start',
      'tools.rescue.quick_pink_running',
      'tools.rescue.quick_sensory_title',
      'tools.rescue.quick_sensory_desc',
      'tools.rescue.quick_breath_title',
      'tools.rescue.quick_breath_desc',
      'tools.rescue.stop_all_audio',
      'tools.pomo_floating_open',
      'tools.pomo_floating_minimize',
      'tools.pomo_floating_expand',
      'tools.mindfulness.back',
      'tools.mindfulness.title',
      'tools.mindfulness.subtitle',
      'tools.mindfulness.quick_title',
      'tools.mindfulness.quick_desc',
      'tools.mindfulness.deep_title',
      'tools.mindfulness.deep_desc',
      'tools.mindfulness.quick_badge',
      'tools.mindfulness.deep_badge',
      'tools.mindfulness.meditation_title',
      'tools.mindfulness.meditation_desc',
      'tools.mindfulness.meditation_deep_desc',
      'tools.mindfulness.manifestation_quick_desc',
      'tools.mindfulness.flow_title',
      'tools.mindfulness.flow_step_1',
      'tools.mindfulness.flow_step_2',
      'tools.mindfulness.flow_step_3',
      'tools.manifestation.badge',
      'tools.manifestation.title',
      'tools.manifestation.subtitle',
      'tools.manifestation.desc',
      'tools.manifestation.mode_quick',
      'tools.manifestation.mode_deep',
      'tools.manifestation.quick_title',
      'tools.manifestation.quick_desc',
      'tools.manifestation.quick_focus_label',
      'tools.manifestation.quick_focus_stability',
      'tools.manifestation.quick_focus_confidence',
      'tools.manifestation.quick_focus_calm',
      'tools.manifestation.quick_preview_label',
      'tools.manifestation.quick_template_stability',
      'tools.manifestation.quick_template_confidence',
      'tools.manifestation.quick_template_calm',
      'tools.manifestation.quick_apply',
      'tools.manifestation.deep_title',
      'tools.manifestation.deep_desc',
      'tools.manifestation.audio_start',
      'tools.manifestation.audio_stop',
      'tools.manifestation.affirmation_title',
      'tools.manifestation.affirmation_desc',
      'tools.manifestation.affirmation_placeholder',
      'tools.manifestation.empty_affirmation',
      'tools.manifestation.vision_title',
      'tools.manifestation.vision_desc',
      'tools.manifestation.vision_title_placeholder',
      'tools.manifestation.vision_note_placeholder',
      'tools.manifestation.empty_vision',
    ].forEach((key) => expectTranslation(key));
  });
});
