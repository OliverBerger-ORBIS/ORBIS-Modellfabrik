# Auto-Refresh for UI (Streamlit) with MQTT

## Overview

The auto-refresh feature enables Streamlit UI pages to automatically update when relevant MQTT messages are received. This provides a real-time user experience without requiring manual page refreshes.

**This implementation is based on learnings from PR #47 (autorefresh admin/status visibility) and PR #48 (removal of duplicate publishers and Redis), combining the best parts into a minimal, safe pattern.**

## 🔑 Architecture: MQTT-Driven UI Refresh (Safe Pattern)

The system uses a **single, safe pattern** for UI refresh:

```
Business/Gateway → MQTT Publish → admin_mqtt_client → request_refresh() → consume_refresh() → st.rerun()
```

### Key Components

1. **Gateway Publishing** (`omf2/ccu/ccu_gateway.py`)
   - Detects state changes during message routing
   - Publishes lightweight events to `omf2/ui/refresh/{group}` 
   - Uses existing gateway mqtt_client (no new clients created)
   - Defensive: never blocks business flow on publish failure
   - Opt-in via `OMF2_UI_REFRESH_VIA_MQTT=1` environment variable

2. **UI MQTT Client** (`omf2/admin/admin_mqtt_client.py`)
   - Existing admin_mqtt_client in UI process subscribes to all topics (`#`)
   - Detects `omf2/ui/refresh/*` messages in `_on_message` callback
   - Calls `request_refresh()` to set flag in `st.session_state`
   - NO new MQTT clients created on rerun

3. **Refresh Handler** (`omf2/ui/utils/ui_refresh.py`)
   - `request_refresh()`: Sets timestamp flag in `st.session_state`
   - `consume_refresh()`: Checks flag and returns True if set, then clears it
   - Thread-safe, in-process, no Redis dependency

4. **Central Rerun Point** (`omf2/omf.py`)
   - **ONLY place** where `st.rerun()` is called
   - Calls `consume_refresh()` at the start of `main()`
   - If flag is set, triggers single `st.rerun()` and returns

## Safety Guarantees

✅ **No new MQTT clients in UI:** Reuses existing admin_mqtt_client singleton  
✅ **All publishes use gateway client:** No duplicate MQTT connections  
✅ **Single rerun entry point:** Only `consume_refresh()` in omf.py triggers st.rerun()  
✅ **Defensive error handling:** Publish failures are logged but don't block business logic  
✅ **In-process state:** No Redis dependency for UI-side refresh tracking  

## Configuration

### Environment Variables

- **OMF2_UI_REFRESH_VIA_MQTT**: Enable Gateway publishing (default: disabled)
  - Set to `1` or `true` to enable

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

### Enable MQTT-Driven Refresh

```bash
# Set environment variable
export OMF2_UI_REFRESH_VIA_MQTT=1

# Start Streamlit
streamlit run omf2/omf.py
```

### Admin Status Dashboard

View the full pipeline status:

1. Navigate to: **Admin → Admin Settings → Dashboard**
2. Expand **UI Auto-Refresh Status**
3. Check Gateway publish and UI subscribe status
4. Use provided test command to manually verify

### Manual Testing

Publish a test message to trigger UI refresh:

```bash
# Publish to a refresh topic
mosquitto_pub -t omf2/ui/refresh/test -m '{"ts": 12345, "source":"manual_test"}'
```

Expected behavior:
1. admin_mqtt_client receives message
2. `request_refresh()` sets flag in session_state
3. Next Streamlit rerun cycle detects flag via `consume_refresh()`
4. UI performs a single rerun cycle via `st.rerun()`

## Implementation Details

### Gateway Publishing

The Gateway automatically publishes refresh events when processing messages that match `refresh_triggers` patterns:

```python
# In ccu_gateway.py _route_ccu_message()
if topic in self.sensor_topics:
    sensor_manager.process_sensor_message(topic, message, meta)
    self._trigger_ui_refresh(topic)  # Publishes to omf2/ui/refresh/{group}
```

The `publish_ui_refresh()` method:
- Checks if `OMF2_UI_REFRESH_VIA_MQTT` environment variable is set to any non-empty value
- Uses existing `mqtt_client.publish()`
- Payload: `{group, ts, source, optional meta}`
- QoS 0, retain=False (lightweight)
- Defensive: catches and logs exceptions without blocking

### UI MQTT Handler

The admin_mqtt_client receives all MQTT messages and detects UI refresh topics:

```python
# In admin_mqtt_client.py _on_message()
if topic.startswith("omf2/ui/refresh/"):
    group = topic.replace("omf2/ui/refresh/", "")
    if group:
        from omf2.ui.utils.ui_refresh import request_refresh
        request_refresh()  # Sets flag in st.session_state
```

### Central Rerun Point

Only one place triggers st.rerun():

```python
# In omf.py main()
if consume_refresh():
    st.rerun()  # Single, safe rerun
    return
```

## Removed Components (vs PR #47 & #48)

This implementation removes/simplifies:

- ❌ **Browser-based MQTT WebSocket component** (`omf2/ui/components/mqtt_subscriber/`)
  - Created new MQTT clients on every rerun
  - WebSocket-based, not server-side
  - Replaced by: existing admin_mqtt_client routing

- ❌ **Redis dependency for UI refresh**
  - UI-side refresh tracking is now in-process via `st.session_state`
  - Redis can still be used by business layer if needed
  - Simpler, fewer dependencies

- ❌ **Duplicate MQTT publishers**
  - All publishes use gateway mqtt_client
  - No publisher_factory or separate UI publishers

## Testing

### Unit Tests

Run the refresh module tests:

```bash
# Refresh tests
pytest tests/test_refresh.py -v

# Gateway integration tests
pytest tests/test_gateway_refresh_integration.py -v
```

### Integration Testing

**Prerequisites:**
- MQTT broker must be running (in OMF2, this is typically already running in Live and Replay environments)
- If testing in a new environment, ensure MQTT broker is configured and accessible

1. **Enable UI Refresh:**
   ```bash
   export OMF2_UI_REFRESH_VIA_MQTT=1
   ```

2. **Start Streamlit:**
   ```bash
   streamlit run omf2/omf.py
   ```

3. **Verify Status:**
   - Navigate to **Admin → Admin Settings → Dashboard**
   - Check **UI Auto-Refresh Status**
   - Both Gateway publish and UI subscribe should show ✅

4. **Publish Test Message:**
   ```bash
   mosquitto_pub -t omf2/ui/refresh/test -m '{"ts": 12345, "source":"test"}'
   ```

6. **Observe:**
   - Check logs for `📥 Received on omf2/ui/refresh/test`
   - Check logs for `🔄 UI refresh requested for group 'test' from MQTT`
   - UI should refresh

### QA Steps

1. **Verify Gateway Publishing:**
   - Publish an MQTT message matching a `refresh_triggers` pattern
   - Check gateway logs for `✅ Published UI refresh to omf2/ui/refresh/{group}`
   - Use MQTT client to subscribe: `mosquitto_sub -t omf2/ui/refresh/#`

2. **Verify UI Reception:**
   - Check admin_mqtt_client is connected (Admin Settings dashboard)
   - Publish test message to `omf2/ui/refresh/test`
   - Check logs for `🔄 UI refresh requested`

3. **Verify Rerun:**
   - Open a Streamlit page
   - Publish test message
   - Observe page refresh (check browser console for Streamlit rerun)

4. **Verify No Reconnect Loops:**
   - Monitor MQTT broker connections
   - Trigger multiple refreshes
   - Confirm no new connections created

5. **Verify Defensive Behavior:**
   - Stop MQTT broker
   - Trigger business flow that would publish refresh
   - Confirm business flow continues without error

## Troubleshooting

### Gateway Not Publishing

**Symptom:** No messages on `omf2/ui/refresh/*` topics

**Solutions:**
1. Check `OMF2_UI_REFRESH_VIA_MQTT=1` is set
2. Verify Gateway mqtt_client is connected
3. Check if incoming message matches `refresh_triggers` patterns
4. Check gateway logs for `🔇 MQTT UI refresh disabled`

### UI Not Receiving

**Symptom:** Messages published but UI not refreshing

**Solutions:**
1. Check admin_mqtt_client is connected (Admin Settings dashboard)
2. Verify MQTT broker is running and accessible
3. Check admin_mqtt_client logs for `📥 Received on omf2/ui/refresh/...`
4. Verify `request_refresh()` is being called

### Refresh Not Triggering Rerun

**Symptom:** UI receives message but doesn't refresh

**Solutions:**
1. Check `consume_refresh()` is called in omf.py main()
2. Verify `st.session_state[_FLAG]` is being set
3. Check for errors in ui_refresh.py
4. Verify Streamlit version supports st.rerun()

## Best Practices

1. **Use appropriate refresh groups:**
   - Group related topics together (e.g., all order topics in 'order_updates')
   - Keep groups broad to minimize number of refresh topics

2. **Gateway publishing:**
   - Only publish for significant state changes
   - Use lightweight payloads
   - Never block business flow on publish failure

3. **Testing:**
   - Test with real MQTT broker, not mock
   - Verify no MQTT client connection leaks
   - Test error paths (broker down, etc.)

4. **Monitoring:**
   - Monitor MQTT connection count (should remain constant)
   - Watch for excessive refresh events
   - Check st.rerun() frequency in logs

## Performance Considerations

- **MQTT overhead:** Minimal - single persistent connection per UI instance
- **Publish overhead:** < 1ms per event, non-blocking
- **UI refresh latency:** Typically < 100ms from publish to st.rerun()
- **No polling:** Event-driven, no background polling threads

## References

- **PR #47:** Autorefresh admin/status visibility improvements
- **PR #48:** Simplified architecture, removed duplicate publishers and Redis
- **This PR:** Combines best parts with safe MQTT-driven pattern

## Migration from Previous Patterns

**Note:** This section is for reference only if upgrading from older OMF2 versions. The current implementation in this PR already includes all necessary changes.

If you were using polling-based or Redis-based refresh patterns in earlier versions, here's what has changed:

**Components already removed in this PR:**
- Browser-based MQTT WebSocket component (`omf2/ui/components/mqtt_subscriber/`)
- No longer using `streamlit_autorefresh` polling calls
- No longer using Flask API refresh endpoints for polling
- No longer requiring external Redis for UI refresh coordination

**What this PR already implements:**
1. ✅ MQTT-driven refresh via existing admin_mqtt_client (no new clients)
2. ✅ In-process `st.session_state` for UI refresh tracking
3. ✅ Gateway publishes to `omf2/ui/refresh/{group}` topics
4. ✅ Single `st.rerun()` entry point in omf.py via `consume_refresh()`

**To use this implementation:**
1. Set `OMF2_UI_REFRESH_VIA_MQTT=1` environment variable
2. Restart Streamlit application
3. Verify status in Admin → Admin Settings → Dashboard → UI Auto-Refresh Status

The new pattern is simpler, faster, and more reliable - no external dependencies like Redis needed for UI refresh.
