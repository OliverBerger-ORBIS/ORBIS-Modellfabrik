import { describe, expect, it } from 'vitest';
import {
  createSensorPolicyState,
  effectiveSensorIntervalSeconds,
  resolveSensorReason,
  shouldPersistReason,
  updateActiveOrdersFromPayload,
} from '../sensorPolicy';

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

  it('treats Arduino warn/alarm payloads as THRESHOLD', () => {
    const state = createSensorPolicyState();
    const ts = new Date('2026-05-08T10:00:00.000Z');
    expect(resolveSensorReason({ vibrationLevel: 'red', magnitude: 20000 }, 'k', ts, 5, state)).toBe(
      'THRESHOLD'
    );
    expect(resolveSensorReason({ vibrationLevel: 'yellow', magnitude: 12000 }, 'k', ts, 5, state)).toBe(
      'THRESHOLD'
    );
    expect(resolveSensorReason({ flameDetected: true, rawValue: 12 }, 'k', ts, 5, state)).toBe('THRESHOLD');
    expect(resolveSensorReason({ gasDetected: true, gasLevel: 2, rawValue: 800 }, 'k', ts, 5, state)).toBe(
      'THRESHOLD'
    );
    expect(resolveSensorReason({ gasLevel: 1, gasDetected: false, rawValue: 520 }, 'k', ts, 5, state)).toBe(
      'THRESHOLD'
    );
  });

  it('keeps quiet Arduino telemetry as INTERVAL', () => {
    const state = createSensorPolicyState();
    const ts = new Date('2026-05-08T10:00:00.000Z');
    expect(resolveSensorReason({ vibrationLevel: 'green', magnitude: 800 }, 'k', ts, 5, state)).toBe(
      'INTERVAL'
    );
    expect(resolveSensorReason({ flameDetected: false, rawValue: 40 }, 'k', ts, 5, state)).toBe('INTERVAL');
    expect(resolveSensorReason({ gasDetected: false, gasLevel: 0, rawValue: 150 }, 'k', ts, 5, state)).toBe(
      'INTERVAL'
    );
  });

  it('uses 5s while orders are active and idle interval otherwise', () => {
    const state = createSensorPolicyState();
    expect(effectiveSensorIntervalSeconds(5, 60, state)).toBe(60);
    updateActiveOrdersFromPayload([{ orderId: 'o-1' }], state);
    expect(effectiveSensorIntervalSeconds(5, 60, state)).toBe(5);
    updateActiveOrdersFromPayload([], state);
    expect(effectiveSensorIntervalSeconds(5, 60, state)).toBe(60);
  });
});
