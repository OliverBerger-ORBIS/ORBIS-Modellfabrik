import assert from 'node:assert/strict';
import test from 'node:test';

import { Subject, firstValueFrom } from 'rxjs';
import { take, toArray } from 'rxjs/operators';

import { createBusiness, type GatewayStreams } from '../index';
import type {
  FtsState,
  ModuleState,
  StockMessage,
  ModulePairingState,
  ModuleFactsheetSnapshot,
  StockSnapshot,
  ProductionFlowMap,
  CcuConfigSnapshot,
  Bme680Snapshot,
  LdrSnapshot,
  CameraFrame,
} from '@omf3/entities';
import type { OrderStreamPayload, GatewayPublishFn } from '@omf3/gateway';

const subject = <T>() => new Subject<T>();

const createTestGateway = (): {
  streams: GatewayStreams;
  emit: {
    order: (payload: OrderStreamPayload) => void;
    stock: (payload: StockMessage) => void;
    module: (payload: ModuleState) => void;
    fts: (payload: FtsState) => void;
    pairing: (payload: ModulePairingState) => void;
    factsheet: (payload: ModuleFactsheetSnapshot) => void;
    stockSnapshot: (payload: StockSnapshot) => void;
    flow: (payload: ProductionFlowMap) => void;
    config: (payload: CcuConfigSnapshot) => void;
    bme680: (payload: Bme680Snapshot) => void;
    ldr: (payload: LdrSnapshot) => void;
    camera: (payload: CameraFrame) => void;
  };
  publishLog: Array<{ topic: string; payload: unknown }>;
} => {
  const orders$ = subject<OrderStreamPayload>();
  const stock$ = subject<StockMessage>();
  const modules$ = subject<ModuleState>();
  const fts$ = subject<FtsState>();
  const pairing$ = subject<ModulePairingState>();
  const moduleFactsheets$ = subject<ModuleFactsheetSnapshot>();
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
      moduleFactsheets$: moduleFactsheets$.asObservable(),
      stockSnapshots$: stockSnapshots$.asObservable(),
      flows$: flows$.asObservable(),
      config$: config$.asObservable(),
      sensorBme680$: sensorBme680$.asObservable(),
      sensorLdr$: sensorLdr$.asObservable(),
      cameraFrames$: cameraFrames$.asObservable(),
      publish,
    },
    emit: {
      order: (payload: OrderStreamPayload) => orders$.next(payload),
      stock: (payload: StockMessage) => stock$.next(payload),
      module: (payload: ModuleState) => modules$.next(payload),
      fts: (payload: FtsState) => fts$.next(payload),
      pairing: (payload: ModulePairingState) => pairing$.next(payload),
      factsheet: (payload: ModuleFactsheetSnapshot) => moduleFactsheets$.next(payload),
      stockSnapshot: (payload: StockSnapshot) => stockSnapshots$.next(payload),
      flow: (payload: ProductionFlowMap) => flows$.next(payload),
      config: (payload: CcuConfigSnapshot) => config$.next(payload),
      bme680: (payload: Bme680Snapshot) => sensorBme680$.next(payload),
      ldr: (payload: LdrSnapshot) => sensorLdr$.next(payload),
      camera: (payload: CameraFrame) => cameraFrames$.next(payload),
    },
    publishLog,
  };
};

test('Business Integration: Gateway → Business Streams Integration', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  // Test that business streams are created
  assert.ok(business.moduleStates$);
  assert.ok(business.ftsStates$);
  assert.ok(business.moduleOverview$);
  assert.ok(business.inventoryOverview$);

  // Emit test data
  gateway.emit.module({
    moduleId: 'TEST-MODULE',
    state: 'ready',
    location: { x: 0, y: 0 },
  } as ModuleState);

  const moduleStates = await firstValueFrom(business.moduleStates$);
  assert.ok(moduleStates['TEST-MODULE']);
  assert.equal(moduleStates['TEST-MODULE'].state, 'ready');
});

test('Business Integration: Order Counts Aggregation', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  // Subscribe first
  const countsPromise = firstValueFrom(business.orderCounts$);

  // Then emit
  gateway.emit.order({
    order: {
      orderId: 'ORD-001',
      state: 'IN_PROGRESS',
      productId: 'BLUE',
      quantity: 1,
    } as any,
    topic: 'ccu/order/active',
  });

  const counts = await countsPromise;
  assert.ok(counts);
  assert.equal(typeof counts.running, 'number');
  assert.equal(typeof counts.queued, 'number');
  assert.equal(typeof counts.completed, 'number');
});

test('Business Integration: Stock By Part Aggregation', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const stockPromise = firstValueFrom(business.stockByPart$);

  // Emit stock message
  gateway.emit.stock({
    itemId: 'BLUE-WORKPIECE',
    location: 'HBW',
    quantity: 5,
    timestamp: new Date().toISOString(),
  } as StockMessage);

  const stock = await stockPromise;
  assert.ok(stock);
  assert.equal(typeof stock, 'object');
});

test('Business Integration: Module States Aggregation', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const statesPromise = lastValueFrom(business.moduleStates$.pipe(take(2), toArray()));

  // Emit multiple module states
  gateway.emit.module({
    moduleId: 'MOD-001',
    state: 'idle',
    location: { x: 0, y: 0 },
  } as ModuleState);

  gateway.emit.module({
    moduleId: 'MOD-002',
    state: 'working',
    location: { x: 100, y: 100 },
  } as ModuleState);

  const states = await statesPromise;
  assert.equal(states.length, 2);
  assert.ok(states[0]['MOD-001']);
  assert.ok(states[1]['MOD-002']);
});

test('Business Integration: FTS States Aggregation', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const ftsStatesPromise = firstValueFrom(business.ftsStates$);

  // Emit FTS state
  gateway.emit.fts({
    serialNumber: 'FTS-001',
    state: 'navigating',
    position: { x: 50, y: 50 },
    battery: 85,
  } as FtsState);

  const ftsStates = await ftsStatesPromise;
  assert.ok(ftsStates);
  assert.ok(ftsStates['FTS-001']);
  assert.equal(ftsStates['FTS-001'].state, 'navigating');
});

test('Business Integration: Module Overview State', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const overviewPromise = firstValueFrom(business.moduleOverview$);

  // Emit module state
  gateway.emit.module({
    moduleId: 'OVERVIEW-MOD',
    state: 'ready',
    location: { x: 0, y: 0 },
  } as ModuleState);

  const overview = await overviewPromise;
  assert.ok(overview);
  assert.equal(typeof overview, 'object');
});

test('Business Integration: Inventory Overview State', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const inventoryPromise = firstValueFrom(business.inventoryOverview$);

  // Emit stock snapshot
  gateway.emit.stockSnapshot({
    items: [
      {
        itemId: 'ITEM-001',
        location: 'HBW',
        quantity: 10,
      },
    ],
    timestamp: new Date().toISOString(),
  } as StockSnapshot);

  const inventory = await inventoryPromise;
  assert.ok(inventory);
  assert.equal(typeof inventory, 'object');
});

test('Business Integration: Production Flows Processing', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const flowsPromise = firstValueFrom(business.flows$);

  // Emit production flow
  gateway.emit.flow({
    flows: [
      {
        flowId: 'FLOW-001',
        source: 'HBW',
        target: 'MPO',
        partType: 'BLUE',
      },
    ],
    timestamp: new Date().toISOString(),
  } as ProductionFlowMap);

  const flows = await flowsPromise;
  assert.ok(flows);
  assert.ok(flows.flows);
});

test('Business Integration: Config Snapshot Processing', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const configPromise = firstValueFrom(business.config$);

  // Emit config snapshot
  gateway.emit.config({
    modules: {
      HBW: { moduleId: 'HBW', type: 'WAREHOUSE', enabled: true },
    },
    timestamp: new Date().toISOString(),
  } as CcuConfigSnapshot);

  const config = await configPromise;
  assert.ok(config);
  assert.ok(config.modules);
});

test('Business Integration: Sensor Overview Aggregation', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const sensorPromise = firstValueFrom(business.sensorOverview$);

  // Emit BME680 sensor data
  gateway.emit.bme680({
    sensors: {
      'sensor-001': {
        temperature: 22.5,
        humidity: 45,
        pressure: 1013.25,
        gasResistance: 50000,
        timestamp: new Date().toISOString(),
      },
    },
    timestamp: new Date().toISOString(),
  } as Bme680Snapshot);

  const sensorOverview = await sensorPromise;
  assert.ok(sensorOverview);
  assert.equal(typeof sensorOverview, 'object');
});

test('Business Integration: Camera Frames Pass-through', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const cameraPromise = firstValueFrom(business.cameraFrames$);

  // Emit camera frame
  gateway.emit.camera({
    moduleId: 'CAMERA-001',
    image: 'base64-encoded-image-data',
    timestamp: new Date().toISOString(),
  } as CameraFrame);

  const frame = await cameraPromise;
  assert.ok(frame);
  assert.equal(frame.moduleId, 'CAMERA-001');
  assert.ok(frame.image);
});

test('Business Integration: Multiple Stream Updates', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  // Subscribe to multiple streams
  const modulePromise = firstValueFrom(business.moduleStates$);
  const ftsPromise = firstValueFrom(business.ftsStates$);

  // Emit to multiple streams
  gateway.emit.module({
    moduleId: 'MULTI-MOD',
    state: 'working',
    location: { x: 10, y: 10 },
  } as ModuleState);

  gateway.emit.fts({
    serialNumber: 'MULTI-FTS',
    state: 'charging',
    position: { x: 20, y: 20 },
    battery: 95,
  } as FtsState);

  const [modules, fts] = await Promise.all([modulePromise, ftsPromise]);

  assert.ok(modules['MULTI-MOD']);
  assert.ok(fts['MULTI-FTS']);
});

test('Business Integration: State Persistence Across Updates', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  const statesPromise = lastValueFrom(business.moduleStates$.pipe(take(3), toArray()));

  // Emit initial state
  gateway.emit.module({
    moduleId: 'PERSIST-MOD',
    state: 'idle',
    location: { x: 0, y: 0 },
  } as ModuleState);

  // Update same module
  gateway.emit.module({
    moduleId: 'PERSIST-MOD',
    state: 'working',
    location: { x: 0, y: 0 },
  } as ModuleState);

  // Add different module
  gateway.emit.module({
    moduleId: 'ANOTHER-MOD',
    state: 'ready',
    location: { x: 100, y: 100 },
  } as ModuleState);

  const states = await statesPromise;
  assert.equal(states.length, 3);
  // Last state should have both modules
  assert.ok(states[2]['PERSIST-MOD']);
  assert.ok(states[2]['ANOTHER-MOD']);
  assert.equal(states[2]['PERSIST-MOD'].state, 'working');
});

test('Business Integration: Publish Commands', async () => {
  const gateway = createTestGateway();
  const business = createBusiness(gateway.streams);

  // Test that business has access to publish
  assert.ok(business);

  // Verify publish log is empty initially
  assert.equal(gateway.publishLog.length, 0);

  // Note: Business layer exposes command functions that use publish internally
  // This test verifies the integration is set up correctly
});
