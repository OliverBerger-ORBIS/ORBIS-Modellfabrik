# Auto-Refresh for UI (Streamlit) - Simplified Redis-backed Architecture

## 🔄 Recent Changes (PR #47 Update)

**This PR simplifies the UI refresh architecture by removing duplicate MQTT publisher/consumer paths introduced in previous PRs.**

### Why the Revert?

Previous implementations (see PR #47) introduced multiple parallel refresh paths that created issues:

1. **Duplicate refresh paths**: Both MQTT WebSocket-based and Redis-backed polling running simultaneously
2. **Reconnection loops**: MQTT WebSocket clients in UI components causing connection storms
3. **Complexity**: Multiple mechanisms doing the same thing, making debugging difficult

### Solution: Single Source of Truth

This PR restores **Redis-backed refresh as the single source-of-truth** for UI updates:

- ✅ **Production**: Gateway publishes refresh timestamps to Redis via `request_refresh()`
- ✅ **UI Polling**: Streamlit UI polls Redis via `consume_refresh()` in main loop
- ✅ **Manual Refresh**: UI components can still trigger manual refresh via button clicks
- ❌ **Removed**: MQTT WebSocket subscriber components in UI code
- ❌ **Removed**: Duplicate MQTT publisher methods in gateway

### References

- **PR #47**: Original MQTT UI refresh implementation
- **PR #49**: Updates and consolidation (this PR updates #49)

## Overview

The auto-refresh feature enables Streamlit UI pages to automatically update when relevant MQTT messages are received. This provides a real-time user experience without requiring manual page refreshes.

## 🔑 Key Point: Redis is Optional for Testing

**The UI works perfectly without Redis!** The system is designed with graceful degradation:

- **Without Redis:** UI displays normally, manual refresh works (F5), no auto-refresh
- **With Redis:** Full auto-refresh capability (~1 second latency on MQTT events)

**For quick testing:** Just run `streamlit run omf2/omf.py` - no Redis needed!

**For full auto-refresh:** Follow the setup instructions below.

> 📘 **See [QUICK_START_AUTO_REFRESH.md](QUICK_START_AUTO_REFRESH.md) for a quick start guide with examples.**

## Simplified Architecture

The system consists of three main components:

1. **Backend Refresh Module** (`omf2/backend/refresh.py`)
   - Redis-based shared store for refresh timestamps
   - In-memory fallback when Redis unavailable
   - Throttle logic to prevent excessive refreshes (minimum 1 second between refreshes)
   - Group-based refresh management (e.g., 'order_updates', 'module_updates')

2. **Gateway Integration** (`omf2/ccu/ccu_gateway.py`)
   - Triggers UI refresh after processing MQTT messages via `request_refresh()`
   - Uses `gateway.yml` refresh_triggers mapping to determine which groups to refresh
   - Supports wildcard pattern matching for topic patterns

3. **UI Polling** (`omf2/omf.py` and `omf2/ui/utils/ui_refresh.py`)
   - `consume_refresh()` checks Redis for new refresh timestamps in main loop
   - Calls `st.rerun()` exactly once when new refresh detected
   - Manual refresh via `request_refresh()` from UI components still works

## Configuration

### Environment Variables

- **REDIS_URL**: Redis connection URL (default: `redis://localhost:6379/0`)

This can also be configured via Streamlit secrets (`.streamlit/secrets.toml`):

```toml
REDIS_URL = "redis://localhost:6379/0"
```
```

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

## Dependencies

### Redis

Redis is required as the shared store for refresh timestamps. The system will function without Redis, but auto-refresh will not work.

**Install Redis locally:**

```bash
# Using apt (Ubuntu/Debian)
sudo apt-get install redis-server

# Using Homebrew (macOS)
brew install redis

# Using Docker
docker run -d -p 6379:6379 --name redis redis:latest
```

**Start Redis:**

```bash
# System service
sudo systemctl start redis

# Docker
docker start redis

# Direct
redis-server
```

### Python Packages

Required Python packages (already in `requirements.txt`):

```
redis>=7.0.0
fakeredis>=2.20.0  # For testing
streamlit>=1.28.0
```

## Usage

### Gateway-Side Refresh Trigger

The gateway automatically triggers refresh when MQTT messages are processed:

```python
from omf2.backend.refresh import request_refresh

# Trigger refresh for a group (called by gateway)
request_refresh('order_updates', min_interval=1.0)
```

### UI-Side Manual Refresh

UI components can trigger manual refresh:

```python
from omf2.ui.utils.ui_refresh import request_refresh

def show_my_page():
    # Button to manually refresh
    if st.button("🔄 Refresh"):
        request_refresh()
        st.rerun()
    
    # Load and display data
    data = get_my_data()
    st.write(data)
```

### Manual Refresh Trigger

You can manually trigger a refresh from Python code:

```python
from omf2.backend.refresh import request_refresh

# Trigger refresh for a group
request_refresh('order_updates', min_interval=1.0)
```

## Testing

### Unit Tests

Run the refresh module tests:

```bash
# All refresh tests
pytest tests/test_refresh.py -v

# Gateway integration tests
pytest tests/test_gateway_refresh_integration.py -v
```

### Integration Testing

1. **Start Redis:**
   ```bash
   docker run -d -p 6379:6379 --name redis redis:latest
   ```

2. **Start Streamlit UI:**
   ```bash
   streamlit run omf2/omf.py
   ```

3. **Publish a test MQTT message:**
   ```bash
   mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "test123"}'
   ```

4. **Verify refresh:**
   - Gateway logs should show: "🔄 UI refresh triggered for group 'order_updates'"
   - Check Redis: `redis-cli GET "ui:last_refresh:order_updates"`
   - UI should auto-refresh within 1-2 seconds

### QA Steps (Production vs Development)

1. **Verify Redis connection:**
   - Check that Redis is running: `redis-cli ping` (should return `PONG`)
   - Check logs for "✅ Redis client initialized"

2. **Verify API endpoint:**

#### Production Behavior (with Redis)

1. **Verify Redis connection:**
   - Check that Redis is running: `redis-cli ping` (should return `PONG`)
   - Check logs for "✅ Redis client initialized"

2. **Verify gateway integration:**
   - Publish an MQTT message matching a refresh_triggers pattern
   - Check gateway logs for "🔄 UI refresh triggered for group"
   - Query Redis: `redis-cli GET "ui:last_refresh:order_updates"`
   - Verify timestamp is recent

3. **Verify UI auto-refresh:**
   - Open a Streamlit page (e.g., Production Orders)
   - Publish an MQTT message
   - Observe that the page refreshes within ~1-2 seconds
   - Check browser console for no errors

4. **Verify throttling:**
   - Publish multiple MQTT messages rapidly
   - Check that refresh timestamp only updates once per second

#### Development Behavior (without Redis)

1. **Verify fallback mode:**
   - Start UI without Redis running
   - Check logs for "⚠️ Redis connection failed... Using in-memory fallback"
   - UI should still load and display normally

2. **Manual refresh:**
   - Use manual refresh buttons in UI
   - Verify data updates correctly
   - F5 browser refresh should always work

3. **Testing:**
   - Run unit tests with fakeredis
   - No Redis dependency for local development

## Troubleshooting

### Redis Connection Issues

**Symptom:** "⚠️ Redis not available" in logs

**Solutions:**
1. Check that Redis is running: `redis-cli ping`
2. Verify REDIS_URL environment variable or secret is correct
3. Check firewall rules if Redis is on a different host
4. **Development**: System works in fallback mode; manual refresh still available

### Auto-Refresh Not Working

**Symptom:** UI doesn't refresh automatically

**Solutions:**
1. Verify that the MQTT topic matches a pattern in `refresh_triggers`
2. Check gateway logs for "🔄 UI refresh triggered"
3. Verify Redis connection
4. Check Redis timestamp: `redis-cli GET "ui:last_refresh:order_updates"`
5. **Development**: Use manual refresh buttons as fallback

### Throttle Too Aggressive

**Symptom:** UI updates are delayed too much

**Solutions:**
1. Adjust `min_interval` parameter in `request_refresh()` calls
2. Consider creating more granular refresh groups
3. Check if multiple rapid messages are being throttled

## Rollback Notes

If you need to rollback this PR (unlikely, as this is the stable version):

1. **Restore MQTT WebSocket UI components:**
   - Restore `omf2/ui/components/mqtt_subscriber/`
   - Restore `omf2/ui/admin/admin_subtab.py`

2. **Restore gateway MQTT publish:**
   - Restore `publish_ui_refresh()` method in `ccu_gateway.py`
   - Set `OMF2_UI_REFRESH_VIA_MQTT=1` environment variable

3. **Configure MQTT WebSocket:**
   - Set `OMF2_UI_MQTT_WS_URL=ws://broker:9001` in environment
   - Update `.streamlit/secrets.toml` with MQTT WebSocket URL

4. **Expect issues:**
   - Reconnection loops under load
   - Race conditions with multiple tabs
   - Higher CPU usage from WebSocket connections

**Recommendation:** Don't rollback. This simplified version is more stable.

## Best Practices

1. **Use appropriate refresh groups:**
   - Group related topics together (e.g., all order topics in 'order_updates')
   - Don't create too many groups (increases polling overhead)

2. **Throttle interval:**
   - Default 1 second is good for most use cases
   - Increase for less critical updates
   - Don't set below 0.5 seconds

3. **Pattern matching:**
   - Use wildcards sparingly (they're less efficient)
   - Prefer exact matches when possible

4. **Testing:**
   - Always test with fakeredis in unit tests
   - Use real Redis for integration tests
   - Test throttling behavior

5. **Production deployment:**
   - Always run Redis in production for multi-process coordination
   - Monitor Redis memory usage (minimal overhead)
   - Use Redis persistence (RDB or AOF) for refresh state durability

## Performance Considerations

- **Redis memory:** Each refresh group uses one key (~100 bytes)
- **UI polling overhead:** Streamlit reruns check Redis once per render (negligible)
- **Gateway overhead:** Throttle logic is very fast (< 1ms per message)
- **Network:** No additional network overhead (Redis already used by other components)

## Summary of Changes (This PR)

### Removed

- ❌ `omf2/ui/components/mqtt_subscriber/` - WebSocket MQTT subscriber component
- ❌ `omf2/ui/admin/admin_subtab.py` - Duplicate admin status page
- ❌ `publish_ui_refresh()` method - MQTT publishing from gateway
- ❌ MQTT refresh code in production/storage order subtabs

### Kept/Restored

- ✅ Redis-backed `request_refresh()` in `omf2/backend/refresh.py`
- ✅ Gateway calls `request_refresh()` directly
- ✅ UI `consume_refresh()` polls Redis timestamps
- ✅ Manual refresh via UI buttons
- ✅ In-memory fallback when Redis unavailable
- ✅ Admin status display consolidated in `dashboard_subtab.py`
