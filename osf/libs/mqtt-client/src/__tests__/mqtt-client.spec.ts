import assert from 'node:assert/strict';
import test from 'node:test';

import { firstValueFrom, filter, take } from 'rxjs';

import { createMqttClient } from '../index';
import { MockMqttAdapter } from '../mock-adapter';

test('mqtt-client emits connection states', async () => {
  const adapter = new MockMqttAdapter();
  const client = createMqttClient(adapter);

  const connected = firstValueFrom(
    client.connectionState$.pipe(filter((state) => state === 'connected'), take(1))
  );

  await client.connect('wss://example.org');

  assert.equal(await connected, 'connected');
});

test('mqtt-client forwards published messages', async () => {
  const adapter = new MockMqttAdapter();
  const client = createMqttClient(adapter);

  await client.connect('wss://example.org');
  await client.subscribe('ccu/orders/active');

  const message = firstValueFrom(client.messages$.pipe(take(1)));
  await client.publish('ccu/orders/active', { id: '42' });

  const result = await message;
  assert.equal(result.topic, 'ccu/orders/active');
  assert.deepEqual(result.payload, { id: '42' });
  assert.ok(result.timestamp);
});

