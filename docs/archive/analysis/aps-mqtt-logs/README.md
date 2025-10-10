# 📦 Archivierte APS-MQTT-Log-Analysen

**Archiviert:** 2025-10-08  
**Grund:** Prozess-Dokumente, konsolidiert in zentrale Referenz

Diese Dokumente beschreiben den **Analyse-Prozess**, wie wir zu unseren Erkenntnissen über die APS-Architektur gekommen sind. Die finalen, verifizierten Ergebnisse sind in der **zentralen Referenz** dokumentiert:

→ **[docs/06-integrations/00-REFERENCE/](../../../06-integrations/00-REFERENCE/README.md)**

---

## 📄 Archivierte Dokumente

### 1. `log-analysis-2025-09-24.md`
**Datum:** 24. September 2025  
**Inhalt:** Initiale Mosquitto-Log-Analyse  
**Erkenntnisse:** Client-IDs, Will Messages, Erste Topic-Zuordnungen

### 2. `startup-analysis-corrected-final-2025-09-28.md`
**Datum:** 28. September 2025  
**Inhalt:** Startup-Sequenz-Analyse (korrigierte Version)  
**Erkenntnisse:** Module-Topic-Zuordnung, Publisher/Subscriber-Patterns

### 3. `pub-sub-pattern-analysis-2025-09-28.md`
**Datum:** 28. September 2025  
**Inhalt:** Pub/Sub-Pattern-Analyse mit Mermaid-Diagrammen  
**Erkenntnisse:** Kommunikations-Flows, QoS-Patterns

### 4. `component-mapping.md`
**Datum:** Verschiedene Updates  
**Inhalt:** Client-ID Mapping und Komponenten-Rollen  
**Erkenntnisse:** Client-ID → Komponenten-Zuordnung

**Hinweis:** Diese Dokumente enthalten teilweise **Fehler** (Serial-Verwechslungen), die in der finalen Referenz korrigiert wurden.

---

## ✅ Finale, verifizierte Informationen

**Siehe stattdessen:**
- [Module Serial Mapping](../../../06-integrations/00-REFERENCE/module-serial-mapping.md) - Korrekte Module-Zuordnung
- [Hardware Architecture](../../../06-integrations/00-REFERENCE/hardware-architecture.md) - System-Übersicht
- [MQTT Topic Conventions](../../../06-integrations/00-REFERENCE/mqtt-topic-conventions.md) - Topic-Patterns
- [CCU-Backend Orchestration](../../../06-integrations/00-REFERENCE/ccu-backend-orchestration.md) - Order-Flow

---

## 🎯 Warum archiviert?

### **Probleme mit den Original-Dokumenten:**
1. ❌ Serial-Number-Verwechslungen (SVR4H73275 ↔ SVR4H76530)
2. ❌ Information verteilt über viele Dateien
3. ❌ Prozess-Beschreibungen vermischt mit Fakten
4. ❌ Keine klare Single Source of Truth

### **Lösung:**
✅ Zentrale **00-REFERENCE** Sektion mit verifizierten, konsolidierten Fakten

---

**Status:** Historische Analysen - Archiviert für Nachvollziehbarkeit


