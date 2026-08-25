import { describe, expect, it } from 'vitest';
import {
  asDate,
  extractPayload,
  pickNumber,
  pickString,
  stableHash,
  toRecord,
} from '../utils';

describe('utils (DB-agnostic)', () => {
  it('stableHash is deterministic for the same object shape', () => {
    expect(stableHash({ a: 1, b: 'x' })).toBe(stableHash({ a: 1, b: 'x' }));
    expect(stableHash({ a: 1 })).not.toBe(stableHash({ a: 2 }));
  });

  it('asDate parses ISO strings and rejects invalid input', () => {
    const d = asDate('2026-08-25T10:00:00.000Z');
    expect(d).toBeInstanceOf(Date);
    expect(d?.toISOString()).toBe('2026-08-25T10:00:00.000Z');
    expect(asDate('')).toBeUndefined();
    expect(asDate('not-a-date')).toBeUndefined();
    expect(asDate(123)).toBeUndefined();
  });

  it('toRecord wraps objects and falls back to empty object', () => {
    expect(toRecord({ k: 1 })).toEqual({ k: 1 });
    expect(toRecord(null)).toEqual({});
    expect(toRecord('x')).toEqual({});
  });

  it('extractPayload unwraps nested stringified payload envelopes', () => {
    const inner = { type: 'BLUE', nfc: 'abc' };
    const wrapped = JSON.stringify({
      payload: JSON.stringify({ payload: inner }),
    });
    expect(extractPayload(wrapped)).toEqual(inner);
  });

  it('extractPayload returns outer object when payload is not JSON', () => {
    const raw = JSON.stringify({ payload: 'plain-text', keep: true });
    expect(extractPayload(raw)).toEqual({ payload: 'plain-text', keep: true });
  });

  it('pickString returns first non-empty string key', () => {
    expect(pickString({ a: '', b: 'ok' }, 'a', 'b')).toBe('ok');
    expect(pickString({ a: 1 }, 'a')).toBeUndefined();
  });

  it('pickNumber returns first finite number key', () => {
    expect(pickNumber({ a: NaN, b: 3.5 }, 'a', 'b')).toBe(3.5);
    expect(pickNumber({ a: '1' }, 'a')).toBeUndefined();
  });
});
