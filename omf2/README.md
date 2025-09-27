# OMF2 - Modular Architecture for ORBIS Modellfabrik

Version: 2.0.0

## Overview

OMF2 implements a new modular architecture for the ORBIS Modellfabrik with domain-specific MQTT clients and gateways. This architecture provides better separation of concerns, improved testability, and cleaner code organization.

## Architecture

### Core Principles

1. **Domain Separation**: Each functional domain (CCU, Node-RED, Message Center, Generic Steering) has its own MQTT client and gateway
2. **Singleton Pattern**: Each MQTT client is implemented as a singleton to prevent resource conflicts
3. **Business Logic Encapsulation**: Gateways provide domain-specific business logic methods
4. **Modular UI**: UI components are organized by domain and functionality
5. **Configuration Management**: Centralized configuration with validation

## Directory Structure

```
omf2/
├── ccu/                              # CCU Domain
│   ├── ccu_mqtt_client.py           # Singleton MQTT client for CCU
│   ├── ccu_gateway.py               # Business logic gateway for CCU
│   └── workpiece_manager.py         # Workpiece management
├── nodered/                          # Node-RED Domain
│   ├── nodered_mqtt_client.py       # Singleton MQTT client for Node-RED
│   └── nodered_gateway.py           # Business logic gateway for Node-RED
├── message_center/                   # Message Center Domain
│   ├── message_center_mqtt_client.py # Singleton MQTT client for messaging
│   └── message_center_gateway.py    # Business logic gateway for messaging
├── generic_steering/                 # Generic Steering Domain
│   ├── generic_steering_mqtt_client.py # Singleton MQTT client for steering
│   └── generic_steering_gateway.py  # Business logic gateway for steering
├── system/                           # System Management
│   ├── admin_settings.py            # System administration and configuration
│   └── logs.py                      # Log management and analysis
├── ui/                              # User Interface Components
│   ├── ccu/
│   │   └── overview_tab.py          # CCU dashboard UI
│   └── system/
│       ├── admin_settings_tab.py    # Admin settings UI
│       └── logs_tab.py              # Log viewer UI
├── config/                          # Configuration Files
│   ├── mqtt_settings.yml           # MQTT broker settings
│   ├── user_roles.yml              # User roles and permissions
│   └── apps.yml                     # Application definitions
├── registry/                        # Data Registry
│   ├── model/v2/
│   │   └── workpieces.yml          # Workpiece definitions
│   └── schemas/
│       └── workpieces.schema.json  # Validation schemas
└── tests/                           # Test Suite
    ├── test_ccu_mqtt_client.py
    ├── test_workpiece_manager.py
    └── test_admin_settings.py
```

## Usage

### Basic Usage

```python
from omf2.ccu import CCUGateway, ccu_mqtt_client
from omf2.nodered import NodeREDGateway, nodered_mqtt_client
from omf2.message_center import MessageCenterGateway, message_center_mqtt_client
from omf2.generic_steering import GenericSteeringGateway, generic_steering_mqtt_client

# Initialize gateways
ccu_gateway = CCUGateway(ccu_mqtt_client)
nodered_gateway = NodeREDGateway(nodered_mqtt_client)
message_gateway = MessageCenterGateway(message_center_mqtt_client)
steering_gateway = GenericSteeringGateway(generic_steering_mqtt_client)

# Use domain-specific methods
ccu_gateway.send_status_update("Bohrstation", "running")
message_gateway.send_broadcast_message("System online", "system")
nodered_gateway.send_input_data("flow_id", {"sensor": "temp", "value": 23.5})
steering_gateway.send_command("device_1", "move", {"position": 100})
```

### Configuration Management

```python
from omf2.system import AdminSettings

admin_settings = AdminSettings()

# MQTT Settings
mqtt_settings = admin_settings.load_mqtt_settings()
available_envs = admin_settings.get_available_environments()
env_config = admin_settings.get_environment_settings("live")

# User Management
user_permissions = admin_settings.get_user_permissions("admin")
has_permission = admin_settings.has_permission("admin", "control")

# App Configuration
enabled_apps = admin_settings.get_enabled_apps("admin")
```

### Workpiece Management

```python
from omf2.ccu.workpiece_manager import get_workpiece_manager

workpiece_manager = get_workpiece_manager()

# Get workpiece by ID
workpiece = workpiece_manager.get_workpiece_by_id("R1")

# Get workpiece by NFC code
workpiece = workpiece_manager.get_workpiece_by_nfc_code("040a8dca341291")

# Validate NFC code
is_valid = workpiece_manager.validate_nfc_code("040a8dca341291")

# Get statistics
stats = workpiece_manager.get_statistics()
```

### Log Management

```python
from omf2.system.logs import get_log_manager, LogLevel

log_manager = get_log_manager()

# Add log entries
log_manager.log_info("component", "Information message")
log_manager.log_error("component", "Error message", {"context": "data"})

# Get logs
recent_logs = log_manager.get_recent_logs(minutes=60)
error_logs = log_manager.get_error_logs(limit=50)
component_logs = log_manager.get_component_logs("ccu")

# Search logs
search_results = log_manager.search_logs("error", limit=100)

# Export logs
log_manager.export_logs(Path("logs_export.json"))
```

### UI Components

```python
# Streamlit UI components
from omf2.ui.ccu import CCUOverviewTab
from omf2.ui.system import AdminSettingsTab, LogsTab

# In Streamlit app
ccu_tab = CCUOverviewTab()
ccu_tab.render()

admin_tab = AdminSettingsTab()
admin_tab.render()

logs_tab = LogsTab()
logs_tab.render()
```

## Configuration

### MQTT Settings (config/mqtt_settings.yml)

```yaml
environments:
  live:
    host: "localhost"
    port: 1883
    enabled: true
  replay:
    host: "localhost" 
    port: 1883
    enabled: true
  mock:
    host: "localhost"
    port: 1883
    enabled: true

default_environment: "replay"
connection_timeout: 60
qos_default: 1
```

### User Roles (config/user_roles.yml)

```yaml
roles:
  admin:
    name: "Administrator"
    permissions: ["*"]
  operator:
    name: "Operator"
    permissions: ["read", "control"]
  viewer:
    name: "Viewer"
    permissions: ["read"]

users:
  admin:
    role: "admin"
    name: "System Administrator"
    active: true
```

### Apps Configuration (config/apps.yml)

```yaml
apps:
  ccu_dashboard:
    name: "CCU Dashboard"
    enabled: true
    module: "omf2.ui.ccu.overview_tab"
    required_permissions: ["read"]
    
  admin_settings:
    name: "Admin Settings"
    enabled: true
    module: "omf2.ui.system.admin_settings_tab"
    required_role: "admin"
```

## Features

### Domain-Specific MQTT Clients

- **CCU Client**: Handles Central Control Unit communication
- **Node-RED Client**: Manages Node-RED flow integration
- **Message Center Client**: Provides centralized messaging
- **Generic Steering Client**: Controls generic devices

### Business Logic Gateways

Each domain has a gateway that provides:
- Domain-specific business methods
- Message formatting and validation
- Topic management and subscription
- Callback handling
- Connection status monitoring

### System Management

- **Admin Settings**: Configuration management for MQTT, users, and apps
- **Log Manager**: Centralized logging with filtering, search, and export
- **User Roles**: Permission-based access control
- **Workpiece Manager**: Workpiece configuration and NFC code validation

### UI Components

- Modular Streamlit-based UI components
- Domain-specific dashboards
- System administration interface
- Log viewer and analysis tools

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest omf2/tests/ -v

# Run specific test files
python -m pytest omf2/tests/test_ccu_mqtt_client.py -v
python -m pytest omf2/tests/test_workpiece_manager.py -v
python -m pytest omf2/tests/test_admin_settings.py -v
```

## Demo

Run the example usage script:

```bash
python omf2/example_usage.py
```

This demonstrates all major components working together.

## Migration from OMF v1

1. **MQTT Clients**: Replace monolithic MQTT client with domain-specific clients
2. **Configuration**: Move settings from registry to config files
3. **UI Components**: Break down monolithic UI into modular components
4. **Business Logic**: Encapsulate domain logic in gateway classes
5. **Testing**: Comprehensive test coverage for all components

## Development Guidelines

1. **Single Responsibility**: Each component has a single, well-defined responsibility
2. **Dependency Injection**: Use dependency injection for better testability
3. **Configuration**: All configuration should be externalized to YAML files
4. **Logging**: Use structured logging with appropriate log levels
5. **Error Handling**: Implement comprehensive error handling and recovery
6. **Documentation**: Document all public APIs and configuration options

## Requirements

- Python 3.8+
- paho-mqtt >= 1.6.1
- PyYAML >= 6.0
- jsonschema >= 4.0
- streamlit >= 1.28.0 (for UI components)

## License

This project is part of the ORBIS Modellfabrik and follows the same licensing terms.