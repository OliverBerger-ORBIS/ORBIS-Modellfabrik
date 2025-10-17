# CCU Message Monitor Component

A Streamlit component for monitoring and filtering CCU MQTT messages.

## Features

- **5-Column Filter Bar**: Filter messages by Topic, Module/FTS, Status, Type, and Actions
- **Persistent Filters**: Filter settings persist across refreshes
- **Automatic Detection**: 
  - Status categories (Connection Status, Module State, FTS State, Factsheet, CCU State)
  - Module/FTS names from payload
  - Message types
- **Cached Preprocessing**: Efficient data processing with Streamlit caching
- **Payload Viewer**: Row selector for detailed payload inspection
- **Regex-based Filtering**: Smart detection of status categories and modules

## Usage

### Basic Usage with Sample Data

```python
import streamlit as st
from omf2.ui.ccu.ccu_message_monitor import render_ccu_message_monitor

# Render with sample data
render_ccu_message_monitor()
```

### Usage with Custom Messages

```python
from omf2.ui.ccu.ccu_message_monitor import render_ccu_message_monitor

# Prepare messages in the expected format
messages = [
    {
        "timestamp": 1234567890.0,  # Unix timestamp
        "topic": "ccu/status",
        "payload": {
            "module": "Bohrstation",
            "state": "running",
            "details": {"serial": "BS-001"}
        }
    },
    # ... more messages
]

render_ccu_message_monitor(messages=messages)
```

### Integration with CCU Gateway

```python
from omf2.ccu import CCUGateway, ccu_mqtt_client
from omf2.ui.ccu.ccu_message_monitor import render_ccu_message_monitor

# Initialize gateway
gateway = CCUGateway(ccu_mqtt_client)

# Get messages from gateway buffers
messages = []
for topic in ["ccu/state", "ccu/status", "ccu/control", "ccu/connection"]:
    buffer = gateway.client.get_buffer(topic)
    messages.extend(buffer)

# Render monitor
render_ccu_message_monitor(messages=messages)
```

## Message Format

Messages should be dictionaries with the following structure:

```python
{
    "timestamp": float,  # Unix timestamp
    "topic": str,        # MQTT topic (e.g., "ccu/status")
    "payload": dict,     # Message payload (can be dict or string)
}
```

### Payload Format Examples

**Status Update:**
```python
{
    "timestamp": "2024-01-15T10:00:00Z",
    "module": "Bohrstation",
    "state": "running",
    "details": {"serial": "BS-001", "workpiece_id": "WP-12345"}
}
```

**Connection Event:**
```python
{
    "timestamp": "2024-01-15T10:00:00Z",
    "component": "FTS-1",
    "connected": true,
    "details": {"reason": "startup"}
}
```

**Control Command:**
```python
{
    "timestamp": "2024-01-15T10:00:00Z",
    "command": "start",
    "target": "Bohrstation",
    "parameters": {"mode": "auto"}
}
```

## Status Categories

The component automatically detects and categorizes messages into:

1. **Connection Status**: Connection-related messages
2. **Module State**: Module state changes (Bohrstation, Frässtation, etc.)
3. **FTS State**: FTS (Fahrerloses Transportsystem) state
4. **Factsheet**: Factsheet-related messages
5. **CCU State**: General CCU state messages

Detection is based on:
- Topic patterns (e.g., "ccu/connection")
- Payload content (keywords, module names)
- Regex patterns

## Testing

### Run Standalone Demo

```bash
streamlit run omf2/ui/ccu/ccu_message_monitor/ccu_message_monitor_component.py
```

Or use the convenience script:

```bash
streamlit run run_ccu_message_monitor_demo.py
```

### Run Integration Example

```bash
streamlit run omf2/ui/ccu/ccu_message_monitor/integration_example.py
```

### Run Unit Tests

```bash
pytest omf2/tests/test_ccu_message_monitor.py -v
```

## Test Scenarios

1. **Filter Persistence**: Set filters, click Refresh, verify filters remain
2. **Topic Filtering**: Select different topics, verify correct messages shown
3. **Module/FTS Filtering**: Select specific modules, verify filtering works
4. **Status Filtering**: Select status categories, verify correct categorization
5. **Combined Filters**: Test multiple filter combinations
6. **Payload Viewer**: Use row selector, verify payload displayed correctly

## Implementation Details

### Session State Keys

The component uses the following session state keys:
- `ccu_msg_topic_filter`: Current topic filter
- `ccu_msg_module_fts_filter`: Current module/FTS filter
- `ccu_msg_status_filter`: Current status filter
- `ccu_msg_type_filter`: Current message type filter
- `ccu_msg_selected_row`: Currently selected row index
- `ccu_msg_show_payload`: Whether to show payload viewer

All keys are initialized before widget creation to ensure persistence.

### Cached Preprocessing

The `_prepare_dataframe()` function is cached with `@st.cache_data(ttl=60)` to:
- Extract relevant fields from messages
- Detect status categories and module names
- Prepare display strings
- Enable efficient filtering

Cache TTL is 60 seconds to balance performance and data freshness.

### Filter Logic

Filters are applied using pandas DataFrame operations for efficiency:
- Topic filter supports exact match and wildcard patterns
- All filters use vectorized operations
- Filters are applied in sequence (AND logic)

## Future Enhancements

Optional enhancements that could be added:

1. **st_aggrid Integration**: For true double-click row selection
2. **Export Functionality**: Export filtered messages to JSON/CSV
3. **Real-time Updates**: Auto-refresh with configurable interval
4. **Advanced Filters**: Date range, payload content search
5. **Message Statistics**: Charts showing message distribution
6. **Alert Highlighting**: Color-code error/warning messages

## Dependencies

- streamlit >= 1.28.0
- pandas >= 2.0.0
- Python >= 3.8

## Files

- `__init__.py`: Package initialization
- `ccu_message_monitor_component.py`: Main component implementation
- `integration_example.py`: Example integration with CCU Gateway
- `README.md`: This file

## License

Part of the ORBIS Modellfabrik project.
