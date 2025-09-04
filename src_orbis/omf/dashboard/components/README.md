# OMF Dashboard Components

## Overview

Das `components` Verzeichnis enthält alle UI-Komponenten für das OMF Dashboard, organisiert nach Funktionsbereichen.

## Components

### Steering Components

#### Main Steering Component
**Datei:** `steering.py`

Haupt-Tab für die Steuerungs-Funktionalität der ORBIS Modellfabrik.

#### Factory Steering Component
**Datei:** `steering_factory.py`

Implementiert die Factory-Steuerung über MQTT-Nachrichten.

##### Features:

##### 🏭 Factory Steuerung
- **Factory Reset:** Zurücksetzen der Fabrik mit `withStorage` und `clearStorage` Optionen
- **Bestellung auslösen:** Werkstück-Bestellungen für verschiedene Farben (Rot, Weiß, Blau)
- **Workflow-Informationen:** Anzeige der Produktions-Workflows

##### ⚙️ Modul-Steuerung
- **MILL, DRILL, AIQS:** Separate Steuerungs-Boxen für jedes Modul
- **Sequenz-Befehle:** PICK → PROCESS → DROP Befehle mit `orderUpdateId` Tracking
- **Workflow-Management:** Verwaltung von `orderId` und `orderUpdateId`
- **Status-Anzeige:** Modul-Status und aktive Workflows

##### 🚛 FTS-Steuerung
- **Status-abhängige Buttons:** "Laden" und "Laden beenden" sind gegenseitig ausschließend
- **Docke an:** FTS an Lade-Station andocken
- **Status abfragen:** Aktuellen FTS-Status abrufen

#### Generic Steering Component
**Datei:** `steering_generic.py`

Implementiert den generischen Message-Generator für MQTT-Nachrichten.

##### Features:

##### 📡 Message-Generator
- **Topic-basierte Auswahl:** User wählt MQTT-Topic statt Template
- **Template-Mapping:** Automatisches Laden des passenden Templates
- **Editierbare Nachrichten:** Topic und Payload können bearbeitet werden
- **JSON-Validierung:** Validierung vor dem Senden
- **MQTT-Integration:** Senden nur bei aktiver MQTT-Verbindung

#### UI Structure:

```python
def show_steering():
    """Hauptfunktion für Steuerung-Tab"""
    
    # Factory Steuerung
    show_factory_steering()
    
    # Generic Steuerung
    show_generic_steering()
```

#### Key Functions:

##### Factory Control:
- `show_factory_reset()`: Factory Reset Dialog mit Bestätigung
- `show_order_request()`: Werkstück-Bestellung mit Farb- und Typ-Auswahl
- `_send_factory_reset_message()`: Factory Reset MQTT-Nachricht senden
- `_send_order_request()`: Bestellungs-Request senden

##### Module Control:
- `_show_module_control_box()`: Einzelne Modul-Steuerungs-Box
- `_send_single_module_step()`: Einzelnen Modul-Befehl senden
- `_get_module_status()`: Modul-Status abrufen

##### FTS Control:
- `show_fts_steering()`: FTS-Steuerung mit Status-abhängigen Buttons
- `_send_fts_command()`: FTS-Befehl senden
- `_get_fts_status()`: FTS-Status abrufen

##### Message Generator:
- `show_generic_steering()`: Topic-basierte Template-Auswahl
- `_generate_topic_specific_params()`: Topic-spezifische Parameter generieren
- `_resolve_topic_variables()`: Variable in Topic-Patterns auflösen

### Overview Components

#### Overview Inventory Component
**Datei:** `overview_inventory.py`

Zeigt den aktuellen Lagerbestand der HBW-Module mit visueller Darstellung.

##### Features:
- **Lagerbestand-Anzeige:** Aktuelle Werkstück-Verfügbarkeit
- **Visuelle Darstellung:** HTML-Templates für Buckets und Werkstücke
- **Auto-Refresh:** Automatische Aktualisierung der Bestände
- **Manual Refresh:** Manuelle Aktualisierung über Sidebar

#### Overview Customer Order Component
**Datei:** `overview_customer_order.py`

Implementiert Kundenaufträge mit direkter MQTT-Integration.

##### Features:
- **Direkte Bestellung:** Werkstück-Bestellungen direkt an Factory
- **Farb-Auswahl:** Rot, Weiß, Blau Werkstücke
- **MQTT-Integration:** Direkter Versand über MQTT
- **Status-Feedback:** Erfolgs-/Fehlermeldungen

#### Overview Purchase Order Component
**Datei:** `overview_purchase_order.py`

Zeigt Rohmaterial-Bestellungen mit visueller Darstellung.

##### Features:
- **Rohmaterial-Bedarf:** Anzeige des aktuellen Bedarfs
- **Visuelle Templates:** HTML-Templates für Buckets
- **Bedarf-Tracking:** Verfolgung von Bestellungen

### Production Order Components

#### Production Order Management Component
**Datei:** `production_order_management.py`

Verwaltung von Fertigungsaufträgen (in Entwicklung).

##### Features:
- **Auftragserstellung:** Neue Fertigungsaufträge anlegen
- **Auftragsverfolgung:** Status und Fortschritt überwachen
- **Auftragshistorie:** Vergangene Aufträge einsehen
- **Prioritätsverwaltung:** Aufträge nach Priorität sortieren
- **Ressourcenplanung:** Verfügbare Module berücksichtigen

#### Production Order Current Component
**Datei:** `production_order_current.py`

Anzeige laufender Fertigungsaufträge (in Entwicklung).

##### Features:
- **Aktive Aufträge:** Anzeige aller laufenden Fertigungsaufträge
- **Fortschrittsanzeige:** Visueller Fortschritt der Produktionsschritte
- **Modul-Status:** Welche Module sind aktuell beschäftigt
- **Werkstück-Verfolgung:** Position der Werkstücke in der Fabrik
- **Echtzeit-Updates:** Live-Aktualisierung der Auftragsstatus

### Message Center Component
**Datei:** `message_center.py`

Zentrale Anzeige aller MQTT-Nachrichten mit Filter- und Suchfunktionen.

##### Features:
- **Nachrichten-Historie:** Alle empfangenen und gesendeten Nachrichten
- **Filter-Funktionen:** Nach Topic, Richtung, Zeitraum filtern
- **Suchfunktion:** Volltext-Suche in Nachrichten
- **Live-Updates:** Echtzeit-Anzeige neuer Nachrichten
- **Export-Funktionen:** Nachrichten exportieren

### Settings Component
**Datei:** `settings.py`

Konfigurations-Interface für das OMF Dashboard.

#### Features:
- **Modul-Konfiguration:** Aktivierung/Deaktivierung von Modulen
- **NFC-Konfiguration:** Werkstück-Konfiguration nach Farben
- **Topic-Konfiguration:** MQTT-Topic-Verwaltung
- **MQTT-Broker:** Broker-Konfiguration und Verbindung
- **MQTT-Mock:** Mock-Modus für Tests

### HTML Templates
**Datei:** `assets/html_templates.py`

Wiederverwendbare HTML-Templates für UI-Elemente.

##### Features:
- **Bucket-Templates:** Visuelle Darstellung von Lager-Buckets
- **Werkstück-Templates:** Farbige Werkstück-Darstellung
- **Responsive Design:** Anpassbare Größen und Layouts

#### MQTT Integration:

##### Connection Management:
- **Mock-Modus:** Simuliert MQTT-Verbindung für Tests
- **Connection Status:** Globale Anzeige des MQTT-Status
- **Button States:** Buttons nur bei aktiver Verbindung aktiv

##### Message Sending:
- **Topic Resolution:** Variable werden in Topics aufgelöst
- **Payload Generation:** Template-basierte Payload-Generierung
- **Error Handling:** Graceful Fehlerbehandlung bei Sendefehlern

#### Configuration:

##### MQTT Mock:
```python
# In Settings aktivierbar
st.session_state.mqtt_mock_enabled = True
```

##### Topic-Mapping:
```yaml
# topic_message_mapping.yml
"module/v1/ff/{module_id}/order":
  template: "module/order"
  direction: "outbound"
  description: "Modul-Befehle senden"
```

#### Error Handling:

- **Graceful Degradation:** Fallback bei fehlenden Komponenten
- **User Feedback:** Erfolgs- und Fehlermeldungen
- **Connection Checks:** MQTT-Verbindung wird vor Senden geprüft
- **JSON Validation:** Payload wird vor Senden validiert

#### Testing:

##### Unit Tests:
- `tests_orbis/test_message_generator.py`: Message-Generator Tests
- `tests_orbis/test_topic_mapping_manager.py`: Topic-Mapping Tests
- `tests_orbis/test_dashboard_mqtt_integration.py`: Dashboard MQTT Tests

##### Integration Tests:
- Dashboard-Integration getestet
- MQTT-Mock-Modus funktioniert
- Template-Mapping korrekt

## Future Enhancements

### Geplante Erweiterungen:
- **Real-time Status:** Live-Updates von Modul- und FTS-Status
- **Advanced Workflows:** Komplexe Workflow-Definitionen
- **History Tracking:** Nachrichten-Historie und Logs
- **Performance Monitoring:** System-Performance-Überwachung
- **User Management:** Benutzer-Rollen und Berechtigungen
- **Production Order Implementation:** Vollständige Fertigungsauftrags-Verwaltung
