# ORBIS Modellfabrik - Projekt Status

**Letzte Aktualisierung:** 20.09.2025  
**Aktueller Sprint:** Sprint 05 (18.09 - 01.10.2025)

> **Dokumentations-Strategie:** Dieses Dokument ist die zentrale Quelle für alle Projekt-Änderungen und Sprint-Status. Keine separate CHANGELOG.md - alles hier!

## 🚀 Aktuelle Arbeiten

### ✅ **APS Dashboard Integration abgeschlossen** (20.09.2025)
- **4 neue APS Tabs** vollständig implementiert
- **APS-spezifische Manager** (VDA5050, TXT Controller, System Control)
- **MQTT-Integration** mit einheitlichem Logging
- **Registry-Erweiterung** für APS-spezifische Topics
- **Fischertechnik TXT-Programme** extrahiert und analysiert
- **Session Manager** mit Replay Station als Default

### 🔄 **Nächste Schritte**
1. ✅ **Sprint-Dokumentation** erstellen (sprint_01 bis sprint_05)
2. ✅ **PROJECT_OVERVIEW.md** zu statischer Dokumentation umwandeln
3. ✅ **Doku Overkill vermeiden** - docs aufräumen und konsolidieren
4. **Mermaid Doku** - Diagramme auslagern, IDE-Einrichtung, Toggle Bearbeiten/Preview, Verweise in MDs
5. **Session Analyse Helper App** dokumentieren - technische Beschreibung und HowTo-Nutzung
6. **Architektur-Dokumentation** an APS-Analyse-Ergebnisse anpassen
7. **Node-RED Simulation** im Dashboard vorbereiten
8. **OMF-Dashboard mit realer Fabrik testen** - Validierung der APS-Integration

## 📊 Sprint-Vorgehen

### **Sprint-Strategie:**
- **2-Wochen-Zyklen** für kontinuierliche Entwicklung
- **PROJECT_STATUS.md** = Zentrale Change-Dokumentation
- **Sprint-Dokumentation** = Detaillierte Rückblicke in `docs/sprints/`
- **Keine CHANGELOG.md** = Redundanz vermeiden

### **Change-Management:**
- **Alle Änderungen** werden hier dokumentiert
- **Sprint-Status** wird kontinuierlich aktualisiert
- **Wichtige Entscheidungen** in `docs/03-decision-records/`

## 📊 Sprint-Status

### Sprint 05 (18.09 - 01.10.2025) - **AKTUELL**
- **Status:** In Bearbeitung
- **Fokus:** DPS TXT Komponente Analyse und Integration
- **Erreicht:** APS Dashboard vollständig in OMF-Dashboard integriert
- **Nächste Schritte:** Sprint-Dokumentation, Architektur-Anpassung

### Sprint 04 (04.09 - 17.09.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF-Architektur, Singleton Pattern, Registry Support
- **Erreicht:** FTS-Steuerung, Pub-Sub Analyse, Client-ID Zuordnung, Node-RED Analyse

### Sprint 03 (23.08 - 03.09.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Tiefe Analyse, Template Analyser, Session Analyse
- **Erreicht:** Topics-Verständnis, Registry-Aufbau

### Sprint 02 (07.08 - 22.08.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Einfaches OMF-Dashboard, Nachrichten-Zentrale
- **Erreicht:** Overview über Modul-Status, erste Commands

### Sprint 01 (24.07 - 06.08.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Verstehen des APS-Systems, Helper-Apps
- **Erreicht:** Session Manager, MQTT-Aufnahme, Themenbezogene Sessions

## 🎯 Wichtige Doings

### **Entscheidungen getroffen:**
- **Singleton Pattern** für MQTT-Client
- **Wrapper Pattern** für Dashboard-Tabs
- **Registry-basierte Konfiguration**
- **Per-Topic-Buffer Pattern** für MQTT-Nachrichten

### **Technische Meilensteine:**
- **APS Dashboard** vollständig integriert
- **MQTT-Logging** einheitlich implementiert
- **Dictionary-Payloads** für korrekte Kommunikation
- **Session Manager** mit Replay Station als Default

### **Offene Punkte:**
- **Mermaid Doku** - Diagramme auslagern, IDE-Einrichtung, Toggle Bearbeiten/Preview, Verweise in MDs
- **Session Analyse Helper App** dokumentieren - technische Beschreibung und HowTo-Nutzung
- **OMF-Dashboard mit realer Fabrik testen** - Validierung der APS-Integration
- **Node-RED Simulation** im Dashboard
- **I18n Unterstützung** (EN, DE, FR)
- **Architektur-Dokumentation** anpassen

## 📋 Next Steps

1. ✅ **Sprint-Dokumentation** erstellen (sprint_01.md bis sprint_05.md)
2. ✅ **PROJECT_OVERVIEW.md** zu statischer Dokumentation umwandeln
3. ✅ **Doku Overkill vermeiden** - docs aufräumen und konsolidieren
4. **Mermaid Doku** - Diagramme auslagern, IDE-Einrichtung, Toggle Bearbeiten/Preview, Verweise in MDs
5. **Session Analyse Helper App** dokumentieren - technische Beschreibung und HowTo-Nutzung
6. **OMF-Dashboard mit realer Fabrik testen** - Validierung der APS-Integration
7. **Architektur-Dokumentation** an APS-Analyse-Ergebnisse anpassen
8. **Node-RED Simulation** vorbereiten
9. **I18n Unterstützung** implementieren

## 🔗 Wichtige Links

- **Aktuelle Sprint-Dokumentation:** `docs/sprints/`
- **Decision Records:** `docs/03-decision-records/`
- **Architektur:** `docs/02-architecture/`
- **APS-Analyse:** `docs/analysis/dps/`

---

**Status:** Projekt läuft erfolgreich, alle geplanten Meilensteine erreicht 🎉
