# ORBIS Modellfabrik - Projekt Status

**Letzte Aktualisierung:** 23.09.2025  
**Aktueller Sprint:** Sprint 05 (18.09 - 01.10.2025)

> **Dokumentations-Strategie:** Dieses Dokument ist die zentrale Quelle für alle Projekt-Änderungen und Sprint-Status. Keine separate CHANGELOG.md - alles hier!

## 🚀 Aktuelle Arbeiten

### 🔄 **APS Dashboard Integration in Bearbeitung** (23.09.2025)
- **APS Overview Tab** - 75% funktionsfähig (Kundenaufträge, Rohmaterial, Lagerbestand ✅)
- **Sensor-Daten fehlen noch** - MQTT Topics für Sensoren noch nicht implementiert
- **APS Control Tab** - System Commands + Status + Monitoring
- **APS Steering Tab** - Factory + FTS + Modules + Orders (funktional)
- **APS Orders Tab** - Order Management (unverändert)
- **Original APS-Dashboard analysiert** - Topics und Payloads extrahiert
- **Code-Duplizierung** - Temporäre Lösung für Key-Konflikte implementiert
- **Original-Sourcen organisiert** - `integrations/ff-central-control-unit/aps-dashboard-source/`
- **Status:** Guter Fortschritt - Sensor-Daten sind nächste Priorität

### ✅ **Mermaid Diagramm-System optimiert** (20.09.2025)
- **Hybrid-Ansatz** implementiert: zentrale vs. dezentrale Diagramme
- **`docs/_shared/diagrams/`** als zentrale Bibliothek für wiederverwendbare Architektur-Diagramme
- **Build-System** mit `npm run diagrams` für automatische SVG-Generierung
- **Kontext-spezifische Diagramme** bleiben bei entsprechenden Dokumenten
- **Obsolet `docs/diagrams/`** entfernt - nutzt jetzt vorhandene `_shared/` Infrastruktur
- **Cross-Platform Testing** erfolgreich - Windows + VSCode getestet

## 📋 Chat-spezifische Arbeiten

### 🎯 **Chat-A: Architektur & Dokumentation**
- ✅ **Namenskonvention etablieren** - APS (As-Is) vs OMF (To-Be) Systeme
- ✅ **System-Context aktualisieren** - Mermaid-Diagramm, ASCII-Art entfernt
- ✅ **APS-CCU Beschreibung** - RPi/Docker-Container, MQTT-Broker Details
- ✅ **Cursor-Agent-Struktur-Plan überarbeiten** - APS/OMF Namenskonvention + bewährte Vorgehensweisen
- ⏳ **Integration-Struktur anpassen** - `/integrations/` auf Komponenten-Namen umstellen
- ⏳ **Dokumentations-Struktur anpassen** - `/docs/06-integrations/APS-Ecosystem/` aufbauen
- ⏳ **Weitere Architektur-Diagramme** - Message-Flow, Registry-Model
- 📋 **Details:** [Chat-A Aktivitäten](docs/07-analysis/chat-activities/chat-a-architecture-2025-09-23.md)

### 🔧 **Chat-B: Code & Implementation**
- ✅ **APS Overview Tab 75% funktionsfähig** - Kundenaufträge, Rohmaterial, Lagerbestand
- 🔄 **Sensor-Daten Integration implementiert** - 6 Sensor-Panels mit echten MQTT-Daten (BME680, LDR, Kamera) - **NOCH NICHT GETESTET**
- ✅ **APS Dashboard Integration systematisch vorantreiben** - APS Overview implementiert
- ⏳ **Sensor-Daten Integration testen** - Mit realer Fabrik validieren (HÖCHSTE PRIORITÄT)
- ⏳ **APS Configuration Tab implementieren** - Fehlender 5. Tab
- ⏳ **Alle APS-Commands testen** - Systematische Validierung
- 📋 **Details:** [Chat-B Aktivitäten](docs/07-analysis/chat-activities/chat-b-implementation-2025-09-23.md)

### 🧪 **Chat-C: Testing & Validation**
- ⏳ **Sensor-Daten Integration testen** - APS Overview Tab mit realer Fabrik validieren (HÖCHSTE PRIORITÄT)
- ⏳ **OMF-Dashboard mit realer Fabrik testen** - Validierung der APS-Integration
- ⏳ **Cross-Platform Testing** - Windows + VSCode für Mermaid
- ⏳ **Template-Analyzer reparieren** - Topics aus Template-Deskriptionen entfernen
- ⏳ **Integration-Struktur testen** - Ob neue Komponenten-Namen funktionieren
- 📋 **Details:** [Chat-C Aktivitäten](docs/07-analysis/chat-activities/chat-c-testing-2025-09-23.md)

## 🚀 Entwicklungsphasen (High-Level)

### **Phase 0: APS as-is lauffähig machen**
- **Status:** ✅ Abgeschlossen
- **Ziel:** Fischertechnik-Fabrik funktionsfähig
- **Erreicht:** APS-CCU, APS-NodeRED, APS-Module laufen

### **Phase 1: APS-Komponenten verstehen** 
- **Status:** ✅ Abgeschlossen
- **Ziel:** APS-CCU und APS-NodeRED analysieren
- **Erreicht:** Session Manager, OMF-Dashboard, APS-Integration

### **Phase 2: OMF-CCU etablieren**
- **Status:** 🔄 In Bearbeitung (Chat-A: Architektur ✅, Chat-B: Code 🔄)
- **Ziel:** OMF-CCU im OMF-Dashboard implementieren
- **Fortschritt:** Namenskonvention etabliert, System-Context aktualisiert, APS Overview Tab implementiert (noch nicht getestet)

### **Phase 3: OMF-NodeRED etablieren**
- **Status:** ⏳ Geplant
- **Ziel:** OMF-NodeRED im OMF-Dashboard implementieren
- **Nächste Schritte:** APS-NodeRED Funktionalität ersetzen

## 🔄 **Chat-B Fortschritt: Sensor-Daten Integration implementiert**

### **✅ Was Chat-B implementiert hat:**
- **APS Overview Tab erweitert** - 6 Sensor-Panels hinzugefügt (BME680, LDR, Kamera)
- **MQTT-Integration** - Echte MQTT-Daten für Sensoren implementiert
- **Fallback-Mechanismus** - Mock-Daten bei MQTT-Fehlern
- **Dokumentation** - `docs/07-analysis/sensor-data-integration-complete.md`

### **⚠️ Was noch fehlt:**
- **Testing mit realer Fabrik** - Sensor-Daten Integration noch nicht validiert
- **MQTT-Topics verifizieren** - Ob die implementierten Topics korrekt sind
- **Real-time Updates testen** - Ob die OMF-Standard MQTT-Pattern funktionieren

### **🎯 Nächste Chat-B Prioritäten:**
1. **Sensor-Daten Integration testen** - Mit realer Fabrik validieren
2. **APS Configuration Tab** - Fehlender 5. Tab implementieren
3. **Alle APS-Commands testen** - Systematische Validierung

## 📋 Nächste Schritte (Prioritätenliste)

### **🔧 Code & Implementation**
1. **APS Configuration Tab implementieren** - Fehlender 5. APS Tab systematisch aufbauen
2. **Alle APS-Commands testen und validieren** - Systematische Überprüfung aller implementierten Befehle
3. **Original APS-Dashboard vollständig analysieren** - Alle Tabs, alle Funktionen, alle Commands
4. **Authentische APS-Integration** - Nicht nur oberflächlich, sondern vollständig funktional
5. **Manager-Duplikate beseitigen** - OrderManager (3x identisch), System-Status-Manager (3x ähnlich) auslagern in `omf/dashboard/managers/`
6. **APS-Tabs Registry-Analyse** - Welche APS-Tabs sind für unsere Steuerung tatsächlich notwendig?
7. **APS-Tabs Registry-Integration** - Verbleibende APS-Tabs auf Registry-Manager umstellen
8. **Registry-Konsolidierung** - Legacy-Konfiguration (`omf/config/`) entfernen, alle Manager auf Registry umstellen
9. **WorkpieceManager implementieren** - `nfc_config.yml` → `registry/model/v1/workpieces.yml` Migration
10. **OMF-Dashboard Tab-Konsolidierung** - APS-Tabs in vorhandene OMF-Tabs integrieren, unnötige Tabs entfernen

### **🧪 Testing & Validation**
8. **Sensor-Daten Integration testen** - APS Overview Tab mit realer Fabrik validieren (HÖCHSTE PRIORITÄT)
9. **OMF-Dashboard mit realer Fabrik testen** - Validierung der APS-Integration
10. **Template-Analyzer reparieren** - Topics aus Template-Deskriptionen entfernen
11. **Cross-Platform Testing** - Windows + VSCode für Mermaid

### **📚 Architektur & Dokumentation**
11. **Architektur-Dokumentation** an APS-Analyse-Ergebnisse anpassen - As-Is (FT APS) vs. To-Be (ORBIS) Strategie
12. **Node-RED Simulation** im Dashboard vorbereiten
13. **Direction-Klärung mapping.yml** - Aus Sicht welcher Komponente? (CCU oder NodeRED)

### **👥 User & Rollen**
14. **OMF-Dashboard User-Konzept definieren** - Standard-User vs. DSP-Admin Rollen
15. **APS-UI Bereich isolieren** - Standard-User sieht nur APS-Bedienung
16. **DSP-Steuerungsbereich implementieren** - DSP-Admin sieht Node-RED-Simulation Tabs
17. **Node-RED-Simulation Tabs erstellen** - DSP-Steuerung für OT-Übernahme
18. **User-Rollen-System implementieren** - Default vs. DSP-Admin Sichtbarkeit
19. **I18n Unterstützung** implementieren (EN, DE, FR)

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
- **APS-Analyse:** `docs/07-analysis/mqtt/`
- **APS Dashboard Integration Status:** `docs/07-analysis/aps-dashboard-integration-status.md`
- **APS Overview Implementation Status:** `docs/07-analysis/aps-overview-implementation-complete.md`

---

**Status:** Projekt läuft erfolgreich, APS Dashboard Integration in systematischer Weiterentwicklung 🔄
