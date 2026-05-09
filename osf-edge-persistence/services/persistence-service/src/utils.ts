import { createHash } from 'node:crypto';

export function stableHash(input: unknown): string {
  return createHash('sha256').update(JSON.stringify(input)).digest('hex');
}

export function asDate(value: unknown): Date | undefined {
  if (typeof value !== 'string' || value.length === 0) {
    return undefined;
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? undefined : date;
}

export function toRecord(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

export function extractPayload(raw: string): unknown {
  const parsed = JSON.parse(raw) as unknown;
  let current = parsed;

  for (let depth = 0; depth < 4; depth += 1) {
    if (current && typeof current === 'object' && 'payload' in current) {
      const payload = (current as Record<string, unknown>).payload;
      if (typeof payload === 'string') {
        try {
          current = JSON.parse(payload);
          continue;
        } catch {
          return current;
        }
      }
      if (payload && typeof payload === 'object') {
        current = payload;
        continue;
      }
    }
    break;
  }

  return current;
}

export function pickString(source: Record<string, unknown>, ...keys: string[]): string | undefined {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === 'string' && value.length > 0) {
      return value;
    }
  }
  return undefined;
}

export function pickNumber(source: Record<string, unknown>, ...keys: string[]): number | undefined {
  for (const key of keys) {
    const value = source[key];
    if (typeof value === 'number' && Number.isFinite(value)) {
      return value;
    }
  }
  return undefined;
}
