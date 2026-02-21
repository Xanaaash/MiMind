import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

import { meditationPlaylist } from '../../config/meditationPlaylist';
import zhCN from '../../../public/locales/zh-CN.json';
import enUS from '../../../public/locales/en-US.json';

const thisDir = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.resolve(thisDir, '../../../public');

type LocaleResource = Record<string, unknown>;

function getByPath(resource: LocaleResource, keyPath: string): unknown {
  return keyPath.split('.').reduce<unknown>((current, key) => {
    if (typeof current !== 'object' || current === null || !(key in current)) {
      return undefined;
    }
    return (current as Record<string, unknown>)[key];
  }, resource);
}

describe('meditation playlist upgrade', () => {
  it('contains at least 12 tracks and full theme coverage', () => {
    expect(meditationPlaylist.length).toBeGreaterThanOrEqual(12);

    const themes = new Set(meditationPlaylist.map((track) => track.theme));
    expect(themes.has('stress')).toBe(true);
    expect(themes.has('sleep')).toBe(true);
    expect(themes.has('focus')).toBe(true);
    expect(themes.has('recovery')).toBe(true);
  });

  it('provides complete metadata and valid local assets', () => {
    meditationPlaylist.forEach((track) => {
      expect(track.sourceName.trim().length).toBeGreaterThan(0);
      expect(track.sourceUrl.startsWith('https://')).toBe(true);
      expect(track.licenseType.trim().length).toBeGreaterThan(0);
      expect(track.tagKeys.length).toBeGreaterThan(0);
      expect(track.titleKey.trim().length).toBeGreaterThan(0);
      expect(track.descKey.trim().length).toBeGreaterThan(0);

      expect(getByPath(zhCN as LocaleResource, track.titleKey)).toBeTypeOf('string');
      expect(getByPath(enUS as LocaleResource, track.titleKey)).toBeTypeOf('string');
      expect(getByPath(zhCN as LocaleResource, track.descKey)).toBeTypeOf('string');
      expect(getByPath(enUS as LocaleResource, track.descKey)).toBeTypeOf('string');
      expect(getByPath(zhCN as LocaleResource, track.attributionKey)).toBeTypeOf('string');
      expect(getByPath(enUS as LocaleResource, track.attributionKey)).toBeTypeOf('string');
      track.tagKeys.forEach((tagKey) => {
        expect(getByPath(zhCN as LocaleResource, tagKey)).toBeTypeOf('string');
        expect(getByPath(enUS as LocaleResource, tagKey)).toBeTypeOf('string');
      });

      const localFile = path.resolve(publicDir, track.src.replace(/^\//, ''));
      expect(fs.existsSync(localFile), `missing file for ${track.id}: ${track.src}`).toBe(true);
    });
  });
});
