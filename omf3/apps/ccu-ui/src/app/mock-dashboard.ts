import { createBusiness } from '@omf3/business';
import { createGateway, type RawMqttMessage, type OrderStreamPayload, type GatewayPublishFn } from '@omf3/gateway';
import type { FtsState, ModuleState, ModuleOverviewState, InventoryOverviewState } from '@omf3/entities';
import {
  createModulePairingFixtureStream,
  createOrderFixtureStream,
  createStockFixtureStream,
  type FixtureStreamOptions,
  type ModuleFixtureName,
  type OrderFixtureName,
  type StockFixtureName,
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
  moduleOverview$: Observable<ModuleOverviewState>;
  inventoryOverview$: Observable<InventoryOverviewState>;
}

export interface DashboardCommandSet {
  calibrateModule: (serialNumber: string) => Promise<void>;
  setFtsCharge: (serialNumber: string, charge: boolean) => Promise<void>;
  dockFts: (serialNumber: string, nodeId?: string) => Promise<void>;
  sendCustomerOrder: (workpieceType: string) => Promise<void>;
  requestRawMaterial: (workpieceType: string) => Promise<void>;
}

export interface MockDashboardController {
  streams: DashboardStreamSet;
  commands: DashboardCommandSet;
  loadFixture: (fixture: OrderFixtureName, options?: FixtureStreamOptions) => Promise<DashboardStreamSet>;
  getCurrentFixture: () => OrderFixtureName;
}

const FIXTURE_DEFAULT_INTERVAL = 25;
const resolveModuleFixture = (fixture: OrderFixtureName): ModuleFixtureName => {
  if (
    fixture === 'white' ||
    fixture === 'blue' ||
    fixture === 'red' ||
    fixture === 'mixed' ||
    fixture === 'storage' ||
    fixture === 'startup'
  ) {
    return fixture;
  }
  return 'default';
};

const resolveStockFixture = (fixture: OrderFixtureName): StockFixtureName => {
  if (fixture === 'startup') {
    return 'startup';
  }
  return 'default';
};

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

const createStreamSet = (messages$: Subject<RawMqttMessage>): {
  streams: DashboardStreamSet;
  commands: DashboardCommandSet;
} => {
  const publish: GatewayPublishFn = async (topic, payload, options) => {
    console.info('[mock-dashboard] publish', topic, payload, options);
  };

  const gateway = createGateway(messages$.asObservable(), { publish });
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
    streams: {
      orders$,
      completedOrders$,
      orderCounts$,
      stockByPart$: business.stockByPart$,
      moduleStates$: business.moduleStates$,
      ftsStates$: business.ftsStates$,
      moduleOverview$: business.moduleOverview$,
      inventoryOverview$: business.inventoryOverview$,
    },
    commands: {
      calibrateModule: business.calibrateModule,
      setFtsCharge: business.setFtsCharge,
      dockFts: business.dockFts,
      sendCustomerOrder: business.sendCustomerOrder,
      requestRawMaterial: business.requestRawMaterial,
    },
  };
};

export const createMockDashboardController = (): MockDashboardController => {
  let messageSubject = new Subject<RawMqttMessage>();
  let bundle = createStreamSet(messageSubject);
  let currentReplays: Subscription[] = [];
  let currentFixture: OrderFixtureName = 'startup';

  const unsubscribeReplays = () => {
    currentReplays.forEach((sub) => sub.unsubscribe());
    currentReplays = [];
  };

  const resetStreams = () => {
    unsubscribeReplays();
    messageSubject.complete();
    messageSubject = new Subject<RawMqttMessage>();
    bundle = createStreamSet(messageSubject);
  };

  const loadFixture = async (
    fixture: OrderFixtureName,
    options?: FixtureStreamOptions
  ): Promise<DashboardStreamSet> => {
    unsubscribeReplays();
    resetStreams();

    const replay$ = createOrderFixtureStream(fixture, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      baseUrl: options?.baseUrl,
      loader: options?.loader,
      loop: options?.loop,
    });

    currentReplays.push(replay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    const moduleFixtureName = resolveModuleFixture(fixture);
    const moduleReplay$ = createModulePairingFixtureStream(moduleFixtureName, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      loader: options?.loader,
      loop: options?.loop,
    });
    currentReplays.push(moduleReplay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    const stockFixtureName = resolveStockFixture(fixture);
    const stockReplay$ = createStockFixtureStream(stockFixtureName, {
      intervalMs: options?.intervalMs ?? FIXTURE_DEFAULT_INTERVAL,
      loader: options?.loader,
      loop: options?.loop,
    });
    currentReplays.push(stockReplay$.subscribe((message: RawMqttMessage) => messageSubject.next(message)));

    currentFixture = fixture;
    return bundle.streams;
  };

  return {
    get streams() {
      return bundle.streams;
    },
    get commands() {
      return bundle.commands;
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

