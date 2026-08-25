import { SensorReason } from './types';

export interface SensorPolicyState {
  lastIntervalByKey: Map<string, number>;
  activeOrderIds: Set<string>;
  /** Orders seen via response/active — used to ignore CCU completed-history dumps. */
  knownOrderIds: Set<string>;
}

export function createSensorPolicyState(): SensorPolicyState {
  return {
    lastIntervalByKey: new Map(),
    activeOrderIds: new Set(),
    knownOrderIds: new Set(),
  };
}

export function hasActiveOrders(state: SensorPolicyState): boolean {
  return state.activeOrderIds.size > 0;
}

function orderIdFromUnknown(value: unknown): string | undefined {
  if (!value || typeof value !== 'object') {
    return undefined;
  }
  const orderId = (value as { orderId?: unknown }).orderId;
  return typeof orderId === 'string' && orderId.length > 0 ? orderId : undefined;
}

/** Replace the in-memory active-order set from a `ccu/order/active` payload. */
export function updateActiveOrdersFromPayload(payload: unknown, state: SensorPolicyState): void {
  const ids = new Set<string>();
  if (Array.isArray(payload)) {
    for (const item of payload) {
      const id = orderIdFromUnknown(item);
      if (id) {
        ids.add(id);
      }
    }
  } else if (payload && typeof payload === 'object') {
    const rec = payload as Record<string, unknown>;
    const direct = orderIdFromUnknown(rec);
    if (direct) {
      ids.add(direct);
    } else {
      for (const value of Object.values(rec)) {
        const id = orderIdFromUnknown(value);
        if (id) {
          ids.add(id);
        }
      }
    }
  }
  state.activeOrderIds = ids;
}

export function effectiveSensorIntervalSeconds(
  activeIntervalSeconds: number,
  idleIntervalSeconds: number,
  state: SensorPolicyState
): number {
  return hasActiveOrders(state) ? activeIntervalSeconds : idleIntervalSeconds;
}

function isWarnOrAlarmPayload(payload: Record<string, unknown>): boolean {
  if (payload.alarm === true || payload.warn === true || payload.thresholdExceeded === true) {
    return true;
  }
  const vibrationLevel = typeof payload.vibrationLevel === 'string' ? payload.vibrationLevel.toLowerCase() : '';
  if (vibrationLevel === 'yellow' || vibrationLevel === 'red') {
    return true;
  }
  if (payload.flameDetected === true) {
    return true;
  }
  const gasLevel = payload.gasLevel;
  if (payload.gasDetected === true || (typeof gasLevel === 'number' && Number.isFinite(gasLevel) && gasLevel >= 1)) {
    return true;
  }
  return false;
}

export function resolveSensorReason(
  payload: Record<string, unknown>,
  _metricKey: string,
  _ts: Date,
  _intervalSeconds: number,
  _state: SensorPolicyState
): SensorReason {
  const explicitReason = payload.reason;
  if (explicitReason === 'EVENT' || explicitReason === 'THRESHOLD' || explicitReason === 'INTERVAL') {
    return explicitReason;
  }

  if (payload.event === true || payload.triggered === true) {
    return 'EVENT';
  }
  if (isWarnOrAlarmPayload(payload)) {
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
