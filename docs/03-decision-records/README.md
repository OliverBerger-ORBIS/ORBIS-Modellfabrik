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
**Letzte Aktualisierung:** 2025-01-17  
**Kurzbeschreibung:** OMF-Logging-System mit QueueListener-Integration, Thread-Safety, automatischer Log-Bereinigung und optimierten Log-Leveln für strukturierte Logs.

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

### 7. [Development Rules Compliance](../archive/03-decision-records_omf_legacy/07-development-rules-compliance.md) *(Legacy)*
**Status:** Archived  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Legacy Development Rules - siehe [I18n Development Rules](i18n-development-rules.md) für aktuelle Regeln.

### 8. [Registry-basierte Konfiguration](08-registry-based-configuration.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Zentrale, versionierte Konfiguration für Schemas, Templates und Module-Definitionen über das Registry-System.

### 9. [Per-Topic-Buffer Pattern](../archive/02-architecture_omf_legacy/per-topic-buffer-pattern.md) *(Legacy)*
**Status:** Archived  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Legacy MQTT-Pattern - siehe [Message Processing Pattern](../02-architecture/message-processing-pattern.md) für aktuelle Implementierung.

### 10. [I18n Development Rules](i18n-development-rules.md) *(NEW)*
**Status:** Accepted  
**Datum:** 2025-10-10  
**Kurzbeschreibung:** Implementierte i18n-Regeln für OMF2 mit DE/EN/FR Support und Lazy Loading.

### 11. [I18n Implementation Complete](i18n-implementation-complete.md) *(NEW)*
**Status:** Accepted  
**Datum:** 2025-10-10  
**Kurzbeschreibung:** Vollständige i18n-Implementierung mit 195+ Translation Keys und 18 YAML-Dateien.

### 12. [UI-Refresh Pattern](10-ui-refresh-pattern.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Thread-sicheres UI-Update-System mit `request_refresh()` statt `st.rerun()` zur Vermeidung von Endlosschleifen.

### 13. [Error Handling und Fault Tolerance](11-error-handling-fault-tolerance.md)
**Status:** Accepted  
**Datum:** 2024-12-19  
**Kurzbeschreibung:** Robuste Fehlerbehandlung mit Try-Catch-Blöcken, Graceful Degradation und User-freundlichen Fehlermeldungen.

### 14. [Step-by-Step Implementation Principle](09-step-by-step-implementation-principle.md) *(NEW)*
**Status:** Accepted  
**Datum:** 2025-10-19  
**Kurzbeschreibung:** Architektur-Validierung vor Umstellung - Schrittweise Implementierung für komplexe Refactoring-Aufgaben.

### 15. [Tab Stream Initialization Pattern](11-tab-stream-initialization-pattern.md) *(OMF3)*
**Status:** Accepted  
**Datum:** 2025-11-15  
**Kurzbeschreibung:** Timing-unabhängige Tab-Stream-Initialisierung mit MessageMonitorService für sofortige Datenanzeige.

### 16. [MessageMonitorService - Speicherverwaltung](12-message-monitor-service-storage.md) *(OMF3)*
**Status:** Accepted  
**Datum:** 2025-11-15  
**Kurzbeschreibung:** Circular Buffer System mit konfigurierbarer Retention, 5MB localStorage-Limit und Überlauf-Prävention.

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
