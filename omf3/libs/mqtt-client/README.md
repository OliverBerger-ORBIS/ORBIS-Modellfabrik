# libs/mqtt-client

This library provides a lightweight, browser-friendly MQTT wrapper that exposes
RxJS streams for messages and connection state. The code is deliberately
domain-agnostic – mapping messages to business entities happens in the gateway
layer.

## API overview

```ts
import { createMqttClient, MockMqttAdapter } from '@omf3/mqtt-client';

const adapter = new MockMqttAdapter(); // replace with real adapter in production
const client = createMqttClient(adapter);

await client.connect('wss://mqtt.example.com');
await client.subscribe('ccu/orders/active');

client.messages$.subscribe((msg) => console.log(msg.topic, msg.payload));
await client.publish('ccu/orders/active', { orderId: '42' });
```

### Exposed types

- `MqttClientWrapper`
- `MqttAdapter` interface (implement for real WebSocket MQTT client)
- `MockMqttAdapter` for tests/local replay
- `MqttMessage`, `ConnState`, `PublishOptions`, `SubscribeOptions`

## Local testing

The library ships with a basic unit test backed by the mock adapter:

```bash
node --test omf3/libs/mqtt-client/src/__tests__/mqtt-client.spec.ts
```

When Nx tests are configured you can add a dedicated target or integrate into
`nx affected --target=test`. For now this simple check ensures the wrapper and
mock behave as expected.

## Notes

- Keep this package free from domain knowledge.
- Real MQTT integration (e.g. using `mqtt` npm package) should implement the
  `MqttAdapter` interface and feed the wrapper.
- Higher-level parsing lives in `libs/gateway`.
# mqtt-client

This library was generated with [Nx](https://nx.dev).

## Building

Run `nx build mqtt-client` to build the library.
