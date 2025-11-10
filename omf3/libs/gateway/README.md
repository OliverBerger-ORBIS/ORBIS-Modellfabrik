# libs/gateway

Maps raw MQTT messages (`topic`, `payload`) to typed domain entities from
`libs/entities`.

## Usage

```ts
import { Subject } from 'rxjs';
import { createGateway } from '@omf3/gateway';

const mqttMessages$ = new Subject<{ topic: string; payload: unknown }>();
const gateway = createGateway(mqttMessages$.asObservable());

gateway.orders$.subscribe((order) => console.log(order.orderId));
```

### Streams

- `orders$`: emits `OrderActive`
- `stock$`: emits `StockMessage`
- `modules$`: emits `ModuleState`
- `fts$`: emits `FtsState`

## Testing

The included unit test shows how to feed a `Subject` with mock messages. Run:

```bash
npm run test -- --target=gateway:test  # or: nx test gateway
nx build gateway                       # optional TypeScript build
```

## Notes

- Domain-agnostic: just shapes data; no business logic.
- Mapping is prefix-based (`ccu/order`, `warehouse/stock`, `module/v1`, `fts/v1`).

