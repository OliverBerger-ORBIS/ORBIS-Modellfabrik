# Auto-Refresh for UI (Streamlit) - Simplified Architecture

## Overview

The auto-refresh feature enables Streamlit UI pages to automatically update when relevant MQTT messages are received. This provides a real-time user experience without requiring manual page refreshes.

**This document reflects the simplified architecture from PR #47 (fix/ui-refresh-simplify)**, which removes duplicated MQTT publisher/subscriber components and restores the canonical Redis-backed refresh path as the single source-of-truth. This PR addresses issues introduced in earlier PRs and updates work from PR #49/#50.

## 🔑 Key Point: Redis is Optional for Testing

**The UI works perfectly without Redis!** The system is designed with graceful degradation:

- **Without Redis:** UI displays normally, manual refresh works (F5), no auto-refresh
- **With Redis:** Full auto-refresh capability (~1 second latency on MQTT events)

**For quick testing:** Just run `streamlit run omf2/omf.py` - no Redis needed!

**For full auto-refresh:** Follow the setup instructions below.

> 📘 **See [QUICK_START_AUTO_REFRESH.md](QUICK_START_AUTO_REFRESH.md) for a quick start guide with examples.**

## Recent Changes (PR #47: fix/ui-refresh-simplify)

**Problem:** Prior Copilot PRs introduced duplicated MQTT publisher/subscriber components that caused:
- Reconnect loops due to multiple MQTT clients being created on UI reruns
- Confusion about which refresh path was active (MQTT vs Redis polling)
- Redundant code paths for UI refresh notifications
- `publish_ui_refresh()` method causing duplicate refresh triggers

**Solution:** PR #47 (fix/ui-refresh-simplify) reverts to the canonical architecture:
1. **Single Refresh Path:** Gateway → `omf2.backend.refresh.request_refresh()` → Redis → UI polling
2. **No MQTT UI Components:** Confirmed removal of `omf2/ui/components/mqtt_subscriber/` and related publisher code
3. **Singleton MQTT Clients:** Existing CCU/Admin clients remain in `st.session_state` (not recreated on reruns)
4. **HTTP Polling Enabled:** UI calls `consume_refresh()` at startup to check Redis backend for updates
5. **Removed Duplicate Methods:** Deleted `CcuGateway.publish_ui_refresh()` and redundant calls from order_manager

**Benefits:**
- Simpler, more maintainable code
- No MQTT reconnect issues
- Clear separation: MQTT for business logic, Redis for UI coordination
- Production-ready with minimal configuration
- Single source-of-truth for refresh logic

**Related PRs:** This PR updates/supersedes work from PR #49/#50 where relevant.

## Architecture

The system consists of a simplified, single-path architecture:

1. **Backend Refresh Module** (`omf2/backend/refresh.py`)
   - Redis-based shared store for refresh timestamps (with in-memory fallback)
   - Throttle logic to prevent excessive refreshes (minimum 1 second between refreshes)
   - Group-based refresh management (e.g., 'order_updates', 'module_updates')
   - Thread-safe operations with global lock

2. **Gateway Integration** (`omf2/ccu/ccu_gateway.py`)
   - Calls `request_refresh(group_name, min_interval=1.0)` when MQTT messages are processed
   - Uses `gateway.yml` refresh_triggers mapping to determine which groups to refresh
   - Supports wildcard pattern matching for topic patterns
   - **Does NOT publish MQTT UI messages** (removed in PR #47)

3. **UI Polling** (`omf2/ui/utils/ui_refresh.py`)
   - `consume_refresh()` is called early in `omf2/omf.py` (line 132)
   - Polls all active refresh groups from Redis backend
   - Triggers `st.rerun()` when new timestamps detected
   - Lightweight, no MQTT clients created in UI code

## Production vs Development Behavior

### Production (with Redis)

**Requirements:**
- Redis server running and accessible via `REDIS_URL`
- Gateway connected to MQTT broker
- Streamlit UI running

**Behavior:**
- Full auto-refresh capability (~1-2 second latency)
- Gateway writes refresh timestamps to Redis on MQTT events
- UI polls Redis backend and triggers rerun when timestamps update
- Throttling prevents excessive refreshes (configurable min_interval)

**Setup:**
```bash
# Start Redis
docker run -d -p 6379:6379 --name redis redis:latest

# Set environment variable
export REDIS_URL="redis://localhost:6379/0"

# Start Streamlit
streamlit run omf2/omf.py
```

### Development (without Redis)

**Requirements:**
- None (Redis optional)

**Behavior:**
- UI displays normally with all functionality
- Manual refresh works (F5 or "Refresh Dashboard" button)
- Auto-refresh disabled (graceful degradation)
- In-memory fallback used (not shared across processes)
- No errors or warnings about Redis

**Setup:**
```bash
# Just start Streamlit - no Redis needed
streamlit run omf2/omf.py
```

**Developer Note:** The manual refresh button is always available and works in both modes. Use it for development and testing without Redis infrastructure.

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

### QA Steps (Post PR #47 Cleanup)

These steps verify the simplified Redis-backed refresh architecture works correctly:

1. **Verify Redis connection:**
   ```bash
   # Check Redis is running
   redis-cli ping  # Should return "PONG"
   
   # Or with Docker
   docker ps | grep redis  # Should show running container
   ```
   - Check Streamlit logs for "✅ Redis client initialized successfully"
   - Check Admin → Dashboard Subtab → Auto-Refresh Status for "✅ Available"

2. **Verify backend refresh module:**
   ```bash
   # Test request_refresh() directly from Python
   python3 -c "
   from omf2.backend.refresh import request_refresh, get_last_refresh
   request_refresh('test_group', min_interval=1.0)
   print('Timestamp:', get_last_refresh('test_group'))
   "
   ```
   - Should print a recent timestamp (Unix epoch time)

3. **Verify gateway integration:**
   ```bash
   # Start Streamlit UI
   streamlit run omf2/omf.py
   
   # In another terminal, publish test MQTT message
   mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "test123", "state": "running"}'
   ```
   - Check gateway logs for "🔄 UI refresh triggered for group 'order_updates'"
   - Verify `request_refresh()` was called (not MQTT publish)

4. **Verify UI auto-refresh (production orders):**
   ```bash
   # With Streamlit running, publish order update
   mosquitto_pub -h localhost -t "ccu/order/active" -m '{"orderId": "ORDER-001", "workpiece": "RED", "state": "processing", "module": "SVR4H73275", "step": "drilling"}'
   ```
   - Open CCU → Production Orders page
   - Page should refresh automatically within ~1-2 seconds
   - Check browser console for no errors
   - Verify no MQTT reconnect messages in logs

5. **Verify no MQTT UI reconnect loops:**
   ```bash
   # Watch logs for reconnect patterns
   tail -f logs/omf2.log | grep -i "mqtt\|connect"
   
   # Click around the UI, change pages
   # Should NOT see repeated "MQTT Client connected" messages
   ```
   - MQTT clients should initialize once at startup
   - No reconnects on page navigation or reruns

6. **Verify throttling:**
   ```bash
   # Publish multiple rapid messages
   for i in {1..10}; do
     mosquitto_pub -h localhost -t "ccu/order/active" -m "{\"orderId\": \"test-$i\"}"
     sleep 0.1
   done
   
   # Check Redis for throttling
   python3 -c "
   from omf2.backend.refresh import get_last_refresh
   import time
   print('Last refresh:', get_last_refresh('order_updates'))
   "
   ```
   - Should see only 1-2 refresh timestamps despite 10 messages
   - Confirms throttling is working (min_interval=1.0)

7. **Verify dev mode manual refresh:**
   ```bash
   # Without Redis
   REDIS_URL="redis://invalid:6379" streamlit run omf2/omf.py
   ```
   - UI should load normally
   - Manual "Refresh Dashboard" button should work (F5 also works)
   - No errors about Redis (graceful fallback)
   - Auto-refresh disabled (expected without Redis)

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

## QA Checklist for PR #47 (fix/ui-refresh-simplify)

Use this checklist to verify the cleanup was successful:

### Code Verification
- [ ] Verify `omf2/ui/publisher/uipublisher.py` does not exist
- [ ] Verify `omf2/gateway/mqtt_publisher.py` does not exist
- [ ] Verify `omf2/factory/publisher_factory.py` does not exist
- [ ] Verify `omf2/ccu/business/ui_notify_helper.py` does not exist
- [ ] Verify `omf2/ui/components/mqtt_subscriber/` directory does not exist
- [ ] Verify `omf2/ui/admin/admin_subtab.py` does not exist
- [ ] Verify `CcuGateway.publish_ui_refresh()` method does not exist in `omf2/ccu/ccu_gateway.py`
- [ ] Verify `publish_ui_refresh` not called in `omf2/ccu/order_manager.py`

### Functional Verification
- [ ] `omf2/backend/refresh.py` exports `request_refresh(group, min_interval)` and `get_last_refresh(group)`
- [ ] `omf2/ccu/ccu_gateway.py::_trigger_ui_refresh()` only calls `request_refresh()` (no MQTT publishing)
- [ ] `omf2/omf.py` calls `consume_refresh()` at line ~135 before rendering
- [ ] MQTT clients (admin, ccu) are initialized as singletons in `st.session_state`
- [ ] Admin dashboard shows refresh status in `dashboard_subtab.py::_render_refresh_status()`

### Runtime Testing (Production Mode with Redis)
1. **Start Redis:**
   ```bash
   docker run -d -p 6379:6379 --name redis redis:latest
   export REDIS_URL="redis://localhost:6379/0"
   ```

2. **Start Streamlit:**
   ```bash
   streamlit run omf2/omf.py
   ```

3. **Verify Auto-Refresh:**
   - Open UI in browser
   - Trigger an MQTT message (e.g., order update)
   - Verify UI refreshes automatically within 1-2 seconds
   - Check gateway logs for "🔄 UI refresh triggered for group"
   - Verify no reconnect loops in logs

4. **Check Admin Status:**
   - Navigate to Admin Settings → Dashboard
   - Expand "🔄 Auto-Refresh Status"
   - Verify Redis status shows "✅ Available"
   - Verify active refresh groups are listed

### Runtime Testing (Dev Mode without Redis)
1. **Start Streamlit (no Redis):**
   ```bash
   streamlit run omf2/omf.py
   ```

2. **Verify Graceful Degradation:**
   - UI should display normally
   - Manual refresh button should work (if present)
   - No errors about Redis in logs (only warnings)
   - In-memory fallback should activate

3. **Check Admin Status:**
   - Navigate to Admin Settings → Dashboard
   - Expand "🔄 Auto-Refresh Status"
   - Verify Redis status shows "❌ Unavailable" or "⚠️ In-memory fallback"
   - Verify helpful message about enabling Redis

### Linting
- [ ] Run `black omf2/` - no formatting issues
- [ ] Run `ruff check omf2/` - no linting errors
- [ ] No circular import errors

### Documentation
- [ ] `docs/operations/auto_refresh.md` references PR #47
- [ ] QA checklist included in documentation
- [ ] Production vs Dev behavior clearly documented

## Future Enhancements

- WebSocket support for push-based refresh (eliminates polling)
- Configurable polling intervals per page
- Refresh event history and analytics
- Multi-Redis support for high availability
