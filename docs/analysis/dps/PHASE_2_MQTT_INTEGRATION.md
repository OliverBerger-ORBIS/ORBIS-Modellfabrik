# Phase 2: MQTT-Integration erweitert

## 🎯 Übersicht

Phase 2 erweitert die bestehende MQTT-Integration um APS-spezifische Funktionalität:

- **APSMqttIntegration** - Zentrale APS-Integration
- **OmfMqttClient** - Erweitert um APS-Funktionalität
- **Registry-Erweiterungen** - APS-Topics und Templates
- **Vollständige Tests** - Unit Tests für alle Komponenten

## 📁 Implementierte Dateien

### 1. APS MQTT Integration
**Datei:** `omf/tools/aps_mqtt_integration.py`

**Funktionalität:**
- Zentrale APS-Integration für MQTT
- VDA5050 Order Management
- TXT Controller Discovery
- System Control Commands
- Message Handlers für alle APS-Topics

**Wichtige Methoden:**
```python
# VDA5050 Orders
create_storage_order(color, workpiece_id, target_module)
create_retrieval_order(color, workpiece_id, source_module)
send_instant_action(action_type, parameters, target_module)

# TXT Controller Management
get_discovered_controllers()
get_controller_by_serial(serial_number)
get_controller_by_ip(ip_address)

# System Control
reset_factory()
charge_fts()
park_factory()
calibrate_system()

# Publishing
publish_order(order, target_module)
publish_instant_action(action, target_module)
```

### 2. OmfMqttClient Erweiterung
**Datei:** `omf/tools/omf_mqtt_client.py`

**Erweiterungen:**
- APS-Integration aktivierbar
- OMF-Logging integriert
- APS-spezifische Methoden

**Neue Methoden:**
```python
enable_aps_integration() -> APSMqttIntegration
get_aps_integration() -> Optional[APSMqttIntegration]
is_aps_enabled() -> bool
```

### 3. Registry-Erweiterungen

#### APS Topics
**Datei:** `registry/model/v1/topics/aps.yml`

**Kategorien:**
- **VDA5050** - VDA5050 Standard Topics
- **SystemControl** - System Control Commands
- **Discovery** - Controller Discovery

**Topics:**
- `module/v1/ff/+/order` - VDA5050 Orders
- `module/v1/ff/+/state` - VDA5050 States
- `module/v1/ff/+/instantAction` - VDA5050 Instant Actions
- `module/v1/ff/+/factsheet` - Module Factsheets
- `ccu/set/+` - System Control Commands
- `fts/v1/ff/+/state` - FTS States

#### TXT Controller Konfiguration
**Datei:** `registry/model/v1/txt_controllers.yml`

**Controller:**
- **SVR4H73275** - DPS (CCU)
- **SVR4H76530** - AIQS (Quality Control)
- **SVR4H76449** - HBW (Warehouse)
- **SVR3QA0022** - MILL (Machining)
- **SVR3QA2098** - DRILL (Machining)

**Discovery-Konfiguration:**
- Factsheet Topics für Controller Discovery
- State Topics für IP-Updates
- Timeout-Konfiguration

#### VDA5050 Templates
**Datei:** `registry/model/v1/templates/vda5050.yml`

**Templates:**
- `module.order` - VDA5050 Order Message
- `module.state` - VDA5050 State Message
- `module.instantaction` - VDA5050 Instant Action
- `module.factsheet` - Module Factsheet
- `ccu.control` - CCU Control Command

### 4. Unit Tests
**Datei:** `tests_orbis/test_omf/test_aps_mqtt_integration.py`

**Test-Klassen:**
- `TestAPSMqttIntegration` - APS Integration Tests
- `TestOmfMqttClientAPSIntegration` - MQTT Client Tests

**Test-Coverage:**
- Initialisierung und Setup
- VDA5050 Order Creation
- Instant Action Creation
- System Commands
- Order Publishing
- Controller Discovery
- State Message Handling
- Error Handling

## 🔧 Verwendung

### 1. APS-Integration aktivieren
```python
from omf.tools.omf_mqtt_client import OmfMqttClient
from omf.tools.mqtt_config import MqttConfig

# MQTT Client erstellen
config = MqttConfig(host="192.168.0.100", port=1883)
mqtt_client = OmfMqttClient(config)

# APS-Integration aktivieren
aps_integration = mqtt_client.enable_aps_integration()
```

### 2. VDA5050 Orders erstellen
```python
# Storage Order
storage_order = aps_integration.create_storage_order("RED", "WP_001", "DPS")
aps_integration.publish_order(storage_order, "DPS")

# Retrieval Order
retrieval_order = aps_integration.create_retrieval_order("BLUE", "WP_002", "HBW")
aps_integration.publish_order(retrieval_order, "HBW")
```

### 3. Instant Actions senden
```python
# Camera Adjustment
action = aps_integration.send_instant_action(
    "camera_adjustment",
    {"direction": "up", "angle": 10},
    "DPS"
)
aps_integration.publish_instant_action(action, "DPS")

# NFC Read
action = aps_integration.send_instant_action("nfc_read", {}, "DPS")
aps_integration.publish_instant_action(action, "DPS")
```

### 4. System Commands
```python
# Factory Reset
aps_integration.reset_factory()

# FTS Charge
aps_integration.charge_fts()

# Park Factory
aps_integration.park_factory()

# System Calibration
aps_integration.calibrate_system()
```

### 5. Controller Discovery
```python
# Discovered Controllers
controllers = aps_integration.get_discovered_controllers()
print(f"Discovered: {list(controllers.keys())}")

# Controller by Serial
dps_controller = aps_integration.get_controller_by_serial("SVR4H73275")
print(f"DPS IP: {dps_controller['ip_address']}")

# Online Controllers
online = aps_integration.get_online_controllers()
print(f"Online: {list(online.keys())}")
```

## 🧪 Testing

### Unit Tests ausführen
```bash
# Alle APS MQTT Tests
python -m pytest tests_orbis/test_omf/test_aps_mqtt_integration.py -v

# Spezifische Test-Klasse
python -m pytest tests_orbis/test_omf/test_aps_mqtt_integration.py::TestAPSMqttIntegration -v

# Mit Coverage
python -m pytest tests_orbis/test_omf/test_aps_mqtt_integration.py --cov=omf.tools.aps_mqtt_integration
```

### Integration Tests
```python
# Beispiel Integration Test
def test_aps_integration_live():
    """Live Integration Test mit echtem MQTT Broker"""
    config = MqttConfig(host="192.168.0.100", port=1883)
    mqtt_client = OmfMqttClient(config)
    
    # Warten auf Verbindung
    time.sleep(2)
    
    # APS-Integration aktivieren
    aps_integration = mqtt_client.enable_aps_integration()
    
    # Test Order
    order = aps_integration.create_storage_order("RED", "WP_TEST")
    success = aps_integration.publish_order(order, "DPS")
    
    assert success is True
    print("✅ APS Integration Live Test erfolgreich")
```

## 📊 Status und Metriken

### Implementierungsstatus
- ✅ **APSMqttIntegration** - Vollständig implementiert
- ✅ **OmfMqttClient** - Erweitert um APS-Funktionalität
- ✅ **Registry-Erweiterungen** - Alle APS-Topics und Templates
- ✅ **Unit Tests** - Vollständige Test-Coverage
- ✅ **Dokumentation** - Vollständig dokumentiert

### Code-Qualität
- ✅ **Development Rules** - Alle Regeln eingehalten
- ✅ **Linting** - Keine Linting-Fehler
- ✅ **Type Hints** - Vollständige Typisierung
- ✅ **Error Handling** - Robuste Fehlerbehandlung
- ✅ **Logging** - OMF-Logging-System verwendet

### Performance
- **Memory Usage** - Optimiert durch Deque-Buffer
- **MQTT QoS** - QoS 2 für kritische Messages
- **Connection Handling** - Robuste Verbindungsverwaltung
- **Message Processing** - Asynchrone Verarbeitung

## 🚀 Nächste Schritte

### Phase 3: Dashboard-Komponenten
- APS-spezifische Dashboard-Tabs
- UI-Komponenten für Orders und System Control
- Integration in bestehende OMF-Dashboard-Struktur

### Phase 4: Testing und Validierung
- Integration Tests mit echtem APS-System
- Performance-Tests
- End-to-End-Tests

### Phase 5: Deployment
- Production-Ready Deployment
- Monitoring und Alerting
- Dokumentation für End-User

## 🔗 Verwandte Dokumentation

- [Phase 1: Core Managers](PHASE_1_CORE_MANAGERS.md)
- [VDA5050 Implementation Plan](VDA5050_IMPLEMENTATION_PLAN.md)
- [APS Dashboard Components Plan](APS_DASHBOARD_COMPONENTS_PLAN.md)
- [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md)
- [Registry Compatibility Analysis](REGISTRY_COMPATIBILITY_ANALYSIS.md)
- [Dynamic IP Solution](DYNAMIC_IP_SOLUTION.md)
