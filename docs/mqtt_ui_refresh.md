# MQTT UI Refresh Feature

This document describes the MQTT-driven UI refresh pipeline for the Orbis Modellfabrik dashboard.

## Overview

The MQTT UI refresh feature provides real-time UI updates by using MQTT messages to trigger data reloads in Streamlit components. This is an **opt-in** feature that complements the existing polling-based refresh mechanism.

## Architecture

```
Business Function → UIPublisher → MQTT Broker → WebSocket → Streamlit Component → UI Reload
                                       ↓
                                  Topic: omf2/ui/refresh/{group}
```

### Components

1. **UIPublisher** (`omf2/ui/publisher/uipublisher.py`)
   - Protocol/ABC defining the interface for UI refresh publishers
   - `publish_refresh(group, payload)` method

2. **MQTTPublisher** (`omf2/gateway/mqtt_publisher.py`)
   - Implementation of UIPublisher using paho MQTT client
   - Publishes to topics: `omf2/ui/refresh/{group}`
   - Includes NoOpPublisher for graceful degradation

3. **PublisherFactory** (`omf2/factory/publisher_factory.py`)
   - Factory methods to obtain UIPublisher instances
   - Integrates with existing gateway infrastructure
   - Returns NoOpPublisher when MQTT unavailable

4. **UI Notify Helper** (`omf2/ccu/business/ui_notify_helper.py`)
   - Helper function for business functions to trigger UI updates
   - `notify_ui_on_change(ui_publisher, group, changed, details)`

5. **MQTT Subscriber Component** (`omf2/ui/components/mqtt_subscriber/`)
   - Custom Streamlit component with JavaScript frontend
   - Connects to MQTT broker via WebSocket
   - Subscribes to refresh topics and pushes messages to Streamlit
   - Invisible (height=0) and defensive

## Configuration

### Enable MQTT UI Refresh

**Option 1: Environment Variable**
```bash
export OMF2_UI_MQTT_WS_URL="ws://broker-host:9001"
```

**Option 2: Streamlit Secrets**
```toml
# .streamlit/secrets.toml
[mqtt]
ws_url = "ws://broker-host:9001"
```

### Optional: Configure Refresh Groups
```toml
# .streamlit/secrets.toml
[ui.refresh_triggers]
order_updates = true
sensor_data = true
module_status = true
```

## Usage

### UI Components (Automatic)

The production and storage orders subtabs automatically use MQTT refresh when configured:
- `omf2/ui/ccu/ccu_orders/production_orders_subtab.py`
- `omf2/ui/ccu/ccu_orders/storage_orders_subtab.py`

When MQTT is enabled, they subscribe to `omf2/ui/refresh/order_updates`.

### Business Functions (Optional)

Business functions can optionally publish refresh notifications:

```python
from omf2.factory.publisher_factory import get_ui_publisher
from omf2.ccu.business.ui_notify_helper import notify_ui_on_change

# Get publisher (returns NoOpPublisher if MQTT unavailable)
ui_publisher = get_ui_publisher()

# After processing data changes, notify UI
notify_ui_on_change(
    ui_publisher,
    group='order_updates',
    changed=True,
    details={'order_id': order_id, 'source': 'order_manager'}
)
```

## Testing

### Test with mosquitto_pub

```bash
# Publish a refresh message
mosquitto_pub -h localhost -p 1883 \
  -t omf2/ui/refresh/order_updates \
  -m '{"ts": 1234567890, "source": "test"}'
```

### Test Fallback (Redis)

```bash
# Set refresh timestamp via Redis
redis-cli SET ui:last_refresh:order_updates $(date +%s)
```

### Check Admin Status

Navigate to **Admin** → **Admin Status** subtab to see:
- MQTT WebSocket configuration status
- Broker URL and source
- Configured refresh groups

## Message Format

MQTT refresh messages follow this JSON format:

```json
{
  "ts": 1234567890,
  "source": "order_manager",
  "order_id": "abc123",
  ...additional fields...
}
```

- `ts`: Timestamp (automatically added if not present)
- `source`: Source of the refresh event
- Additional fields: Optional context data

## Defensive Design

The feature is designed to fail gracefully:

1. **No MQTT Configuration**: Uses existing polling mechanism
2. **MQTT Connection Fails**: NoOpPublisher returns False, UI continues with polling
3. **Component Load Error**: Streamlit UI continues normally
4. **WebSocket Connection Fails**: Frontend component returns None, no crash

## Integration Points

### Current Integrations

- ✅ Production Orders subtab
- ✅ Storage Orders subtab
- ✅ Admin Status display

### Potential Future Integrations

- Sensor data displays
- Module status displays
- System logs viewer
- Real-time dashboards

## Performance Notes

- Component is invisible (0 height)
- WebSocket connection is persistent
- Minimal overhead when MQTT disabled
- Existing polling remains as fallback
- No impact on non-MQTT users

## Troubleshooting

### MQTT not working

1. Check Admin Status subtab for configuration
2. Verify broker URL is correct (WebSocket port, usually 9001)
3. Check browser console for connection errors
4. Verify MQTT broker WebSocket listener is enabled
5. Test with mosquitto_pub to verify broker connectivity

### UI not refreshing

1. Verify MQTT message is published to correct topic
2. Check message format includes 'ts' field
3. Verify component is loaded (check browser console)
4. Confirm fallback polling still works
5. Check Streamlit logs for errors

### Component not loading

1. Verify frontend files are included in package
2. Check pyproject.toml includes `ui/components/mqtt_subscriber/frontend/*.html`
3. Verify mqtt.js CDN is accessible
4. Check browser console for JavaScript errors

## Security Considerations

- WebSocket URL should use WSS (secure WebSocket) in production
- MQTT broker should require authentication
- Consider firewall rules for WebSocket port
- Use TLS/SSL for broker connections
- Limit MQTT topic subscriptions to necessary groups

## Future Enhancements

- [ ] Authentication for WebSocket connections
- [ ] Compression for large payloads
- [ ] Reconnection backoff strategy
- [ ] Message queue for offline handling
- [ ] Metrics and monitoring integration
- [ ] Dynamic topic subscription based on active tabs
