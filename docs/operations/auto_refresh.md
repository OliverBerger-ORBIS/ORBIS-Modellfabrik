# Auto-Refresh for UI (Streamlit) with Redis Backend

## Overview

The auto-refresh feature enables Streamlit UI pages to automatically update when relevant MQTT messages are received. This provides a real-time user experience without requiring manual page refreshes.

**IMPORTANT:** This PR (#51) reverts changes introduced by Copilot PRs (ref: PR #47, updates PRs #49 and #50) that created duplicate refresh paths and reconnect loops. Redis-backed refresh remains the production source-of-truth.

## 🔑 Key Point: Redis is Optional for Testing

**The UI works perfectly without Redis!** The system is designed with graceful degradation:

- **Without Redis:** UI displays normally, manual refresh works (F5), no auto-refresh
- **With Redis:** Full auto-refresh capability (~1 second latency on MQTT events)

**For quick testing:** Just run `streamlit run omf2/omf.py` - no Redis needed!

**For full auto-refresh:** Follow the setup instructions below.

> 📘 **See [QUICK_START_AUTO_REFRESH.md](QUICK_START_AUTO_REFRESH.md) for a quick start guide with examples.**

## Architecture

The system uses a **Redis-backed refresh architecture** with the following components:

1. **Backend Refresh Module** (`omf2/backend/refresh.py`)
   - Redis-based shared store for refresh timestamps (with in-memory fallback)
   - Throttle logic to prevent excessive refreshes (minimum 1 second between refreshes)
   - Group-based refresh management (e.g., 'order_updates', 'module_updates')
   - Functions: `request_refresh(group, min_interval)`, `get_last_refresh(group)`

2. **Gateway Integration** (`omf2/ccu/ccu_gateway.py`)
   - Triggers UI refresh after processing MQTT messages via `request_refresh()`
   - Uses `gateway.yml` refresh_triggers mapping to determine which groups to refresh
   - **NO MQTT UI publishing** - uses Redis only

3. **UI Polling** (`omf2/omf.py` and `omf2/ui/utils/ui_refresh.py`)
   - Top-level `consume_refresh()` check in omf.py polls backend via `get_last_refresh()`
   - Checks all refresh groups on every rerun
   - Triggers `st.rerun()` when new refresh detected

## What Was Reverted

**Problems Introduced by Copilot PRs:**
- Duplicate refresh paths via MQTT UI publishing alongside Redis
- Additional MQTT subscriber components that created reconnect loops
- Conflicting publisher/consumer artifacts in UI code
- Environment variable OMF2_UI_REFRESH_VIA_MQTT enabled by default

**This PR (#51) Reverts:**
- Removed `omf2/ui/admin/admin_subtab.py` (old status display)
- Removed `omf2/ui/components/mqtt_subscriber/` (MQTT WebSocket component)
- Removed MQTT publish calls from `_trigger_ui_refresh()` in gateway
- Restored pure Redis-backed refresh via `request_refresh()` calls
- Updated `consume_refresh()` to poll backend directly

**What Remains:**
- Redis-backed refresh system as production source-of-truth
- Manual "Refresh Dashboard" button for Dev mode (not removed)
- Optional MQTT publishing via `OMF2_UI_REFRESH_VIA_MQTT` (disabled by default)
- Defensive session_state guards for MQTT clients (no reinit on reruns)

## Configuration

### Environment Variables

- **REDIS_URL**: Redis connection URL (default: `redis://localhost:6379/0`)
- **REFRESH_API_URL**: Base URL for the refresh API (default: `http://localhost:5001`)

These can also be configured via Streamlit secrets (`.streamlit/secrets.toml`):

```toml
REDIS_URL = "redis://localhost:6379/0"
REFRESH_API_URL = "http://localhost:5001"
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
flask>=3.0.0
fakeredis>=2.20.0  # For testing
streamlit>=1.28.0
requests>=2.31.0
```

## Usage

### Backend API Server

Start the Flask API server:

```bash
# Start the API server
python -m omf2.backend.api_refresh

# Or with custom host/port
python -c "from omf2.backend.api_refresh import run_api; run_api(host='0.0.0.0', port=5001)"
```

### Streamlit UI Integration

The UI pages automatically poll the API and refresh when needed:

```python
from omf2.ui.common.refresh_polling import should_reload_data, init_auto_refresh_polling

def show_my_page():
    # Initialize auto-refresh polling (1 second interval)
    init_auto_refresh_polling('order_updates', interval_ms=1000)
    
    # Check if we should reload data
    should_reload = should_reload_data('order_updates')
    
    if should_reload:
        logger.debug("🔄 Reloading data due to refresh trigger")
    
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

# UI polling helper tests
pytest tests/test_streamlit_polling_helper.py -v
```

### Integration Testing

1. **Start Redis:**
   ```bash
   docker run -d -p 6379:6379 --name redis redis:latest
   ```

2. **Start the API server:**
   ```bash
   python -m omf2.backend.api_refresh
   ```

3. **Publish a test MQTT message:**
   ```bash
   mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "test123"}'
   ```

4. **Check the API:**
   ```bash
   curl "http://localhost:5001/api/last_refresh?group=order_updates"
   ```

5. **Observe Streamlit UI:**
   - Open the production orders page
   - The page should automatically refresh within 1 second

### QA Steps for PR #51

**These steps verify that the reverted changes work correctly and Redis-backed refresh is operational.**

#### 1. Verify Redis Connection
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Check Redis keys for refresh groups
redis-cli KEYS "ui:last_refresh:*"
```

Expected in logs:
- "✅ Redis client initialized successfully"
- OR "⚠️ Redis not available. Using in-memory fallback"

#### 2. Verify Gateway Refresh Trigger
```bash
# Publish test MQTT message matching a refresh_triggers topic
mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "test123", "state": "active"}'

# Check Redis for updated timestamp
redis-cli GET "ui:last_refresh:order_updates"
```

Expected in gateway logs:
- "🔄 UI refresh triggered for group 'order_updates' (topic: ccu/order/active)"
- "✅ Refresh requested for group 'order_updates' at [timestamp] (Redis)"

#### 3. Verify Backend Refresh API
```bash
# Test the Python API directly
python3 -c "from omf2.backend.refresh import get_last_refresh, request_refresh; request_refresh('test_group', 1.0); print(get_last_refresh('test_group'))"

# Check all refresh groups
python3 -c "from omf2.backend.refresh import get_all_refresh_groups; print(get_all_refresh_groups())"
```

Expected output:
- First command should print a timestamp (e.g., 1698765432.123)
- Second command should list groups like: ['order_updates', 'test_group']

#### 4. Verify UI Polling Behavior
```bash
# Start Streamlit dashboard
streamlit run omf2/omf.py

# In another terminal, publish MQTT message
mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "test456"}'

# In another terminal, check Redis timestamp
redis-cli GET "ui:last_refresh:order_updates"
```

Expected UI behavior:
- Dashboard should detect refresh within 1-2 seconds (on next rerun)
- Page should reload automatically
- No reconnect loops or errors in browser console

#### 5. Verify No MQTT UI Publish (Default)
```bash
# Monitor MQTT topics
mosquitto_sub -h localhost -t "omf2/ui/refresh/#" -v

# Publish business message
mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "test789"}'
```

Expected behavior:
- **Should NOT see any messages on omf2/ui/refresh/*** topics (unless OMF2_UI_REFRESH_VIA_MQTT=1)
- Gateway should only call `request_refresh()` → writes to Redis
- No MQTT publishing to UI topics

#### 6. Verify Admin Status Display
```bash
# Open Streamlit dashboard
streamlit run omf2/omf.py

# Navigate to: Admin → Admin Settings → Dashboard
```

Expected in UI:
- "Refresh System Status" section visible
- Shows Redis connection status
- Shows active refresh groups
- Info message: "Uses Redis-backed timestamps with UI polling"

#### 7. Verify Manual Refresh Button (Dev Mode)
```bash
# Open Streamlit dashboard in Dev mode
streamlit run omf2/omf.py
```

Expected:
- Manual "Refresh Dashboard" button should still be present (not removed)
- Button should work when clicked (triggers page refresh)

#### 8. Test Without Redis (Fallback)
```bash
# Stop Redis
docker stop redis  # or: sudo systemctl stop redis

# Start Streamlit
streamlit run omf2/omf.py
```

Expected behavior:
- App starts normally
- Logs show: "⚠️ Redis connection failed... Using in-memory fallback"
- Manual refresh (F5) works
- No auto-refresh capability (expected)
- No crashes or errors

### Success Criteria

✅ Redis-backed refresh working (timestamps stored in Redis)
✅ Gateway calls `request_refresh()` only (no MQTT publish)
✅ UI polling detects refresh within 1-2 seconds
✅ No reconnect loops or duplicate refresh paths
✅ Admin status shows Redis connection status
✅ Manual refresh button still works
✅ Graceful fallback when Redis unavailable
✅ No errors in logs or browser console

### Regression Checks

❌ No `omf2/ui/admin/admin_subtab.py` file
❌ No `omf2/ui/components/mqtt_subscriber/` directory
❌ No MQTT messages on `omf2/ui/refresh/#` topics (by default)
❌ No environment variable `OMF2_UI_REFRESH_VIA_MQTT` set by default

### Original QA Steps (Legacy Reference)
   - `curl http://localhost:5001/api/health` (should return `{"status": "ok"}`)

3. **Verify gateway integration:**
   - Publish an MQTT message matching a refresh_triggers pattern
   - Check gateway logs for "🔄 UI refresh triggered for group"
   - Query the API: `curl "http://localhost:5001/api/last_refresh?group=order_updates"`
   - Verify timestamp is recent

4. **Verify UI auto-refresh:**
   - Open a Streamlit page with auto-refresh enabled
   - Publish an MQTT message
   - Observe that the page refreshes within ~1 second
   - Check browser console for no errors

5. **Verify throttling:**
   - Publish multiple MQTT messages rapidly
   - Check that refresh timestamp only updates once per second

## Troubleshooting

### Redis Connection Issues

**Symptom:** "⚠️ Redis not available" in logs

**Solutions:**
1. Check that Redis is running: `redis-cli ping`
2. Verify REDIS_URL environment variable or secret is correct
3. Check firewall rules if Redis is on a different host

### API Not Responding

**Symptom:** UI polling fails, no auto-refresh

**Solutions:**
1. Check that the API server is running
2. Verify REFRESH_API_URL is correct
3. Check API logs for errors
4. Test API manually: `curl http://localhost:5001/api/health`

### Auto-Refresh Not Working

**Symptom:** UI doesn't refresh automatically

**Solutions:**
1. Verify that the MQTT topic matches a pattern in `refresh_triggers`
2. Check gateway logs for "🔄 UI refresh triggered"
3. Verify Redis connection
4. Check API endpoint returns recent timestamp
5. Ensure `streamlit_autorefresh` is installed (or fallback is working)

### Throttle Too Aggressive

**Symptom:** UI updates are delayed too much

**Solutions:**
1. Adjust `min_interval` parameter in `request_refresh()` calls
2. Consider creating more granular refresh groups
3. Check if multiple rapid messages are being throttled

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

5. **Monitoring:**
   - Monitor Redis memory usage
   - Check API response times
   - Watch for excessive polling

## Performance Considerations

- **Redis memory:** Each refresh group uses one key (~100 bytes)
- **API overhead:** Each UI page polls every 1 second (minimal overhead)
- **Gateway overhead:** Throttle logic is very fast (< 1ms per message)
- **Network:** API polling is lightweight (< 100 bytes per request)

## Future Enhancements

- WebSocket support for push-based refresh (eliminates polling)
- Configurable polling intervals per page
- Refresh event history and analytics
- Multi-Redis support for high availability
