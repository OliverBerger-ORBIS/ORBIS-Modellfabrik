# OMF Dashboard Refactoring 
- Dokumentation,des Standes dashbboard-v3.0.0-wip-complex-services.

## 📋 Übersicht der Refactoring-Arbeiten

**Datum:** 01.09.2025  
**Ausgangspunkt:** `omf-v1.0.0` (funktionierender Stand)  
**Ziel:** Integration von OrderManagerService für Lagerbestand und Auftragsverwaltung

## 🎯 Refactoring-Ziele

### 1. **Service-basierte Architektur**
- Trennung von `hbw_manager_service` → `order_manager_service`
- Verwendung von MQTT Event Manager für Message Distribution
- Service Registry für zentrale Service-Verwaltung

### 2. **Dashboard-Integration**
- Lagerbestand-Tab mit 3x3 Grid (A1-C3)
- Auftragsverwaltung für Produktionsschritte
- Live MQTT-Daten Integration

### 3. **Verbesserte Logging-Infrastruktur**
- Zentrale Logging-Konfiguration
- Separate Log-Dateien für verschiedene Komponenten
- Log-Viewer im Dashboard für bessere Nachvollziehbarkeit

## 🔧 Technische Erkenntnisse

### MQTT-Client Interface
- **Verwendung:** MQTT-Client Interface für konsistente Verbindungen
- **Broker-Konfiguration:** Replay-Broker (localhost:1884) als Standard
- **Event Manager:** Zentrale Message-Verteilung an Services

### Service-Architektur
```
MQTT Event Manager
├── ModuleControllerService (Module Status)
├── MQTTStatusService (Broker Status)
└── OrderManagerService (Lagerbestand & Aufträge)
```

### OrderManagerService Verantwortlichkeiten
- **Lagerbestand-Tab:** 3x3 Grid mit Werkstück-Typen
- **Aufträge-Tab:** Produktionsschritte Tracking
- **Bestellung-Tab:** Bestellungsverwaltung
- **Bestellung-Rohware-Tab:** Rohware-Bestellungen

## 📊 Lagerbestand-Implementierung

### MQTT-Topic: `ccu/state/stock`
```json
{
  "ts": "2025-08-19T09:17:08.337Z",
  "stockItems": [
    {
      "workpiece": {
        "id": "04798eca341290",
        "type": "WHITE",
        "state": "RAW"
      },
      "location": "B1",
      "hbw": "SVR3QA0022"
    }
  ]
}
```

### 3x3 Grid-Layout (A1-C3)
```
A1 | A2 | A3
B1 | B2 | B3
C1 | C2 | C3
```

### Werkstück-Typen
- **RED:** Rote Werkstücke
- **BLUE:** Blaue Werkstücke  
- **WHITE:** Weiße Werkstücke
- **EMPTY:** Leere Positionen

### FIFO-Prinzip
- **First In, First Out:** Älteste Werkstücke werden zuerst verarbeitet
- **Lager-Positionen:** A1-C3 für verschiedene Werkstück-Typen
- **Status-Tracking:** RAW, PROCESSED, FINISHED

## 🏗️ Neue Architektur-Komponenten

### 1. OrderManagerService
**Datei:** `src_orbis/omf/services/order_manager_service.py`

**Funktionen:**
- `process_mqtt_message()`: Verarbeitet `ccu/state/stock` Nachrichten
- `get_inventory()`: Liefert 3x3 Grid-Daten
- `get_statistics()`: Berechnet Lagerbestand-Statistiken
- `get_debug_info()`: Debug-Informationen für Dashboard

### 2. Service Registry
**Datei:** `src_orbis/omf/services/service_registry.py`

**Erweiterungen:**
- OrderManagerService Registration
- MQTT Event Manager Integration
- Service Lifecycle Management

### 3. Logging-Infrastruktur
**Datei:** `src_orbis/omf/utils/logging_config.py`

**Features:**
- Separate Log-Dateien für Dashboard, MQTT, Services
- Log-Viewer im Dashboard (📋 Logs Tab)
- Strukturierte Logging für bessere Nachvollziehbarkeit

### 4. MQTT Event Manager
**Integration:** Alle Services verwenden MQTT Event Manager
- **Topic-Subscription:** Automatische Topic-Verteilung
- **Message Processing:** Service-spezifische Message-Verarbeitung
- **Error Handling:** Robuste Fehlerbehandlung

## 📁 Bestehende Settings-Integration

### Modul-Config
- **Quelle:** `src_orbis/omf/config/module_config.yml`
- **Verwendung:** Modul-Status Tab, Service-Initialisierung
- **Integration:** OrderManagerService verwendet Modul-Informationen

### MQTT-Config
- **Quelle:** `src_orbis/omf/config/mqtt_config.yml`
- **Erweiterung:** Replay-Broker Konfiguration
- **Standard:** Connection zu Replay-Broker (localhost:1884)

### Topic-Config
- **Quelle:** `src_orbis/omf/config/topic_config.yml`
- **Integration:** OrderManagerService abonniert `ccu/state/stock`
- **Erweiterung:** Neue Topics für Auftragsverwaltung

## 🔍 Implementierte Features

### ✅ Erfolgreich implementiert:
1. **OrderManagerService:** Grundstruktur und MQTT-Integration
2. **Service Registry:** OrderManagerService Registration
3. **Logging-Infrastruktur:** Zentrale Logging-Konfiguration
4. **MQTT Event Manager:** Service-Integration
5. **Replay-Broker:** Standard-Konfiguration

### ❌ Probleme aufgetreten:
1. **overview.py Deletion:** Kritischer Fehler - Datei gelöscht
2. **NameError GLOBAL_INVENTORY_STATS:** Variable-Scoping Probleme
3. **Dashboard-UI Integration:** OrderManagerService → UI Datenfluss
4. **Performance Issues:** Streamlit Rerun-Probleme

## 🎯 Nächste Schritte

### 1. **Sauberer Neustart**
- Zurück zu `omf-v1.0.0` (funktionierender Stand)
- `overview.py` wiederherstellen
- Schrittweise Integration des OrderManagerService

### 2. **Systematische Integration**
- OrderManagerService in bestehende Architektur integrieren
- Lagerbestand-Tab implementieren
- Auftragsverwaltung hinzufügen

### 3. **Testing & Validation**
- MQTT Message Processing testen
- UI-Integration validieren
- Performance optimieren

## 📝 Wichtige Erkenntnisse

### Architektur-Entscheidungen:
1. **Service-basierte Architektur:** Bessere Trennung der Verantwortlichkeiten
2. **MQTT Event Manager:** Zentrale Message-Verteilung
3. **Logging-Infrastruktur:** Bessere Nachvollziehbarkeit
4. **Replay-Broker:** Standard für Entwicklung und Testing

### Technische Herausforderungen:
1. **Streamlit Session State:** Thread-safety bei Service-Updates
2. **MQTT Message Processing:** Robuste Fehlerbehandlung
3. **UI-Integration:** Datenfluss von Services zu Dashboard-Komponenten
4. **Performance:** Streamlit Rerun-Optimierung

### Best Practices:
1. **Häufige Commits:** Nach jedem erfolgreichen Schritt
2. **Rollback-Strategie:** Immer funktionierenden Stand haben
3. **Testing:** Nach jeder Änderung testen
4. **Dokumentation:** Änderungen dokumentieren

---

**Status:** Refactoring dokumentiert, bereit für sauberen Neustart  
**Nächster Schritt:** Zurück zu `omf-v1.0.0` und systematische Integration
