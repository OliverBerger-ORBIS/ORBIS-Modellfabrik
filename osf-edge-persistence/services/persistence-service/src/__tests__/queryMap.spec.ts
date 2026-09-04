import { describe, expect, it } from 'vitest';
import {
  clampQueryLimit,
  isValidNfcId,
  mapEventSource,
  mapTimelineRow,
  mapWorkpieceRow,
  parseTimeRangeFilter,
  QUERY_LIMIT_DEFAULT,
  QUERY_LIMIT_MAX,
  resolveTimelineStation,
} from '../queryMap';

describe('queryMap nfc and limits', () => {
  it('accepts B-soft style NFC ids', () => {
    expect(isValidNfcId('92e0ad91595f63')).toBe(true);
    expect(isValidNfcId('ab')).toBe(false);
    expect(isValidNfcId('../etc/passwd')).toBe(false);
    expect(isValidNfcId('nfc;drop')).toBe(false);
  });

  it('clamps limit', () => {
    expect(clampQueryLimit(undefined)).toBe(QUERY_LIMIT_DEFAULT);
    expect(clampQueryLimit(0)).toBe(QUERY_LIMIT_DEFAULT);
    expect(clampQueryLimit(9_999)).toBe(QUERY_LIMIT_MAX);
    expect(clampQueryLimit(12)).toBe(12);
  });

  it('parses from/to query params', () => {
    const filter = parseTimeRangeFilter(
      new URLSearchParams('from=2026-09-03T08:00:00.000Z&to=2026-09-03T12:00:00.000Z&limit=20')
    );
    expect(filter.limit).toBe(20);
    expect(filter.from?.toISOString()).toBe('2026-09-03T08:00:00.000Z');
    expect(filter.to?.toISOString()).toBe('2026-09-03T12:00:00.000Z');
  });

  it('rejects invalid from timestamp', () => {
    expect(() => parseTimeRangeFilter(new URLSearchParams('from=not-a-date'))).toThrow(
      /Invalid timestamp/
    );
  });
});

describe('queryMap station and source', () => {
  it('maps intake to DPS / osf', () => {
    expect(
      resolveTimelineStation({
        topic: 'osf/workpiece/intake',
        source: 'osf',
        module_type: null,
        module_serial: null,
      })
    ).toBe('DPS');
    expect(mapEventSource('osf', 'osf/workpiece/intake')).toBe('osf');
  });

  it('maps known module serials', () => {
    expect(
      resolveTimelineStation({
        topic: 'module/v1/ff/SVR4H76449/state',
        source: 'module',
        module_type: null,
        module_serial: 'SVR4H76449',
      })
    ).toBe('DRILL');
  });

  it('maps FTS serial topics to FTS', () => {
    expect(
      resolveTimelineStation({
        topic: 'fts/v1/ff/5iO4/state',
        source: 'fts',
        module_type: 'FTS',
        module_serial: '5iO4',
      })
    ).toBe('FTS');
    expect(mapEventSource('fts', 'fts/v1/ff/5iO4/state')).toBe('fts');
  });
});

describe('queryMap DTO mapping', () => {
  it('maps workpiece rows', () => {
    const dto = mapWorkpieceRow({
      workpiece_id: '92e0ad91595f63',
      type: 'WHITE',
      current_state: 'FINISHED',
      last_location: 'DPS',
      first_seen_at: new Date('2026-09-03T09:00:00.000Z'),
      last_seen_at: new Date('2026-09-03T10:00:00.000Z'),
    });
    expect(dto.nfc).toBe('92e0ad91595f63');
    expect(dto.color).toBe('WHITE');
    expect(dto.lastSeenAt).toBe('2026-09-03T10:00:00.000Z');
  });

  it('maps FINISHED module events with order join', () => {
    const dto = mapTimelineRow({
      id: 1,
      ts: new Date('2026-09-03T09:15:00.000Z'),
      event_type: 'PICK',
      topic: 'module/v1/ff/SVR3QA0022/state',
      source: 'module',
      module_type: 'HBW',
      module_serial: 'SVR3QA0022',
      order_id: 'ord-1',
      workpiece_id: '92e0ad91595f63',
      workpiece_type: 'WHITE',
      action: 'PICK',
      action_state: 'FINISHED',
      order_type: 'STORAGE',
    });
    expect(dto.station).toBe('HBW');
    expect(dto.eventSource).toBe('module');
    expect(dto.orderType).toBe('STORAGE');
    expect(dto.action).toBe('PICK');
  });
});
