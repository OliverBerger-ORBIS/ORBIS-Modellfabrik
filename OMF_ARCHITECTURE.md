# OMF (ORBIS Modellfabrik) Dashboard Architecture

## Overview

Das OMF Dashboard ist eine moderne, modulare Web-Anwendung zur Steuerung und Überwachung der ORBIS Modellfabrik. Es basiert auf Streamlit und implementiert eine klare Trennung zwischen UI-Komponenten, Business Logic und Daten-Management.

## Architecture Overview

```
OMF Dashboard
├── Frontend (Streamlit)
│   ├── Main Dashboard (omf_dashboard.py)
│   └── Components
│       ├── Overview Components
│       │   ├── overview_inventory.py      # Lagerbestand
│       │   ├── overview_customer_order.py # Kundenaufträge
│       │   └── overview_purchase_order.py # Rohmaterial-Bestellungen
│       ├── Production Order Components
│       │   ├── production_order_management.py # Auftragsverwaltung
│       │   └── production_order_current.py    # Laufende Aufträge
│       ├── Steering Components
│       │   ├── steering_factory.py       # Factory-Steuerung
│       │   └── steering_generic.py       # Generic-Steuerung
│       ├── Message Center (message_center.py)
│       ├── Settings (settings.py)
│       └── Assets
│           └── html_templates.py         # HTML-Templates
├── Business Logic (tools/)
│   ├── MessageGenerator ✨ ENHANCED
│   ├── TopicMappingManager ✨ NEW
│   ├── WorkflowOrderManager ✨ NEW
│   └── Configuration Managers
└── Data Layer
    ├── Message Templates
    ├── Topic Mappings ✨ NEW
    └── Configuration Files
```

## Core Components

### 1. Dashboard Frontend

**Main Entry Point:** `src_orbis/omf/dashboard/omf_dashboard.py`

#### Tab Structure:
- **Übersicht:** Modul-Status, Lagerbestand, Kundenaufträge, Rohmaterial-Bestellungen
- **Fertigungsaufträge:** Auftragsverwaltung und laufende Fertigungsaufträge
- **Nachrichtenzentrale:** MQTT-Nachrichten mit Filterung
- **Steuerung:** Factory-, Modul- und FTS-Steuerung mit Message-Generator
- **Einstellungen:** Dashboard-, Modul-, NFC-, MQTT-, Topic- und Template-Konfiguration

### 2. Overview Components ✨ NEW

#### Overview Inventory Component
**File:** `src_orbis/omf/dashboard/components/overview_inventory.py`

#### Features:
- **Lagerbestand-Anzeige:** Aktuelle Werkstück-Verfügbarkeit
- **Visuelle Darstellung:** HTML-Templates für Buckets und Werkstücke
- **Auto-Refresh:** Automatische Aktualisierung der Bestände
- **Manual Refresh:** Manuelle Aktualisierung über Sidebar

#### Overview Customer Order Component
**File:** `src_orbis/omf/dashboard/components/overview_customer_order.py`

#### Features:
- **Direkte Bestellung:** Werkstück-Bestellungen direkt an Factory
- **Farb-Auswahl:** Rot, Weiß, Blau Werkstücke
- **MQTT-Integration:** Direkter Versand über MQTT
- **Status-Feedback:** Erfolgs-/Fehlermeldungen

#### Overview Purchase Order Component
**File:** `src_orbis/omf/dashboard/components/overview_purchase_order.py`

#### Features:
- **Rohmaterial-Bedarf:** Anzeige des aktuellen Bedarfs
- **Visuelle Templates:** HTML-Templates für Buckets
- **Bedarf-Tracking:** Verfolgung von Bestellungen

### 3. Production Order Components ✨ NEW

#### Production Order Management Component
**File:** `src_orbis/omf/dashboard/components/production_order_management.py`

#### Features:
- **Auftragserstellung:** Neue Fertigungsaufträge anlegen
- **Auftragsverfolgung:** Status und Fortschritt überwachen
- **Auftragshistorie:** Vergangene Aufträge einsehen
- **Prioritätsverwaltung:** Aufträge nach Priorität sortieren
- **Ressourcenplanung:** Verfügbare Module berücksichtigen

#### Production Order Current Component
**File:** `src_orbis/omf/dashboard/components/production_order_current.py`

#### Features:
- **Aktive Aufträge:** Anzeige aller laufenden Fertigungsaufträge
- **Fortschrittsanzeige:** Visueller Fortschritt der Produktionsschritte
- **Modul-Status:** Welche Module sind aktuell beschäftigt
- **Werkstück-Verfolgung:** Position der Werkstücke in der Fabrik
- **Echtzeit-Updates:** Live-Aktualisierung der Auftragsstatus

### 4. Steering Components ✨ NEW

#### Factory Steering Component
**File:** `src_orbis/omf/dashboard/components/steering_factory.py`

#### Features:
- **Factory Control:** Reset und Bestellungen
- **Module Control:** MILL, DRILL, AIQS Sequenz-Steuerung
- **FTS Control:** Status-abhängige FTS-Steuerung

#### Generic Steering Component
**File:** `src_orbis/omf/dashboard/components/steering_generic.py`

#### Features:
- **Message Generator:** Topic-basierte Template-Auswahl

#### Key Innovations:
- **Topic-Mapping:** User wählt Topic, Template wird automatisch geladen
- **Workflow Management:** `orderId`/`orderUpdateId` Tracking für Sequenzen
- **MQTT Mock:** Test-Modus ohne echte MQTT-Verbindung
- **Variable Resolution:** `{module_id}` → konkrete Seriennummern

### 5. HTML Templates ✨ NEW

**File:** `src_orbis/omf/dashboard/assets/html_templates.py`

#### Features:
- **Bucket-Templates:** Visuelle Darstellung von Lager-Buckets
- **Werkstück-Templates:** Farbige Werkstück-Darstellung
- **Responsive Design:** Anpassbare Größen und Layouts

### 6. Business Logic Layer

#### MessageGenerator ✨ ENHANCED
**File:** `src_orbis/omf/tools/message_generator.py`

**New Features:**
- **Topic-specific Parameters:** Automatische Parameter-Anpassung
- **Workflow Integration:** Unterstützt `WorkflowOrderManager`
- **Enhanced Templates:** `orderUpdateId` und `subActionId` Support
- **Fallback Mechanisms:** Robuste Fehlerbehandlung

#### TopicMappingManager ✨ NEW
**File:** `src_orbis/omf/tools/topic_mapping_manager.py`

**Purpose:** Verwaltet Mapping zwischen MQTT-Topics und Message-Templates

**Features:**
- **YAML-based Configuration:** `topic_message_mapping.yml`
- **Category Management:** Topics nach Funktionsbereichen gruppiert
- **Variable Resolution:** `{module_id}` → konkrete Werte
- **Template Lookup:** Automatisches Finden passender Templates

#### WorkflowOrderManager ✨ NEW
**File:** `src_orbis/omf/tools/workflow_order_manager.py`

**Purpose:** Verwaltet sequentielle Modul-Befehle mit `orderId`/`orderUpdateId`

**Features:**
- **Order Tracking:** Aktive Workflows pro Modul
- **Sequential Updates:** `orderUpdateId` Inkrementierung (1, 2, 3...)
- **Workflow History:** Abgeschlossene Workflows speichern
- **Singleton Pattern:** Globale Workflow-Verwaltung

### 7. Configuration Management

#### Topic-Message Mapping ✨ NEW
**File:** `src_orbis/omf/config/topic_message_mapping.yml`

```yaml
topic_mappings:
  "module/v1/ff/{module_id}/order":
    template: "module/order"
    direction: "outbound"
    description: "Modul-Befehle senden"
    variable_fields:
      module_id: "<module_serial_number>"
```

#### Template Categories:
- **CCU:** Zentrale Steuerung und Status
- **Module:** Modul-spezifische Befehle und Status
- **TXT:** Fischertechnik TXT-Integration
- **Node-RED:** Node-RED Dashboard-Integration

## Data Flow

### 1. User Interaction Flow

```
User selects Topic → TopicMappingManager → Template → MessageGenerator → MQTT
```

### 2. Module Control Flow

```
User clicks PICK → WorkflowOrderManager → MessageGenerator → MQTT → Module
```

### 3. Factory Control Flow

```
User clicks Reset → MessageGenerator → MQTT → Factory Reset
```

## Key Design Principles

### 1. Separation of Concerns
- **UI Layer:** Streamlit Components für Benutzerinteraktion
- **Business Logic:** Tools für Message-Generierung und Workflow-Management
- **Data Layer:** YAML-Konfigurationen und Templates

### 2. Modularity
- **Component-based:** Jede Funktionalität in separater Komponente
- **Tool-based:** Business Logic in wiederverwendbaren Tools
- **Configuration-driven:** Verhalten über YAML-Dateien konfigurierbar

### 3. Error Handling
- **Graceful Degradation:** Fallback bei fehlenden Komponenten
- **User Feedback:** Benutzerfreundliche Fehlermeldungen
- **Robust Communication:** MQTT-Verbindung mit Mock-Support

### 4. Testability
- **Unit Tests:** Umfassende Tests für alle Tools
- **Mock Support:** MQTT-Mock für Tests ohne Hardware
- **Isolated Components:** Unabhängig testbare Komponenten

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

### Environment Configuration
- **Virtual Environment:** `.venv` für Dependencies
- **Path Management:** Relative Pfade für Portabilität
- **Import Handling:** Robuste Import-Mechanismen

### Template System
- **Semantic Templates:** Strukturierte Template-Definitionen
- **Variable Support:** Dynamische Parameter
- **Validation Rules:** Template-Validierung
- **Usage Examples:** Mehrere Beispiele pro Template

### MQTT Configuration
- **Broker Settings:** Konfigurierbare MQTT-Broker
- **Topic Structure:** Hierarchische Topic-Organisation
- **Message Format:** JSON-basierte Nachrichten
- **Mock Support:** Test-Modus ohne echte Verbindung

## Security Considerations

### MQTT Security
- **Connection Validation:** MQTT-Verbindung wird vor Senden geprüft
- **Message Validation:** JSON-Validierung vor Senden
- **Error Handling:** Sichere Fehlerbehandlung

### Configuration Security
- **YAML Validation:** Konfigurationsdateien werden validiert
- **Path Security:** Sichere Pfad-Behandlung
- **Import Security:** Sichere Import-Mechanismen

## Performance Considerations

### Caching
- **Template Caching:** Templates werden einmal geladen
- **Configuration Caching:** Konfigurationen werden gecacht
- **Singleton Pattern:** Globale Instanzen für Performance

### Memory Management
- **Lazy Loading:** Komponenten werden bei Bedarf geladen
- **Resource Cleanup:** Automatische Ressourcen-Bereinigung
- **Efficient Data Structures:** Optimierte Datenstrukturen

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
- **Real-time Status:** Live-Updates von Modul-Status
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

Das OMF Dashboard implementiert eine moderne, modulare Architektur mit klarer Trennung von UI, Business Logic und Daten-Management. Die neue Steuerungs-Funktionalität erweitert das System um leistungsstarke Werkzeuge für die Modellfabrik-Steuerung, während die bestehende Architektur beibehalten wird.

**Key Achievements:**
- ✅ **Topic-basierte Template-Auswahl** für intuitive Benutzerführung
- ✅ **Workflow-Management** für sequentielle Modul-Befehle
- ✅ **MQTT-Mock-Support** für Tests ohne Hardware
- ✅ **Umfassende Unit Tests** für alle neuen Komponenten
- ✅ **Robuste Fehlerbehandlung** mit Graceful Degradation
- ✅ **Modulare Architektur** für einfache Erweiterungen
