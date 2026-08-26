import { pickString, toRecord } from './utils';

const NFC_REJECT = new Set(['PASSED', 'FAILED', 'OK', 'NOK', 'ERROR', 'SUCCESS']);

export function isNfcLikeId(value: string | undefined): boolean {
  if (!value) {
    return false;
  }
  const trimmed = value.trim();
  if (trimmed.length < 6) {
    return false;
  }
  return !NFC_REJECT.has(trimmed.toUpperCase());
}

export function asNfcId(value: unknown): string | undefined {
  if (typeof value !== 'string' || !isNfcLikeId(value)) {
    return undefined;
  }
  return value.trim();
}

function actionStateRecord(payload: Record<string, unknown>): Record<string, unknown> {
  return toRecord(payload.actionState);
}

function metadataRecord(action: Record<string, unknown>): Record<string, unknown> {
  return toRecord(action.metadata);
}

/** NFC ids from FTS `load[]` or module `loads[]` (NFC-like loadId only). */
export function collectLoadNfcIds(payload: Record<string, unknown>): string[] {
  const buckets = [payload.load, payload.loads];
  const ids: string[] = [];
  const seen = new Set<string>();
  for (const bucket of buckets) {
    if (!Array.isArray(bucket)) {
      continue;
    }
    for (const item of bucket) {
      const row = toRecord(item);
      const id = asNfcId(row.loadId);
      if (id && !seen.has(id)) {
        seen.add(id);
        ids.push(id);
      }
    }
  }
  return ids;
}

/**
 * Stateless NFC resolution for a single MQTT payload (Replay + Live).
 * Primary sources are APS fields that exist in session logs:
 * CCU workpieceId, RGB_NFC/PICK/DROP result, FTS loadId.
 * `nfc` on osf/workpiece/intake — live bridge and/or session logs (patched references).
 * No sticky maps / cross-message order lookup (those stay in OSF-UI T&T).
 */
export function resolveWorkpieceId(payload: Record<string, unknown>): string | undefined {
  const top = asNfcId(pickString(payload, 'workpieceId', 'nfc'));
  if (top) {
    return top;
  }

  const action = actionStateRecord(payload);
  const command = (pickString(action, 'command') ?? '').toUpperCase();
  const resultId = asNfcId(action.result);
  if (resultId && (command === 'RGB_NFC' || command === 'PICK' || command === 'DROP')) {
    return resultId;
  }

  const metaWp = metadataRecord(action).workpiece;
  if (metaWp && typeof metaWp === 'object') {
    const metaId = asNfcId(toRecord(metaWp).workpieceId);
    if (metaId) {
      return metaId;
    }
  }

  const nestedOrder = toRecord(payload.order);
  const orderWp = asNfcId(pickString(nestedOrder, 'workpieceId'));
  if (orderWp) {
    return orderWp;
  }

  const loadIds = collectLoadNfcIds(payload);
  // Single carrier id only — never pick first of a multi-load remainder (same as T&T).
  if (loadIds.length === 1) {
    return loadIds[0];
  }
  return undefined;
}

function asWorkpieceColor(value: string | undefined): string | undefined {
  if (!value) {
    return undefined;
  }
  const upper = value.toUpperCase();
  return upper === 'WHITE' || upper === 'RED' || upper === 'BLUE' || upper === 'UNKNOWN' ? upper : undefined;
}

export function resolveWorkpieceType(payload: Record<string, unknown>): string | undefined {
  const top = asWorkpieceColor(pickString(payload, 'workpieceType', 'productRaw', 'type'));
  if (top) {
    return top;
  }
  const action = actionStateRecord(payload);
  const metaType = asWorkpieceColor(pickString(metadataRecord(action), 'type'));
  if (metaType) {
    return metaType;
  }
  const commandMetaType = asWorkpieceColor(
    pickString(metadataRecord(toRecord(payload.action)), 'type')
  );
  if (commandMetaType) {
    return commandMetaType;
  }
  const loadBuckets = [payload.load, payload.loads];
  const colors = new Set<string>();
  for (const bucket of loadBuckets) {
    if (!Array.isArray(bucket)) {
      continue;
    }
    for (const item of bucket) {
      const color = asWorkpieceColor(pickString(toRecord(item), 'loadType', 'type'));
      if (color && color !== 'UNKNOWN') {
        colors.add(color);
      }
    }
  }
  if (colors.size === 1) {
    return [...colors][0];
  }
  return undefined;
}
