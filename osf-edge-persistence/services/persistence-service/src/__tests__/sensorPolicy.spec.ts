import { describe, expect, it } from 'vitest';
import { createSensorPolicyState, resolveSensorReason, shouldPersistReason } from '../sensorPolicy';

describe('sensor policy', () => {
  it('persists EVENT and THRESHOLD always', () => {
    const state = createSensorPolicyState();
    const ts = new Date('2026-05-08T10:00:00.000Z');
    expect(shouldPersistReason('EVENT', ts, 'm1', 3600, state)).toBe(true);
    expect(shouldPersistReason('THRESHOLD', ts, 'm1', 3600, state)).toBe(true);
  });

  it('persists INTERVAL only when interval is due', () => {
    const state = createSensorPolicyState();
    const key = 'arduino:station:magnitude';
    const t1 = new Date('2026-05-08T10:00:00.000Z');
    const t2 = new Date('2026-05-08T10:10:00.000Z');
    const t3 = new Date('2026-05-08T11:10:00.000Z');
    expect(shouldPersistReason('INTERVAL', t1, key, 3600, state)).toBe(true);
    expect(shouldPersistReason('INTERVAL', t2, key, 3600, state)).toBe(false);
    expect(shouldPersistReason('INTERVAL', t3, key, 3600, state)).toBe(true);
  });

  it('detects explicit payload reasons', () => {
    const state = createSensorPolicyState();
    const ts = new Date('2026-05-08T10:00:00.000Z');
    expect(resolveSensorReason({ reason: 'EVENT' }, 'k1', ts, 3600, state)).toBe('EVENT');
    expect(resolveSensorReason({ reason: 'THRESHOLD' }, 'k1', ts, 3600, state)).toBe('THRESHOLD');
    expect(resolveSensorReason({ reason: 'INTERVAL' }, 'k1', ts, 3600, state)).toBe('INTERVAL');
  });
});
