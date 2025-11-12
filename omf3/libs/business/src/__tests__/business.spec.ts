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
} from '@omf3/entities';

const subject = <T>() => new Subject<T>();

const createGateway = (): {
  streams: GatewayStreams;
  subjects: {
    orders$: Subject<OrderActive>;
    stock$: Subject<StockMessage>;
    modules$: Subject<ModuleState>;
    fts$: Subject<FtsState>;
  };
} => {
  const orders$ = subject<OrderActive>();
  const stock$ = subject<StockMessage>();
  const modules$ = subject<ModuleState>();
  const fts$ = subject<FtsState>();

  return {
    streams: {
      orders$: orders$.asObservable(),
      stock$: stock$.asObservable(),
      modules$: modules$.asObservable(),
      fts$: fts$.asObservable(),
    },
    subjects: {
      orders$,
      stock$,
      modules$,
      fts$,
    },
  };
};

test('aggregates order counts', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const countsPromise = firstValueFrom(business.orderCounts$.pipe(skip(3)));

  subjects.orders$.next({ orderId: 'o1', productId: 'A', quantity: 1, status: 'running' });
  subjects.orders$.next({ orderId: 'o2', productId: 'B', quantity: 2, status: 'queued' });
  subjects.orders$.next({ orderId: 'o3', productId: 'C', quantity: 1, status: 'completed' });

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

  subjects.orders$.next({ orderId: 'o1', productId: 'X', quantity: 1, status: 'running' });
  subjects.orders$.next({ orderId: 'o1', productId: 'X', quantity: 1, status: 'completed' });

  const active = await activePromise;
  const completed = await completedPromise;

  assert.equal(active['o1'], undefined);
  assert.equal(completed['o1']?.status, 'completed');
});

