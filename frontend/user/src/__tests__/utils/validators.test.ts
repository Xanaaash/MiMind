import { describe, it, expect } from 'vitest';
import { required, minLength, maxLength, emailFormat, runValidators } from '../../utils/validators';

describe('required', () => {
  const v = required('Required');
  it('returns error for empty string', () => expect(v('')).toBe('Required'));
  it('returns error for whitespace-only', () => expect(v('   ')).toBe('Required'));
  it('returns null for non-empty', () => expect(v('hello')).toBeNull());
});

describe('minLength', () => {
  const v = minLength(3, 'Too short');
  it('returns error when too short', () => expect(v('ab')).toBe('Too short'));
  it('returns null when long enough', () => expect(v('abc')).toBeNull());
  it('trims before checking', () => expect(v('  ab  ')).toBe('Too short'));
});

describe('maxLength', () => {
  const v = maxLength(5, 'Too long');
  it('returns error when too long', () => expect(v('abcdef')).toBe('Too long'));
  it('returns null when within limit', () => expect(v('abcde')).toBeNull());
});

describe('emailFormat', () => {
  const v = emailFormat('Bad email');
  it('accepts valid email', () => expect(v('a@b.com')).toBeNull());
  it('rejects no @', () => expect(v('ab.com')).toBe('Bad email'));
  it('rejects no domain', () => expect(v('a@')).toBe('Bad email'));
  it('rejects empty', () => expect(v('')).toBe('Bad email'));
});

describe('runValidators', () => {
  it('returns first error', () => {
    const result = runValidators('', [required('R'), minLength(3, 'M')]);
    expect(result).toBe('R');
  });

  it('returns null when all pass', () => {
    const result = runValidators('hello@world.com', [
      required('R'),
      emailFormat('E'),
    ]);
    expect(result).toBeNull();
  });

  it('skips first and catches second', () => {
    const result = runValidators('ab', [required('R'), minLength(3, 'M')]);
    expect(result).toBe('M');
  });
});
