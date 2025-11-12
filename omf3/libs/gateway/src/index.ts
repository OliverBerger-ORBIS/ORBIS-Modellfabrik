import { Observable } from 'rxjs';
import { filter, map, mergeMap, shareReplay } from 'rxjs/operators';

import {
  safeJsonParse,
  OrderActive,
  StockMessage,
  ModuleState,
  FtsState,
} from '@omf3/entities';

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
}

const matchTopic = (topic: string, prefix: string) => topic.startsWith(prefix);

const parsePayload = <T>(payload: unknown): T | null => {
  const parsed = safeJsonParse(payload);
  return typeof parsed === 'object' && parsed !== null ? (parsed as T) : null;
};

export const createGateway = (
  mqttMessages$: Observable<RawMqttMessage>
): GatewayStreams => {
  const shared = mqttMessages$.pipe(shareReplay({ bufferSize: 1, refCount: true }));

  const orders$ = shared.pipe(
    filter((msg) => matchTopic(msg.topic, 'ccu/order')),
    map((msg) => parsePayload<OrderActive | OrderActive[]>(msg.payload)),
    filter((payload): payload is OrderActive | OrderActive[] => payload !== null),
    mergeMap((payload) => (Array.isArray(payload) ? payload : [payload])),
    filter((payload): payload is OrderActive => payload !== null)
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

  return {
    orders$,
    stock$,
    modules$,
    fts$,
  };
};

