import { Observable } from 'rxjs';
import { map, scan, shareReplay, startWith } from 'rxjs/operators';

import type {
  FtsState,
  ModuleState,
  OrderActive,
  StockMessage,
} from '@omf3/entities';

export interface GatewayStreams {
  orders$: Observable<OrderActive>;
  stock$: Observable<StockMessage>;
  modules$: Observable<ModuleState>;
  fts$: Observable<FtsState>;
}

export interface BusinessStreams {
  orderCounts$: Observable<Record<'running' | 'queued' | 'completed', number>>;
  stockByPart$: Observable<Record<string, number>>;
  moduleStates$: Observable<Record<string, ModuleState>>;
  ftsStates$: Observable<Record<string, FtsState>>;
}

export const createBusiness = (gateway: GatewayStreams): BusinessStreams => {
  const ordersState$ = gateway.orders$.pipe(
    scan(
      (acc, order) => {
        if (!order.orderId) {
          return acc;
        }

        return { ...acc, [order.orderId]: order };
      },
      {} as Record<string, OrderActive>
    ),
    startWith({} as Record<string, OrderActive>),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const orderCounts$ = ordersState$.pipe(
    map((orders) => {
      const counts = {
        running: 0,
        queued: 0,
        completed: 0,
      };

      Object.values(orders).forEach((order) => {
        if (order.status === 'running') counts.running += 1;
        if (order.status === 'queued') counts.queued += 1;
        if (order.status === 'completed') counts.completed += 1;
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
    orderCounts$,
    stockByPart$,
    moduleStates$,
    ftsStates$,
  };
};

