import assert from 'node:assert/strict';
import test from 'node:test';

import { Subject, firstValueFrom } from 'rxjs';
import { skip } from 'rxjs/operators';

import { createBusiness, type GatewayStreams } from '@omf3/business';
import type {
  FtsState,
  ModuleState,
  OrderActive,
  StockMessage,
  ModulePairingState,
} from '@omf3/entities';
import type { OrderStreamPayload, GatewayPublishFn } from '@omf3/gateway';

const subject = <T>() => new Subject<T>();

const createGateway = (): {
  streams: GatewayStreams;
  subjects: {
    orders$: Subject<OrderStreamPayload>;
    stock$: Subject<StockMessage>;
    modules$: Subject<ModuleState>;
    fts$: Subject<FtsState>;
    pairing$: Subject<ModulePairingState>;
  };
} => {
  const orders$ = subject<OrderStreamPayload>();
  const stock$ = subject<StockMessage>();
  const modules$ = subject<ModuleState>();
  const fts$ = subject<FtsState>();
  const pairing$ = subject<ModulePairingState>();
  const publish: GatewayPublishFn = async () => {
    // noop for tests
  };

  return {
    streams: {
      orders$: orders$.asObservable(),
      stock$: stock$.asObservable(),
      modules$: modules$.asObservable(),
      fts$: fts$.asObservable(),
      pairing$: pairing$.asObservable(),
      publish,
    },
    subjects: {
      orders$,
      stock$,
      modules$,
      fts$,
      pairing$,
    },
  };
};

test('aggregates order counts', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const countsPromise = firstValueFrom(business.orderCounts$.pipe(skip(3)));

  subjects.orders$.next({ order: { orderId: 'o1', productId: 'A', quantity: 1, status: 'running' }, topic: 'ccu/order/active' });
  subjects.orders$.next({ order: { orderId: 'o2', productId: 'B', quantity: 2, status: 'queued' }, topic: 'ccu/order/active' });
  subjects.orders$.next({ order: { orderId: 'o3', productId: 'C', quantity: 1, status: 'completed' }, topic: 'ccu/order/completed' });

  const counts = await countsPromise;
  assert.equal(counts.running, 1);
  assert.equal(counts.queued, 1);
  assert.equal(counts.completed, 1);
});

test('summarises stock per part', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const levelsPromise = firstValueFrom(business.stockByPart$.pipe(skip(2)));

  subjects.stock$.next({ moduleId: 'm1', partId: 'PARTX', amount: 10 });
  subjects.stock$.next({ moduleId: 'm1', partId: 'PARTX', amount: 20 });

  const levels = await levelsPromise;
  assert.equal(levels.PARTX, 30);
});

test('captures latest module and fts states', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const modulePromise = firstValueFrom(business.moduleStates$.pipe(skip(1)));
  const ftsPromise = firstValueFrom(business.ftsStates$.pipe(skip(1)));

  subjects.modules$.next({ moduleId: 'SVR3QA0022', state: 'working' });
  subjects.fts$.next({ ftsId: '5iO4', status: 'moving' });

  const moduleStates = await modulePromise;
  const ftsStates = await ftsPromise;

  assert.equal(moduleStates.SVR3QA0022?.state, 'working');
  assert.equal(ftsStates['5iO4']?.status, 'moving');
});

test('moves completed orders to completed stream', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const activePromise = firstValueFrom(business.orders$.pipe(skip(2)));
  const completedPromise = firstValueFrom(business.completedOrders$.pipe(skip(2)));

  subjects.orders$.next({ order: { orderId: 'o1', productId: 'X', quantity: 1, status: 'running' }, topic: 'ccu/order/active' });
  subjects.orders$.next({ order: { orderId: 'o1', productId: 'X', quantity: 1, status: 'completed' }, topic: 'ccu/order/completed' });

  const active = await activePromise;
  const completed = await completedPromise;

  assert.equal(active['o1'], undefined);
  assert.equal(completed['o1']?.status, 'completed');
});

test('aggregates module pairing overview', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const overviewPromise = firstValueFrom(business.moduleOverview$.pipe(skip(1)));

  subjects.pairing$.next({
    modules: [
      {
        serialNumber: 'SVR3QA0022',
        connected: true,
        available: 'READY',
        hasCalibration: true,
        subType: 'HBW',
      },
    ],
    transports: [
      {
        serialNumber: '5iO4',
        connected: true,
        available: 'READY',
        charging: false,
      },
    ],
    timestamp: '2025-11-10T18:02:09.702936',
  });

  const overview = await overviewPromise;
  assert.equal(overview.modules['SVR3QA0022'].connected, true);
  assert.equal(overview.modules['SVR3QA0022'].messageCount, 1);
  assert.equal(overview.modules['SVR3QA0022'].lastUpdate, '2025-11-10T18:02:09.702936');
  assert.equal(overview.transports['5iO4'].availability, 'READY');
});

