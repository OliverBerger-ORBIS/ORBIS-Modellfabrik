export interface TimeRangeFilter {
  from?: Date;
  to?: Date;
  limit: number;
}

export type TimelineEventSource = 'osf' | 'module' | 'fts' | 'ccu' | 'unknown';

export interface WorkpieceSummaryDto {
  nfc: string;
  color: string | null;
  currentState: string | null;
  lastLocation: string | null;
  firstSeenAt: string | null;
  lastSeenAt: string | null;
}

export interface TimelineEventDto {
  ts: string;
  nfc: string;
  color: string | null;
  station: string;
  action: string | null;
  actionState: string | null;
  orderId: string | null;
  orderType: string | null;
  moduleSerial: string | null;
  eventSource: TimelineEventSource;
  eventType: string;
}

export interface ShopfloorEventQueryRow {
  id: number;
  ts: Date | string;
  event_type: string;
  topic: string;
  source: string;
  module_type: string | null;
  module_serial: string | null;
  order_id: string | null;
  workpiece_id: string;
  workpiece_type: string | null;
  action: string | null;
  action_state: string | null;
  order_type: string | null;
}

export interface WorkpieceQueryRow {
  workpiece_id: string;
  type: string | null;
  current_state: string | null;
  last_location: string | null;
  first_seen_at: Date | string | null;
  last_seen_at: Date | string | null;
}

export interface HistoryQueryStore {
  listWorkpieces(filter: TimeRangeFilter): Promise<WorkpieceSummaryDto[]>;
  listTimeline(nfc: string, filter: TimeRangeFilter): Promise<TimelineEventDto[]>;
}
