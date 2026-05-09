export type SensorReason = 'EVENT' | 'INTERVAL' | 'THRESHOLD';

export interface ShopfloorEventRow {
  ts: Date;
  dedupKey: string;
  eventType: string;
  topic: string;
  source: string;
  moduleType?: string;
  moduleSerial?: string;
  orderId?: string;
  workpieceId?: string;
  workpieceType?: string;
  action?: string;
  actionState?: string;
  payload: Record<string, unknown>;
}

export interface ProductionOrderRow {
  orderId: string;
  orderType?: string;
  workpieceId?: string;
  workpieceType?: string;
  state?: string;
  receivedAt?: Date;
  startedAt?: Date;
  stoppedAt?: Date;
}

export interface ProductionStepRow {
  dedupKey: string;
  orderId?: string;
  stepId?: string;
  stepType?: string;
  moduleType?: string;
  moduleSerial?: string;
  command?: string;
  state?: string;
  source?: string;
  target?: string;
  startedAt?: Date;
  stoppedAt?: Date;
  payload: Record<string, unknown>;
}

export interface WorkpieceRow {
  workpieceId: string;
  type?: string;
  currentState?: string;
  lastLocation?: string;
  firstSeenAt?: Date;
  lastSeenAt?: Date;
}

export interface SensorSnapshotRow {
  ts: Date;
  source: 'arduino' | 'txt' | 'module';
  stationId?: string;
  sensorType?: string;
  metricName: string;
  valueNumeric?: number;
  valueText?: string;
  unit?: string;
  reason: SensorReason;
  orderId?: string;
  workpieceId?: string;
  relatedEventDedupKey?: string;
  payload: Record<string, unknown>;
  dedupKey: string;
}

export interface RawMessageRow {
  receivedAt: Date;
  topic: string;
  qos: number;
  retain: boolean;
  payloadJson?: unknown;
  payloadText?: string;
  persistedReason: string;
  payloadHash: string;
  dedupKey: string;
}

export interface NormalizedMessage {
  raw?: RawMessageRow;
  shopfloorEvents: ShopfloorEventRow[];
  productionOrders: ProductionOrderRow[];
  productionSteps: ProductionStepRow[];
  workpieces: WorkpieceRow[];
  sensorSnapshots: SensorSnapshotRow[];
}
