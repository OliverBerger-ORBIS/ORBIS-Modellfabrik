# Services

## MessageMonitorService

The `MessageMonitorService` provides enhanced MQTT message handling with the following features:

### Features

1. **Immediate Availability**: BehaviorSubject per topic provides instant access to the last message
2. **Message History**: Circular buffers store message history with configurable retention
3. **Schema Validation**: JSON schema validation with fallback for unknown schemas
4. **Persistence**: localStorage-based persistence (excludes camera data)
5. **Multi-Tab Sync**: BroadcastChannel synchronizes messages across browser tabs

### Usage

#### Getting the Last Message

```typescript
constructor(private messageMonitor: MessageMonitorService) {}

ngOnInit() {
  // Get last message for a topic - immediate value from BehaviorSubject
  this.messageMonitor.getLastMessage('/j1/txt/1/i/bme680')
    .subscribe(message => {
      if (message && message.valid) {
        console.log('Last BME680 reading:', message.payload);
      }
    });
}
```

#### Getting Message History

```typescript
// Get message history for debugging or replay
const history = this.messageMonitor.getHistory('/j1/txt/1/i/bme680');
console.log(`${history.length} messages in history`);
```

#### Configuring Retention

```typescript
// Set custom retention for a topic
this.messageMonitor.setRetention('my/custom/topic', 200);

// Check current retention
const retention = this.messageMonitor.getRetention('my/custom/topic');
```

### Default Retention Configuration

- **Default**: 50 messages per topic
- **Camera (`/j1/txt/1/i/cam`)**: 10 messages (large payloads, high frequency)
- **Sensors (`/j1/txt/1/i/bme680`, `/j1/txt/1/i/ldr`)**: 100 messages (frequent updates, small payloads)

### Integration with Gateway

The MessageMonitorService works alongside the existing gateway:

- **Gateway**: Provides real-time RxJS streams with `shareReplay(1)` for current subscriptions
- **MessageMonitorService**: Provides reliable access to last messages and history, even for late subscribers

Example pattern:

```typescript
// Use gateway for real-time updates
gateway.sensorBme680$.subscribe(data => {
  // Handle real-time updates
});

// Use MessageMonitor for reliable last value or history
this.messageMonitor.getLastMessage('/j1/txt/1/i/bme680')
  .subscribe(message => {
    // Always get the last value, even if subscribed late
  });
```

### Persistence Behavior

- Messages are persisted to localStorage (max 5MB total)
- Camera data (`/j1/txt/1/i/cam`) is NOT persisted (too large)
- Persisted data is loaded on service initialization
- Retention limits apply to persisted data

### Multi-Tab Synchronization

When a message is received in one tab, it's automatically synchronized to all other tabs via BroadcastChannel. This ensures consistent state across all browser tabs.

### Schema Validation

The service is designed to validate messages against JSON schemas from `omf2/registry/schemas/`.

**Current Status**: Schema validation is implemented but operates in **fallback mode** (all messages accepted as valid). This is intentional to ensure the service works immediately without requiring schema assets.

**To enable schema validation**:
1. Add schemas to `project.json` assets configuration
2. Load schemas via HttpClient on service initialization  
3. Register schemas with the Ajv validator

When schema validation is enabled:
- Invalid messages are still stored (with `valid: false` flag)
- Validation errors are logged to console
- `validationErrors` array contains error details
- Messages without schemas are accepted (fallback behavior)

## ConnectionService

The `ConnectionService` automatically feeds all MQTT messages to the `MessageMonitorService`. No additional configuration is required.
