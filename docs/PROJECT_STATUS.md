# ORBIS Modellfabrik - Projekt Status

**Letzte Aktualisierung:** 18.12.2025
**Aktueller Status:** OSF (vormals OMF3) UI-Finishing & Kunden-Demos; OMF2 als Legacy eingefroren

## 📋 Wichtige Erkenntnisse (Session-Notizen)

### AIQS-Kamera-Daten Analyse (17.12.2025)
- **Erkenntnis:** AIQS-Kamera-Daten (Photos von Workpieces) werden **NICHT über MQTT** übertragen
- **Analyse:** `production_order_white_20251110_184459.log` Session vollständig analysiert
- **Ergebnis:** 
  - ❌ Keine Bilddaten in `module/v1/ff/SVR4H76530/state` Payloads
  - ❌ Keine separaten Kamera-Topics für AIQS gefunden
  - ✅ CHECK_QUALITY Commands enthalten nur `type` und `workpieceId` in Metadata
- **Lösung:** Direkter HTTP-Zugriff auf TXT-Controller erforderlich
  - **TXT-AIQS IP:** 192.168.0.103 (DHCP, kann variieren)
  - **Web-Interface:** Port 80
  - **API-Endpoint:** Muss noch ermittelt werden (TXT Controller Web-Interface prüfen)
- **Referenz:** `docs/06-integrations/00-REFERENCE/module-serial-mapping.md` für Serial → IP Mapping

> **Dokumentations-Strategie:** Dieses Dokument bündelt Projektstatus, Roadmap und Sprint-History; für Release-Versionen nutzen wir SemVer + die separate CHANGELOG.md.

## 🚀 Aktuelle Arbeiten (Dezember 2025)

### ✅ OSF Kern stabil
- Angular + Nx Workspace, MQTT/Gateway/Business/Entities Libraries sowie CCU-UI Grundrahmen sind produktionsreif und dienen als stabile Basis für Kunden-Demos.
- MessageMonitorService, Tab Stream Pattern, i18n Runtime Switching und CI/CD-Pipeline laufen zuverlässig; OMF2 bleibt als Legacy-Referenz bestehen.

### 🔄 Laufende Schwerpunkte
- **Module-/Shopfloor-Tab** wird zum zentralen Einstiegspunkt ausgebaut: Status-Tiles pro Modul, Sequenz-Kommandos, HBW-Lageransicht und konsistentes UX-Pattern für weitere Tabs (AGV, Konfiguration).
- **DSP-Storytelling**: Responsive `dsp-responsive-mockup.svg`, MC/EDGE-Animation mit gestaffelten Highlights sowie interaktive Verlinkungen vom DSP-Layer zu OSF-Ansichten.
- **Remote Demo Pipeline**: OBS/Teams Setup mit Konftel Cam50, Video- und Präsentationsmodus für Kunden (z. B. Gedore) inkl. DSP-Animationen.
- **OSF Rebranding & Migration**: Umbenennung von OMF3 → OSF, Vorbereitung des Azure DevOps Repos und Docker-basierten Deployments (Hilcher-Box/RPi) als Teil des DSP-Kastens.

## 📅 Externe Events (Q4 2025)

### DSP-Kundentag @ Bostalsee (03.–04.12.) – ✅ Abgeschlossen
- 03.12.: Aufbau & Test der Fischertechnik-Modellfabrik (FMF) vor Ort, Abgleich der DSP-Story mit aktueller OSF-Version.
- 04.12.: Live-Demo der OSF (Shopfloor, Module-Tab, DSP-Animation) gegenüber DSP-Kundenkreis; Feedback floss in die aktuellen UI-Todos ein.
- Status DSP-Event: Erfolgreich abgeschlossen, Assets (Slides, OBS-Szenen, Videos) sind referenzfähig für weitere Kunden.

### Kundenpräsentation Gedore (Dezember) – 🔄 In Arbeit
- Aufbau eines dedizierten OBS-/Teams-Setups inkl. Konftel Cam50, dedizierter Video- und DSP-Animationssequenzen.
- Erstellung kundenspezifischer DSP-Animationen (Edge/Device Layer, Prozessketten) sowie Abstimmung der Moderationsstory.
- Nachbereitung: Weitere Animationen & Linking-Konzepte, die direkt in OSF integriert werden.

## 📦 Plattformzustand

### OSF Application Stack (2025)
- Angular + Nx Workspace mit klar getrennten Libraries (MQTT, Gateway, Business, Entities) bildet den Kern.
- CCU-UI liefert Tabs für Module, Orders, Track&Trace, AGV sowie spezialisierte Ansichten (Message Monitor, DSP, Process).
- State-Handling basiert auf MessageMonitorService + Tab Stream Pattern (BehaviorSubjects, Circular Buffer, localStorage Persistence).
- Tooling: Nx, Jest, ESLint, Storybook-Fallback, CI/CD via GitHub Actions, SemVer + CHANGELOG.

### Legacy Referenz (FMF / OMF2)
- OMF2 bleibt eingefroren als Dokumentationsbasis für Registry-Modelle und Topic-Schemas.
- Node-RED/APS-Analysen liegen archiviert vor; Migrationswissen wird nur noch bei Bedarf referenziert.

## 📋 Nächste Schritte (Roadmap Q1 2026)

1. **Shopfloor UX Refresh** – Module-Tab als Startpunkt (Status-Kacheln, Sequenz-Controls, HBW-Lager) und konsistente Layouts für AGV & Konfiguration.
2. **Process & DSP Story** – Neuer Process-Tab für Geschäftsprozesse (Customer Order, Purchase Order, Production, Storage) plus erweitert animierte DSP-Kette.
3. **Interaktive Verlinkungen** – DSP-Architektur klickbar (AGV → AGV-Tab, Devices → Modules, ERP → Process) inkl. gestaffelter Edge-Animation.
4. **OSF Rebranding & Migration** – Repos/Wording von OMF3 → OSF, Vorbereitung Azure DevOps Mirror, Containerisierung für Hilcher/RPi.
5. **Demo Excellence** – OBS/Teams Playbooks, kundenspezifische Animationen (Gedore), Blog-Serie zu OSF & DSP zur Lead-Generierung.

## 📝 Offene Todos
1. ✅ **Module-Tab Status-Erweiterung** – Copilot/PR-Statusleisten (AIQS/DPS) in `omf3/apps/ccu-ui` übernehmen, Komponenten generalisieren und für HBW/DRILL/MILL identische Detailbereiche bereitstellen. **(Erledigt: 18.12.2025)**
2. ✅ **Sequence Commands bündeln** – Sequenzlisten für AIQS/DRILL/MILL in ein gemeinsames Collapsible-Panel am unteren Rand verschieben (Accordion-Komponente + konsistente Beschriftung). **(Erledigt: 18.12.2025)**
3. **HBW Lageransicht** – Lagerstände/Slots darstellen im Modules-Tab, sobald HBW selektiert ist. HBW ist per default selektiert. (z. B. 3x3 Grid-Darstellung)  Vergleich mit Stock-Darstellung aus overview-Tab. GGf ist es ausreichend, die Inventory-Section mit Stock-Info beim Modules-Tab mit Selektion von HBW darzustellen. Verpacken der Darstellung in eine "Struktur", die resizable ist und in das übrige Angular-Design passt. Die Komponente könnte angepasst werden, so dass auch die Einzelnen Lagerplätze nicht unbedingt, die dort angebenen Größe von (ca 120-160px haben muss). 
4. **Shopfloor-Benennung** – Module-Tab in der UI/Navigation zu „Shopfloor“ umbenennen und Dokumentation/Tooltips anpassen, damit er als Einstiegspunkt wahrgenommen wird. Der Shopdfloor wird dann an Position 2 der Navigatiosleiste verschoben. (Overview-Tab wird ggf durch TASK 8 Obsolet, da dann alle Info anders angeordnet wird und auf andere Tabs verteilt wird, so dass eine logische Abfolge resultiert.) Neue Logos für Module und Digital Twin, sowie Anzeige der Commands in Module-Tab mit den SVGs für drop-event, pick-event und process-event.
5. **Konfigurations-Tab Layout** – Shopfloor-Layout links, Module rechts; bei kleiner Breite Modulbereich nach unten umbrechen (CSS Grid/Flex + Angular Breakpoints). (Diese Vorgehen soll für alle Tabs gelten, bei denen wir shopfloor-Laxyout verwenden)
6. **AGV-Tab Reflow** – Layout an Module(=Shopfloor)/Konfiguration angleichen: links Route & Live-Position, rechts Status, Actions, Load-Info, Commands.
7. **DSP Edge Animation** – Animationssequenz überarbeiten (MC-Funktionen → EDGE xyz_2 verlinken → xyz_1/3 ergänzen → alle drei gestrichelt highlighten) als Grundlage fürs OSF/DSP-Logo.
8. **Process-Tab Neuaufbau** – Geschäftsprozesse (Customer Orders, Purchase Orders, Production, Storage) mit Swimlanes/Karten darstellen; dient als Customer und Purchase Order ERP-Brücke. PRODUCTION und STORAGE ORder als Shopfloor Prozesse aus ERP gesteuert)
9. **Orders-Tab Klarstellung** – Tab in „Shopfloor Orders“ umbenennen, Finished-Liste per Default eingeklappt, letzter Auftrag automatisch expandiert.
10. **DSP → AGV Link** – Klick auf AGV/FTS-Icon führt Nutzer direkt zum AGV-Tab (Router-Link + Tracking).
11. **DSP → Modules Link** – Klick auf Device im DSP-Architektur responsive Darstellung setzt Module-Tab mit vorselektiertem Device (QueryParam/State Transfer, 1:1 Zuordnung).
12. **DSP → ERP Link** – Klick auf BP-ERP öffnet neuen Process-Tab (Purchase/Customer Orders) und zeigt ERP-Bezug.
13. **OSF Rebranding** – Bezeichner OMF3 → OSF in Code, Assets, Doku; Angular Prefixes, ENV Variablen und README angleichen.
14. **Azure DevOps Migration** – Mirror/Move Repository inkl. Pipelines nach ORBIS Azure DevOps, Rechte & Secrets definieren.
15. **OSF Deployment & Storytelling** – Docker-Setup für Hilcher-Box/RPi abschließen, anschließende Blog-Serie zu OSF & DSP Story vorbereiten.
16. **AIQS-Kamera-Integration (sf-system)** – Anzeige der Information aus der AIQS-Station: Photo des Workpieces. AIQS-Kamera-Daten werden nicht über MQTT übertragen, sondern müssen direkt vom TXT-Controller (IP: 192.168.0.103) via HTTP abgerufen werden. Integration in Module-Tab bei AIQS-Auswahl. API-Endpoint muss noch ermittelt werden (TXT Controller Web-Interface prüfen, Python-Code in `integrations/TXT-AIQS/lib/camera.py` analysieren).

**Letzte Aktualisierung:** 18.12.2025

## 📊 Sprint-Vorgehen

### **Sprint-Strategie:**
- **2-Wochen-Zyklen** für kontinuierliche Entwicklung
- **PROJECT_STATUS.md** = Zentrale Change-Dokumentation
- **Sprint-Dokumentation** = Detaillierte Rückblicke in `docs/sprints/`
- **SemVer + CHANGELOG.md** = Release-Historie bleibt separat nachvollziehbar

### **Change-Management:**
- **Alle Änderungen** werden hier dokumentiert
- **Sprint-Status** wird kontinuierlich aktualisiert
- **Wichtige Entscheidungen** in `docs/03-decision-records/`

## 📊 Sprint-Status

### Sprint 11 (12.12 - 24.12.2025) - **AKTUELL**
- **Status:** In Bearbeitung
- **Fokus:** Gedore Remote-Präsentation, DSP-Animationen, OBS/Teams Playbook, Module-Tab UX.
- **Erreicht:** Konftel Cam50 Settings + OBS-Doku aktualisiert, DSP-Mockup interaktiv geplant, Todo-Backlog priorisiert. Module-Tab Status-Erweiterung abgeschlossen (DPS/AIQS/HBW/DRILL/MILL mit einheitlicher Struktur, Workpiece-Informationen integriert, Sequence Commands gebündelt).
- **In Arbeit:** DSP-Links (AGV/Devices/ERP), Process-Tab Konzept, kundenspezifische Animationen.

### Sprint 10 (28.11 - 11.12.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** DSP-Kundentag Bostalsee, Module-Tab Feinschliff, Responsive DSP-Mockup, Rebranding-Plan.
- **Erreicht:** Aufbau/Test FMF vor Ort, Live-Demo OSF + DSP, `dsp-responsive-mockup.svg` erstellt, OBS Pipeline stabilisiert.
- **Nachlauf:** Feedback aus DSP-Event in Todo-Liste übernommen.

### Sprint 09 (13.11 - 27.11.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF3 Integration, MessageMonitorService, UI-Verbesserungen, Messevorbereitung.
- **Erreicht:** MessageMonitorService, I18n Runtime Switching, CI/CD Umstellung, Message Monitor Tab, Tab Stream Pattern, Shopfloor-Highlighting, MQTT-Verbindungsstatus.
- **Outcome:** Grundlage für OSF-Demos geschaffen, Messeunterlagen vorbereitet.

### Sprint 08 (30.10 - 12.11.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Asset-Management Refactoring, Sprachprüfung, OMF3 Entwicklung Start
- **Erreicht:** Asset-Management konsolidiert, Sprachprüfung abgeschlossen, OMF3 Grundstruktur aufgebaut (Angular + Nx Workspace, MQTT-Client, Gateway, Business, Entities, CCU-UI Skeleton)
- **Meilenstein:** OMF3 Grundstruktur steht ✅

### Sprint 07 (16.10 - 29.10.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF2-Refactoring und Architektur-Migration
- **Erreicht:** Drei-Schichten-Architektur, Registry Manager, Gateway-Routing, Business Manager, Production Order Manager, Storage Orders Logic, i18n-System, Best Practice Logging, 341/341 Tests
- **Meilenstein:** OMF2 ist produktionsreif und demo-fähig ✅

### Sprint 06 (02.10 - 15.10.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OMF2-Refactoring und Architektur-Migration
- **Erreicht:** Drei-Schichten-Architektur, Registry Manager, Gateway-Routing, Business Manager, Production Order Manager, Storage Orders Logic, i18n-System, Best Practice Logging, 341/341 Tests

### Sprint 05 (18.09 - 01.10.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Component-Strukturierung und User-Konzept Vorbereitung
- **Erreicht:** APS Dashboard vollständig in OMF-Dashboard integriert, Component-Bereinigung abgeschlossen

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
- **OMF3 Architektur** Angular + Nx Workspace für moderne Frontend-Entwicklung
- **Library-Struktur** Getrennte Libraries für MQTT, Gateway, Business, Entities
- **Tab Stream Pattern** Zwei Patterns für konsistente Dateninitialisierung
- **MessageMonitorService** Persistence-Strategie (localStorage, keine Camera-Daten)
- **I18n Runtime** URL-basierte Locale-Routing für bessere UX
- **CI/CD** Vollständige Umstellung auf OMF3 Tests

### **Technische Meilensteine:**
- **OMF3 Architektur** Angular + Nx Workspace etabliert
- **Library-Struktur** MQTT-Client, Gateway, Business, Entities implementiert
- **MessageMonitorService** State Persistence mit BehaviorSubject + CircularBuffer
- **I18n Runtime** URL-basierte Locale-Routing ohne Reload
- **CI/CD** Vollständige Umstellung auf OMF3 Tests
- **Tab Stream Pattern** Konsistente Dateninitialisierung dokumentiert und getestet
- **UI-Polish** Konsistente Highlighting und Status-Anzeigen

## 🔗 Wichtige Links

- **Aktuelle Sprint-Dokumentation:** `docs/sprints/`
- **Decision Records:** `docs/03-decision-records/`
- **Architektur:** `docs/02-architecture/`
- **OMF3 README:** `omf3/README.md`
- **APS-Analyse:** `docs/06-integrations/`

---

**Status:** OSF Entwicklung läuft erfolgreich; OMF2/FMF bleibt nur noch als Legacy-Referenz bestehen 🎯
