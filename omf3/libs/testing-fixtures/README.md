# libs/testing-fixtures

Replay helpers for deterministic demo data in the OMF3 workspace.

## Usage

```ts
import { createOrderFixtureStream } from '@omf3/testing-fixtures';

const stream$ = createOrderFixtureStream('white');
stream$.subscribe((message) => {
  console.log(message.topic, message.payload);
});
```

- Fixtures live under `omf3/testing/fixtures/orders`.
- When running in the browser, the library fetches files from `/fixtures/orders/**`.
- In unit tests you can inject a custom loader:

```ts
const messages = await loadOrderFixture('white', {
  baseUrl: '/path/to/fixtures/orders',
  loader: async (path) => readFile(path, 'utf-8'),
});
```

## Testing

```
nx test testing-fixtures
```

