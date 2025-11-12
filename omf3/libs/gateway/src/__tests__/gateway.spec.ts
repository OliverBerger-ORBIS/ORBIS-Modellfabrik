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

  const order = await result;
  assert.equal(order.orderId, '123');
  assert.equal(order.status, 'running');
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
  assert.equal(orderOne.orderId, '123');
  assert.equal(orderTwo.orderId, '456');
});

