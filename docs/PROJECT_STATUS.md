# ORBIS Modellfabrik - Projekt Status

**Letzte Aktualisierung:** 24.09.2025  
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
- ✅ **Integration-Struktur angepasst** - TXT-Module umorganisiert (TXT-DPS, TXT-FTS, TXT-AIQS)
- ✅ **Dokumentations-Struktur bereinigt** - Namenskonvention vereinheitlicht, Legacy-Ordner entfernt
- ✅ **Cursor-Agent-Struktur-Plan aktualisiert** - Vollständig konsistent mit tatsächlicher Struktur
- ✅ **APS-Ecosystem dokumentiert** - Phase 0 "as IS" System-Übersicht erstellt
- ✅ **APS-CCU README erstellt** - Herz der Fabrik als zentrale Steuerungseinheit
- ✅ **Doku-Leichen bereinigt** - Redundante Dokumente gelöscht, Verlinkungen korrigiert
- ✅ **User-Rollen-System dokumentiert** - Operator, Supervisor, Admin Rollen in Architektur integriert
- ✅ **Veraltete Component-Dokumentation bereinigt** - Abschnitte 4-7 aus omf-dashboard-architecture.md entfernt
- ✅ **Architektur-Bereinigung abgeschlossen** - Verifikations-Warnungen entfernt, Mermaid-Diagramme standardisiert, Verlinkungen korrigiert, Namenskonventionen geprüft, redundante Dokumente bereinigt
- 📋 **Neue Aufgabe:** **Component-Dokumentation nach Implementierung** - Dokumentation des tatsächlichen "Ablaufs" nach Implementierung oder nach Klarstellung der Implementierung
- 📋 **Details:** [Chat-A Aktivitäten](docs/07-analysis/chat-activities/chat-a-architecture-cleanup-2025-09-25.md)

### 🔧 **Chat-B: Code & Implementation**
- ✅ **APS Overview Tab implementiert** - Kundenaufträge, Rohmaterial, Lagerbestand, Sensor-Daten
- ✅ **Registry-Konsolidierung abgeschlossen** - Alle Legacy-Konfigurationen zu Registry migriert, 5 neue Manager implementiert
- ✅ **Message Center Modul-Filter implementiert** - HBW, DPS, DRILL, MILL, AIQS, CHRG, FTS mit Registry-basierter Filterung
- ✅ **Session State Integration** - Alle Filter verwenden eindeutige Keys für Persistenz
- ✅ **Component-Strukturierung abgeschlossen** - User-Konzept umgesetzt: operator/, supervisor/, admin/ Verzeichnisse
- ✅ **Component-Bereinigung erfolgreich** - 22 ungenutzte Components identifiziert und gelöscht
- ✅ **Logger-Standardisierung** - Alle Components mit konsistenten omf.* Logger-Pfaden
- ✅ **Import-Standardisierung** - Alle relativen Imports zu absoluten Imports geändert
- ✅ **Factory Reset im Header** - Funktional implementiert mit MQTT-Gateway
- ✅ **MQTT Connection-Loop Problem gelöst** - Strenge Environment-Prüfung implementiert
- ✅ **Pre-commit Hooks** - st.rerun() und MQTT Connection-Loop Prevention
- ⏳ **User Konzept umsetzen** - Rollenbasierte Tab-Sichtbarkeit implementieren (NÄCHSTE PRIORITÄT)
- ⏳ **APS Configuration Tab implementieren** - Fehlender 5. Tab
- 📋 **Details:** [Chat-B Aktivitäten](docs/07-analysis/chat-activities/chat-b-implementation-2025-09-23.md)

### 🧪 **Chat-C: Testing & Validation**
- ✅ **OMF-Dashboard Testing abgeschlossen** - Umfassendes Testing mit realer Fabrik durchgeführt
- ✅ **15 kritische Probleme identifiziert** - Vollständige Liste der nicht funktionierenden Bereiche
- ✅ **Testing-Protokoll erstellt** - Detaillierte Dokumentation aller Tests und Ergebnisse
- 📋 **Details:** [Chat-C Testing-Protokoll](docs/07-analysis/chat-activities/chat-c-testing-2025-09-25.md)

### 🔧 **Chat-D: Fix aus Testing-Session**
- [ ] **🚨 KRITISCH: APS-Modul-Status reparieren** - Status-Nachrichten werden nicht verarbeitet
- [ ] **🚨 KRITISCH: Replay Station Reconnects beheben** - Regression (war schon gefixed)
- [ ] **🚨 KRITISCH: APS Orders Tab implementieren** - Große Baustelle: Nachrichten auswerten
- [ ] **Kamera-Controls implementieren** - hoch, rechts, runter etc. mit 10-Grad-Schritten
- [ ] **Kamera-Button-Problem lösen** - 2x-Klick-Problem beheben
- [ ] **Bild-machen implementieren** - Kamera-Aufnahme-Funktion
- [ ] **Bild-Anzeigen implementieren** - Aufgenommene Bilder anzeigen
- [ ] **APS Processes Controls implementieren** - "add Step", "save workflow"
- [ ] **Modal Auto-Close implementieren** - Modal sollte sich nach erfolgreichem Command schließen
- [ ] **APS Configuration Icons reparieren** - Factory Layout Icons werden nicht gefunden
- [ ] **APS Configuration Bearbeitung implementieren** - Abschnitt noch nicht implementiert
- [ ] **Layout-Probleme beheben** - Controls nach unten, aktueller Prozess oben
- [ ] **Factory Layout I18n-Konflikt beheben** - I18n-Unterstützung verursacht Darstellungsfehler
- [ ] **I18n-Übersetzung erweitern** - Nur Hauptkomponenten übersetzt
- [ ] **Template-Analyzer reparieren** - Topics aus Template-Deskriptionen entfernen



## 📋 BACKLOG

### **🔧 Code & Implementation**

2. **APS Order Tab implementieren** - Tab systematisch aufbauen
3. **Alle APS-Commands testen und validieren** - Systematische Überprüfung aller implementierten Befehle
4. **Manager-Duplikate beseitigen** - OrderManager (3x identisch), System-Status-Manager (3x ähnlich) auslagern
5. ✅ **Registry-Konsolidierung** - Legacy-Konfiguration (`omf/config/`) entfernen, alle Manager auf Registry umstellen
6. ✅ **Message Center Modul-Filter** - HBW, DPS, DRILL, MILL, AIQS, CHRG, FTS mit Registry-basierter Filterung implementiert

### **🧪 Testing & Validation**
6. **OMF-Dashboard mit realer Fabrik testen** - Validierung der APS-Integration
7. **Template-Analyzer reparieren** - Topics aus Template-Deskriptionen entfernen
8. **Cross-Platform Testing** - Windows + VSCode für Mermaid

### **📚 Architektur & Dokumentation**
9. **Weitere Architektur-Diagramme** - Message-Flow, Registry-Model
10. **Architektur-Dokumentation** an APS-Analyse-Ergebnisse anpassen

### **🔍 TXT-Controller Analyse (Niedrige Priorität)**
16. **TXT-AIQS tiefere Analyse** - AI Quality System: Funktionsanalyse, MQTT-Topics, Image Recognition Workflow, Quality Control Process Mapping
17. **TXT-DPS tiefere Analyse** - Delivery and Pickup Station: Browser-Interface erkunden, Code-Analyse, Integration testen
18. **TXT-FTS tiefere Analyse** - FTS Steuerung: VDA 5050-Implementierung verifizieren, Node-RED Flows analysieren, OPC-UA Kommunikation dokumentieren

### **🏭 APS-CCU Dokumentation (Mittlere Priorität)**
19. **APS-CCU tiefere Analyse** - Central Control Unit: Docker-Container analysieren, Node-RED Flows dokumentieren, Dashboard-Integration testen, OMF-Integration vorbereiten

### **👥 User & Rollen**
24. **I18n Unterstützung** implementieren (EN, DE, FR)
- **Rollenbasierte Tab-Sichtbarkeit implementieren**
  - **Operator (APS-Business-User):** APS Overview, APS Orders, APS Processes, APS Configuration, APS Modules
  - **Supervisor (Werksleiter/DSP-User):** WL Module Control, APS Control
  - **Admin (System-Admin):** Steering, Message Center, Logs, Settings
- **Tab-Filterung basierend auf User-Rolle**
- **Session State für User-Rolle**

#### **✅ Abgeschlossen:**
- ✅ **Sprint-Dokumentation** erstellen (sprint_01 bis sprint_05)
- ✅ **PROJECT_OVERVIEW.md** zu statischer Dokumentation umwandeln
- ✅ **Doku Overkill vermeiden** - docs aufräumen und konsolidieren
- ✅ **Mermaid Doku** - Hybrid-Ansatz mit `docs/_shared/diagrams/` implementiert
- ✅ **Mermaid Diagramme vollständig implementieren** - Dokumentation reorganisiert und committed
- ✅ **Hybrid-Ansatz für Diagramm-Organisation** - `docs/_shared/diagrams/` als zentrale Bibliothek
- ✅ **Pre-commit und Git/GitHub Workflow** - Projekt so anpassen dass pre-commit und git/github Workflow funktioniert
- ✅ **Session Analyse Helper App** dokumentieren - technische Beschreibung und HowTo-Nutzung
- ✅ **Registry-Konsolidierung** - Alle Legacy-Konfigurationen zu Registry migriert, 5 neue Manager implementiert (Commit: 74ddf51)

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

### **🔧 TECHNISCHE PRIORITÄTEN:**
- **Sensor-Daten Integration testen** - Mit realer Fabrik validieren
- **Alle APS-Commands testen** - Systematische Validierung
- **Manager-Duplikate beseitigen** - OrderManager (3x), System-Status-Manager (3x)

### **🌐 ZUKUNFTSPLANUNG:**
- **I18n (EN, DE, FR) umsetzen** - Internationalisierung
- **Weitere Architektur-Diagramme** - Message-Flow, Registry-Model

## 📊 Sprint-Status

### Sprint 05 (18.09 - 01.10.2025) - **AKTUELL**
- **Status:** In Bearbeitung
- **Fokus:** Component-Strukturierung und User-Konzept Vorbereitung
- **Erreicht:** APS Dashboard vollständig in OMF-Dashboard integriert, Component-Bereinigung abgeschlossen
- **Nächste Schritte:** User-Konzept umsetzen (Rollenbasierte Tab-Sichtbarkeit), Sprint-Dokumentation

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
- **APS-Analyse:** `docs/06-integrations/mosquitto/`
- **APS Dashboard Integration Status:** `docs/07-analysis/aps-dashboard-integration-status.md`
- **APS Overview Implementation Status:** `docs/07-analysis/aps-overview-implementation-complete.md`

---

**Status:** Projekt läuft erfolgreich, APS Dashboard Integration in systematischer Weiterentwicklung 🔄
