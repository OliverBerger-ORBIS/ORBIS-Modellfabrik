import { resolveModuleType } from './moduleSerialMap';
import type {
  ShopfloorEventQueryRow,
  TimelineEventDto,
  TimelineEventSource,
  TimeRangeFilter,
  WorkpieceQueryRow,
  WorkpieceSummaryDto,
} from './queryTypes';

export const QUERY_LIMIT_DEFAULT = 500;
export const QUERY_LIMIT_MAX = 2000;

const NFC_PATTERN = /^[A-Za-z0-9_-]{6,128}$/;

export function isValidNfcId(value: string): boolean {
  return NFC_PATTERN.test(value);
}

export function clampQueryLimit(raw: number | undefined): number {
  if (raw === undefined || !Number.isFinite(raw)) {
    return QUERY_LIMIT_DEFAULT;
  }
  const n = Math.trunc(raw);
  if (n < 1) {
    return QUERY_LIMIT_DEFAULT;
  }
  return Math.min(n, QUERY_LIMIT_MAX);
}

export function parseQueryInstant(value: string | null): Date | undefined {
  if (!value || !value.trim()) {
    return undefined;
  }
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    throw new Error(`Invalid timestamp: ${value}`);
  }
  return parsed;
}

export function parseTimeRangeFilter(search: URLSearchParams): TimeRangeFilter {
  return {
    from: parseQueryInstant(search.get('from')),
    to: parseQueryInstant(search.get('to')),
    limit: clampQueryLimit(search.get('limit') ? Number(search.get('limit')) : undefined),
  };
}

export function toIsoTimestamp(value: Date | string | null | undefined): string | null {
  if (value === null || value === undefined) {
    return null;
  }
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value.toISOString();
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? String(value) : parsed.toISOString();
}

export function mapEventSource(source: string, topic: string): TimelineEventSource {
  const normalized = (source || '').toLowerCase();
  if (normalized === 'osf' || topic === 'osf/workpiece/intake') {
    return 'osf';
  }
  if (normalized === 'module' || topic.startsWith('module/')) {
    return 'module';
  }
  if (normalized === 'fts' || topic.startsWith('fts/')) {
    return 'fts';
  }
  if (normalized === 'ccu' || topic.startsWith('ccu/')) {
    return 'ccu';
  }
  return 'unknown';
}

export function resolveTimelineStation(row: {
  topic: string;
  source: string;
  module_type: string | null;
  module_serial: string | null;
}): string {
  if (row.source === 'osf' || row.topic === 'osf/workpiece/intake') {
    return 'DPS';
  }
  const mapped = resolveModuleType({
    payloadModuleType: row.module_type ?? undefined,
    topicModuleType: row.topic.startsWith('fts/') ? 'FTS' : undefined,
    moduleSerial: row.module_serial ?? undefined,
  });
  if (mapped) {
    return mapped;
  }
  if (row.topic.startsWith('fts/')) {
    return 'FTS';
  }
  return row.module_type?.trim() || '—';
}

export function mapWorkpieceRow(row: WorkpieceQueryRow): WorkpieceSummaryDto {
  return {
    nfc: row.workpiece_id,
    color: row.type,
    currentState: row.current_state,
    lastLocation: row.last_location,
    firstSeenAt: toIsoTimestamp(row.first_seen_at),
    lastSeenAt: toIsoTimestamp(row.last_seen_at),
  };
}

export function mapTimelineRow(row: ShopfloorEventQueryRow): TimelineEventDto {
  const ts = toIsoTimestamp(row.ts) ?? new Date(0).toISOString();
  return {
    ts,
    nfc: row.workpiece_id,
    color: row.workpiece_type,
    station: resolveTimelineStation(row),
    action: row.action,
    actionState: row.action_state,
    orderId: row.order_id,
    orderType: row.order_type,
    moduleSerial: row.module_serial,
    eventSource: mapEventSource(row.source, row.topic),
    eventType: row.event_type,
  };
}
