import { SensorReason } from './types';

export interface SensorPolicyState {
  lastIntervalByKey: Map<string, number>;
}

export function createSensorPolicyState(): SensorPolicyState {
  return {
    lastIntervalByKey: new Map<string, number>(),
  };
}

export function resolveSensorReason(
  payload: Record<string, unknown>,
  metricKey: string,
  ts: Date,
  intervalSeconds: number,
  state: SensorPolicyState
): SensorReason {
  const explicitReason = payload.reason;
  if (explicitReason === 'EVENT' || explicitReason === 'THRESHOLD' || explicitReason === 'INTERVAL') {
    return explicitReason;
  }

  if (payload.event === true || payload.triggered === true) {
    return 'EVENT';
  }
  if (payload.alarm === true || payload.warn === true || payload.thresholdExceeded === true) {
    return 'THRESHOLD';
  }

  return 'INTERVAL';
}

export function shouldPersistReason(
  reason: SensorReason,
  ts: Date,
  metricKey: string,
  intervalSeconds: number,
  state: SensorPolicyState
): boolean {
  if (reason === 'EVENT' || reason === 'THRESHOLD') {
    return true;
  }

  const tsMs = ts.getTime();
  const last = state.lastIntervalByKey.get(metricKey);
  if (last === undefined || tsMs - last >= intervalSeconds * 1000) {
    state.lastIntervalByKey.set(metricKey, tsMs);
    return true;
  }
  return false;
}
