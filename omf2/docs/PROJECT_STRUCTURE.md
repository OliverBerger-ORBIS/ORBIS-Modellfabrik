## Projektstruktur und Prinzipien für omf2

Dieses Dokument beschreibt die Zielstruktur, Modularisierung und zentrale Prinzipien für die Entwicklung von **omf2** innerhalb der ORBIS-Modellfabrik.  
Es dient als Referenz für alle Teammitglieder und als Vorgabe für Coding Agents.

---

## 1. Grundstruktur omf2 (Registry bleibt in omf2/registry)
Die Registry bleibt in omf2/registry/ - nur die UI-Struktur wird reorganisiert

```
omf2/
  registry/                                    # ✅ IMPLEMENTIERT
    manager/                                  # ✅ NEU HINZUGEFÜGT
      registry_manager.py                     # ✅ Registry Manager (Singleton)
    modules.yml                               # ✅ DIREKT UNTER REGISTRY
    mqtt_clients.yml                          # ✅ DIREKT UNTER REGISTRY
    stations.yml                              # ✅ DIREKT UNTER REGISTRY
    txt_controllers.yml                       # ✅ DIREKT UNTER REGISTRY
    workpieces.yml                            # ✅ DIREKT UNTER REGISTRY
    topics/                                   # ✅ DIREKT UNTER REGISTRY
      ccu.yml
      fts.yml
      module.yml
      nodered.yml
      txt.yml
    schemas/                                  # ✅ NEU: SCHEMA-INTEGRATION
      module_v1_ff_serial_connection.schema.json
      ccu_global.schema.json
      j1_txt_1_i_bme680.schema.json
      # ... 44 Schema-Dateien
    tools/                                    # ✅ NEU: REGISTRY-TOOLS
      add_schema_to_topics.py
      test_payload_generator.py
  assets/                                      # ✅ IMPLEMENTIERT
    logos/
      orbis_logo.txt                           # ✅ HINZUGEFÜGT
    icons/
      module.png.txt                           # ✅ HINZUGEFÜGT
  ccu/                                         # ✅ IMPLEMENTIERT
    ccu_gateway.py
    ccu_mqtt_client.py
    module_manager.py                          # ✅ NEU: Schema-basierte Message-Verarbeitung
    # helpers/                                 # ❌ NOCH NICHT IMPLEMENTIERT
    #   ccu_factory_layout.py
  nodered/                                     # ✅ IMPLEMENTIERT
    nodered_gateway.py
    nodered_pub_mqtt_client.py
    nodered_sub_mqtt_client.py
    nodered_mqtt_client.py                     # ✅ HINZUGEFÜGT
    # helpers/                                 # ❌ NOCH NICHT IMPLEMENTIERT
    #   nodered_utils.py
  admin/                                       # ✅ IMPLEMENTIERT
    admin_gateway.py
    admin_mqtt_client.py
    admin_settings.py
    log_manager.py                             # ✅ NEU: Log Manager (vorher logs.py)
    # helpers/                                 # ❌ NOCH NICHT IMPLEMENTIERT
    #   admin_utils.py
  ui/                                          # ✅ IMPLEMENTIERT
    main_dashboard.py                          # ✅ HINZUGEFÜGT
    user_manager.py                            # ✅ HINZUGEFÜGT
    common/                                    # ✅ HINZUGEFÜGT
    ccu/
      ccu_overview/
        ccu_overview_tab.py
      ccu_orders/
        ccu_orders_tab.py
      ccu_process/
        ccu_process_tab.py
      ccu_configuration/
        ccu_configuration_tab.py
        ccu_factory_configuration_subtab.py
        ccu_parameter_configuration_subtab.py
      ccu_modules/
        ccu_modules_tab.py
    nodered/
      nodered_overview/
        nodered_overview_tab.py
      nodered_processes/
        nodered_processes_tab.py
    admin/
      admin_settings/
        admin_settings_tab.py
        workpiece_subtab.py
        dashboard_subtab.py
        module_subtab.py
        mqtt_subtab.py
        topics_subtab.py
        schemas_subtab.py
      # logs/                                   # ❌ NOCH NICHT IMPLEMENTIERT
      #   logs_tab.py
      generic_steering/
        generic_steering_tab.py
      message_center/
        message_center_tab.py
    components/                                # ❌ NOCH NICHT IMPLEMENTIERT
      # factory_layout.py
      # custom_button.py
      # status_indicator.py
    utils/
      ui_refresh.py                            # ✅ IMPLEMENTIERT
  config/                                      # ✅ IMPLEMENTIERT
    mqtt_settings.yml
    apps.yml
    # user_roles.yml                           # ❌ NOCH NICHT IMPLEMENTIERT
  factory/                                     # ✅ IMPLEMENTIERT
    client_factory.py
    gateway_factory.py
  tests/                                       # ✅ IMPLEMENTIERT (FLACH)
    test_admin_mqtt_client.py                 # ✅ HINZUGEFÜGT
    test_admin_settings.py
    test_ccu_mqtt_client.py
    test_comprehensive_architecture.py         # ✅ HINZUGEFÜGT
    test_gateway_factory.py                   # ✅ HINZUGEFÜGT
    test_registry_manager_comprehensive.py
    test_registry_v2_integration.py            # ✅ HINZUGEFÜGT
    test_registry_v2_integration_simple.py    # ✅ HINZUGEFÜGT
    test_st_rerun_forbidden.py                # ✅ HINZUGEFÜGT
    test_streamlit_dashboard.py               # ✅ HINZUGEFÜGT
    test_streamlit_startup.py                 # ✅ HINZUGEFÜGT
    test_ui_components.py                    # ✅ HINZUGEFÜGT
    test_workpiece_manager.py
    # ccu/                                     # ❌ NOCH NICHT IMPLEMENTIERT
    #   test_ccu_gateway.py
    #   test_workpiece_manager.py
    # nodered/                                 # ❌ NOCH NICHT IMPLEMENTIERT
    #   test_nodered_gateway.py
    # system/                                   # ❌ NOCH NICHT IMPLEMENTIERT
    #   test_admin_settings.py
    #   test_logs.py
  common/                                      # ✅ IMPLEMENTIERT
    i18n.py
    logger.py
    workpiece_manager.py                       # ✅ NEU: Registry-basierte Workpiece-Icons
    # Schema-driven Messages - Direkte JSON-Schema Integration
  # ZUSÄTZLICHE ENTWICKLUNGEN:                 # ✅ HINZUGEFÜGT
  omf.py                                       # ✅ HAUPTANWENDUNG
  example_usage.py                            # ✅ BEISPIEL-SKRIPT
  scripts/                                    # ✅ HILFSSKRIPTE
    check_st_rerun.py
  dashboard/                                   # ✅ DASHBOARD-UTILS
    utils/
  # DOKUMENTATION:                             # ✅ HINZUGEFÜGT
  architektur-mqtt-gateway-streamlit.md
  cop.md
  IMPLEMENTATION_STATUS.md
  refactoring-backlog-omf2.md
```

---

## 2. Prinzipien & Verantwortlichkeiten

### **Registry (nach erfolgtem refactoring im Projekt-Root)**
- Enthält **alle fachlichen Modelle, Schemata und Registry-Manager**.
- `manager/` innerhalb von `registry/` enthält alle Klassen, die den Zugriff, das Parsen und die Validierung der Registry-Daten kapseln (z. B. `registry_manager.py`, `workpiece_registry_manager.py`).

### **Assets**
- Der Ordner `omf2/assets/` dient als zentrale Ablage für alle statischen Ressourcen, die in der UI verwendet werden.
  - **logos/**: Firmen- und Produktlogos.
  - **icons/**: PNG, SVG, und andere Icon-Grafiken (z. B. für Module oder Statusanzeigen).
  - **schemas/**: JSON-Schemas für Message-Validierung etc.
- Assets werden in der UI direkt aus diesem Verzeichnis geladen und versioniert.

### **Factory-Pattern**
- Zentral für die Erzeugung/Verwaltung von Singleton-Clients und Gateways.
- Ablage in `omf2/factory/` (z. B. `client_factory.py`, `gateway_factory.py`).
- Nutze Factories immer, wenn Clients/Gateways domänenübergreifend oder konfigurierbar erstellt werden sollen.

### **Modulare Domänenstruktur**
- Jede Domäne (`ccu`, `nodered`, `admin`) erhält ein eigenes Verzeichnis in `omf2/`
- `nodered/` enthält zwei MQTT-Clients: `nodered_pub_mqtt_client.py` und `nodered_sub_mqtt_client.py`.
- Wiederverwendbare, aber **nur domänenintern** genutzte Komponenten in `helpers/`-Unterordner innerhalb der jeweiligen Domäne.
  - **MQTT-Client (Singleton):** `<domäne>_mqtt_client.py`
  - **Gateway:** `<domäne>_gateway.py`
  - **(optional) Manager:** Für Entitäten, z. B. `workpiece_manager.py`

### **Spezialisierte Manager vs. Registry-Manager**
- **Registry-Manager** (z. B. `registry/manager/workpiece_registry_manager.py`):
  - Zuständig für das Laden, Validieren und reine Daten-Handling von Entitäten aus der Registry.
  - Kennt nur die Struktur und Schemata der Registry, ist *nicht* domänenspezifisch.
  - Stellt Methoden bereit wie `get_workpiece_definition()`, `validate_against_schema()`, etc.
- **Domänenspezifische Manager** (z. B. `omf2/ccu/workpiece_manager.py`):
  - Übernehmen die fachliche/geschäftslogische Verwaltung der Entitäten im Anwendungskontext (z. B. Lebenszyklus, Statuswechsel, Zuordnung, Abläufe).
  - Arbeiten mit Instanzen/Objekten, steuern Abläufe/Prozesse und nutzen dazu ggf. die Registry-Manager als Datenquelle.
  - Stellt Methoden bereit wie `add_workpiece()`, `assign_to_machine()`, `update_workpiece_state()`, etc.

**Beispiel:**  
- Der Registry-Manager lädt und validiert alle Workpiece-Definitionen aus YAML/JSON.
- Der domänenspezifische Manager (z. B. im CCU-Modul) nutzt diese Definitionen, um konkrete Workpieces im Betriebsablauf zu verwalten und zu steuern.

### **UI**
- **Jeder Haupt-Tab und Subtab liegt immer in einem eigenen Unterordner** im jeweiligen Bereich unter `ui/`.  
  Das gilt auch für Tabs ohne Subtabs – damit bleibt die Struktur konsistent und zukunftssicher.
- Beispiel:
    - `ui/ccu/ccu_overview/ccu_overview_tab.py`
    - `ui/ccu/ccu_configuration/ccu_configuration_tab.py`
    - `ui/ccu/ccu_configuration/ccu_factory_configuration_subtab.py`
    - `ui/admin/admin_settings/workpiece_subtab.py`
- **Wiederverwendbare UI-Komponenten** (z.B. `factory_layout.py`, `status_indicator.py`) liegen in `ui/components/`.

### **Config**
- Technische, betreiberspezifische und laufzeitveränderliche Einstellungen in `omf2/config/`.

### **Tests**
- Tests werden nach Domänen/Modulen in `omf2/tests/<domäne>/` abgelegt.
- Wo sinnvoll, Trennung von Unit- und Integration-Tests.

### **Common**
- Gemeinsame Utilities, Logger, i18n etc. zentral unter `omf2/common/`.

### **🎯 ZENTRALE INITIALISIERUNG (omf.py)**

**Registry Manager wird zentral in `omf.py` initialisiert:**
```python
# Initialize Registry Manager (Singleton - nur einmal initialisiert)
if 'registry_manager' not in st.session_state:
    from omf2.registry.manager.registry_manager import get_registry_manager
    st.session_state['registry_manager'] = get_registry_manager("omf2/registry/")
    logger.info("📚 Registry Manager initialized on startup")
```

**Verwendung in allen Domänen:**
```python
# Registry Manager aus Session State holen
registry_manager = st.session_state.get('registry_manager')
if registry_manager:
    topics = registry_manager.get_topics()
    schemas = registry_manager.get_schemas()
    # etc.
```

**Vorteile:**
- **✅ Singleton Pattern** verhindert mehrfache Initialisierung
- **✅ Verfügbar in allen Domänen** (Admin, CCU, Node-RED, Common)
- **✅ Thread-safe** durch Session State
- **✅ Effizient** - nur einmal geladen beim App-Start

---

## 3. Business Logic Manager (Entitäts-Verwaltung)

### 3.1 ModuleManager (Schema-basierte Message-Verarbeitung)

**Datei:** `omf2/ccu/module_manager.py`

**Zweck:** Verwaltung von Modulen mit Schema-basierter Message-Verarbeitung

**Funktionen:**
- **Schema-basierte Message-Verarbeitung:** Verwendet Registry-Schemas für korrekte Daten-Extraktion
- **Status-Management:** Connection, Availability, Configuration Status
- **Icon-Verwaltung:** Registry-basierte Module-Icons
- **Gateway-Pattern:** Nutzt CCU Gateway für MQTT-Zugriff

**Architektur:**
```python
# UI → ModuleManager → CCU Gateway → MQTT Client
def render_ccu_modules_tab():
    module_manager = get_ccu_module_manager()
    modules = module_manager.get_all_modules()
    
    for module_id, module_data in modules.items():
        icon = module_manager.get_module_icon(module_id)  # Registry-basiert
        connection = module_manager.get_connection_display(module_data)  # UISymbols
```

### 3.2 WorkpieceManager (Registry-basierte Icons)

**Datei:** `omf2/common/workpiece_manager.py`

**Zweck:** Zentrale Verwaltung von Workpiece-Icons aus der Registry

**Funktionen:**
- **Workpiece-Icons:** Lädt Icons aus `registry/workpieces.yml`
- **Farb-spezifische Icons:** 🔵⚪🔴 für blue/white/red
- **Singleton-Pattern:** Zentrale Icon-Verwaltung
- **UISymbols-Integration:** Über `UISymbols.get_workpiece_icon()`

**Registry-Integration:**
```yaml
# registry/workpieces.yml
icons:
  general:
    all_workpieces: "🔵⚪🔴"  # Drei Farb-Symbole
    workpiece: "📦"
  colors:
    blue: "🔵"
    white: "⚪"
    red: "🔴"
```

---

## 4. Migration und Übertrag von Quellen

- **Bei Bedarf** können Sourcen (z.B. Gateways, Manager, Modelle) aus `omf/`, `registry/model/v1/` oder anderen Alt-Verzeichnissen übernommen werden.
- Die Übernahme erfolgt ggf. als Kopie, Anpassung an die neue Struktur und Benennung.
- Die Migration von Workpieces und Schemata erfolgt von `registry/model/v1/workpieces.yml` und `registry/schemas/workpieces.schema.json` nach `omf2/registry/` bzw. `omf2/registry/schemas/`.

---

## 4. Namenskonventionen
- Siehe Beispiele in der Struktur oben.
- Keine Bindestriche, sondern Unterstriche.
- Klar sprechende Namen.

- **Dateien:** `<domäne>_mqtt_[pub|sub]_client.py`, `<domäne>_gateway.py`, `workpiece_manager.py` usw.
- **Klassen:** `CCUGateway`, `NodeRedGateway`, `MessageCenterGateway`, `WorkpieceManager` etc.
- **Configs/Schemas:** Klar sprechende Namen, z. B. `mqtt_settings.yml`, `user_roles.yml`, `workpieces.schema.json`.

---

## 5. Environment-Handling

### 5.1 Environment-Typen
Das OMF2 Dashboard unterstützt drei Environment-Modi:

- **🟢 Live**: Real-time MQTT-Verbindung zur echten APS-Fabrik
  - Direkte Verbindung zu 192.168.0.100:1883
  - Echte Hardware-Kommunikation
  - Produktions-Modus

- **🔄 Replay**: Historische Daten-Wiedergabe
  - Session-Daten aus `data/omf-data/sessions/`
  - Kontrollierte Test-Szenarien
  - Reproduzierbare Tests

- **🧪 Mock**: Simulierte Daten für Entwicklung
  - Simulierte MQTT-Nachrichten
  - Keine Hardware-Abhängigkeit
  - Entwicklung und Testing

### 5.2 Environment-Integration
- **Default Environment**: `mock` für sichere Entwicklung
- **Environment-Selector**: Im Dashboard-Header mit Beschreibungen
- **Automatischer Reload**: Bei Environment-Wechsel
- **MQTT-Client-Reset**: Bei Environment-Wechsel für saubere Verbindungen

### 5.3 Environment-spezifische Konfiguration
```python
# Environment-spezifische MQTT-Konfiguration
environments = {
    'live': {
        'broker_host': '192.168.0.100',
        'broker_port': 1883,
        'description': 'Real-time MQTT connection'
    },
    'replay': {
        'broker_host': 'localhost',
        'broker_port': 1883,
        'description': 'Historical data playback'
    },
    'mock': {
        'broker_host': 'localhost',
        'broker_port': 1883,
        'description': 'Simulated data for testing'
    }
}
```

## 6. Aktuelle Implementierung und Weiterentwicklung

### 6.1 Implementierungsstatus (Stand: 2025-09-29)

**✅ VOLLSTÄNDIG IMPLEMENTIERT:**
- Registry v2 mit allen Schemas und Mappings
- MQTT-Clients (Admin, CCU, Node-RED) mit Singleton-Pattern
- Gateway-Factory und Client-Factory
- UI-Struktur mit allen Tabs und Subtabs
- Registry Manager Singleton
- UI-Refresh-Strategie (request_refresh statt st.rerun)
- Grundlegende Test-Suite

**⚠️ TEILWEISE IMPLEMENTIERT:**
- Assets-Verzeichnis (Grundstruktur vorhanden)
- Config-Dateien (mqtt_settings.yml, apps.yml)
- Admin-Settings mit Subtabs
- Test-Struktur (flach, nicht domänen-spezifisch)

**❌ NOCH NICHT IMPLEMENTIERT:**
- Helper-Verzeichnisse (ccu/helpers/, nodered/helpers/, admin/helpers/)
- UI-Komponenten (factory_layout.py, custom_button.py, status_indicator.py)
- Logs-Tab (ui/admin/logs/logs_tab.py)
- User-Roles-Konfiguration (user_roles.yml)
- Domänen-spezifische Test-Struktur

**✅ ZUSÄTZLICHE ENTWICKLUNGEN:**
- Hauptanwendung (omf.py)
- Beispiel-Skript (example_usage.py)
- Hilfsskripte (scripts/)
- Dashboard-Utils (dashboard/utils/)
- Umfangreiche Dokumentation
- Architektur-Dokumente
- **Schema-Integration:** 44 JSON-Schemas für Topic-Validierung
- **Registry-Migration:** Vereinfachte Struktur ohne `model/v2/` Pfad
- **UI-Schema-Integration:** Schema-Validierung in Admin Settings

### 6.2 Prinzipien für zukünftige Aufgaben und Coding Agents

- **Strukturierte Ablage:** Jede neue Komponente/Manager/Client wird nach diesem Muster angelegt.
- **Modularität:** Domänenübergreifende oder -spezifische Logik strikt trennen.
- **Referenzmigration:** Bei neuen Aufgaben prüfen, ob Altbestand übernommen werden muss (siehe Punkt 3).
- **Tests & Dokumentation:** Jede neue Komponente wird mit passenden Tests und Docstrings/README versehen.
- **Environment-Awareness:** Alle MQTT-Clients müssen Environment-Wechsel unterstützen.
- **Referenz auf dieses Dokument:** Jede Aufgabenbeschreibung für Coding Agents, die die Projektstruktur betreffen, soll auf dieses Dokument verweisen.
- **Implementierungsstatus beachten:** Berücksichtige den aktuellen Implementierungsstand bei neuen Entwicklungen.

---

## 7. Beispiel für die Referenz in Coding-Agent-Aufgaben

> **Bitte beachte die Vorgaben aus `omf2/projekt-struktur-omf2.md` für die Ablage, Benennung und Modularisierung!**
> 
> **Aktueller Implementierungsstand:** Siehe Abschnitt 6.1 für den aktuellen Status der Implementierung.

---

## 8. Changelog der Weiterentwicklung

### Version 2.1.0 (2025-10-01)

**Registry-Migration und Schema-Integration:**
- ✅ **Registry-Struktur vereinfacht:** Entfernung von `model/v2/` Pfad
- ✅ **Schema-Integration:** 44 JSON-Schemas für Topic-Validierung
- ✅ **UI-Schema-Integration:** Schema-Validierung in Admin Settings
- ✅ **Registry-Tools:** Automatische Schema-Zuordnung zu Topics
- ✅ **Pfad-Korrekturen:** Alle Komponenten verwenden neue Registry-Pfade

### Version 2.0.0 (2025-09-29)

**Hinzugefügt:**
- ✅ Hauptanwendung (omf.py)
- ✅ Beispiel-Skript (example_usage.py)
- ✅ Hilfsskripte (scripts/)
- ✅ Dashboard-Utils (dashboard/utils/)
- ✅ Umfangreiche Dokumentation
- ✅ Architektur-Dokumente
- ✅ Zusätzliche Schemas in Registry v2
- ✅ Node-RED MQTT-Client (nodered_mqtt_client.py)
- ✅ UI-Manager (user_manager.py)
- ✅ UI-Common-Verzeichnis
- ✅ Umfangreiche Test-Suite

**Geändert:**
- 🔄 Test-Struktur (flach statt domänen-spezifisch)
- 🔄 Assets-Struktur (Grundstruktur implementiert)

**Noch zu implementieren:**
- ❌ Helper-Verzeichnisse
- ❌ UI-Komponenten
- ❌ Logs-Tab
- ❌ User-Roles-Konfiguration
- ❌ Domänen-spezifische Test-Struktur

---

**Letzte Aktualisierung:** 2025-10-02