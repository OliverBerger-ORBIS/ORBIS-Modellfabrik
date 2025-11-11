import { createBusiness } from '@omf3/business';
import { createGateway, type RawMqttMessage } from '@omf3/gateway';
import { createMqttClient, MockMqttAdapter } from '@omf3/mqtt-client';
import type {
  FtsState,
  ModuleState,
  OrderActive,
  StockMessage,
} from '@omf3/entities';
import { map, scan, shareReplay } from 'rxjs/operators';
import { Subject, type Observable } from 'rxjs';

export interface DashboardStreams {
  activeOrders$: Observable<OrderActive[]>;
  orderCounts$: Observable<Record<'running' | 'queued' | 'completed', number>>;
  stockByPart$: Observable<Record<string, number>>;
  moduleStates$: Observable<Record<string, ModuleState>>;
  ftsStates$: Observable<Record<string, FtsState>>;
}

export const createMockDashboardStreams = (): DashboardStreams => {
  const adapter = new MockMqttAdapter();
  const client = createMqttClient(adapter);

  const rawMessages$ = new Subject<RawMqttMessage>();

  adapter.messages$.subscribe((message) => {
    rawMessages$.next({
      topic: message.topic,
      payload: message.payload,
      timestamp: message.timestamp,
      qos: message.options?.qos,
      retain: message.options?.retain,
    });
  });

  void client.connect('mock://ccu-ui');

  const topics = [
    'ccu/order/active',
    'warehouse/stock/level',
    'module/v1/ff/SVR3QA0022/state',
    'module/v1/ff/SVR4H73275/state',
    'fts/v1/demo/alpha',
  ];

  topics.forEach((topic) => {
    void client.subscribe(topic);
  });

  const gateway = createGateway(rawMessages$.asObservable());
  const business = createBusiness(gateway);

  seedMockData(client);

  const activeOrders$ = gateway.orders$.pipe(
    scan(
      (acc, order) => {
        if (!order.orderId) {
          return acc;
        }
        return { ...acc, [order.orderId]: order };
      },
      {} as Record<string, OrderActive>
    ),
    map((orders) => Object.values(orders)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  return {
    activeOrders$,
    orderCounts$: business.orderCounts$,
    stockByPart$: business.stockByPart$,
    moduleStates$: business.moduleStates$,
    ftsStates$: business.ftsStates$,
  };
};

const publish = (
  client: ReturnType<typeof createMqttClient>,
  topic: string,
  payload: unknown
) => {
  void client.publish(topic, JSON.stringify(payload));
};

const seedMockData = (client: ReturnType<typeof createMqttClient>) => {
  publish(client, 'ccu/order/active', {
    orderId: 'ORDER-1001',
    productId: 'Widget-A',
    quantity: 2,
    status: 'running',
    startedAt: new Date().toISOString(),
  } satisfies OrderActive);

  publish(client, 'ccu/order/active', {
    orderId: 'ORDER-1002',
    productId: 'Widget-B',
    quantity: 1,
    status: 'queued',
  } satisfies OrderActive);

  publish(client, 'warehouse/stock/level', {
    moduleId: 'HBW',
    partId: 'Widget-A',
    amount: 12,
  } satisfies StockMessage);

  publish(client, 'warehouse/stock/level', {
    moduleId: 'HBW',
    partId: 'Widget-B',
    amount: 5,
  } satisfies StockMessage);

  publish(client, 'module/v1/ff/SVR3QA0022/state', {
    moduleId: 'SVR3QA0022',
    state: 'working',
    lastSeen: new Date().toISOString(),
    details: { orderId: 'ORDER-1001' },
  } satisfies ModuleState);

  publish(client, 'module/v1/ff/SVR4H73275/state', {
    moduleId: 'SVR4H73275',
    state: 'idle',
    lastSeen: new Date().toISOString(),
  } satisfies ModuleState);

  publish(client, 'fts/v1/demo/alpha', {
    ftsId: 'FTS-Alpha',
    position: { x: 12, y: 6 },
    status: 'moving',
  } satisfies FtsState);
};

