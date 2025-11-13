import { Observable } from 'rxjs';
import { filter, map, mergeMap, shareReplay } from 'rxjs/operators';

import {
  safeJsonParse,
  OrderActive,
  StockMessage,
  ModuleState,
  FtsState,
  ModulePairingState,
  ModuleFactsheetSnapshot,
  StockSnapshot,
  ProductionFlowMap,
} from '@omf3/entities';

export interface GatewayPublishOptions {
  qos?: 0 | 1 | 2;
  retain?: boolean;
}

export type GatewayPublishFn = (
  topic: string,
  payload: unknown,
  options?: GatewayPublishOptions
) => Promise<void>;

export type OrderStreamPayload = {
  order: OrderActive;
  topic: 'ccu/order/active' | 'ccu/order/completed' | string;
};

export interface RawMqttMessage<T = unknown> {
  topic: string;
  payload: T;
  timestamp?: string;
  qos?: number;
  retain?: boolean;
}

export interface GatewayStreams {
  orders$: Observable<OrderStreamPayload>;
  stock$: Observable<StockMessage>;
  modules$: Observable<ModuleState>;
  fts$: Observable<FtsState>;
  pairing$: Observable<ModulePairingState>;
  moduleFactsheets$: Observable<ModuleFactsheetSnapshot>;
  stockSnapshots$: Observable<StockSnapshot>;
  flows$: Observable<ProductionFlowMap>;
  publish: GatewayPublishFn;
}

const matchTopic = (topic: string, prefix: string) => topic.startsWith(prefix);

const parsePayload = <T>(payload: unknown): T | null => {
  const parsed = safeJsonParse(payload);
  return typeof parsed === 'object' && parsed !== null ? (parsed as T) : null;
};

const extractModuleSerialFromTopic = (topic: string): string | null => {
  const parts = topic.split('/');
  if (parts.length < 4) {
    return null;
  }

  // Patterns we expect:
  // module/v1/ff/<serial>/factsheet
  // module/v1/ff/NodeRed/<serial>/factsheet
  if (parts[0] !== 'module' || parts[1] !== 'v1') {
    return null;
  }

  if (parts[2] === 'ff' && parts.length >= 5) {
    if (parts[3] === 'NodeRed' && parts.length >= 6) {
      return parts[4];
    }
    return parts[3];
  }

  return null;
};

export const createGateway = (
  mqttMessages$: Observable<RawMqttMessage>,
  options?: {
    publish?: GatewayPublishFn;
  }
): GatewayStreams => {
  const publish: GatewayPublishFn =
    options?.publish ??
    (async (topic, payload) => {
      console.warn('[gateway] publish called without implementation', {
        topic,
        payload,
      });
    });

  const shared = mqttMessages$.pipe(shareReplay({ bufferSize: 1, refCount: true }));

  const orders$ = shared.pipe(
    filter((msg) => matchTopic(msg.topic, 'ccu/order')),
    map((msg) => ({
      topic: msg.topic,
      payload: parsePayload<OrderActive | OrderActive[]>(msg.payload),
    })),
    filter(
      (entry): entry is { topic: string; payload: OrderActive | OrderActive[] } =>
        entry.payload !== null
    ),
    mergeMap((entry) =>
      Array.isArray(entry.payload)
        ? entry.payload.map((order) => ({ topic: entry.topic, order }))
        : [{ topic: entry.topic, order: entry.payload }]
    ),
    filter((entry): entry is OrderStreamPayload => entry.order !== null)
  );

  const stock$ = shared.pipe(
    filter((msg) => matchTopic(msg.topic, 'warehouse/stock')),
    map((msg) => parsePayload<StockMessage>(msg.payload)),
    filter((payload): payload is StockMessage => payload !== null)
  );

  const modules$ = shared.pipe(
    filter((msg) => matchTopic(msg.topic, 'module/v1')),
    map((msg) => parsePayload<ModuleState>(msg.payload)),
    filter((payload): payload is ModuleState => payload !== null)
  );

  const fts$ = shared.pipe(
    filter((msg) => matchTopic(msg.topic, 'fts/v1')),
    map((msg) => parsePayload<FtsState>(msg.payload)),
    filter((payload): payload is FtsState => payload !== null)
  );

  const pairing$ = shared.pipe(
    filter((msg) => msg.topic === 'ccu/pairing/state'),
    map((msg) => ({
      payload: parsePayload<ModulePairingState>(msg.payload),
      fallbackTimestamp: msg.timestamp ?? new Date().toISOString(),
    })),
    filter(
      (
        entry
      ): entry is {
        payload: ModulePairingState;
        fallbackTimestamp: string;
      } => entry.payload !== null
    ),
    map(({ payload, fallbackTimestamp }) => ({
      ...payload,
      timestamp: payload.timestamp ?? fallbackTimestamp,
    })),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const moduleFactsheets$ = shared.pipe(
    filter((msg) => msg.topic.startsWith('module/v1/') && msg.topic.endsWith('/factsheet')),
    map((msg) => {
      const parsed = parsePayload<ModuleFactsheetSnapshot>(msg.payload);
      if (!parsed) {
        return null;
      }

      const serial = parsed.serialNumber ?? extractModuleSerialFromTopic(msg.topic);
      if (!serial) {
        return null;
      }

      return {
        ...parsed,
        serialNumber: serial,
        timestamp: parsed.timestamp ?? msg.timestamp ?? new Date().toISOString(),
        topic: msg.topic,
      } as ModuleFactsheetSnapshot;
    }),
    filter(
      (snapshot): snapshot is ModuleFactsheetSnapshot =>
        snapshot !== null && typeof snapshot.serialNumber === 'string'
    ),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const stockSnapshots$ = shared.pipe(
    filter((msg) => msg.topic === 'ccu/state/stock'),
    map((msg) => {
      const parsed = parsePayload<StockSnapshot>(msg.payload);
      if (!parsed) {
        return null;
      }

      return {
        ...parsed,
        ts: parsed.ts ?? msg.timestamp ?? new Date().toISOString(),
      } as StockSnapshot;
    }),
    filter((snapshot): snapshot is StockSnapshot => snapshot !== null && Array.isArray(snapshot.stockItems)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const flows$ = shared.pipe(
    filter((msg) => msg.topic === 'ccu/state/flows'),
    map((msg) => parsePayload<ProductionFlowMap>(msg.payload)),
    filter((payload): payload is ProductionFlowMap => payload !== null),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  return {
    orders$,
    stock$,
    modules$,
    fts$,
    pairing$,
    moduleFactsheets$,
    stockSnapshots$,
    flows$,
    publish,
  };
};

