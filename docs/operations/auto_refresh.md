# Auto-Refresh for UI (Streamlit) - Simplified In-Process Implementation

## Overview

The auto-refresh feature enables Streamlit UI pages to automatically update when relevant business events occur. This provides a real-time user experience without requiring manual page refreshes.

**This implementation has been simplified to remove Redis dependency and MQTT-based refresh mechanisms introduced in prior PRs (including PR #47).**

## 🔑 Key Changes from Previous Implementation

**What Changed:**
- **Removed Redis dependency:** Refresh timestamps now stored in-memory (thread-safe)
- **Removed MQTT UI refresh path:** No more `omf2/ui/refresh/{group}` MQTT topics
- **Removed duplicated components:** Deleted `mqtt_subscriber` component and `admin_subtab`
- **Single refresh entry point:** All refresh requests use `request_refresh()` from `omf2/backend/refresh.py`
- **Simplified gateway:** Gateway calls `request_refresh()` directly instead of publishing MQTT messages

**Why These Changes:**
- Reduced complexity and external dependencies
- Eliminated duplicate refresh paths that were introduced in PR #47
- Made the system easier to understand, test, and maintain
- Removed need for external Redis server in development/testing

## Architecture

The system consists of three main components:

1. **Backend Refresh Module** (`omf2/backend/refresh.py`)
   - In-memory, thread-safe store for refresh timestamps
   - Throttle logic to prevent excessive refreshes (minimum 1 second between refreshes)
   - Group-based refresh management (e.g., 'order_updates', 'module_updates')
   - No external dependencies (Redis removed)

2. **Gateway Integration** (`omf2/ccu/ccu_gateway.py`)
   - Triggers UI refresh after processing MQTT messages via `request_refresh()`
   - Uses `gateway.yml` refresh_triggers mapping to determine which groups to refresh
   - Supports wildcard pattern matching for topic patterns

3. **UI Consumption** (`omf2/omf.py` and `omf2/ui/utils/ui_refresh.py`)
   - `consume_refresh()` checks for timestamp updates in all refresh groups
   - Calls `st.rerun()` exactly once when refresh is detected
   - Single-entry point for all UI refreshes

## Configuration

### Gateway Configuration

The gateway configuration is stored in `omf2/registry/gateway.yml` under the `refresh_triggers` section:

```yaml
gateway:
  refresh_triggers:
    # Order Updates
    order_updates:
      - ccu/order/active
      - ccu/order/completed
      - ccu/order/request
      - ccu/order/response
    
    # Module State Updates
    module_updates:
      - module/v1/ff/*/state
      - module/v1/ff/*/connection
      - fts/v1/ff/*/state
    
    # Sensor Data Updates
    sensor_updates:
      - /j1/txt/1/i/bme680
      - /j1/txt/1/i/ldr
    
    # Stock Updates
    stock_updates:
      - /j1/txt/1/f/i/stock
      - ccu/state/stock
```

**Pattern Matching:**
- Exact match: `ccu/order/active`
- Wildcard match: `module/v1/ff/*/state` (matches any module ID)

### Editing Configuration via UI

The configuration can be edited via the Dashboard Gateway Configuration UI:

1. Navigate to: **CCU → Configuration → Gateway Configuration**
2. Edit the YAML configuration in the text area
3. Click **Save Changes** to persist the configuration

## Usage

### Triggering a Refresh (Backend/Gateway)

When business logic detects an event that should trigger a UI refresh:

```python
from omf2.backend.refresh import request_refresh

# Trigger refresh for a group
request_refresh('order_updates', min_interval=1.0)
```

This is already integrated in:
- `omf2/ccu/ccu_gateway.py::_trigger_ui_refresh()` - Called when MQTT topics match refresh_triggers
- `omf2/ccu/order_manager.py` - Called after processing orders

### Consuming Refreshes (UI)

The UI automatically consumes refreshes via `omf2/omf.py::main()`:

```python
def main():
    # ... initialization ...
    
    # Handle UI refresh requests (only place where st.rerun() is allowed)
    if consume_refresh():
        st.rerun()
        return
    
    # ... rest of UI rendering ...
```

The `consume_refresh()` function:
1. Checks all refresh groups for timestamp updates
2. Compares with last-seen timestamps in session state
3. Returns True if any group has a newer timestamp
4. Updates session state to mark timestamps as seen

## Testing

### Unit Tests

Run the refresh module tests:

```bash
# All refresh tests
pytest tests/test_refresh.py -v

# Gateway integration tests
pytest tests/test_gateway_refresh_integration.py -v
```

### Manual Testing (No Redis Required!)

1. **Start the Streamlit app:**
   ```bash
   streamlit run omf2/omf.py
   ```

2. **Publish a test MQTT message that matches a refresh trigger:**
   ```bash
   mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "test123"}'
   ```

3. **Observe:**
   - Gateway logs should show: "🔄 UI refresh triggered for group 'order_updates'"
   - Gateway logs should show: "✅ Refresh requested for group 'order_updates'"
   - UI should refresh automatically (st.rerun() called)

### QA Steps (from PR Requirements)

**Environment:**
- No Redis required
- Ensure `OMF2_UI_AUTOREFRESH` is not set (not needed for this implementation)

**Steps:**
1. Start gateway (ensure existing sidebar-managed MQTT client used)
2. Start Streamlit app: `streamlit run omf2/omf.py`
3. Trigger business event that matches a refresh_trigger pattern
   - Example: Publish to `ccu/order/active` topic
4. Verify in gateway logs:
   - "🔄 UI refresh triggered for group 'order_updates'"
   - "✅ Refresh requested for group 'order_updates'"
5. Verify in UI:
   - Page refreshes automatically (check Streamlit console for rerun)
   - Data is updated
   - No MQTT reconnect loops
   - No errors in browser console

## Troubleshooting

### Refresh Not Working

**Symptom:** UI doesn't refresh automatically

**Solutions:**
1. Verify that the MQTT topic matches a pattern in `refresh_triggers` (gateway.yml)
2. Check gateway logs for "🔄 UI refresh triggered"
3. Check that `consume_refresh()` is being called in `omf2/omf.py::main()`
4. Verify Streamlit is detecting the timestamp change (check debug logs)

### Throttle Too Aggressive

**Symptom:** UI updates are delayed too much

**Solutions:**
1. Adjust `min_interval` parameter in `request_refresh()` calls (default: 1.0 second)
2. Consider creating more granular refresh groups
3. Check if multiple rapid messages are being throttled

## Rollback Notes

If you need to rollback to the previous Redis/MQTT-based implementation:

1. Revert this PR and restore PR #47 changes
2. Start Redis server: `docker run -d -p 6379:6379 redis`
3. Start Flask API server: `python -m omf2.backend.api_refresh`
4. Set environment variables:
   - `REDIS_URL=redis://localhost:6379/0`
   - `OMF2_UI_REFRESH_VIA_MQTT=1`
   - `OMF2_UI_MQTT_WS_URL=ws://broker:9001` (if MQTT UI needed)

## Best Practices

1. **Use appropriate refresh groups:**
   - Group related topics together (e.g., all order topics in 'order_updates')
   - Don't create too many groups

2. **Throttle interval:**
   - Default 1 second is good for most use cases
   - Increase for less critical updates
   - Don't set below 0.5 seconds

3. **Pattern matching:**
   - Use wildcards sparingly
   - Prefer exact matches when possible

4. **Testing:**
   - Test refresh behavior with unit tests
   - Test throttling behavior
   - Verify no memory leaks in long-running sessions

## Performance Considerations

- **Memory:** Each refresh group uses one in-memory key (~100 bytes)
- **UI overhead:** `consume_refresh()` called once per Streamlit rerun (minimal overhead)
- **Gateway overhead:** Throttle logic is very fast (< 1ms per message)
- **Thread safety:** All operations are thread-safe via lock

## Reference

- **PR #47:** Previous implementation with Redis/MQTT refresh (reverted by this PR)
- **This PR:** Simplified in-process refresh implementation
