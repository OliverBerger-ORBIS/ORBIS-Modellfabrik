import { Observable } from 'rxjs';
import { map, scan, shareReplay, startWith } from 'rxjs/operators';

import type {
  FtsState,
  ModuleState,
  OrderActive,
  StockMessage,
} from '@omf3/entities';
import { OrderStreamPayload } from '@omf3/gateway';

export interface GatewayStreams {
  orders$: Observable<OrderStreamPayload>;
  stock$: Observable<StockMessage>;
  modules$: Observable<ModuleState>;
  fts$: Observable<FtsState>;
}

export interface BusinessStreams {
  orders$: Observable<Record<string, OrderActive>>;
  completedOrders$: Observable<Record<string, OrderActive>>;
  orderCounts$: Observable<Record<'running' | 'queued' | 'completed', number>>;
  stockByPart$: Observable<Record<string, number>>;
  moduleStates$: Observable<Record<string, ModuleState>>;
  ftsStates$: Observable<Record<string, FtsState>>;
}

const COMPLETION_STATES = new Set(['COMPLETED', 'FINISHED']);

interface OrdersAccumulator {
  active: Record<string, OrderActive>;
  completed: Record<string, OrderActive>;
}

const normalizeState = (order: OrderActive): string => (order.state ?? order.status ?? '').toUpperCase();

const harmonizeOrder = (order: OrderActive): OrderActive => ({
  ...order,
  state: normalizeState(order),
});

const accumulateOrders = (acc: OrdersAccumulator, payload: OrderStreamPayload): OrdersAccumulator => {
  const { order } = payload;
  if (!order.orderId) {
    return acc;
  }

  const harmonized = harmonizeOrder(order);
  const state = harmonized.state ?? '';

  const nextActive = { ...acc.active };
  const nextCompleted = { ...acc.completed };

  if (COMPLETION_STATES.has(state) || payload.topic.includes('/completed')) {
    nextCompleted[harmonized.orderId] = harmonized;
    delete nextActive[harmonized.orderId];
  } else {
    nextActive[harmonized.orderId] = harmonized;
    if (nextCompleted[harmonized.orderId]) {
      delete nextCompleted[harmonized.orderId];
    }
  }

  return {
    active: nextActive,
    completed: nextCompleted,
  };
};

export const createBusiness = (gateway: GatewayStreams): BusinessStreams => {
  const ordersState$ = gateway.orders$.pipe(
    scan(accumulateOrders, { active: {}, completed: {} } as OrdersAccumulator),
    startWith({ active: {}, completed: {} } as OrdersAccumulator),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const orders$ = ordersState$.pipe(
    map((state) => state.active),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const completedOrders$ = ordersState$.pipe(
    map((state) => state.completed),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const orderCounts$ = ordersState$.pipe(
    map((state) => {
      const counts = {
        running: 0,
        queued: 0,
        completed: Object.keys(state.completed).length,
      };

      Object.values(state.active).forEach((order) => {
        const normalized = normalizeState(order);
        if (normalized === 'QUEUED' || normalized === 'PENDING' || normalized === '') {
          counts.queued += 1;
        } else if (['RUNNING', 'IN_PROGRESS'].includes(normalized)) {
          counts.running += 1;
        }
      });

      return counts;
    }),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const stockByPart$ = gateway.stock$.pipe(
    scan(
      (acc, msg) => {
        if (!msg.partId) {
          return acc;
        }

        const next = { ...acc };
        next[msg.partId] = (next[msg.partId] ?? 0) + (msg.amount ?? 0);
        return next;
      },
      {} as Record<string, number>
    ),
    startWith({} as Record<string, number>),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const moduleStates$ = gateway.modules$.pipe(
    scan(
      (acc, module) => {
        if (!module.moduleId) {
          return acc;
        }

        return { ...acc, [module.moduleId]: module };
      },
      {} as Record<string, ModuleState>
    ),
    startWith({} as Record<string, ModuleState>),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const ftsStates$ = gateway.fts$.pipe(
    scan(
      (acc, fts) => {
        const id = fts.ftsId ?? 'unknown';
        return { ...acc, [id]: fts };
      },
      {} as Record<string, FtsState>
    ),
    startWith({} as Record<string, FtsState>),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  return {
    orders$,
    completedOrders$,
    orderCounts$,
    stockByPart$,
    moduleStates$,
    ftsStates$,
  };
};

