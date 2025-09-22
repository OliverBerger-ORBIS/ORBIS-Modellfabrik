# ORBIS Modellfabrik - Projekt Status

**Letzte Aktualisierung:** 22.09.2025  
**Aktueller Sprint:** Sprint 05 (18.09 - 01.10.2025)

> **Dokumentations-Strategie:** Dieses Dokument ist die zentrale Quelle für alle Projekt-Änderungen und Sprint-Status. Keine separate CHANGELOG.md - alles hier!

## 🚀 Aktuelle Arbeiten

### ✅ **APS Dashboard Integration erfolgreich** (22.09.2025)
- **3 konsolidierte APS Tabs** (von 4 auf 3 reduziert)
- **APS Control Tab** - System Commands + Status + Monitoring
- **APS Steering Tab** - Factory + FTS + Modules + Orders (funktional)
- **APS Orders Tab** - Order Management (unverändert)
- **Original APS-Dashboard analysiert** - Topics und Payloads extrahiert
- **Authentische APS-Integration** - Factory Reset und FTS Charging funktionieren
- **Original-Sourcen organisiert** - `integrations/ff-central-control-unit/aps-dashboard-source/`

### ✅ **Mermaid Diagramm-System optimiert** (20.09.2025)
- **Hybrid-Ansatz** implementiert: zentrale vs. dezentrale Diagramme
- **`docs/_shared/diagrams/`** als zentrale Bibliothek für wiederverwendbare Architektur-Diagramme
- **Build-System** mit `npm run diagrams` für automatische SVG-Generierung
- **Kontext-spezifische Diagramme** bleiben bei entsprechenden Dokumenten
- **Obsolet `docs/diagrams/`** entfernt - nutzt jetzt vorhandene `_shared/` Infrastruktur
- **Cross-Platform Testing** erfolgreich - Windows + VSCode getestet

### 🔄 **Nächste Schritte**
1. **APS-Dashboard Tabs systematisch aufbauen** - Verwendung der Original-Sourcen als Referenz
2. **Original APS-Dashboard vollständig analysieren** - Alle Commands, Topics und Payloads dokumentieren
3. **OMF-Dashboard mit realer Fabrik testen** - Validierung der APS-Integration
4. **Namenskonvention etablieren** - APS (As-Is) vs OMF (To-Be) Systeme, einheitliche Bezeichnungen für Dokumentation und Architektur

## 🚀 Entwicklungsphasen

### **Phase 0: APS as-is lauffähig machen**
- **Status:** ✅ Abgeschlossen
- **Ziel:** Fischertechnik-Fabrik funktionsfähig
- **Erreicht:** APS-CCU, APS-NodeRED, APS-Module laufen

### **Phase 1: APS-Komponenten verstehen** 
- **Status:** ✅ Abgeschlossen
- **Ziel:** APS-CCU und APS-NodeRED analysieren
- **Erreicht:** Session Manager, OMF-Dashboard, APS-Integration

### **Phase 2: OMF-CCU etablieren**
- **Status:** 🔄 In Bearbeitung
- **Ziel:** OMF-CCU im OMF-Dashboard implementieren
- **Nächste Schritte:** APS-CCU Funktionalität vollständig übernehmen

### **Phase 3: OMF-NodeRED etablieren**
- **Status:** ⏳ Geplant
- **Ziel:** OMF-NodeRED im OMF-Dashboard implementieren
- **Nächste Schritte:** APS-NodeRED Funktionalität ersetzen
3. **Fehlender APS-Tab integrieren** - 5. APS Tab (APS Configuration) noch nicht eingebunden
4. **Manager-Duplikate beseitigen** - OrderManager (3x identisch), System-Status-Manager (3x ähnlich) auslagern in `omf/dashboard/managers/`
4. **APS-Tabs Registry-Analyse** - Welche APS-Tabs sind für unsere Steuerung tatsächlich notwendig?
5. **APS-Tabs Registry-Integration** - Verbleibende APS-Tabs auf Registry-Manager umstellen
6. **Registry-Konsolidierung** - Legacy-Konfiguration (`omf/config/`) entfernen, alle Manager auf Registry umstellen
7. **WorkpieceManager implementieren** - `nfc_config.yml` → `registry/model/v1/workpieces.yml` Migration (siehe `docs/archive/analysis/dps/REGISTRY_COMPATIBILITY_ANALYSIS.md`)
8. **OMF-Dashboard Tab-Konsolidierung** - APS-Tabs in vorhandene OMF-Tabs integrieren, unnötige Tabs entfernen
9. **Architektur-Dokumentation** an APS-Analyse-Ergebnisse anpassen - As-Is (FT APS) vs. To-Be (ORBIS) Strategie
10. **Node-RED Simulation** im Dashboard vorbereiten
11. **Template-Analyzer reparieren** - Topics aus Template-Deskriptionen entfernen
12. **Direction-Klärung mapping.yml** - Aus Sicht welcher Komponente? (CCU oder NodeRED)
13. **OMF-Dashboard User-Konzept definieren** - Standard-User vs. DSP-Admin Rollen
14. **APS-UI Bereich isolieren** - Standard-User sieht nur APS-Bedienung
15. **DSP-Steuerungsbereich implementieren** - DSP-Admin sieht Node-RED-Simulation Tabs
16. **Node-RED-Simulation Tabs erstellen** - DSP-Steuerung für OT-Übernahme
17. **User-Rollen-System implementieren** - Default vs. DSP-Admin Sichtbarkeit
18. **I18n Unterstützung** implementieren (EN, DE, FR)

#### **✅ Abgeschlossen:**
- ✅ **Sprint-Dokumentation** erstellen (sprint_01 bis sprint_05)
- ✅ **PROJECT_OVERVIEW.md** zu statischer Dokumentation umwandeln
- ✅ **Doku Overkill vermeiden** - docs aufräumen und konsolidieren
- ✅ **Mermaid Doku** - Hybrid-Ansatz mit `docs/_shared/diagrams/` implementiert
- ✅ **Mermaid Diagramme vollständig implementieren** - Dokumentation reorganisiert und committed
- ✅ **Hybrid-Ansatz für Diagramm-Organisation** - `docs/_shared/diagrams/` als zentrale Bibliothek
- ✅ **Pre-commit und Git/GitHub Workflow** - Projekt so anpassen dass pre-commit und git/github Workflow funktioniert
- ✅ **Session Analyse Helper App** dokumentieren - technische Beschreibung und HowTo-Nutzung

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
- **Mermaid Doku** - Hybrid-Ansatz implementiert mit `docs/_shared/diagrams/`
- **Code-Cleanup** - Sequenz-Kontrolle Helper Apps entfernt (VDA5050 übernimmt)


## 🔗 Wichtige Links

- **Aktuelle Sprint-Dokumentation:** `docs/sprints/`
- **Decision Records:** `docs/03-decision-records/`
- **Architektur:** `docs/02-architecture/`
- **APS-Analyse:** `docs/analysis/dps/`

---

**Status:** Projekt läuft erfolgreich, alle geplanten Meilensteine erreicht 🎉
