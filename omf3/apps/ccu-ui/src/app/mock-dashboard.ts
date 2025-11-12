import { createBusiness } from '@omf3/business';
import { createGateway, type RawMqttMessage } from '@omf3/gateway';
import type { FtsState, ModuleState } from '@omf3/entities';
import {
  createOrderFixtureStream,
  type FixtureStreamOptions,
  type OrderFixtureName,
} from '@omf3/testing-fixtures';
import { Subject, type Observable, Subscription } from 'rxjs';
import { map, scan, shareReplay } from 'rxjs/operators';
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

const createStreamSet = (messages$: Subject<RawMqttMessage>): DashboardStreamSet => {
  const gateway = createGateway(messages$.asObservable());
  const business = createBusiness(gateway);

  const orders$ = business.orders$.pipe(
    map((orders) => Object.values(orders)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  const completedOrders$ = business.completedOrders$.pipe(
    map((orders) => Object.values(orders)),
    shareReplay({ bufferSize: 1, refCount: true })
  );

  return {
    orders$,
    completedOrders$,
    orderCounts$: business.orderCounts$,
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

