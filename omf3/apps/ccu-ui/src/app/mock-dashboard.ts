import { createBusiness } from '@omf3/business';
import { createGateway, type RawMqttMessage, type OrderStreamPayload } from '@omf3/gateway';
import type { FtsState, ModuleState } from '@omf3/entities';
import {
  createOrderFixtureStream,
  type FixtureStreamOptions,
  type OrderFixtureName,
} from '@omf3/testing-fixtures';
import { Subject, type Observable, Subscription } from 'rxjs';
import { map, scan, shareReplay, startWith } from 'rxjs/operators';
import type { OrderActive } from '@omf3/entities';

export interface DashboardStreamSet {
  orders$: Observable<OrderActive[]>;
  completedOrders$: Observable<OrderActive[]>;
  orderCounts$: Observable<Record<'running' | 'queued' | 'completed', number>>;
  stockByPart$: Observable<Record<string, number>>;
  moduleStates$: Observable<Record<string, ModuleState>>;
  ftsStates$: Observable<Record<string, FtsState>>;
}

export interface MockDashboardController {
  streams: DashboardStreamSet;
  loadFixture: (fixture: OrderFixtureName, options?: FixtureStreamOptions) => Promise<DashboardStreamSet>;
  getCurrentFixture: () => OrderFixtureName;
}

const FIXTURE_DEFAULT_INTERVAL = 25;

interface OrdersAccumulator {
  active: Record<string, OrderActive>;
  completed: Record<string, OrderActive>;
}

const COMPLETION_STATES = new Set(['COMPLETED', 'FINISHED']);

const normalizeOrder = (order: OrderActive): OrderActive => {
  const normalizedState = (order.state ?? order.status ?? '').toUpperCase();
  return {
    ...order,
    state: normalizedState,
    status: order.status ?? order.state ?? normalizedState.toLowerCase(),
  };
};

const accumulateOrders = (acc: OrdersAccumulator, payload: OrderStreamPayload): OrdersAccumulator => {
  const { order } = payload;
  if (!order.orderId) {
    return acc;
  }

  const harmonized = normalizeOrder(order);
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

const createStreamSet = (messages$: Subject<RawMqttMessage>): DashboardStreamSet => {
  const gateway = createGateway(messages$.asObservable());
  const business = createBusiness(gateway);

  const ordersState$ = gateway.orders$.pipe(
    scan(accumulateOrders, { active: {}, completed: {} } as OrdersAccumulator),
    startWith({ active: {}, completed: {} } as OrdersAccumulator),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const orders$ = ordersState$.pipe(
    map((state) => Object.values(state.active)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const completedOrders$ = ordersState$.pipe(
    map((state) => Object.values(state.completed)),
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
        const stateValue = (order.state ?? '').toUpperCase();
        if (stateValue === 'RUNNING' || stateValue === 'IN_PROGRESS') {
          counts.running += 1;
        } else {
          counts.queued += 1;
        }
      });

      return counts;
    }),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  return {
    orders$,
    completedOrders$,
    orderCounts$,
    stockByPart$: business.stockByPart$,
    moduleStates$: business.moduleStates$,
    ftsStates$: business.ftsStates$,
  };
};

export const createMockDashboardController = (): MockDashboardController => {
  let messageSubject = new Subject<RawMqttMessage>();
  let streams = createStreamSet(messageSubject);
  let currentReplay: Subscription | null = null;
  let currentFixture: OrderFixtureName = 'white';

  const resetStreams = () => {
    messageSubject.complete();
    messageSubject = new Subject<RawMqttMessage>();
    streams = createStreamSet(messageSubject);
  };

  const loadFixture = async (
    fixture: OrderFixtureName,
    options?: FixtureStreamOptions
  ): Promise<DashboardStreamSet> => {
    if (currentReplay) {
      currentReplay.unsubscribe();
      currentReplay = null;
    }

    resetStreams();

    const replay$ = createOrderFixtureStream(fixture, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      baseUrl: options?.baseUrl,
      loader: options?.loader,
      loop: options?.loop,
    });

    currentReplay = replay$.subscribe((message) => messageSubject.next(message));
    currentFixture = fixture;
    return streams;
  };

  return {
    get streams() {
      return streams;
    },
    loadFixture,
    getCurrentFixture() {
      return currentFixture;
    },
  };
};

let sharedController: MockDashboardController | null = null;

export const getDashboardController = (): MockDashboardController => {
  if (!sharedController) {
    sharedController = createMockDashboardController();
  }
  return sharedController;
};

