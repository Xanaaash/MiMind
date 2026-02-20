export type Validator = (value: string) => string | null;

export function required(message: string): Validator {
  return (value) => (value.trim().length === 0 ? message : null);
}

export function minLength(min: number, message: string): Validator {
  return (value) => (value.trim().length < min ? message : null);
}

export function maxLength(max: number, message: string): Validator {
  return (value) => (value.trim().length > max ? message : null);
}

export function emailFormat(message: string): Validator {
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return (value) => (EMAIL_RE.test(value.trim()) ? null : message);
}

export function runValidators(value: string, validators: Validator[]): string | null {
  for (const validator of validators) {
    const result = validator(value);
    if (result) return result;
  }
  return null;
}
