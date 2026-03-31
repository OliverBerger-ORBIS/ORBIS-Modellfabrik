import assert from 'node:assert/strict';
import test from 'node:test';

import { utcIsoTimestampMs } from '../utc-iso-timestamp';

const MS_Z = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;

test('utcIsoTimestampMs returns ISO-8601 UTC with milliseconds and Z suffix', () => {
  const s = utcIsoTimestampMs();
  assert.match(s, MS_Z, `expected ${s} to match ${MS_Z}`);
});

test('utcIsoTimestampMs uses provided Date (UTC string shape)', () => {
  const d = new Date('2026-01-15T14:30:45.678Z');
  assert.strictEqual(utcIsoTimestampMs(d), '2026-01-15T14:30:45.678Z');
});

test('utcIsoTimestampMs matches Date#toISOString for same instant', () => {
  const d = new Date(Date.UTC(2025, 0, 1, 0, 0, 0, 1));
  assert.strictEqual(utcIsoTimestampMs(d), d.toISOString());
});
