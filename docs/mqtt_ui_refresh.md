# MQTT UI Refresh Feature

This document describes the MQTT-driven UI refresh pipeline for the Orbis Modellfabrik dashboard.

## Overview

The MQTT UI refresh feature provides real-time UI updates by reusing the existing MQTT client infrastructure. Business functions can publish refresh events via the gateway, which are then received by Streamlit components via WebSocket. This is an **opt-in** feature with two separate configuration flags.

## Architecture (Simplified)

```
MQTT Client → Gateway → Manager → Gateway.publish_ui_refresh()
                                           ↓
                                     omf2/ui/refresh/{group}
                                           ↓
                                   MQTT Broker (WebSocket)
                                           ↓
                              Streamlit mqtt_subscriber Component
                                           ↓
                                      UI Reload
```

### Key Principle

**Single MQTT connection**: The gateway reuses the existing `mqtt_client` connection instead of creating new publishers/subscribers.

### Components

1. **Gateway.publish_ui_refresh()** (`omf2/ccu/ccu_gateway.py`)
   - Method in existing CcuGateway class
   - Reuses existing `mqtt_client` connection
   - Publishes to topics: `omf2/ui/refresh/{group}`
   - Opt-in via `OMF2_UI_REFRESH_VIA_MQTT` env var
   - Defensive: never blocks business flow

2. **MQTT Subscriber Component** (`omf2/ui/components/mqtt_subscriber/`)
   - Custom Streamlit component with JavaScript frontend
   - Connects to MQTT broker via WebSocket
   - Subscribes to refresh topics and pushes messages to Streamlit
   - Invisible (height=0) and defensive
   - Opt-in via `OMF2_UI_MQTT_WS_URL` env var

## Configuration

### Two Separate Opt-In Flags

**1. Gateway Publish** (Business functions → MQTT):
```bash
export OMF2_UI_REFRESH_VIA_MQTT=1
```

**2. UI Subscribe** (MQTT → WebSocket → Streamlit):
```bash
export OMF2_UI_MQTT_WS_URL="ws://broker-host:9001"
```

Or in `.streamlit/secrets.toml`:
```toml
[mqtt]
ws_url = "ws://broker-host:9001"
```

### Why Two Flags?

- **Gateway publish** can be enabled independently for logging/monitoring
- **UI subscribe** can be disabled if WebSocket unavailable
- Allows testing each component separately

## Usage

### UI Components (Automatic)

The production and storage orders subtabs automatically use MQTT refresh when `OMF2_UI_MQTT_WS_URL` is configured:
- `omf2/ui/ccu/ccu_orders/production_orders_subtab.py`
- `omf2/ui/ccu/ccu_orders/storage_orders_subtab.py`

When enabled, they subscribe to `omf2/ui/refresh/order_updates`.

### Business Functions (Example Pattern)

Business functions can call `gateway.publish_ui_refresh()` after state changes:

```python
# Example from OrderManager.process_ccu_order_active()
from omf2.factory.gateway_factory import GatewayFactory

gateway_factory = GatewayFactory()
gateway = gateway_factory.get_ccu_gateway()

if gateway and hasattr(gateway, "publish_ui_refresh"):
    gateway.publish_ui_refresh(
        "order_updates",
        {"source": "order_manager", "count": len(orders), "type": "active"}
    )
```

**Pattern for other managers:**
1. Get gateway via GatewayFactory
2. Check if `publish_ui_refresh` method exists
3. Call with refresh group and optional payload
4. Method is defensive - never blocks on failure

## Testing

### Test with mosquitto_pub

```bash
# Publish a refresh message
mosquitto_pub -h localhost -p 1883 \
  -t omf2/ui/refresh/order_updates \
  -m '{"ts": 1234567890, "source": "test"}'
```

### Check Admin Status

Navigate to **Admin** → **Admin Status** subtab to see:
- Gateway MQTT publish status (`OMF2_UI_REFRESH_VIA_MQTT`)
- UI MQTT subscribe status (`OMF2_UI_MQTT_WS_URL`)
- Full pipeline status
- Broker URL and configuration source

### Verify Configuration

```bash
# Enable full pipeline
export OMF2_UI_REFRESH_VIA_MQTT=1
export OMF2_UI_MQTT_WS_URL="ws://localhost:9001"

# Start Streamlit
streamlit run omf2/ui/main_dashboard.py

# Check Admin Status subtab - should show:
# - Gateway: ✅ Enabled
# - UI: ✅ Enabled
# - Full pipeline: ✅ Active
```

## Message Format

MQTT refresh messages follow this JSON format:

```json
{
  "ts": 1234567890,
  "source": "order_manager",
  "count": 5,
  "type": "active"
}
```

- `ts`: Timestamp (automatically added if not present)
- `source`: Source of the refresh event (e.g., "order_manager", "gateway")
- Additional fields: Optional context data

## Defensive Design

The feature is designed to fail gracefully:

1. **Gateway publish disabled**: Method returns silently, no errors
2. **No MQTT client**: Method logs and returns, business flow continues
3. **MQTT publish fails**: Exception caught, logged, business flow continues
4. **UI subscribe disabled**: Existing polling mechanism remains active
5. **WebSocket connection fails**: Frontend component returns None, no crash

## Integration Points

### Current Integrations

- ✅ Production Orders subtab (UI subscriber)
- ✅ Storage Orders subtab (UI subscriber)
- ✅ OrderManager (Gateway publisher example)
- ✅ Admin Status display (configuration monitoring)

### Potential Future Integrations

- Gateway auto-publish via `_trigger_ui_refresh()` (when refresh_triggers match)
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
