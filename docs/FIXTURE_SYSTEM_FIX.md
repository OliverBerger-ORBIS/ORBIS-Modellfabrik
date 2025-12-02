# Fixture System Fix - Summary

## Problem Statement

The fixture system in omf3 had a critical issue where:
- Fixture button appeared in mock mode
- Clicking the button loaded fixture data
- **BUT** the UI did not update with the new data
- This affected ALL tabs: Track & Trace, Order, Overview, Module, Process, FTS, Sensor, Configuration

## Root Cause

When fixtures are loaded via `loadTabFixture()`, the function calls `resetStreams()` which:
1. Unsubscribes from existing fixture streams
2. Completes the old `messageSubject`
3. Creates a NEW `messageSubject`
4. Recreates the business logic streams

**The Bug**: After creating the new `messageSubject`, the code did NOT re-establish the subscription that forwards messages to `MessageMonitorService`. This broke the message flow:

```
Before Fix:
Fixture Messages → messageSubject → ❌ NOT FORWARDED ❌ → MessageMonitorService → Services → UI

After Fix:
Fixture Messages → messageSubject → ✅ setupMessageMonitorForwarding() ✅ → MessageMonitorService → Services → UI
```

## The Fix

### Changes to `mock-dashboard.ts`

1. **Extracted forwarding setup into a function**:
   ```typescript
   const setupMessageMonitorForwarding = () => {
     // Unsubscribe existing subscription if any
     if (messageMonitorSubscription) {
       messageMonitorSubscription.unsubscribe();
     }
     
     // In mock mode, forward fixture messages to MessageMonitor
     if (!mqttClient && messageMonitor) {
       messageMonitorSubscription = messageSubject.subscribe((message) => {
         messageMonitor.addMessage(message.topic, payload, message.timestamp);
       });
     }
   };
   ```

2. **Called it after creating new messageSubject**:
   ```typescript
   const resetStreams = () => {
     // ... existing code ...
     messageSubject.complete();
     messageSubject = new Subject<RawMqttMessage>();
     
     // CRITICAL FIX: Reconnect MessageMonitor forwarding
     setupMessageMonitorForwarding();
     
     // ... rest of code ...
   };
   ```

3. **Called it during initialization**:
   ```typescript
   export const createMockDashboardController = (options) => {
     // ... setup ...
     
     // Initial setup of MessageMonitor forwarding
     setupMessageMonitorForwarding();
     
     // ... rest of code ...
   };
   ```

## Message Flow Architecture

### Complete Message Flow

```
┌──────────────────┐
│ Fixture Files    │
│ (.log)           │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ loadOrderFixture │
│ loadModuleFixture│
│ etc.             │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ createOrderStream│
│ createModuleStream
│ etc.             │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│createTabFixture  │
│Preset()          │
│ (combines streams)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ loadTabFixture() │
│ (mock-dashboard) │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ messageSubject   │
│ .next()          │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│ setupMessageMonitor      │
│ Forwarding()             │
│ [CRITICAL FIX HERE]      │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────┐
│ MessageMonitor   │
│ Service          │
│ .addMessage()    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Services         │
│ (via             │
│ getLastMessage())│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ UI Components    │
│ (Change Detection│
│ triggered)       │
└──────────────────┘
```

## Impact

### Fixed Tabs
- ✅ **Order Tab**: Orders now update when fixtures are loaded
- ✅ **Overview Tab**: Overview data now updates when fixtures are loaded
- ✅ **Module Tab**: Module states now update when fixtures are loaded
- ✅ **Process Tab**: Process data now updates when fixtures are loaded
- ✅ **FTS Tab**: FTS states now update when fixtures are loaded
- ✅ **Sensor Tab**: Sensor data now updates when fixtures are loaded
- ✅ **Configuration Tab**: Configuration now updates when fixtures are loaded
- ✅ **Track & Trace Tab**: Message flow fixed, but workpiece display depends on fixture data quality (see below)

### Track & Trace Specific Notes

The Track & Trace tab has an additional data requirement. The `WorkpieceHistoryService` processes FTS state messages and looks for workpiece load information:

```typescript
state.load?.forEach((loadItem) => {
  if (loadItem.loadId && loadItem.loadType) {
    // Track workpiece history
  }
});
```

**Current Issue**: The existing `track-trace.log` fixture has FTS state messages with `loadId: null` and `loadType: null`, so no workpieces are tracked.

**Solution**: To display workpieces in Track & Trace, fixture files need FTS state messages with actual load data:

```json
{
  "topic": "fts/v1/ff/5iO4/state",
  "timestamp": "2025-11-10T17:00:00.000Z",
  "payload": {
    "serialNumber": "5iO4",
    "orderId": "uuid-here",
    "lastNodeId": "SVR3QA0022",
    "driving": false,
    "load": [
      {
        "loadId": "04a189ca341290",
        "loadType": "BLUE",
        "loadPosition": "1"
      }
    ],
    "actionState": {
      "id": "action-id",
      "command": "DOCK",
      "state": "FINISHED",
      "timestamp": "2025-11-10T17:00:00.000Z"
    }
  }
}
```

This is **not an architecture bug** - it's a fixture data quality issue. The message flow fix ensures that when proper fixture data is available, the Track & Trace tab will display it correctly.

## Validation

- ✅ All 524 existing tests pass
- ✅ Build succeeds (development and production)
- ✅ CodeQL security scan: 0 vulnerabilities
- ✅ Code review passed

## Documentation

Comprehensive documentation added to `omf3/libs/testing-fixtures/README.md`:

- Architecture overview
- Message flow diagram
- Tab fixture presets reference
- Guide for adding new fixtures
- Best practices
- Troubleshooting guide

## Future Enhancements

The fixture system is now fully documented and extensible. Potential enhancements:

1. **Multi-file fixtures**: Combine topics from multiple log files
2. **Fixture recording**: Record live MQTT messages to fixture files
3. **Fixture validation**: Validate fixture files against expected schemas
4. **Parameterized fixtures**: Support fixtures with customizable values

## Conclusion

The **core fixture system issue is FIXED**. All tabs now properly receive and process fixture data. The message flow from fixtures → MessageMonitor → Services → UI is working correctly.

For Track & Trace specifically, the next step would be to enhance the fixture data with actual workpiece load information, but this is a separate data quality improvement, not a bug fix.
