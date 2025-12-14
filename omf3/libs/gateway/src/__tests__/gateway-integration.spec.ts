import assert from 'node:assert/strict';
import test from 'node:test';

import { Subject, firstValueFrom, lastValueFrom } from 'rxjs';
import { take, toArray } from 'rxjs/operators';

import { createGateway, type RawMqttMessage, type GatewayPublishFn } from '../index';

const createMessage = (topic: string, payload: unknown, timestamp?: string): RawMqttMessage => ({
  topic,
  payload: JSON.stringify(payload),
  timestamp: timestamp ?? new Date().toISOString(),
});

test('Gateway Integration: MQTT Client → Gateway Message Flow', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  // Simulate MQTT messages arriving
  const orderPromise = firstValueFrom(gateway.orders$);
  const modulePromise = firstValueFrom(gateway.modules$);

  subject.next(
    createMessage('ccu/order/active', {
      orderId: 'ORD-123',
      productId: 'PROD-456',
      quantity: 2,
      status: 'running',
    })
  );

  subject.next(
    createMessage('module/v1/ff/TEST-MODULE/state', {
      moduleId: 'TEST-MODULE',
      state: 'ready',
    })
  );

  const [order, module] = await Promise.all([orderPromise, modulePromise]);

  assert.equal(order.order.orderId, 'ORD-123');
  assert.equal(order.topic, 'ccu/order/active');
  assert.equal(module.moduleId, 'TEST-MODULE');
  assert.equal(module.state, 'ready');
});

test('Gateway Integration: Topic-based Message Routing', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  // Test multiple order topics are routed correctly
  const ordersPromise = lastValueFrom(gateway.orders$.pipe(take(3), toArray()));

  subject.next(createMessage('ccu/order/active', { orderId: '1', status: 'active' }));
  subject.next(createMessage('ccu/order/completed', { orderId: '2', status: 'completed' }));
  subject.next(createMessage('ccu/order/active', { orderId: '3', status: 'active' }));

  const orders = await ordersPromise;
  assert.equal(orders.length, 3);
  assert.equal(orders[0].topic, 'ccu/order/active');
  assert.equal(orders[1].topic, 'ccu/order/completed');
  assert.equal(orders[2].topic, 'ccu/order/active');
});

test('Gateway Integration: Type Conversion (Raw → Typed Entities)', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const orderPromise = firstValueFrom(gateway.orders$);

  // Send raw MQTT message
  const rawPayload = {
    orderId: 'TYPED-001',
    productId: 'BLUE-WORKPIECE',
    quantity: 5,
    status: 'in_progress',
    timestamp: '2024-01-01T10:00:00Z',
  };

  subject.next(createMessage('ccu/order/active', rawPayload));

  const result = await orderPromise;

  // Verify typed entity structure
  assert.equal(result.order.orderId, 'TYPED-001');
  assert.equal(result.order.productId, 'BLUE-WORKPIECE');
  assert.equal(result.order.quantity, 5);
  assert.equal(result.order.status, 'in_progress');
  assert.equal(typeof result.order.orderId, 'string');
  assert.equal(typeof result.order.quantity, 'number');
});

test('Gateway Integration: Error Handling with Invalid Messages', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  // Send invalid JSON payload
  subject.next({
    topic: 'ccu/order/active',
    payload: 'invalid-json-{',
    timestamp: new Date().toISOString(),
  });

  // Gateway should handle gracefully - stream should not error
  subject.complete();

  // Should reject when no valid messages arrive
  await assert.rejects(() => firstValueFrom(gateway.orders$));
});

test('Gateway Integration: Timestamp Preservation', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const timestamp = '2024-01-01T12:00:00.000Z';
  const pairingPromise = firstValueFrom(gateway.pairing$);

  subject.next(
    createMessage(
      'ccu/pairing/state',
      {
        modules: [{ serialNumber: 'SN-001', connected: true }],
        transports: [],
      },
      timestamp
    )
  );

  const result = await pairingPromise;
  assert.equal(result.timestamp, timestamp);
});

test('Gateway Integration: Array Payload Handling', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const ordersPromise = lastValueFrom(gateway.orders$.pipe(take(3), toArray()));

  // Send array payload
  subject.next(
    createMessage('ccu/order/completed', [
      { orderId: 'ARRAY-1', status: 'completed' },
      { orderId: 'ARRAY-2', status: 'completed' },
      { orderId: 'ARRAY-3', status: 'completed' },
    ])
  );

  const orders = await ordersPromise;
  assert.equal(orders.length, 3);
  assert.equal(orders[0].order.orderId, 'ARRAY-1');
  assert.equal(orders[1].order.orderId, 'ARRAY-2');
  assert.equal(orders[2].order.orderId, 'ARRAY-3');
});

test('Gateway Integration: Publish Function', async () => {
  let publishedMessages: Array<{ topic: string; payload: unknown }> = [];

  const mockPublish: GatewayPublishFn = async (topic, payload) => {
    publishedMessages.push({ topic, payload });
  };

  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable(), { publish: mockPublish });

  // Verify gateway has publish capability
  assert.ok(gateway);

  // Note: Gateway itself doesn't expose publish - it's passed to business layer
  // This test verifies the gateway can be created with a publish function
  assert.equal(publishedMessages.length, 0);
});

test('Gateway Integration: Multiple Concurrent Streams', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  // Subscribe to multiple streams concurrently
  const orderPromise = firstValueFrom(gateway.orders$);
  const modulePromise = firstValueFrom(gateway.modules$);
  const pairingPromise = firstValueFrom(gateway.pairing$);

  // Send messages to different topics
  subject.next(createMessage('ccu/order/active', { orderId: 'MULTI-1' }));
  subject.next(createMessage('module/v1/ff/MOD-1/state', { moduleId: 'MOD-1', state: 'idle' }));
  subject.next(
    createMessage('ccu/pairing/state', {
      modules: [{ serialNumber: 'PAIR-1', connected: true }],
      transports: [],
    })
  );

  const [order, module, pairing] = await Promise.all([orderPromise, modulePromise, pairingPromise]);

  assert.equal(order.order.orderId, 'MULTI-1');
  assert.equal(module.moduleId, 'MOD-1');
  assert.equal(pairing.modules[0].serialNumber, 'PAIR-1');
});

test('Gateway Integration: Message Filtering by Topic Pattern', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const modulePromise = firstValueFrom(gateway.modules$);

  // Send various messages, only module state should be captured
  subject.next(createMessage('ccu/order/active', { orderId: 'FILTER-1' }));
  subject.next(createMessage('module/v1/ff/FILTER-MOD/state', { moduleId: 'FILTER-MOD', state: 'working' }));
  subject.next(createMessage('some/other/topic', { data: 'ignored' }));

  const module = await modulePromise;
  assert.equal(module.moduleId, 'FILTER-MOD');
  assert.equal(module.state, 'working');
});

test('Gateway Integration: Empty Payload Handling', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const ordersPromise = firstValueFrom(gateway.orders$);

  // Send message with empty object payload
  subject.next(createMessage('ccu/order/active', {}));

  // Should complete without throwing
  const result = await ordersPromise;

  assert.ok(result);
  assert.equal(typeof result.order, 'object');
});

test('Gateway Integration: Rapid Message Sequence', async () => {
  const subject = new Subject<RawMqttMessage>();
  const gateway = createGateway(subject.asObservable());

  const ordersPromise = lastValueFrom(gateway.orders$.pipe(take(10), toArray()));

  // Send 10 messages rapidly
  for (let i = 0; i < 10; i++) {
    subject.next(
      createMessage('ccu/order/active', {
        orderId: `RAPID-${i}`,
        status: 'active',
      })
    );
  }

  const orders = await ordersPromise;
  assert.equal(orders.length, 10);
  assert.equal(orders[0].order.orderId, 'RAPID-0');
  assert.equal(orders[9].order.orderId, 'RAPID-9');
});
