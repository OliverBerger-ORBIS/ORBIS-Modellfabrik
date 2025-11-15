# OMF Decision Records

Übersicht aller Architektur-Entscheidungen für das OMF-Dashboard.

## Entscheidungen

### OMF3 Decision Records

### 15. [Tab Stream Initialization Pattern](11-tab-stream-initialization-pattern.md) *(OMF3)*
**Status:** Accepted  
**Datum:** 2025-11-15  
**Kurzbeschreibung:** Timing-unabhängige Tab-Stream-Initialisierung mit MessageMonitorService für sofortige Datenanzeige.

### 16. [MessageMonitorService - Speicherverwaltung](12-message-monitor-service-storage.md) *(OMF3)*
**Status:** Accepted  
**Datum:** 2025-11-15  
**Kurzbeschreibung:** Circular Buffer System mit konfigurierbarer Retention, 5MB localStorage-Limit und Überlauf-Prävention.

### 17. [MQTT Connection Loop Prevention](13-mqtt-connection-loop-prevention.md) *(OMF3)*
**Status:** Accepted  
**Datum:** 2025-11-XX  
**Kurzbeschreibung:** Verhindert MQTT Connection Loops durch korrekte Lifecycle-Verwaltung.

## Legacy Decision Records (archiviert)

Legacy OMF2 Decision Records wurden archiviert. Siehe `docs/archive/03-decision-records_omf_legacy/` für historische Entscheidungen.

## Template

Für neue Decision Records verwenden Sie das [Template](decision_template.md).

---

*Letzte Aktualisierung: 2025-11-15*
