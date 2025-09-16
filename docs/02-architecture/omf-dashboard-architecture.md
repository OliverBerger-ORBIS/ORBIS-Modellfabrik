# OMF (ORBIS Modellfabrik) Dashboard Architecture

## Overview

Das OMF Dashboard ist eine moderne, modulare Web-Anwendung zur Steuerung und Überwachung der ORBIS Modellfabrik. Es basiert auf Streamlit und implementiert die **Per-Topic-Buffer Architektur** mit **MQTT-Singleton Pattern** für optimale Performance und Einfachheit.

## Architecture Overview

```
OMF Dashboard
├── Frontend (Streamlit)
│   ├── Main Dashboard (omf_dashboard.py)
│   └── Components
│       ├── Overview Components
│       │   ├── overview_inventory.py      # Lagerbestand
│       │   ├── overview_customer_order.py # Kundenaufträge
│       │   ├── overview_purchase_order.py # Rohmaterial-Bestellungen
│       │   └── overview_module_status.py  # Modul-Status (Per-Topic-Buffer)
│       ├── Production Order Components
│       │   ├── production_order_management.py # Auftragsverwaltung
│       │   └── production_order_current.py    # Laufende Aufträge
│       ├── Steering Components
│       │   ├── steering_factory.py       # Factory-Steuerung (Hybrid-Architektur)
│       │   ├── steering_sequence.py      # Sequenz-Steuerung
│       │   └── steering_generic.py       # Generic-Steuerung
│       ├── Message Center (message_center.py) # Priority-based Subscriptions
│       ├── FTS Components
│       │   └── fts_instantaction.py      # FTS-Steuerung (Per-Topic-Buffer)
│       ├── Settings (settings.py)
│       └── Assets
│           └── html_templates.py         # HTML-Templates
├── Business Logic (tools/)
│   ├── MQTT-Singleton Factory ✨ NEW
│   │   ├── omf_mqtt_factory.py          # Singleton-Pattern
│   │   └── omf_mqtt_client.py           # Per-Topic-Buffer Client
│   ├── Hybrid Publishing ✨ NEW
│   │   ├── message_gateway.py           # Publishing Gateway
│   │   └── message_generator.py         # Payload Generation
│   ├── Workflow Management ✨ ENHANCED
│   │   └── workflow_order_manager.py    # Order-ID Management
│   └── Configuration Managers
└── Data Layer
    ├── Message Templates
    ├── MQTT Configuration ✨ NEW
    │   ├── mqtt_config.py               # MQTT-Konfiguration
    │   └── mqtt_topics.py               # Topic-Definitionen
    └── Configuration Files
```

## Core Architecture Patterns

### 1. **MQTT-Singleton Pattern** ✨ NEW
- **Eine MQTT-Client-Instanz** pro Streamlit-Session
- **Zentraler Zugriff** über `st.session_state["mqtt_client"]`
- **Stabile Verbindungen** ohne Verletzung des Singleton-Patterns
- **Umgebungswechsel** (live/mock/replay) ohne Probleme
- **📖 Detaillierte Dokumentation:** [Singleton-Pattern Compliance](docs_orbis/singleton-pattern-compliance.md)

### 2. **Per-Topic-Buffer Pattern** ✨ NEW
- **Topic-spezifische Buffer** für jede MQTT-Subscription
- **Automatische Nachrichtensammlung** in separaten Buffers
- **Effiziente Verarbeitung** ohne Message-Processor Overhead
- **Direkte Buffer-Zugriffe** für optimale Performance
- **📖 Detaillierte Dokumentation:** [Per-Topic-Buffer Pattern](docs_orbis/per-topic-buffer-pattern.md)

### 3. **Hybrid-Architektur für Publishing** ✨ NEW
- **MessageGenerator** für Payload-Erstellung
- **Session State** für Preview/Edit-Funktionalität
- **MessageGateway** für finales Publishing
- **WorkflowOrderManager** für orderId/orderUpdateId Verwaltung

## Core Components

### 1. Dashboard Frontend

**Main Entry Point:** `src_orbis/omf/dashboard/omf_dashboard.py`

#### Tab Structure:
- **Übersicht:** Modul-Status (Per-Topic-Buffer), Lagerbestand, Kundenaufträge, Rohmaterial-Bestellungen
- **Fertigungsaufträge:** Auftragsverwaltung und laufende Fertigungsaufträge
- **Nachrichtenzentrale:** Priority-based Subscriptions mit Per-Topic-Buffer
- **Steuerung:** Factory-, Modul- und FTS-Steuerung mit Hybrid-Architektur
- **Einstellungen:** Dashboard-, Modul-, NFC-, MQTT-, Topic- und Template-Konfiguration

### 2. MQTT-Singleton Factory ✨ NEW

#### OMF MQTT Factory
**File:** `src_orbis/omf/tools/omf_mqtt_factory.py`

**Purpose:** Verwaltet MQTT-Client-Instanzen nach Singleton-Pattern

**Features:**
- **Singleton Pattern:** Eine Client-Instanz pro Session
- **Environment Support:** live/mock/replay Umgebungen
- **Automatic Connection:** Automatische Verbindung beim Start
- **Session Management:** Persistente Client-Instanzen

```python
def ensure_dashboard_client(environment: str, config: dict) -> OMFMqttClient:
    """Erstellt oder gibt existierenden MQTT-Client zurück (Singleton)"""
    if "mqtt_client" not in st.session_state:
        st.session_state["mqtt_client"] = OMFMqttClient(environment, config)
    return st.session_state["mqtt_client"]
```

#### OMF MQTT Client
**File:** `src_orbis/omf/tools/omf_mqtt_client.py`

**Purpose:** Per-Topic-Buffer MQTT-Client

**Features:**
- **Per-Topic-Buffer:** Topic-spezifische Nachrichtensammlung
- **Automatic Subscription:** Automatische Topic-Subscriptions
- **Buffer Management:** Effiziente Buffer-Verwaltung
- **Connection Management:** Robuste Verbindungsverwaltung

```python
class OMFMqttClient:
    def __init__(self, environment: str, config: dict):
        self._buffers = {}  # Per-Topic-Buffer
        self._connected = False
        
    def subscribe_many(self, topics: list):
        """Subscribe zu mehreren Topics"""
        for topic in topics:
            self.subscribe(topic)
            
    def get_buffer(self, topic_filter: str) -> list:
        """Gibt Buffer für Topic-Filter zurück"""
        return self._buffers.get(topic_filter, [])
```

### 3. Hybrid Publishing Architecture ✨ NEW

#### Message Gateway
**File:** `src_orbis/omf/tools/message_gateway.py`

**Purpose:** Einheitliche API für MQTT-Publishing

**Features:**
- **Payload Enrichment:** Automatische Anreicherung von Payloads
- **Order-ID Management:** Automatische orderId/orderUpdateId Verwaltung
- **Error Handling:** Robuste Fehlerbehandlung
- **QoS Management:** Quality of Service Level Verwaltung

```python
class MessageGateway:
    def __init__(self, mqtt_client: OMFMqttClient):
        self.mqtt_client = mqtt_client
        
    def send(self, topic: str, builder: callable, ensure_order_id: bool = False) -> bool:
        """Sendet Nachricht über MQTT-Client"""
        payload = builder()
        
        if ensure_order_id:
            payload = self._ensure_order_id(payload)
            
        return self.mqtt_client.publish_json(topic, payload, qos=1, retain=False)
```

#### Message Generator
**File:** `src_orbis/omf/tools/message_generator.py`

**Purpose:** Generiert semantisch korrekte MQTT-Nachrichten

**Features:**
- **Template-based:** YAML-basierte Template-Definitionen
- **FTS Navigation:** Spezielle FTS-Navigations-Nachrichten
- **Module Commands:** Modul-spezifische Befehle
- **Route Definitions:** Vordefinierte FTS-Routen

```python
def generate_fts_navigation_message(self, route_type: str, load_type: str) -> dict:
    """Generiert FTS-Navigations-Nachricht"""
    route_def = self.route_definitions.get(route_type)
    if not route_def:
        return None
        
    return {
        "topic": "fts/v1/ff/5iO4/navigation",
        "payload": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "serialNumber": "5iO4",
            "route": route_def,
            "loadType": load_type
        }
    }
```

### 4. Overview Components

#### Overview Module Status ✨ ENHANCED
**File:** `src_orbis/omf/dashboard/components/overview_module_status.py`

**Features:**
- **Per-Topic-Buffer:** Effiziente Nachrichtenverarbeitung
- **Module Status:** Connection, Availability, IP-Status
- **Real-time Updates:** Live-Aktualisierung der Modul-Status
- **Topic Processing:** `module/v1/ff/+/state`, `module/v1/ff/+/connection`, `ccu/pairing/state`

```python
def show_overview_module_status():
    # Per-Topic-Buffer für Modul-Status
    state_messages = list(client.get_buffer("module/v1/ff/+/state"))
    connection_messages = list(client.get_buffer("module/v1/ff/+/connection"))
    pairing_messages = list(client.get_buffer("ccu/pairing/state"))
    factsheet_messages = list(client.get_buffer("module/v1/ff/+/factsheet"))
    
    # Verarbeitung
    _process_module_messages(state_messages, connection_messages, pairing_messages, factsheet_messages)
```

### 5. Message Center ✨ ENHANCED

**File:** `src_orbis/omf/dashboard/components/message_center.py`

**Features:**
- **Priority-based Subscriptions:** PRIO 1-6 für verschiedene Topic-Filter
- **Per-Topic-Buffer:** Effiziente Nachrichtenverarbeitung
- **Live Message Display:** Echtzeit-Anzeige empfangener Nachrichten
- **Test-Bereich:** MQTT-Nachrichten senden und testen

```python
def show_message_center():
    # Priority-basierte Subscriptions
    priority_level = st.session_state.get("mc_priority", 1)
    
    if priority_level >= 6:
        # Alle Topics
        client.subscribe("#")
    else:
        # Spezifische Topics basierend auf Priority
        filters = get_priority_filters(priority_level)
        client.subscribe_many(filters)
    
    # Per-Topic-Buffer abrufen und verarbeiten
    for topic_filter in active_filters:
        messages = list(client.get_buffer(topic_filter))
        _display_messages(messages)
```

### 6. Factory Steering ✨ ENHANCED

**File:** `src_orbis/omf/dashboard/components/steering_factory.py`

**Features:**
- **Hybrid-Architektur:** MessageGenerator + Session State + MessageGateway
- **FTS Navigation:** DPS-HBW, HBW-DPS, Produktions-Routen
- **Module Sequences:** AIQS, MILL, DRILL mit Sequenzklammer
- **Factory Reset:** Kompletter Factory-Reset
- **Order Commands:** ROT, WEISS, BLAU Aufträge

```python
def _prepare_navigation_message(navigation_type: str):
    # MessageGenerator verwenden
    generator = get_omf_message_generator()
    
    # Navigation Message generieren
    message = generator.generate_fts_navigation_message(
        route_type=route_mapping[navigation_type],
        load_type=load_type_mapping[navigation_type]
    )
    
    # Session State für Preview
    st.session_state["pending_message"] = {
        "topic": message["topic"],
        "payload": message["payload"],
        "type": "navigation"
    }
```

### 7. FTS InstantAction ✨ ENHANCED

**File:** `src_orbis/omf/dashboard/components/fts_instantaction.py`

**Features:**
- **Per-Topic-Buffer:** Effiziente FTS-Nachrichtenverarbeitung
- **Real-time Updates:** Live-Aktualisierung der FTS-Status
- **Instant Actions:** Sofortige FTS-Befehle

```python
def show_fts_instantaction():
    # Per-Topic-Buffer für FTS-Nachrichten
    instantaction_messages = list(client.get_buffer("fts/v1/ff/5iO4/instantAction"))
    
    # Verarbeitung
    process_fts_instantaction_messages_from_buffers(instantaction_messages)
```

## Data Flow

### 1. Per-Topic-Buffer Flow

```
MQTT Broker → OMFMqttClient → Per-Topic-Buffer → Component Processing
```

### 2. Hybrid Publishing Flow

```
User Action → MessageGenerator → Session State → MessageGateway → MQTT Broker
```

### 3. Module Control Flow

```
User clicks PICK → _prepare_module_sequence → Session State → _send_sequence_message → MessageGateway → MQTT → Module
```

### 4. FTS Navigation Flow

```
User clicks DPS-HBW → _prepare_navigation_message → MessageGenerator → Session State → _send_pending_message → MQTT → FTS
```

## Key Design Principles

### 1. **MQTT-Singleton Pattern**
- **Eine Client-Instanz** pro Streamlit-Session
- **Zentraler Zugriff** über `st.session_state["mqtt_client"]`
- **Keine Verletzung** des Singleton-Patterns
- **Stabile Verbindungen** ohne Probleme
- **📖 Detaillierte Dokumentation:** [Singleton-Pattern Compliance](docs_orbis/singleton-pattern-compliance.md)

### 2. **Per-Topic-Buffer Pattern**
- **Topic-spezifische Buffer** für jede Subscription
- **Automatische Nachrichtensammlung** in separaten Buffers
- **Effiziente Verarbeitung** ohne Message-Processor Overhead
- **Direkte Buffer-Zugriffe** für optimale Performance
- **📖 Detaillierte Dokumentation:** [Per-Topic-Buffer Pattern](docs_orbis/per-topic-buffer-pattern.md)

### 3. **Hybrid-Architektur**
- **MessageGenerator** für Payload-Erstellung
- **Session State** für Preview/Edit-Funktionalität
- **MessageGateway** für finales Publishing
- **WorkflowOrderManager** für ID-Management

### 4. **Separation of Concerns**
- **UI Layer:** Streamlit Components für Benutzerinteraktion
- **Business Logic:** Tools für Message-Generierung und Workflow-Management
- **Data Layer:** YAML-Konfigurationen und Templates
- **MQTT Layer:** Per-Topic-Buffer und Singleton-Pattern

## Technology Stack

### Frontend
- **Streamlit:** Web-Framework für Python
- **Streamlit Components:** Custom UI-Komponenten
- **Session State:** UI-State-Management

### Backend
- **Python 3.9+:** Hauptprogrammiersprache
- **Paho-MQTT:** MQTT-Client für Kommunikation
- **PyYAML:** YAML-Konfiguration
- **Pathlib:** Robuste Pfad-Behandlung

### MQTT Architecture ✨ NEW
- **OMFMqttClient:** Per-Topic-Buffer Client
- **OMFMqttFactory:** Singleton-Pattern Factory
- **MessageGateway:** Publishing Gateway
- **MessageGenerator:** Payload Generation

### Development Tools
- **Black:** Code-Formatierung (line-length: 120)
- **Ruff:** Linting (ignores E501, E402)
- **Isort:** Import-Sortierung
- **Pre-commit:** Git-Hooks für Code-Qualität

### Testing
- **unittest:** Unit-Testing-Framework
- **tempfile:** Temporäre Test-Dateien
- **Mocking:** Komponenten-Isolation

## Configuration Management

### MQTT Configuration ✨ NEW
- **mqtt_config.py:** MQTT-Konfiguration für verschiedene Umgebungen
- **mqtt_topics.py:** Topic-Definitionen und Priority-Filter
- **Environment Support:** live/mock/replay Konfigurationen

### Template System
- **Semantic Templates:** Strukturierte Template-Definitionen
- **Variable Support:** Dynamische Parameter
- **Validation Rules:** Template-Validierung
- **Usage Examples:** Mehrere Beispiele pro Template

### Priority-based Subscriptions ✨ NEW
- **PRIO 1:** Module-spezifische Topics
- **PRIO 2:** FTS-spezifische Topics
- **PRIO 3:** Order-spezifische Topics
- **PRIO 4:** System-spezifische Topics
- **PRIO 5:** Erweiterte Topics
- **PRIO 6:** Alle Topics (`#`)

## Performance Considerations

### Per-Topic-Buffer Vorteile ✨ NEW
- **Keine Message-Processor Overhead**
- **Direkte Buffer-Zugriffe**
- **Effiziente Topic-Filterung**
- **Einfache Erweiterung**

### MQTT-Singleton Vorteile ✨ NEW
- **Eine Client-Instanz** pro Session
- **Stabile Verbindungen**
- **Umgebungswechsel** ohne Probleme
- **Konsistente Architektur**

### Caching
- **Template Caching:** Templates werden einmal geladen
- **Configuration Caching:** Konfigurationen werden gecacht
- **Singleton Pattern:** Globale Instanzen für Performance

### Memory Management
- **Lazy Loading:** Komponenten werden bei Bedarf geladen
- **Resource Cleanup:** Automatische Ressourcen-Bereinigung
- **Efficient Data Structures:** Optimierte Datenstrukturen

## Security Considerations

### MQTT-Singleton Security ✨ NEW
- **Eine Client-Instanz** pro Session
- **Keine Verletzung** des Singleton-Patterns
- **Stabile Verbindungen**
- **Konsistente Architektur**

### Per-Topic-Buffer Security ✨ NEW
- **Topic-spezifische Buffer**
- **Automatische Nachrichtensammlung**
- **Effiziente Verarbeitung**
- **Robuste Error-Handling**

### MQTT Security
- **Connection Validation:** MQTT-Verbindung wird vor Senden geprüft
- **Message Validation:** JSON-Validierung vor Senden
- **Error Handling:** Sichere Fehlerbehandlung

### Configuration Security
- **YAML Validation:** Konfigurationsdateien werden validiert
- **Path Security:** Sichere Pfad-Behandlung
- **Import Security:** Sichere Import-Mechanismen

## Deployment

### Local Development
```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
streamlit run src_orbis/omf/dashboard/omf_dashboard.py --server.port 8506
```

### Production Considerations
- **Environment Variables:** Konfiguration über Umgebungsvariablen
- **Logging:** Detailliertes Logging für Debugging
- **Monitoring:** System-Monitoring und Health-Checks
- **Backup:** Konfigurations-Backup-Strategien

## Future Enhancements

### Planned Features
- **Real-time Status:** Live-Updates von Modul-Status (bereits implementiert)
- **Advanced Workflows:** Komplexe Workflow-Definitionen
- **History Tracking:** Nachrichten-Historie und Logs
- **Performance Monitoring:** System-Performance-Überwachung
- **User Management:** Benutzer-Rollen und Berechtigungen

### Technical Improvements
- **WebSocket Support:** Real-time Kommunikation
- **Database Integration:** Persistente Daten-Speicherung
- **API Endpoints:** REST-API für externe Integration
- **Containerization:** Docker-Support für Deployment
- **CI/CD Pipeline:** Automatisierte Tests und Deployment

## Conclusion

Das OMF Dashboard implementiert eine moderne **Per-Topic-Buffer Architektur** mit **MQTT-Singleton Pattern** für optimale Performance und Einfachheit. Die neue Architektur kombiniert die Vorteile des MQTT-Singleton Patterns mit effizienten Per-Topic-Buffers und einer Hybrid-Architektur für Publishing.

**Key Achievements:**
- ✅ **MQTT-Singleton Pattern** für stabile Verbindungen
- ✅ **Per-Topic-Buffer System** für effiziente Nachrichtenverarbeitung
- ✅ **Hybrid-Architektur** für Publishing (MessageGenerator + Session State + MessageGateway)
- ✅ **Priority-based Subscriptions** für flexible Topic-Filterung
- ✅ **Umfassende Unit Tests** für alle neuen Komponenten
- ✅ **Robuste Fehlerbehandlung** mit Graceful Degradation
- ✅ **Modulare Architektur** für einfache Erweiterungen

**Architecture Patterns:**
- **Per-Topic-Buffer Pattern:** Effiziente MQTT-Nachrichtenverarbeitung
- **MQTT-Singleton Pattern:** Stabile Client-Verwaltung
- **Hybrid-Architektur:** Optimale Publishing-Strategie

## 📚 Architecture Documentation

### Pattern-Spezifische Dokumentation
- **[Singleton-Pattern Compliance](docs_orbis/singleton-pattern-compliance.md)** - MQTT-Singleton Pattern Richtlinien und Best Practices
- **[Per-Topic-Buffer Pattern](docs_orbis/per-topic-buffer-pattern.md)** - Effiziente MQTT-Nachrichtenverarbeitung

### Integration Dokumentation
- **[MQTT Integration](docs_orbis/mqtt/dashboard-mqtt-integration.md)** - Dashboard MQTT-Integration
- **[Topic Configuration](docs_orbis/topic-configuration-guide.md)** - Topic-Konfiguration und Priority-Filter
- **[Module Configuration](docs_orbis/module-configuration-guide.md)** - Modul-Konfiguration und Icons

### Replay-Workflow (Unabhängige Systeme)
- **[Session Manager](src_orbis/helper_apps/session_manager/README.md)** - Unabhängige Helper-App für Session-Analyse
- **[Replay Station](src_orbis/helper_apps/replay_station/README.md)** - Replay-Funktionalität über lokalen MQTT-Broker
- **[MQTT Replay Pattern](docs_orbis/guides/communication/mqtt-replay-pattern.md)** - Replay-Workflow-Dokumentation

### Development Guidelines
- **[Development Rules](OMF_DEVELOPMENT_RULES.md)** - Projekt-spezifische Entwicklungsrichtlinien
- **[Import Standards](docs_orbis/IMPORT_STANDARDS_GUIDE.md)** - Import-Standards und Best Practices
- **[Release Notes Procedure](docs_orbis/RELEASE_NOTES_PROCEDURE.md)** - Release Notes Erstellung