import assert from 'node:assert/strict';
import test from 'node:test';
import { Subject } from 'rxjs';

import { createBusiness, type GatewayStreams } from '../index';
import type { GatewayPublishFn } from '@osf/gateway';

const subject = <T>() => new Subject<T>();

const createGateway = (): {
  streams: GatewayStreams;
  publishLog: Array<{ topic: string; payload: unknown; options?: { qos?: number; retain?: boolean } }>;
} => {
  const orders$ = subject();
  const stock$ = subject();
  const modules$ = subject();
  const fts$ = subject();
  const pairing$ = subject();
  const moduleFactsheets$ = subject();
  const stockSnapshots$ = subject();
  const flows$ = subject();
  const config$ = subject();
  const sensorBme680$ = subject();
  const sensorLdr$ = subject();
  const cameraFrames$ = subject();
  
  const publishLog: Array<{ topic: string; payload: unknown; options?: { qos?: number; retain?: boolean } }> = [];
  const publish: GatewayPublishFn = async (topic, payload, options) => {
    publishLog.push({ topic, payload, options });
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
    publishLog,
  };
};

test('calibrateModule publishes ccu/set/calibration with correct payload', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.calibrateModule('SVR3QA0022');

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'ccu/set/calibration');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.serialNumber, 'SVR3QA0022');
  assert.equal(payload.command, 'startCalibration');
  assert.equal(typeof payload.timestamp, 'string');
  assert.ok(payload.timestamp.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/), 'timestamp should be ISO format');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('calibrateModule does not publish if serialNumber is empty', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.calibrateModule('');

  assert.equal(publishLog.length, 0);
});

test('setFtsCharge publishes ccu/set/charge with charge=true', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.setFtsCharge('5iO4', true);

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'ccu/set/charge');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.serialNumber, '5iO4');
  assert.equal(payload.charge, true);
  // Note: ccu/set/charge does NOT include timestamp in payload (based on session logs)
  assert.equal(payload.timestamp, undefined, 'ccu/set/charge should not have timestamp');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('setFtsCharge publishes ccu/set/charge with charge=false (Stop Charging)', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.setFtsCharge('5iO4', false);

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'ccu/set/charge');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.serialNumber, '5iO4');
  assert.equal(payload.charge, false);
  // Note: ccu/set/charge does NOT include timestamp in payload (based on session logs)
  assert.equal(payload.timestamp, undefined, 'ccu/set/charge should not have timestamp');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('setFtsCharge does not publish if serialNumber is empty', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.setFtsCharge('', true);

  assert.equal(publishLog.length, 0);
});

test('dockFts publishes fts/v1/ff/{serial}/instantAction with correct payload', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.dockFts('5iO4', 'SVR4H73275');

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'fts/v1/ff/5iO4/instantAction');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.serialNumber, '5iO4');
  assert.equal(typeof payload.timestamp, 'string');
  assert.ok(Array.isArray(payload.actions));
  assert.equal(payload.actions.length, 1);
  
  const action = payload.actions[0];
  assert.equal(action.actionType, 'findInitialDockPosition');
  assert.equal(typeof action.actionId, 'string');
  assert.ok(action.actionId.startsWith('dock-'), 'actionId should start with "dock-"');
  assert.equal(action.metadata.nodeId, 'SVR4H73275');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('dockFts uses default nodeId SVR4H73275 if nodeId is not provided', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.dockFts('5iO4');

  assert.equal(publishLog.length, 1);
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.actions[0].metadata.nodeId, 'SVR4H73275');
});

test('dockFts uses default nodeId SVR4H73275 if nodeId is UNKNOWN', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.dockFts('5iO4', 'UNKNOWN');

  assert.equal(publishLog.length, 1);
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.actions[0].metadata.nodeId, 'SVR4H73275');
});

test('dockFts does not publish if serialNumber is empty', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.dockFts('');

  assert.equal(publishLog.length, 0);
});

test('sendCustomerOrder publishes ccu/order/request with correct payload', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.sendCustomerOrder('BLUE');

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'ccu/order/request');

  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.type, 'BLUE');
  assert.equal(payload.orderType, 'PRODUCTION');
  assert.equal(typeof payload.timestamp, 'string');
  assert.ok(payload.timestamp.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/), 'timestamp should be ISO format');
  assert.ok(
    payload.requestId?.match(/^OSF-UI_[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i),
    `requestId should match OSF-UI_<UUID>, got: ${payload.requestId}`
  );

  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('sendCustomerOrder generates unique requestId per call', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.sendCustomerOrder('BLUE');
  await business.sendCustomerOrder('RED');

  assert.equal(publishLog.length, 2);
  const id1 = (publishLog[0]?.payload as any).requestId;
  const id2 = (publishLog[1]?.payload as any).requestId;
  assert.notEqual(id1, id2, 'each order should have unique requestId');
  assert.ok(id1?.startsWith('OSF-UI_'), 'requestId should have OSF-UI_ prefix');
  assert.ok(id2?.startsWith('OSF-UI_'), 'requestId should have OSF-UI_ prefix');
});

test('sendCustomerOrder supports all workpiece types', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.sendCustomerOrder('WHITE');
  await business.sendCustomerOrder('RED');

  assert.equal(publishLog.length, 2);
  assert.equal((publishLog[0]?.payload as any).type, 'WHITE');
  assert.equal((publishLog[1]?.payload as any).type, 'RED');
});

test('sendCustomerOrder does not publish if workpieceType is empty', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.sendCustomerOrder('' as any);

  assert.equal(publishLog.length, 0);
});

test('requestRawMaterial publishes omf/order/raw_material with correct payload', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.requestRawMaterial('BLUE');

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'omf/order/raw_material');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.type, 'BLUE');
  assert.equal(payload.orderType, 'RAW_MATERIAL');
  assert.equal(payload.workpieceType, 'BLUE');
  assert.equal(typeof payload.timestamp, 'string');
  assert.ok(payload.timestamp.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/), 'timestamp should be ISO format');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('requestRawMaterial does not publish if workpieceType is empty', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.requestRawMaterial('' as any);

  assert.equal(publishLog.length, 0);
});

test('moveCamera publishes /j1/txt/1/o/ptu with correct payload for movement commands', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.moveCamera('relmove_up', 10);

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, '/j1/txt/1/o/ptu');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.cmd, 'relmove_up');
  assert.equal(payload.degree, 10);
  assert.equal(typeof payload.ts, 'string');
  // Format: ISO timestamp with milliseconds ending with Z (e.g., "2025-11-10T16:48:45.975Z")
  assert.ok(payload.ts.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/), 'ts should be ISO format with milliseconds ending with Z');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('moveCamera supports all movement commands', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.moveCamera('relmove_down', 5);
  await business.moveCamera('relmove_left', 15);
  await business.moveCamera('relmove_right', 20);
  await business.moveCamera('home', 0);

  assert.equal(publishLog.length, 4);
  assert.equal((publishLog[0]?.payload as any).cmd, 'relmove_down');
  assert.equal((publishLog[0]?.payload as any).degree, 5);
  assert.equal((publishLog[1]?.payload as any).cmd, 'relmove_left');
  assert.equal((publishLog[1]?.payload as any).degree, 15);
  assert.equal((publishLog[2]?.payload as any).cmd, 'relmove_right');
  assert.equal((publishLog[2]?.payload as any).degree, 20);
  assert.equal((publishLog[3]?.payload as any).cmd, 'home');
  // 'home' command should not have 'degree' field (based on examples)
  assert.equal((publishLog[3]?.payload as any).degree, undefined);
});

test('moveCamera with home command does not include degree field', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.moveCamera('home', 0);

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, '/j1/txt/1/o/ptu');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.cmd, 'home');
  assert.equal(typeof payload.ts, 'string');
  // 'home' command should not have 'degree' field (based on examples)
  assert.equal(payload.degree, undefined);
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('moveCamera with stop command does not include degree field', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.moveCamera('stop', 0);

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, '/j1/txt/1/o/ptu');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.cmd, 'stop');
  assert.equal(typeof payload.ts, 'string');
  // 'stop' command should not have 'degree' field (based on examples)
  assert.equal(payload.degree, undefined);
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('resetFactory publishes ccu/set/reset with default withStorage=false', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.resetFactory();

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'ccu/set/reset');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.withStorage, false);
  assert.equal(typeof payload.timestamp, 'string');
  assert.ok(payload.timestamp.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/), 'timestamp should be ISO format with milliseconds ending with Z');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('resetFactory publishes ccu/set/reset with withStorage=true when specified', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.resetFactory(true);

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'ccu/set/reset');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.withStorage, true);
  assert.equal(typeof payload.timestamp, 'string');
  assert.ok(payload.timestamp.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/), 'timestamp should be ISO format with milliseconds ending with Z');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

test('resetFactory publishes ccu/set/reset with withStorage=false when explicitly set', async () => {
  const { streams, publishLog } = createGateway();
  const business = createBusiness(streams);

  await business.resetFactory(false);

  assert.equal(publishLog.length, 1);
  assert.equal(publishLog[0]?.topic, 'ccu/set/reset');
  
  const payload = publishLog[0]?.payload as any;
  assert.equal(payload.withStorage, false);
  assert.equal(typeof payload.timestamp, 'string');
  assert.ok(payload.timestamp.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/), 'timestamp should be ISO format with milliseconds ending with Z');
  
  const options = publishLog[0]?.options;
  assert.equal(options?.qos, 1);
  assert.equal(options?.retain, false);
});

