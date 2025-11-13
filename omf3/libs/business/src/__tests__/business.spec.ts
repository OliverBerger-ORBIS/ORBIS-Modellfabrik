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
  StockSnapshot,
  ProductionFlowMap,
  CcuConfigSnapshot,
  Bme680Snapshot,
  LdrSnapshot,
  CameraFrame,
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
    stockSnapshots$: Subject<StockSnapshot>;
    flows$: Subject<ProductionFlowMap>;
    config$: Subject<CcuConfigSnapshot>;
    sensorBme680$: Subject<Bme680Snapshot>;
    sensorLdr$: Subject<LdrSnapshot>;
    cameraFrames$: Subject<CameraFrame>;
  };
  publishLog: Array<{ topic: string; payload: unknown }>;
} => {
  const orders$ = subject<OrderStreamPayload>();
  const stock$ = subject<StockMessage>();
  const modules$ = subject<ModuleState>();
  const fts$ = subject<FtsState>();
  const pairing$ = subject<ModulePairingState>();
  const stockSnapshots$ = subject<StockSnapshot>();
  const flows$ = subject<ProductionFlowMap>();
  const config$ = subject<CcuConfigSnapshot>();
  const sensorBme680$ = subject<Bme680Snapshot>();
  const sensorLdr$ = subject<LdrSnapshot>();
  const cameraFrames$ = subject<CameraFrame>();
  const publishLog: Array<{ topic: string; payload: unknown }> = [];
  const publish: GatewayPublishFn = async (topic, payload) => {
    publishLog.push({ topic, payload });
  };

  return {
    streams: {
      orders$: orders$.asObservable(),
      stock$: stock$.asObservable(),
      modules$: modules$.asObservable(),
      fts$: fts$.asObservable(),
      pairing$: pairing$.asObservable(),
      stockSnapshots$: stockSnapshots$.asObservable(),
      flows$: flows$.asObservable(),
      config$: config$.asObservable(),
      sensorBme680$: sensorBme680$.asObservable(),
      sensorLdr$: sensorLdr$.asObservable(),
      cameraFrames$: cameraFrames$.asObservable(),
      publish,
    },
    subjects: {
      orders$,
      stock$,
      modules$,
      fts$,
      pairing$,
      stockSnapshots$,
      flows$,
      config$,
      sensorBme680$,
      sensorLdr$,
      cameraFrames$,
    },
    publishLog,
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

test('aggregates inventory overview', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const inventoryPromise = firstValueFrom(business.inventoryOverview$.pipe(skip(1)));

  subjects.stockSnapshots$.next({
    ts: '2025-11-10T16:47:29.479Z',
    stockItems: [
      { location: 'A1', workpiece: { id: 'w1', type: 'BLUE', state: 'RAW' } },
      { location: 'B2', workpiece: { id: 'w2', type: 'RED', state: 'RESERVED' } },
    ],
  });

  const inventory = await inventoryPromise;
  assert.equal(inventory.availableCounts.BLUE, 1);
  assert.equal(inventory.reservedCounts.RED, 1);
  assert.equal(inventory.slots.A1?.workpiece?.type, 'BLUE');
  assert.equal(inventory.slots.B2?.workpiece?.state, 'RESERVED');
});

test('sends customer order via publish', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.sendCustomerOrder('BLUE');

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'ccu/order/request');
  assert.equal((publishLog[0]?.payload as any)?.type, 'BLUE');
});

test('exposes flows stream', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const flowsPromise = firstValueFrom(business.flows$.pipe(skip(1)));

  subjects.flows$.next({
    BLUE: { steps: ['DRILL', 'MILL', 'AIQS'] },
    RED: { steps: ['MILL', 'AIQS'] },
  });

  const flows = await flowsPromise;
  assert.equal(flows.BLUE.steps.length, 3);
  assert.equal(flows.RED.steps[0], 'MILL');
});

test('exposes config stream', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const configPromise = firstValueFrom(business.config$.pipe(skip(1)));

  subjects.config$.next({
    productionDurations: { BLUE: 550, WHITE: 580, RED: 560 },
    productionSettings: { maxParallelOrders: 4 },
    ftsSettings: { chargeThresholdPercent: 10 },
    timestamp: '2025-11-10T17:48:46.094154',
  });

  const config = await configPromise;
  assert.equal(config.productionSettings?.maxParallelOrders, 4);
  assert.equal(config.productionDurations?.BLUE, 550);
  assert.equal(config.ftsSettings?.chargeThresholdPercent, 10);
});

test('aggregates sensor overview', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const sensorPromise = firstValueFrom(business.sensorOverview$.pipe(skip(1)));

  subjects.sensorBme680$.next({
    ts: '2025-11-10T16:48:42.378Z',
    t: 22,
    h: 48,
    p: 1013,
    aq: 2.5,
  });
  subjects.sensorLdr$.next({
    ts: '2025-11-10T16:48:41.961Z',
    ldr: 9500,
  });

  const overview = await sensorPromise;
  assert.equal(overview.temperatureC, 22);
  assert.equal(overview.humidityPercent, 48);
  assert.equal(overview.pressureHpa, 1013);
  assert.equal(overview.lightLux, 9500);
  assert.equal(overview.airQualityScore, 2.5);
  assert.equal(overview.airQualityClassification, 'Moderate');
});

test('passes through camera frames', async () => {
  const { streams, subjects } = createGateway();
  const business = createBusiness(streams);

  const framePromise = firstValueFrom(business.cameraFrames$);

  subjects.cameraFrames$.next({
    timestamp: '2025-11-10T16:48:45.975Z',
    dataUrl: 'data:image/jpeg;base64,AAA',
  });

  const frame = await framePromise;
  assert.equal(frame.timestamp, '2025-11-10T16:48:45.975Z');
  assert.equal(frame.dataUrl, 'data:image/jpeg;base64,AAA');
});

