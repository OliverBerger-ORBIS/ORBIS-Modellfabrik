# libs/business

Derived, reactive aggregates that sit on top of the MQTT gateway stream.

## Usage

```ts
import { createBusiness } from '@osf/business';
import { createGateway } from '@osf/gateway';
import { Subject } from 'rxjs';

const rawMessages$ = new Subject<{ topic: string; payload: unknown }>();
const gateway = createGateway(rawMessages$.asObservable());
const business = createBusiness(gateway);

business.orderCounts$.subscribe((counts) => console.log(counts));
```

### Exposed streams

- `orderCounts$` – number of orders by status (`running`, `queued`, `completed`)
- `stockByPart$` – cumulative stock level per part id
- `moduleStates$` – latest state per module id
- `ftsStates$` – latest FTS state per id

All streams are `shareReplay(1)` so late subscribers receive the current value immediately.

## Testing

```bash
npx nx test business
npx nx build business   # optional TypeScript build
```

## Notes

- Business logic stays framework neutral; it only consumes the typed gateway interface.
- Add more derived streams (alerts, KPIs, etc.) in this library to keep Angular components thin.

