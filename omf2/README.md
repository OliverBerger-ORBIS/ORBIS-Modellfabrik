# OMF2 - Modular Architecture for ORBIS Modellfabrik

**Version: 2.0.0**  
**Status: IN ENTWICKLUNG** 🚧  
**Datum: 2025-09-29**  
**Tests: Teilweise implementiert** ⚠️

## Overview

OMF2 implements a **gekapselte MQTT-Architektur** for the ORBIS Modellfabrik with domain-specific MQTT clients and gateways. This architecture provides better separation of concerns, improved testability, and cleaner code organization.

**🚧 IMPLEMENTIERUNGSSTATUS:**
- ✅ Thread-sichere Singleton-Pattern für MQTT-Clients
- ✅ Registry v2 Integration in Gateways (teilweise)
- ⚠️ Test-Abdeckung (in Entwicklung)
- ⚠️ Error-Handling (teilweise implementiert)
- ⚠️ MQTT-Kommunikation (Mock-Mode funktional)

## Architecture

### Core Principles

1. **Domain Separation**: Each functional domain (CCU, Node-RED, Message Center, Generic Steering) has its own MQTT client and gateway
2. **Singleton Pattern**: Each MQTT client is implemented as a singleton to prevent resource conflicts
3. **Business Logic Encapsulation**: Gateways provide domain-specific business logic methods
4. **Modular UI**: UI components are organized by domain and functionality
5. **Configuration Management**: Centralized configuration with validation

## Directory Structure

### Current Structure (v2.0 - Active)

```
omf2/
├── ccu/                              # CCU Domain
│   ├── ccu_gateway.py               # CCU Business Logic Gateway
│   ├── ccu_mqtt_client.py           # CCU MQTT Client (Singleton)
│   └── helpers/                      # CCU Helper Functions
│       └── ccu_factory_layout.py    # Factory Layout Management
├── nodered/                          # Node-RED Domain
│   ├── nodered_gateway.py           # Node-RED Business Logic Gateway
│   ├── nodered_pub_mqtt_client.py   # Node-RED Publisher MQTT Client
│   ├── nodered_sub_mqtt_client.py   # Node-RED Subscriber MQTT Client
│   └── helpers/                      # Node-RED Helper Functions
│       └── nodered_utils.py         # Node-RED Utilities
├── admin/                            # Admin Domain
│   ├── admin_gateway.py             # Admin Business Logic Gateway
│   └── admin_mqtt_client.py         # Admin MQTT Client (Singleton)
├── common/                           # Common Components
│   ├── message_templates.py         # Message Templates Singleton
│   ├── workpiece_manager.py        # Workpiece Manager (Registry v2)
│   ├── logger.py                    # Logging Configuration
│   └── i18n.py                      # Internationalization
├── registry/                        # Registry v2 Management
│   ├── manager/
│   │   └── registry_manager.py     # Registry Manager (Singleton)
│   ├── schemas/                     # JSON Schema Files (44 schemas)
│   │   ├── module_v1_ff_serial_connection.schema.json
│   │   ├── ccu_global.schema.json
│   │   └── ... (44 schema files)
│   ├── topics/                      # Topic Definitions with Schema Integration
│   │   ├── ccu.yml
│   │   ├── module.yml
│   │   └── ...
│   ├── modules.yml                  # Module Definitions
│   ├── workpieces.yml               # Workpiece Definitions
│   └── tools/                       # Registry Tools
│       ├── add_schema_to_topics.py
│       └── test_payload_generator.py
├── factory/                          # Factory Components
│   ├── gateway_factory.py           # Gateway Factory
│   └── client_factory.py            # Client Factory
├── ui/                              # User Interface Components
│   ├── utils/                       # UI Utilities
│   │   └── ui_refresh.py            # UI-Refresh-Strategie
│   ├── ccu/                         # CCU UI Components
│   │   ├── ccu_overview/
│   │   │   └── ccu_overview_tab.py  # CCU Dashboard Tab
│   │   ├── ccu_orders/
│   │   │   └── ccu_orders_tab.py    # Order Management Tab
│   │   ├── ccu_process/
│   │   │   └── ccu_process_tab.py   # Process Management Tab
│   │   ├── ccu_configuration/
│   │   │   └── ccu_configuration_tab.py # CCU Configuration Tab
│   │   └── ccu_modules/
│   │       └── ccu_modules_tab.py    # Module Management Tab
│   ├── nodered/                     # Node-RED UI Components
│   │   ├── nodered_overview/
│   │   │   └── nodered_overview_tab.py # Node-RED Overview Tab
│   │   └── nodered_processes/
│   │       └── nodered_processes_tab.py # Node-RED Processes Tab
│   └── admin/                       # Admin UI Components
│       ├── generic_steering/
│       │   └── generic_steering_tab.py # Generic Steering Tab
│       ├── message_center/
│       │   └── message_center_tab.py # Message Center Tab
│       ├── admin_settings/
│       │   └── admin_settings_tab.py # Admin Settings Tab
│       └── logs/
│           └── logs_tab.py          # System Logs Tab
├── assets/                          # Static Assets
│   ├── logos/                       # Company and Product Logos
│   ├── icons/                       # UI Icons (PNG, SVG)
│   └── templates/                   # HTML Templates
├── config/                          # Configuration Files
│   ├── mqtt_settings.yml            # MQTT Configuration
│   ├── user_roles.yml               # User Role Configuration
│   └── apps.yml                     # App Configuration
├── common/                          # Common Components
│   ├── message_templates.py         # Message Templates Singleton
│   ├── logger.py                    # Logging Configuration
│   └── i18n.py                      # Internationalization
└── tests/                           # Test Suite
    ├── test_message_templates.py    # Message Templates Tests
    ├── test_ui_components.py        # UI Components Tests
    └── test_helper_apps/            # Helper Apps Tests
```

### Legacy Structure (v1.0 - Deprecated)

```
omf2/
├── system/                           # System Management (DEPRECATED)
├── config/                          # Configuration Files (DEPRECATED)
└── registry/                        # Data Registry (MOVED TO PROJECT ROOT)
```

## 🚧 IMPLEMENTIERUNGSSTATUS

### **📁 IMPLEMENTIERTE KOMPONENTEN:**

**Core-Architektur:**
- ✅ **MessageTemplates Singleton** (`omf2/common/message_templates.py`)
- ✅ **Gateway-Factory** (`omf2/factory/gateway_factory.py`)
- ✅ **CcuGateway** (`omf2/ccu/ccu_gateway.py`)
- ✅ **NoderedGateway** (`omf2/nodered/nodered_gateway.py`)
- ✅ **AdminGateway** (`omf2/admin/admin_gateway.py`)

**Registry v2 Integration:**
- ✅ **Registry Manager** (`omf2/registry/manager/registry_manager.py`) - Zentrale Komponente für alle Registry-Daten
- ✅ **Topics, Templates, Mappings** (`omf2/registry/`) - Vereinfachte Struktur ohne `model/v2/`
- ✅ **Schema-Integration** (`omf2/registry/schemas/`) - 44 JSON-Schemas für Topic-Validierung
- ✅ **MQTT Clients, Workpieces, Modules, Stations, TXT Controllers** (vollständig implementiert)
- ✅ **UI-Schema-Integration** - Schema-Validierung in Admin Settings

**UI-Komponenten:**
- ⚠️ **CCU Tabs** (`omf2/ui/ccu/`) - Grundstruktur vorhanden
- ⚠️ **Node-RED Tabs** (`omf2/ui/nodered/`) - Grundstruktur vorhanden
- ⚠️ **Admin Tabs** (`omf2/ui/admin/`) - Grundstruktur vorhanden

**Tests:**
- ⚠️ **Tests** (teilweise implementiert)
- ⚠️ **Thread-Safety** (teilweise getestet)
- ⚠️ **Registry v2 Integration** (teilweise getestet)
- ⚠️ **Performance** (nicht optimiert)

## Usage

### 🚧 VERWENDUNG (IN ENTWICKLUNG)

```python
# Gateway-Factory verwenden (empfohlen)
from omf2.factory.gateway_factory import get_ccu_gateway, get_nodered_gateway, get_admin_gateway

# Gateways erstellen (Singleton-Pattern)
ccu_gateway = get_ccu_gateway()
nodered_gateway = get_nodered_gateway()
admin_gateway = get_admin_gateway()

# Business-Operationen ausführen (teilweise implementiert)
# ccu_gateway.reset_factory()  # TODO: Implementieren
# ccu_gateway.send_global_command("start", {"line": "1"})  # TODO: Implementieren
# nodered_gateway.get_normalized_module_states()  # TODO: Implementieren
admin_gateway.generate_message_template("ccu/global", {"command": "status"})  # ✅ Funktioniert
```

### **🚧 ARCHITEKTUR-VORTEILE (IN ENTWICKLUNG):**
- **Thread-sicher**: MQTT-Clients verwenden Singleton-Pattern ✅
- **Registry v2**: Teilweise Integration in Gateways ⚠️
- **Testbar**: Tests in Entwicklung ⚠️
- **Performance**: Nicht optimiert ⚠️
- **Wartbar**: Klare Trennung der Domänen ✅
- **UI-Refresh-Strategie**: `request_refresh()` statt `st.rerun()` ✅

### 🚧 Configuration Management (IN ENTWICKLUNG)

```python
# TODO: AdminSettings implementieren
# from omf2.admin import AdminSettings

# admin_settings = AdminSettings()

# MQTT Settings (teilweise implementiert)
# mqtt_settings = admin_settings.load_mqtt_settings()
# available_envs = admin_settings.get_available_environments()
# env_config = admin_settings.get_environment_settings("live")

# User Management (TODO: Implementieren)
# user_permissions = admin_settings.get_user_permissions("admin")
# has_permission = admin_settings.has_permission("admin", "control")

# App Configuration (TODO: Implementieren)
# enabled_apps = admin_settings.get_enabled_apps("admin")
```

### ✅ Registry Manager (VOLLSTÄNDIG IMPLEMENTIERT)

```python
# Registry Manager verwenden (zentral initialisiert in omf.py)
# Registry Manager ist bereits in st.session_state verfügbar

# Registry Manager aus Session State holen
registry_manager = st.session_state.get('registry_manager')
if registry_manager:
    # Alle Registry-Daten laden
    topics = registry_manager.get_topics()
    schemas = registry_manager.get_schemas()  # ✅ NEU: Schema-Integration
    mqtt_clients = registry_manager.get_mqtt_clients()
    workpieces = registry_manager.get_workpieces()
    modules = registry_manager.get_modules()
    stations = registry_manager.get_stations()
    txt_controllers = registry_manager.get_txt_controllers()
    
    # Schema-Validierung für Topics
    topic_schema = registry_manager.get_topic_schema("module/v1/ff/SVR3QA0022/state")
    topic_description = registry_manager.get_topic_description("module/v1/ff/SVR3QA0022/state")
    
    # Payload-Validierung
    is_valid = registry_manager.validate_topic_payload("module/v1/ff/SVR3QA0022/state", payload)
    
    # Registry-Statistiken
    stats = registry_manager.get_registry_stats()
```

**🎯 ZENTRALE INITIALISIERUNG:**
- **Registry Manager wird in `omf.py` initialisiert** beim App-Start
- **Verfügbar in allen Domänen** (Admin, CCU, Node-RED, Common)
- **Singleton Pattern** verhindert mehrfache Initialisierung
- **Session State** macht es thread-safe und effizient
- **Schema-Integration** für Topic-Validierung und Payload-Validierung

### ✅ Workpiece Management (VOLLSTÄNDIG IMPLEMENTIERT)

```python
# WorkpieceManager verwenden
from omf2.common.workpiece_manager import get_workpiece_manager

workpiece_manager = get_workpiece_manager()

# Get workpiece by ID
workpiece = workpiece_manager.get_workpiece_by_id("B1")

# Get workpiece by NFC code
workpiece = workpiece_manager.get_workpiece_by_nfc_code("047389ca341291")

# Get workpieces by color
blue_workpieces = workpiece_manager.get_workpieces_by_color("BLUE")
red_workpieces = workpiece_manager.get_workpieces_by_color("RED")
white_workpieces = workpiece_manager.get_workpieces_by_color("WHITE")

# Get statistics
stats = workpiece_manager.get_statistics()
```

### 🚧 Log Management (TEILWEISE IMPLEMENTIERT)

```python
# TODO: LogManager vollständig implementieren
# from omf2.admin.logs import get_log_manager, LogLevel

# log_manager = get_log_manager()

# Add log entries (TODO: Implementieren)
# log_manager.log_info("component", "Information message")
# log_manager.log_error("component", "Error message", {"context": "data"})

# Get logs (TODO: Implementieren)
# recent_logs = log_manager.get_recent_logs(minutes=60)
# error_logs = log_manager.get_error_logs(limit=50)
# component_logs = log_manager.get_component_logs("ccu")

# Search logs (TODO: Implementieren)
# search_results = log_manager.search_logs("error", limit=100)

# Export logs (TODO: Implementieren)
# log_manager.export_logs(Path("logs_export.json"))
```

### 🚧 UI Components (GRUNDSTRUKTUR VORHANDEN)

```python
# Streamlit UI components (teilweise implementiert)
# from omf2.ui.ccu.ccu_overview import CCUOverviewTab
# from omf2.ui.admin.admin_settings import AdminSettingsTab
# from omf2.ui.admin.logs import LogsTab

# In Streamlit app (TODO: Vollständig implementieren)
# ccu_tab = CCUOverviewTab()
# ccu_tab.render()

# admin_tab = AdminSettingsTab()
# admin_tab.render()

# logs_tab = LogsTab()
# logs_tab.render()
```

## Configuration

### 🚧 MQTT Settings (config/mqtt_settings.yml) - KORREKTUR ERFORDERLICH

```yaml
# AKTUELLE KONFIGURATION (TEILWEISE FALSCH):
environments:
  live:
    mqtt:
      host: "192.168.0.100"  # ✅ Korrekt
      port: 1883
      client_id_postfix: "_live"  # ✅ Korrekt
  replay:
    mqtt:
      host: "localhost"  # ✅ Korrekt
      port: 1883
      client_id_postfix: "_replay"  # ✅ Korrekt
  mock:
    mqtt:
      host: "localhost"  # ✅ Korrekt
      port: 1883
      client_id_postfix: "_mock"  # ✅ Korrekt

# TODO: Weitere Konfigurationen implementieren
default_environment: "mock"  # ✅ Korrekt (stabiler)
connection_timeout: 60
qos_default: 1
```

### 🚧 User Roles (config/user_roles.yml) - TODO: IMPLEMENTIEREN

```yaml
# TODO: User Roles implementieren
# roles:
#   admin:
#     name: "Administrator"
#     permissions: ["*"]
#   operator:
#     name: "Operator"
#     permissions: ["read", "control"]

# users:
#   admin:
#     role: "admin"
#     name: "System Administrator"
#     active: true
```

### 🚧 Apps Configuration (config/apps.yml) - TEILWEISE IMPLEMENTIERT

```yaml
# TODO: Apps Configuration vollständig implementieren
# apps:
#   ccu_dashboard:
#     name: "CCU Dashboard"
#     enabled: true
#     module: "omf2.ui.ccu.ccu_overview.ccu_overview_tab"
#     required_permissions: ["read"]
    
#   admin_settings:
#     name: "Admin Settings"
#     enabled: true
#     module: "omf2.ui.admin.admin_settings.admin_settings_tab"
#     required_role: "admin"
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

## 🚧 Testing (IN ENTWICKLUNG)

```bash
# TODO: Test suite vollständig implementieren
# python -m pytest omf2/tests/ -v

# TODO: Spezifische Tests implementieren
# python -m pytest omf2/tests/test_ccu_mqtt_client.py -v
# python -m pytest omf2/tests/test_workpiece_manager.py -v
# python -m pytest omf2/tests/test_admin_settings.py -v
```

**HINWEIS:** Test suite ist noch nicht vollständig implementiert.

## 🚧 Demo (TODO: IMPLEMENTIEREN)

```bash
# TODO: Example usage script implementieren
# python omf2/example_usage.py
```

**HINWEIS:** Example usage script ist noch nicht implementiert.

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