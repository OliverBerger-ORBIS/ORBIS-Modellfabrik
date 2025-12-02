# libs/testing-fixtures

Replay helpers for deterministic demo data in the OMF3 workspace.

## Overview

The testing fixtures system provides a way to load and replay MQTT messages for testing and demonstration purposes. It supports tab-specific fixture configurations that allow each UI tab to load relevant test data independently.

## Quick Start

### Basic Usage

```ts
import { createOrderFixtureStream } from '@omf3/testing-fixtures';

const stream$ = createOrderFixtureStream('white');
stream$.subscribe((message) => {
  console.log(message.topic, message.payload);
});
```

### Tab-Specific Fixtures

```ts
import { createTabFixturePreset } from '@omf3/testing-fixtures';

// Load preset for Order tab with white workpiece data
const stream$ = createTabFixturePreset('order-white', {
  intervalMs: 25, // Delay between messages
  loop: false // Don't loop the fixture
});
```

## Architecture

### Core Components

1. **Fixture Loaders** (`index.ts`)
   - `loadOrderFixture()` - Load order/production data
   - `loadModulePairingFixture()` - Load module pairing/status data
   - `loadStockFixture()` - Load warehouse/stock data
   - `loadFlowFixture()` - Load production flow data
   - `loadConfigFixture()` - Load configuration data
   - `loadSensorFixture()` - Load sensor data (BME680, LDR, camera)

2. **Fixture Streams** (`index.ts`)
   - `createOrderFixtureStream()` - Create observable stream of order messages
   - `createModulePairingFixtureStream()` - Create observable stream of module messages
   - Similar functions for stock, flow, config, and sensor fixtures
   - Support for interval delays and looping

3. **Tab-Specific Fixtures** (`tab-fixtures.ts`)
   - `TAB_FIXTURE_PRESETS` - Predefined fixture configurations for each tab
   - `createTabFixturePreset()` - Load a preset configuration by name
   - `createTabFixtureStream()` - Create combined stream from multiple fixture types
   - `createCustomTabFixture()` - Create custom fixture configuration

### Message Flow

```
Fixture Files (.log)
    ↓
loadOrderFixture() / loadModulePairingFixture() / etc.
    ↓
createOrderFixtureStream() / createModulePairingFixtureStream() / etc.
    ↓
createTabFixturePreset() [combines multiple streams]
    ↓
loadTabFixture() [in mock-dashboard.ts]
    ↓
messageSubject.next()
    ↓
setupMessageMonitorForwarding() [CRITICAL]
    ↓
MessageMonitorService.addMessage()
    ↓
Services (OrderService, WorkpieceHistoryService, etc.)
    ↓
UI Components (via messageMonitor.getLastMessage())
```

### Critical Fix: Message Flow Reconnection

When fixtures are loaded, `resetStreams()` creates a new `messageSubject`. **The critical fix** is that `setupMessageMonitorForwarding()` must be called after creating the new subject to re-establish the subscription that forwards messages to `MessageMonitorService`. Without this, messages from fixtures are not propagated to services, causing the UI to not update.

## File Organization

- Fixtures live under `omf3/testing/fixtures/orders`, `omf3/testing/fixtures/modules`, etc.
- When running in the browser, the library fetches files from `/fixtures/**`.
- In unit tests you can inject a custom loader:

```ts
const messages = await loadOrderFixture('white', {
  baseUrl: '/path/to/fixtures/orders',
  loader: async (path) => readFile(path, 'utf-8'),
});
```

## Tab Fixture Presets

Available presets in `TAB_FIXTURE_PRESETS`:

### Startup/Default
- `startup` - Initial factory state with no active orders

### Order Tab
- `order-white` - White workpiece production order
- `order-white-step3` - White workpiece order stopped at step 3
- `order-blue` - Blue workpiece production order
- `order-red` - Red workpiece production order
- `order-mixed` - Mixed workpiece types
- `order-storage` - Storage order (inbound raw materials)

### Other Tabs
- `module-default` - Default module states
- `process-startup` - Initial process/flow state
- `sensor-startup` - Initial sensor readings
- `config-default` - Default configuration
- `overview-startup` / `overview-active` - Overview scenarios
- `dsp-action-default` - DSP action scenario
- `track-trace-default` - Track & trace workpiece genealogy

## Adding New Fixtures

### Step 1: Create Fixture Files

Create `.log` files in the appropriate directory:

Fixture files contain one JSON object per line:
```json
{"topic": "ccu/order/active", "timestamp": "2025-11-10T17:00:00.000Z", "payload": {...}}
{"topic": "fts/v1/ff/5iO4/state", "timestamp": "2025-11-10T17:00:01.000Z", "payload": {...}}
```

### Step 2: Register Fixture in Paths

Add the fixture to the appropriate path map in `index.ts`:

```typescript
const FIXTURE_PATHS: Record<OrderFixtureName, string> = {
  // ... existing fixtures
  'my-new-fixture': 'my-new-fixture/orders.log',
};
```

### Step 3: Create Tab Preset (Optional)

Add a preset configuration in `tab-fixtures.ts`:

```typescript
export const TAB_FIXTURE_PRESETS: Record<string, TabFixtureConfig> = {
  'my-tab-scenario': {
    orders: 'my-new-fixture',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
};
```

### Step 4: Use in Tab Component

```typescript
async loadFixture(fixture: OrderFixtureName): Promise<void> {
  await this.dashboard.loadTabFixture('my-tab-scenario');
}
```

## Troubleshooting

### Issue: Fixture loads but UI doesn't update

**Cause**: MessageMonitor forwarding subscription not established after `resetStreams()`.

**Solution**: Ensure `setupMessageMonitorForwarding()` is called in `resetStreams()` (already fixed in mock-dashboard.ts).

### Issue: Track & Trace shows no workpieces

**Cause**: FTS state messages don't have `loadId` and `loadType` populated in the `load` array.

**Solution**: Ensure FTS state messages in the fixture include actual load data:
```json
{
  "topic": "fts/v1/ff/5iO4/state",
  "payload": {
    "load": [
      {"loadId": "04a189ca341290", "loadType": "BLUE", "loadPosition": "1"}
    ],
    "orderId": "uuid-here",
    "lastNodeId": "SVR3QA0022",
    ...
  }
}
```

### Issue: Services don't receive messages

**Cause**: Services may be subscribed before MessageMonitor has received the fixture messages.

**Solution**: Services should use `getLastMessage()` which returns an observable that emits the current value and all future updates.

## Testing

```bash
nx test testing-fixtures
```

