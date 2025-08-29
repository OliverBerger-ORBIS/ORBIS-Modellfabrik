# OMF Dashboard Components

## Overview

Das `components` Verzeichnis enthält alle UI-Komponenten für das OMF Dashboard, organisiert nach Funktionsbereichen.

## Components

### Steering Component

**Datei:** `steering.py`

Implementiert die Steuerungs-Funktionalität für die ORBIS Modellfabrik über MQTT-Nachrichten.

#### Features:

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
    show_factory_control()
    
    # Modul-Steuerung
    show_module_sequence_control()
    
    # FTS-Steuerung
    show_fts_control()
    
    # Message-Generator
    show_message_generator()
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
- `show_fts_control()`: FTS-Steuerung mit Status-abhängigen Buttons
- `_send_fts_command()`: FTS-Befehl senden
- `_get_fts_status()`: FTS-Status abrufen

##### Message Generator:
- `show_message_generator()`: Topic-basierte Template-Auswahl
- `_generate_topic_specific_params()`: Topic-spezifische Parameter generieren
- `_resolve_topic_variables()`: Variable in Topic-Patterns auflösen

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

##### Integration Tests:
- Dashboard-Integration getestet
- MQTT-Mock-Modus funktioniert
- Template-Mapping korrekt

## Settings Component

**Datei:** `settings.py`

Konfigurations-Interface für das OMF Dashboard.

#### Features:
- **Modul-Konfiguration:** Aktivierung/Deaktivierung von Modulen
- **NFC-Konfiguration:** Werkstück-Konfiguration nach Farben
- **Topic-Konfiguration:** MQTT-Topic-Verwaltung
- **MQTT-Broker:** Broker-Konfiguration und Verbindung
- **MQTT-Mock:** Mock-Modus für Tests

## Future Enhancements

### Geplante Erweiterungen:
- **Real-time Status:** Live-Updates von Modul- und FTS-Status
- **Advanced Workflows:** Komplexe Workflow-Definitionen
- **History Tracking:** Nachrichten-Historie und Logs
- **Performance Monitoring:** System-Performance-Überwachung
- **User Management:** Benutzer-Rollen und Berechtigungen
