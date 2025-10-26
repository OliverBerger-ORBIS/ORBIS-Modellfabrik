# Auto-Refresh Implementation for UI

This directory contains the implementation for automatic UI refresh triggered by MQTT messages.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis

```bash
# Using Docker (recommended for testing)
docker run -d -p 6379:6379 --name redis redis:latest

# Or using system Redis
redis-server
```

### 3. Test the Backend

```bash
# Run unit tests
pytest tests/test_refresh.py tests/test_gateway_refresh_integration.py tests/test_streamlit_polling_helper.py -v

# Run integration example
python tools/test_auto_refresh.py
```

### 4. Start the API Server

```bash
python -m omf2.backend.api_refresh
```

The API will be available at `http://localhost:5001`

### 5. Test the API

```bash
# Health check
curl http://localhost:5001/api/health

# Get refresh timestamp
curl "http://localhost:5001/api/last_refresh?group=order_updates"

# List all refresh groups
curl http://localhost:5001/api/refresh_groups
```

## Architecture

```
┌─────────────────┐
│  MQTT Broker    │
└────────┬────────┘
         │ messages
         v
┌─────────────────┐        ┌──────────────┐
│  CCU Gateway    │───────>│    Redis     │
│ (on_message)    │ write  │ (timestamps) │
└─────────────────┘        └──────┬───────┘
                                  │ read
                           ┌──────v───────┐
                           │  Flask API   │
                           │  (polling)   │
                           └──────┬───────┘
                                  │ HTTP
                           ┌──────v───────┐
                           │  Streamlit   │
                           │     UI       │
                           └──────────────┘
```

## Components

### Backend

- **omf2/backend/refresh.py**: Core refresh logic with Redis
- **omf2/backend/api_refresh.py**: Flask API for polling

### Gateway Integration

- **omf2/ccu/ccu_gateway.py**: Triggers refresh after MQTT message processing

### UI Integration

- **omf2/ui/common/refresh_polling.py**: Helper functions for Streamlit
- **omf2/ui/ccu/ccu_orders/production_orders_subtab.py**: Production orders with auto-refresh
- **omf2/ui/ccu/ccu_orders/storage_orders_subtab.py**: Storage orders with auto-refresh

### Configuration

- **omf2/ui/ccu/ccu_configuration/dashboard_gateway_configuration_subtab.py**: UI for editing refresh_triggers
- **omf2/registry/gateway.yml**: Configuration file with refresh_triggers

### Tests

- **tests/test_refresh.py**: Unit tests for refresh module (8 tests)
- **tests/test_gateway_refresh_integration.py**: Integration tests (6 tests)
- **tests/test_streamlit_polling_helper.py**: UI helper tests (14 tests)

## Configuration

### Environment Variables

Set these in your environment or `.streamlit/secrets.toml`:

```toml
REDIS_URL = "redis://localhost:6379/0"
REFRESH_API_URL = "http://localhost:5001"
```

### Gateway Configuration

Edit `omf2/registry/gateway.yml` to configure refresh triggers:

```yaml
gateway:
  refresh_triggers:
    order_updates:
      - ccu/order/active
      - ccu/order/completed
    
    module_updates:
      - module/v1/ff/*/state  # Wildcard pattern
```

Or use the Dashboard UI: **CCU → Configuration → Gateway Configuration**

## Testing

### Run All Tests

```bash
pytest tests/test_refresh.py tests/test_gateway_refresh_integration.py tests/test_streamlit_polling_helper.py -v
```

Expected output: **28 tests passed**

### Manual Testing

1. Start Redis: `docker run -d -p 6379:6379 redis:latest`
2. Start API: `python -m omf2.backend.api_refresh`
3. Run integration example: `python tools/test_auto_refresh.py`
4. Publish MQTT message (if MQTT broker is running)
5. Check API: `curl "http://localhost:5001/api/last_refresh?group=order_updates"`

## Usage in Streamlit Pages

```python
from omf2.ui.common.refresh_polling import should_reload_data, init_auto_refresh_polling

def show_my_page():
    # Initialize auto-refresh (1 second interval)
    init_auto_refresh_polling('order_updates', interval_ms=1000)
    
    # Check if data should be reloaded
    should_reload = should_reload_data('order_updates')
    
    if should_reload:
        logger.debug("🔄 Reloading data")
    
    # Load and display data
    data = load_data()
    st.write(data)
```

## Troubleshooting

### Redis Connection Failed

**Error**: "⚠️ Redis not available"

**Solution**:
1. Check Redis is running: `redis-cli ping`
2. Verify REDIS_URL is correct
3. Check firewall rules

### API Not Responding

**Error**: Cannot connect to API

**Solution**:
1. Start API server: `python -m omf2.backend.api_refresh`
2. Check API is running: `curl http://localhost:5001/api/health`
3. Verify REFRESH_API_URL is correct

### UI Not Refreshing

**Issue**: Streamlit page doesn't auto-refresh

**Solution**:
1. Check Redis connection
2. Verify MQTT messages match refresh_triggers patterns
3. Check API returns recent timestamp
4. Look for errors in browser console

## Documentation

See [docs/operations/auto_refresh.md](docs/operations/auto_refresh.md) for complete documentation.

## Performance

- **Redis memory**: ~100 bytes per refresh group
- **API overhead**: Minimal (< 100 bytes per request)
- **Gateway overhead**: < 1ms per message
- **UI polling**: 1 request per second per page

## Future Improvements

- WebSocket support for push-based refresh (eliminate polling)
- Configurable polling intervals per page
- Refresh event history and analytics
- Multi-Redis support for HA
