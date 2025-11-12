import assert from 'node:assert/strict';
import test from 'node:test';

import { Subject, firstValueFrom } from 'rxjs';
import { skip } from 'rxjs/operators';

import { createGateway, RawMqttMessage } from '@omf3/gateway';

const createMessage = (topic: string, payload: unknown): RawMqttMessage => ({
  topic,
  payload: JSON.stringify(payload),
  timestamp: new Date().toISOString(),
});

test('maps orders topic to OrderActive', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const result = firstValueFrom(gateway.orders$);
  subject.next(
    createMessage('ccu/order/active', {
      orderId: '123',
      productId: 'ABC',
      quantity: 1,
      status: 'running',
    })
  );

  const payload = await result;
  assert.equal(payload.order.orderId, '123');
  assert.equal(payload.order.status, 'running');
  assert.equal(payload.topic, 'ccu/order/active');
});

test('maps module state messages', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const result = firstValueFrom(gateway.modules$);
  subject.next(
    createMessage('module/v1/ff/SVR3QA0022/state', {
      moduleId: 'SVR3QA0022',
      state: 'working',
    })
  );

  const moduleState = await result;
  assert.equal(moduleState.moduleId, 'SVR3QA0022');
  assert.equal(moduleState.state, 'working');
});

test('ignores non-json payloads gracefully', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  subject.next({
    topic: 'ccu/order/active',
    payload: 'not-json',
  });
  subject.complete();

  await assert.rejects(() => firstValueFrom(gateway.orders$));
});

test('emits each order when payload is an array', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const first = firstValueFrom(gateway.orders$);
  const second = firstValueFrom(gateway.orders$.pipe(skip(1)));
  subject.next({
    topic: 'ccu/order/completed',
    payload: JSON.stringify([
      { orderId: '123', productId: 'A', quantity: 1, status: 'completed' },
      { orderId: '456', productId: 'B', quantity: 2, status: 'completed' },
    ]),
    timestamp: new Date().toISOString(),
  });

  const orderOne = await first;
  const orderTwo = await second;
  assert.equal(orderOne.order.orderId, '123');
  assert.equal(orderTwo.order.orderId, '456');
  assert.equal(orderOne.topic, 'ccu/order/completed');
});

test('maps pairing state messages with timestamp', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const result = firstValueFrom(gateway.pairing$);
  subject.next({
    topic: 'ccu/pairing/state',
    payload: JSON.stringify({
      modules: [{ serialNumber: 'SVR3QA0022', connected: true, available: 'READY', hasCalibration: true }],
      transports: [{ serialNumber: '5iO4', connected: true, charging: false }],
    }),
    timestamp: '2025-11-10T18:02:09.702936',
  });

  const pairing = await result;
  assert.equal(pairing.modules.length, 1);
  assert.equal(pairing.modules[0].serialNumber, 'SVR3QA0022');
  assert.equal(pairing.transports.length, 1);
  assert.equal(pairing.timestamp, '2025-11-10T18:02:09.702936');
});

