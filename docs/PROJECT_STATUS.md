# ORBIS Modellfabrik - Projekt Status

**Aktueller Status:** OSF (vormals OMF3) UI-Finishing & Kunden-Demos; OMF2 als Legacy eingefroren

> **Dokumentations-Strategie:** Dieses Dokument bündelt Projektstatus, Roadmap und Sprint-History; für Release-Versionen nutzen wir SemVer + die separate CHANGELOG.md.

## 🚀 Aktuelle Arbeiten (Januar 2026)

### ✅ OSF Kern stabil
- Angular + Nx Workspace, MQTT/Gateway/Business/Entities Libraries sowie OSF-UI Grundrahmen sind produktionsreif und dienen als stabile Basis für Kunden-Demos.
- MessageMonitorService, Tab Stream Pattern, i18n Runtime Switching und CI/CD-Pipeline laufen zuverlässig; OMF2 bleibt als Legacy-Referenz bestehen.

### ✅ Abgeschlossene Schwerpunkte (Sprint 11)
- **Shopfloor-Tab** ist zentraler Einstiegspunkt: Status-Tiles pro Modul, Sequenz-Kommandos, HBW-Lageransicht und konsistentes UX-Pattern für weitere Tabs (AGV, Konfiguration). ✅
- **DSP-Storytelling**: Responsive `dsp-responsive-mockup.svg`, MC/EDGE-Animation mit gestaffelten Highlights sowie interaktive Verlinkungen vom DSP-Layer zu OSF-Ansichten. ✅
- **Remote Demo Pipeline**: OBS/Teams Setup mit Konftel Cam50, Video- und Präsentationsmodus für Kunden (Gedore, DSP-Kundentag) inkl. DSP-Animationen. ✅
- **OSF Rebranding**: Umbenennung von OMF3 → OSF vollständig durchgeführt. ✅

### 🔄 Laufende Schwerpunkte (Sprint 12)
- **OSF Migration & Deployment**: Azure DevOps Migration, Docker-Setup für Hilcher-Box/RPi.
- **Angular-App Optimierung**: Resizing-Optimierung für Landscape/Portrait in OBS-Präsentationen.
- **AIQS-Kamera-Integration**: MQTT-Publikation und OSF-UI Integration (blockiert durch ROBO Pro Workflow).
- **Storytelling**: Blog-Serie zu OSF & DSP Story in Vorbereitung.

## 📅 Externe Events (Q4 2025)

### DSP-Kundentag @ Bostalsee (03.–04.12.) – ✅ Abgeschlossen
- 03.12.: Aufbau & Test der Fischertechnik-Modellfabrik (FMF) vor Ort, Abgleich der DSP-Story mit aktueller OSF-Version.
- 04.12.: Live-Demo der OSF (Shopfloor, Module-Tab, DSP-Animation) gegenüber DSP-Kundenkreis; Feedback floss in die aktuellen UI-Todos ein.
- Status DSP-Event: Erfolgreich abgeschlossen, Assets (Slides, OBS-Szenen, Videos) sind referenzfähig für weitere Kunden.

### Kundenpräsentation Gedore (16.12.2025) – ✅ Abgeschlossen
- Aufbau eines dedizierten OBS-/Teams-Setups inkl. Konftel Cam50, dedizierter Video- und DSP-Animationssequenzen.
- Erstellung kundenspezifischer DSP-Animationen (Edge/Device Layer, Prozessketten) sowie Abstimmung der Moderationsstory.
- Status Gedore-Präsentation: Erfolgreich abgeschlossen, kundenspezifische Animationen und OBS-Setup sind referenzfähig für weitere Kunden.

## 📦 Plattformzustand

### OSF Application Stack (2025)
- Angular + Nx Workspace mit klar getrennten Libraries (MQTT, Gateway, Business, Entities) bildet den Kern.
- CCU-UI liefert Tabs für Module, Orders, Track&Trace, AGV sowie spezialisierte Ansichten (Message Monitor, DSP, Process).
- State-Handling basiert auf MessageMonitorService + Tab Stream Pattern (BehaviorSubjects, Circular Buffer, localStorage Persistence).
- Tooling: Nx, Jest, ESLint, Storybook-Fallback, CI/CD via GitHub Actions, SemVer + CHANGELOG.

### Legacy Referenz (FMF / OMF2)
- OMF2 bleibt eingefroren als Dokumentationsbasis für Registry-Modelle und Topic-Schemas.
- Node-RED/APS-Analysen liegen archiviert vor; Migrationswissen wird nur noch bei Bedarf referenziert.

## 📋 Roadmap Q1 2026

### ✅ Abgeschlossen (Sprint 11, Dezember 2025)
1. ✅ **Shopfloor UX Refresh** – Module-Tab als Startpunkt (Status-Kacheln, Sequenz-Controls, HBW-Lager) und konsistente Layouts für AGV & Konfiguration. **(Erledigt: Sprint 11, Tasks 1-6)**
2. ✅ **Process & DSP Story** – Process-Tab für Geschäftsprozesse (Customer Order, Purchase Order, Production, Storage) plus erweitert animierte DSP-Kette. **(Erledigt: Sprint 11, Tasks 7-8)**
3. ✅ **Interaktive Verlinkungen** – DSP-Architektur klickbar (AGV → AGV-Tab, Devices → Modules, ERP → Process) inkl. gestaffelter Edge-Animation. **(Erledigt: Sprint 11, Tasks 10-12)**
4. ✅ **OSF Rebranding** – Repos/Wording von OMF3 → OSF vollständig durchgeführt. **(Erledigt: Sprint 11, Task 13)**

### 🔄 In Arbeit / Geplant
4. ⏳ **OSF Migration & Deployment** – Azure DevOps Mirror, Containerisierung für Hilcher/RPi. **(In Arbeit: Tasks 19-20)**
5. ⏳ **Demo Excellence** – OBS/Teams Playbooks erstellt, kundenspezifische Animationen (Gedore) abgeschlossen, Blog-Serie zu OSF & DSP in Vorbereitung. **(In Arbeit: Task 17)**

## 📝 Offene Todos
1. ✅ **Module-Tab Status-Erweiterung** – Copilot/PR-Statusleisten (AIQS/DPS) in `osf/apps/osf-ui` übernehmen, Komponenten generalisieren und für HBW/DRILL/MILL identische Detailbereiche bereitstellen. **(Erledigt: 18.12.2025)**
2. ✅ **Sequence Commands bündeln** – Sequenzlisten für AIQS/DRILL/MILL in ein gemeinsames Collapsible-Panel am unteren Rand verschieben (Accordion-Komponente + konsistente Beschriftung). **(Erledigt: 18.12.2025)**
3. ✅ **HBW Lageransicht** – Lagerstände/Slots darstellen im Modules-Tab, sobald HBW selektiert ist. HBW ist per default selektiert. (z. B. 3x3 Grid-Darstellung)  Vergleich mit Stock-Darstellung aus overview-Tab. GGf ist es ausreichend, die Inventory-Section mit Stock-Info beim Modules-Tab mit Selektion von HBW darzustellen. Verpacken der Darstellung in eine "Struktur", die resizable ist und in das übrige Angular-Design passt. Die Komponente könnte angepasst werden, so dass auch die Einzelnen Lagerplätze nicht unbedingt, die dort angebenen Größe von (ca 120-160px haben muss). 
4. ✅ **Shopfloor-Benennung** – Module-Tab in der UI/Navigation zu „Shopfloor“ umbenennen und Dokumentation/Tooltips anpassen, damit er als Einstiegspunkt wahrgenommen wird. Der Shopdfloor wird dann an Position 2 der Navigatiosleiste verschoben. (Overview-Tab wird ggf durch TASK 8 Obsolet, da dann alle Info anders angeordnet wird und auf andere Tabs verteilt wird, so dass eine logische Abfolge resultiert.) Neue Logos für Module und Digital Twin, sowie Anzeige der Commands in Module-Tab mit den SVGs für drop-event, pick-event und process-event.
5. ✅ **Konfigurations-Tab Layout** – Shopfloor-Layout links, Module rechts; bei kleiner Breite Modulbereich nach unten umbrechen (CSS Grid/Flex + Angular Breakpoints). (Diese Vorgehen soll für alle Tabs gelten, bei denen wir shopfloor-Layout verwenden) **(Erledigt: 19.12.2025)**
6. ✅ **AGV-Tab Reflow** – Layout an Module(=Shopfloor)/Konfiguration angleichen: links Route & Live-Position, rechts Status, Actions, Load-Info, Commands. **(Erledigt: 19.12.2025 - Layout bleibt wie es ist, da es sehr gut funktioniert)**
7. ✅**DSP Edge Animation** – Animationssequenz überarbeiten (MC-Funktionen → EDGE xyz_2 verlinken → xyz_1/3 ergänzen → alle drei gestrichelt highlighten) als Grundlage fürs OSF/DSP-Logo.
8. ✅**Process-Tab Neuaufbau** – Geschäftsprozesse (Customer Orders, Purchase Orders, Production, Storage) mit Swimlanes/Karten darstellen; dient als Customer und Purchase Order ERP-Brücke. PRODUCTION und STORAGE ORder als Shopfloor Prozesse aus ERP gesteuert). Implementiert als Akkordeon-Struktur mit zwei Hauptbereichen: "Beschaffungs-Prozess" (Purchase Orders + Storage Flow) und "Produktions-Prozess" (Customer Orders + Production Flow). Process-Tab an Position 3 in der Navileiste verschoben. **(Erledigt: 19.12.2025)**
9. ✅**Orders-Tab Klarstellung** – Tab an Position 4, Layout umgekehrt: Shopfloor links (3fr), Steps rechts (2fr) mit responsive Breakpoint bei 1200px. Shopfloor-Preview in jeder OrderCard links angezeigt (wie ursprünglich). Beschreibung angepasst: "Shopfloor-Aufträge" mit I18n-Keys für DE/FR. Finished-Liste per Default eingeklappt, bei Storage Orders wird der oberste Auftrag automatisch expandiert beim Expandieren der Finished-Liste. Aktive Orders bleiben immer expanded. **(Erledigt: 19.12.2025)**
10. ✅**DSP → AGV Link** – Klick auf AGV/FTS-Icon (sf-systems) im dsp-Tab führt Nutzer direkt zum AGV-Tab.
11. ✅**DSP → Modules Link** – Klick auf Device im DSP-Architektur responsive Darstellung setzt Module-Tab (shopfloor-Tab) mit vorselektiertem Device (QueryParam/State Transfer, 1:1 Zuordnung).
12. ✅ **DSP → ERP Link** – Klick auf BP-ERP öffnet den Process-Tab (Purchase/Customer Orders) und zeigt ERP-Bezug. Bei ausführen einer Purchase Order wird "fake-Info" zur Order angezeigt in einer ERP-BOX (Supplier-ID, Order-Amount (def. 1), Order-Date, planned delivery-Date). Bei Ausführen einer Customer-Order wird "fake-Info" angezeigt mit Customer-ID, ERP-Order-Number, Order-Amount (default = 1), Order-Date, planned delivery-date. -> Diese Info wird im Track-Trace-Scenario wieder aufgenommen und angezeigt. **(Erledigt: 20.12.2025 - ERP-Daten Verknüpfung, Order Status, zusätzliche Datenfelder, TURN LEFT/RIGHT Icons, i18n)**
13. ✅ **OSF Rebranding** – Bezeichner OMF3 → OSF in Code, Assets, Doku; Angular Prefixes, ENV Variablen und README angleichen. Sowie konsequente Umbenennung der tabs-Komponenten (module-tab → shopfloor-tab, fts-tab → agv-tab, wobei fts nur bei der deutschen Übersetzung und bei den topics die von außen vorgegeben sind erhalten bleibt). Die app wurde zu osf-ui umbenannt (anstatt ccu-ui). Die Änderungen wurden durch den ganzen Workspace bis in GIT und die dortige Verwaltung durchgezogen. **(Erledigt: 20.12.2025 - App-Umbenennung ccu-ui → osf-ui, Workspace-Umbenennung omf3 → osf, Komponenten-Umbenennung module-tab → shopfloor-tab und fts-tab → agv-tab, package.json name aktualisiert, wichtigste Dokumentation aktualisiert)**
14. ✅ **Dokumentation** Mal wieder aufräumen in den docs. **(Erledigt: 23.12.2025)**
   - ✅ **DSP-Architektur-Diagramme erstellt:**
     - `dsp-architecture-functional-view.svg` - Functional View mit allen Layern, Containern und Connections (Key-Namen statt Icons, L-Form Connections, bidirektional)
     - `dsp-architecture-edge-mc-functions.svg` - Edge & MC Functions Detailansicht
     - `dsp-architecture-component-view.svg` - Component View mit 8 Edge-Komponenten
     - `dsp-architecture-deployment-view.svg` - Deployment View mit 4 Pipeline-Steps
     - Alle Diagramme in `DSP_Architecture_Objects_Reference.md` eingebettet
   - ✅ **SVG-Inventory erstellt:**
     - `docs/02-architecture/dsp-svg-inventory.md` - Übersicht aller verfügbaren SVG-Assets (filtert bereits dokumentierte SVGs aus)
     - Generierungsscript: `scripts/generate-svg-inventory.js`
   - ✅ **Objects Reference aktualisiert:**
     - Business Applications erweitert (SCM, CRM hinzugefügt)
     - Device-Unterscheidung entfernt (alle Devices als verfügbar)
     - SVG-Tiles für alle Icon-Kategorien (Business, Edge Functions, MC Functions, Edge Components, Shopfloor Systems/Devices)
   - ✅ **HOWTO_ADD_CUSTOMER.md aktualisiert:**
     - FMF_CONFIG als Template empfohlen (statt Default-Config)
     - Pfade korrigiert (omf3/ccu-ui → osf/osf-ui)
     - Business Processes Liste erweitert (bp-scm, bp-crm)
   - ✅ **Dokumentation Cleanup abgeschlossen:**
     - `deployment-alternatives.md` aktualisiert (OMF3 → OSF, ccu-ui → osf-ui, GitHub Pages automatisch via CI/CD, Local Builds aus IDE, Docker/Rasp-Pi geplant)
     - `github-pages-deployment.md` aktualisiert (automatisches Deployment via GitHub Actions dokumentiert)
     - Alle OMF3/ccu-ui Referenzen in aktuellen Dokumentationen angepasst (build-commands-guide.md, analysis/README.md, publish-buttons-*.md, versioning.md, integration-testing-workflow.md)
     - Sprint-Dokumentationen und Archive-Dokumentationen bleiben unverändert (historische Namen beibehalten)
15. ✅ **OBS-Video** Testen und Aufbau der OBS-Video Präsentation auf Windows. **Status:** Dokumentation erstellt (`docs/04-howto/presentation/obs-video-presentation-setup.md`). OBS Studio Setup und Tests auf Windows abgeschlossen. **Dokumentation:** Vollständige Anleitung für OBS Studio Setup mit Teams-Integration, Szenen-Konfiguration, Kamera-Setup, Hotkeys und Operator-Checkliste vorhanden.
16. ✅ **Stations und OPC-UA-Module** Erweiterung der Konfiguration um Infos (aus omf2) **(Erledigt: 22.12.2025)**
   - `ModuleHardwareService` erstellt für Hardware-Konfiguration (OPC-UA Server, TXT Controller)
   - `modules_hardware.json` erstellt mit OMF2-Daten (englische Texte als Default)
   - Configuration Tab erweitert: Separate Sections für OPC-UA Server und TXT Controller mit Icons
   - Icons erstellt/angepasst: `opc-ua-server.svg`, `txt-controller.svg` (66% Größe der Station-Icons)
   - Sections werden nur angezeigt, wenn Hardware vorhanden ist
   - TXT Controller IPs als DHCP markiert (dynamisch vergeben)
   - i18n Keys für DE/FR hinzugefügt
   - Tests erstellt: `ModuleHardwareService` vollständig getestet, Configuration Tab Tests erweitert
17. ⏳ **Storytelling** – Blog-Serie zu OSF & DSP Story vorbereiten. **Status:** Blog-Serie konzipiert, Themen/Struktur vorbereitet. **Nächste Schritte:** Blog-Artikel erstellen und veröffentlichen.
18. ⏳ **AIQS-Kamera-Integration (sf-system)** – Anzeige der Kamera-Bilder von Workpieces aus der AIQS-Station. **Strategie (23.12.2025):** Kamera-Bilder über MQTT-Topic publizieren (nicht HTTP). **Topic-Format:** `/j1/txt/1/i/quality_check` (Quality-Check Bilder mit Result PASSED/FAILED). **Referenz-Implementierung:** TXT-DPS verwendet bereits MQTT-Kamera-Publikation (`/j1/txt/1/i/cam` mit Base64-Format, siehe `integrations/TXT-DPS/workspaces/FF_DPS_24V/lib/SSC_Publisher.py`). **TXT-AIQS Anpassung:** `lib/sorting_line.py` erweitert mit `publish_quality_check_image()` Funktion, publiziert Bilder nach Quality-Check (PASSED/FAILED) mit Base64-kodierten PNG-Bildern. **Status:** ✅ Source-Dateien vom TXT-Controller kopiert (`integrations/TXT-AIQS/workspaces/FF_AI_24V/`). ✅ HTTP-Ansatz verworfen, `AiqsCameraService` gelöscht (nicht verwendet). ✅ **ROBO Pro Coding Workflow etabliert** (06.01.2026): ROBO Pro Coding als primäre Deployment-Methode dokumentiert. Decision Record: `docs/03-decision-records/18-txt-controller-deployment.md`. How-To: `docs/04-howto/txt-controller-deployment.md`. Verzeichnis-Struktur: `vendor/fischertechnik/` (Originale), `integrations/TXT-{MODULE}/archives/` (Varianten), `integrations/TXT-{MODULE}/workspaces/` (Entpackte Versionen). ✅ **Archive erstellt** (07.01.2026): `FF_AI_24V_wav.ft` (Sound-Implementierung) und `FF_AI_24V_cam.ft` (Sound + Camera-Publikation) in `integrations/TXT-AIQS/archives/` erstellt. ⏳ **Nächste Schritte (Sprint 13):** 1) Deployment beider Varianten auf TXT-Controller, 2) Testing (Sound, Camera-Publikation), 3) OSF-UI Integration (Gateway `qualityCheckImages$` Stream, Topic-Abonnement `/j1/txt/1/i/quality_check`, Anzeige im AIQS-Tab/Shopfloor-Tab). **Referenz:** `docs/03-decision-records/18-txt-controller-deployment.md`, `docs/04-howto/txt-controller-deployment.md`, `integrations/TXT-AIQS/workspaces/FF_AI_24V_cam/lib/sorting_line.py` (Zeilen 168-193)
19. ⏳ **Azure DevOps Migration** – Mirror/Move Repository inkl. Pipelines nach ORBIS Azure DevOps, Rechte & Secrets definieren. **Status:** Migrationsstrategie erarbeitet, Rechte/Secrets definiert. **Nächste Schritte:** Migration durchführen, Pipelines migrieren.
20. ⏳ **OSF Deployment** – Docker-Setup für Hilcher-Box/RPi planen und durchführen. **Status:** Docker-Setup geplant, erste Schritte durchgeführt. **Nächste Schritte:** Docker-Deployment finalisieren.
21. ⏳ **Angular-App Optimierung für Präsentation** – Resizing-Optimierung für Landscape und Portrait-Ausrichtung in OBS-Präsentationen. **Ziel:** Optimale Raumausnutzung in beiden Ausrichtungen. **Status:** Erste Layout-Optimierungen umgesetzt. Manche Tabs bereits gut aufbereitet (z.B. AGV-Tab), DSP-Tab noch zu statisch. **Anforderungen:** Responsive Layouts für Landscape (1920×1080) und Portrait (1080×1920), optimale Raumausnutzung, dynamisches Resizing ohne Layout-Brüche. **Referenz:** `docs/04-howto/presentation/obs-video-presentation-setup.md`

**Letzte Aktualisierung:** 07.01.2026

## 📊 Sprint-Vorgehen


### **Sprint-Strategie:**
- **2-Wochen-Zyklen** für kontinuierliche Entwicklung
- **Jeder Sprint erhält ein eigenes Dokument** im Format `sprint_nn.md` im Ordner `docs/sprints/` (siehe `sprint_template.md`).
- **PROJECT_STATUS.md** = Zentrale Change-Dokumentation (nur aktueller Stand, keine Sprint-Details)
- **Sprint-Dokumentation** = Detaillierte Rückblicke und Historie in den einzelnen Sprint-Dokumenten
- **SemVer + CHANGELOG.md** = Release-Historie bleibt separat nachvollziehbar

### **Change-Management:**
- **Alle Änderungen** werden hier dokumentiert
- **Sprint-Status** wird kontinuierlich aktualisiert
- **Wichtige Entscheidungen** in `docs/03-decision-records/`

## 📊 Sprint-Status



### Sprint 12 (25.12.2025 - 07.01.2026) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** OBS-Video-Präsentation, Angular-App Optimierung, AIQS-Kamera-Integration, OSF Deployment, Azure DevOps Migration, Storytelling-Vorbereitung
- **Erreicht:**
  - **OBS-Video (Task 15, abgeschlossen):** OBS Studio Setup, Teams-Integration, Szenen, Kamera, Hotkeys, Checkliste dokumentiert.
  - **AIQS-Kamera-Integration (Task 18, teilweise abgeschlossen):** Source-Dateien vom TXT-Controller kopiert, HTTP-Ansatz verworfen, MQTT-Publikation vorbereitet, Referenz-Implementierung dokumentiert. ✅ **ROBO Pro Coding Workflow etabliert** (06.01.2026): ROBO Pro Coding als primäre Deployment-Methode dokumentiert, Decision Record und How-To erstellt, Verzeichnis-Struktur definiert, Konsolidierung abgeschlossen (25+ Dokumente → 2 Hauptdokumente). ✅ **Archive erstellt** (07.01.2026): `FF_AI_24V_wav.ft` (Sound-Implementierung) und `FF_AI_24V_cam.ft` (Sound + Camera-Publikation) in `integrations/TXT-AIQS/archives/` erstellt. **Nächste Schritte (Sprint 13):** Deployment und Testing beider Varianten, OSF-UI Integration.
  - **OSF Deployment (Task 20, teilweise):** Docker-Setup für Hilcher-Box/RPi geplant, erste Schritte durchgeführt. **Nachlauf (Sprint 13):** Docker-Deployment finalisieren.
  - **Azure DevOps Migration (Task 19, teilweise):** Migrationsstrategie erarbeitet, Rechte/Secrets definiert, Vorbereitung der Pipeline-Migration. **Nachlauf (Sprint 13):** Migration abschließen.
  - **Storytelling (Task 17, in Vorbereitung):** Blog-Serie zu OSF & DSP Story konzipiert, Themen und Struktur vorbereitet. **Nachlauf (Sprint 13):** Blog-Artikel erstellen.
  - **Angular-App Optimierung für Präsentation (Task 21, teilweise):** Erste Layout-Optimierungen für Landscape/Portrait umgesetzt, DSP-Tab noch in Arbeit. **Nachlauf (Sprint 13):** Resizing-Optimierung für alle Tabs abschließen.

### Sprint 11 (12.12 - 24.12.2025) - **ABGESCHLOSSEN**
- **Status:** ✅ Abgeschlossen
- **Fokus:** Shopfloor UX Refresh, Process-Tab Neuaufbau, Orders-Tab Klarstellung, DSP-Links, Track-Trace Erweiterungen, Gedore Remote-Präsentation Vorbereitung.
- **Erreicht:**
  - **Module-Tab (Tasks 1-4):** Status-Erweiterung für alle Module (DPS/AIQS/HBW/DRILL/MILL) mit einheitlicher Struktur, Workpiece-Informationen, gebündelte Sequence Commands, HBW Stock-Grid optimiert, Shopfloor-Modul-Hervorhebung (selektiertes Modul mit blauem Rand), I18n für Details-Section (DE/EN/FR), Tab umbenannt zu "Shopfloor" und an Position 2 verschoben.
  - **Configuration-Tab (Task 5):** Layout mit CSS Grid (Shopfloor links, Module rechts, responsive Breakpoints).
  - **AGV-Tab (Task 6):** Layout-Review abgeschlossen (bestehendes Layout beibehalten).
  - **DSP Edge Animation (Task 7):** Animationssequenz überarbeitet (MC-Funktionen → EDGE xyz_2 verlinken → xyz_1/3 ergänzen → alle drei gestrichelt highlighten).
  - **Process-Tab (Task 8):** Neuaufbau als Akkordeon-Struktur mit "Beschaffungs-Prozess" (Purchase Orders + Storage Flow) und "Produktions-Prozess" (Customer Orders + Production Flow), ERP-Info-Box für Purchase/Customer Orders, Tab an Position 3 verschoben.
  - **Orders-Tab (Task 9):** Layout umgekehrt (Shopfloor links 3fr, Steps rechts 2fr), responsive Breakpoint bei 1200px, Shopfloor-Preview in OrderCards, Finished-Liste per Default eingeklappt, Storage Orders Auto-Expand, Tab an Position 4 verschoben.
  - **DSP → ERP Link (Task 12):** ERP-Daten Verknüpfung zwischen Process-Tab und Track-Trace implementiert, `ErpOrderDataService` für Purchase/Customer Orders, ERP-Info-Box zeigt Supplier/Customer IDs, Order Dates, Planned Delivery Dates.
  - **Track-Trace Erweiterungen (Tasks 10-12):** TURN LEFT/RIGHT Icons basierend auf FTS Order Stream, Order Status (Active/Completed) aus dualen Order Streams, ERP-Daten Integration, zusätzliche Datenfelder (Raw Material Order Date, Delivery Date, Storage Date, Customer Order Date, Production Start Date, Delivery End Date), I18n mit englischen Defaults und DE/FR Übersetzungen, Architektur-Dokumentation erweitert.
  - **OSF Rebranding (Task 13):** Vollständige Umbenennung von OMF3 → OSF und ccu-ui → osf-ui durchgeführt. Workspace-Verzeichnis omf3 → osf umbenannt, alle Komponenten aktualisiert (module-tab → shopfloor-tab, fts-tab → agv-tab), package.json name aktualisiert, wichtigste Dokumentation aktualisiert, alle Referenzen in Code, Tests, CI/CD und Dokumentation angepasst.
  - **DSP-Architektur-Dokumentation (Task 14):** 4 neue SVG-Diagramme erstellt (functional-view, edge-mc-functions, component-view, deployment-view), SVG-Inventory nach `docs/02-architecture/` verschoben, Objects Reference aktualisiert mit SVG-Tiles für alle Icon-Kategorien, Business Applications erweitert (SCM, CRM), HOWTO_ADD_CUSTOMER aktualisiert (FMF als Template, Pfade korrigiert), Dokumentation Cleanup abgeschlossen (deployment-alternatives.md, github-pages-deployment.md, alle OMF3/ccu-ui Referenzen in aktuellen Dokumentationen angepasst).
    - **Dokumentation & Tests:** Track-Trace Architektur-Dokumentation aktualisiert, Tests für `WorkpieceHistoryService` und `ErpOrderDataService` erweitert/erstellt.
    - **Demo-Vorbereitung:** Konftel Cam50 Settings + OBS-Doku aktualisiert, DSP-Mockup interaktiv geplant.
    - **OBS-Video Setup (Task 15, teilweise):** OBS Studio Setup und Tests auf Windows abgeschlossen, Angular-App Optimierung für Präsentation folgt (Task 21).
- **Nachlauf:** kundenspezifische Animationen für Gedore-Präsentation, Angular-App Optimierung für OBS-Präsentationen (Task 21).

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
  - **DSP-Architektur-Referenz:** `osf/apps/osf-ui/src/app/components/dsp-animation/configs/DSP_Architecture_Objects_Reference.md`
  - **DSP SVG-Inventory:** `docs/02-architecture/dsp-svg-inventory.md`
- **OSF README:** `osf/README.md`
- **APS-Analyse:** `docs/06-integrations/`

---

**Status:** OSF Entwicklung läuft erfolgreich; OMF2/FMF bleibt nur noch als Legacy-Referenz bestehen 🎯
