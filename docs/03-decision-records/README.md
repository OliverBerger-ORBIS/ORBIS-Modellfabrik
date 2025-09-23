# OMF-Dashboard Decision Records

Übersicht aller Architektur-Entscheidungen für das OMF-Dashboard.

## Entscheidungen

### 1. [Singleton-Pattern für MQTT-Client](01-singleton-pattern-mqtt-client.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Verwendung des Singleton-Pattern für den MQTT-Client über `ensure_dashboard_client()` zur Vermeidung von Ressourcenverschwendung und Gewährleistung von Konsistenz.

### 2. [Einheitliches Logging-System](02-unified-logging-system.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** OMF-Logging-System mit JSON-Formatierung, zentraler Konfiguration und einheitlichen Logger-Instanzen für strukturierte Logs.

### 3. [Komponenten-Trennung (UI ↔ Business-Logik)](03-component-separation-ui-business-logic.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Wrapper-Pattern mit separaten Manager-Klassen für Business-Logik und UI-Komponenten für bessere Wartbarkeit und Testbarkeit.

### 4. [Wrapper-Pattern für Dashboard-Tabs](04-wrapper-pattern-dashboard-tabs.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Einheitliche Struktur für Dashboard-Tabs mit Untertabs und klarer Hierarchie für bessere Modularität.

### 5. [Session State Management](05-session-state-management.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Verwendung von Streamlit Session State für Manager-Instanzen und persistente Zustände über Reruns hinweg.

### 6. [MQTT-Integration über zentralen Client](06-mqtt-integration-central-client.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Singleton MQTT-Client für alle MQTT-Operationen mit zentralem Logging und konsistenter Payload-Behandlung.

### 7. [Development Rules Compliance](07-development-rules-compliance.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Befolgung der OMF Development Rules für einheitliche Entwicklungsstandards, Code-Qualität, Formatierung und Registry-Pfad-Konstanten.

### 8. [Registry-basierte Konfiguration](08-registry-based-configuration.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Zentrale, versionierte Konfiguration für Schemas, Templates und Module-Definitionen über das Registry-System.

### 9. [Per-Topic-Buffer Pattern](09-per-topic-buffer-pattern.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Effiziente MQTT-Nachrichtenverarbeitung mit Topic-spezifischen Puffern für bessere Performance und Organisation.

### 10. [UI-Refresh Pattern](10-ui-refresh-pattern.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Thread-sicheres UI-Update-System mit `request_refresh()` statt `st.rerun()` zur Vermeidung von Endlosschleifen.

### 11. [Error Handling und Fault Tolerance](11-error-handling-fault-tolerance.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Robuste Fehlerbehandlung mit Try-Catch-Blöcken, Graceful Degradation und User-freundlichen Fehlermeldungen.

## Verwendung

### Neue Komponente hinzufügen:
1. **Wrapper-Komponente** erstellen (z.B. `new_component.py`)
2. **Sub-Komponenten** für spezifische Funktionen
3. **Manager-Klasse** für Business-Logik
4. **In `omf_dashboard.py`** registrieren
5. **Tab** in `display_tabs()` hinzufügen

### MQTT-Nachrichten senden:
```python
# Immer über Singleton-Client
client = st.session_state.get("mqtt_client")
result = client.publish(topic, payload, qos=1, retain=False)
```

### Logging verwenden:
```python
from omf.dashboard.tools.logging_config import get_logger
logger = get_logger("omf.dashboard.component_name")
logger.info("📤 MQTT Publish: topic → payload")
```

## Template

Für neue Decision Records verwenden Sie das [Template](decision_template.md).

---

*Letzte Aktualisierung: 2024-12-19*
