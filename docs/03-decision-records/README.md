# OSF Decision Records

Architektur-Entscheidungen (ADRs) für die OSF-Entwicklung.

---

## Vorgehensweise: Wann wird ein Decision Record erstellt?

### Wer
- **Erstellen:** Jeder, der eine architekturrelevante Entscheidung trifft (z.B. bei Implementierung, Refactoring, Technik-Wahl)
- **Review:** Verantwortliche Person bzw. Team vor dem Merge

### Warum
- Nachvollziehbarkeit: *Warum wurde so entschieden?*
- Kontext für spätere Änderungen
- Vermeidung von Wiederholung vergebener Alternativen

### Wann
- **Vor oder während** einer technischen Entscheidung mit Auswirkung auf Architektur, Patterns oder Wartbarkeit
- Typische Auslöser: Technik-Wahl, neues Pattern, Breaking Change, Abweichung von bestehenden Konventionen

### Wie
1. [Template](decision_template.md) als Vorlage nutzen
2. Neue Datei: `NN-kurzer-titel.md` (NN = nächste freie Nummer, siehe Liste unten)
3. Ausfüllen: Kontext, Entscheidung, Alternativen, Konsequenzen
4. In diese README unter "Entscheidungen" eintragen
5. Bei Bedarf: Verweise in Architektur-Doku oder How-Tos ergänzen

---

## Entscheidungen

### 11. [Tab Stream Initialization Pattern](11-tab-stream-initialization-pattern.md)
**Status:** Accepted | **Datum:** 2025-11-15  
Timing-unabhängige Tab-Stream-Initialisierung mit MessageMonitorService für sofortige Datenanzeige.

### 12. [MessageMonitorService - Speicherverwaltung](12-message-monitor-service-storage.md)
**Status:** Accepted | **Datum:** 2025-11-15  
Circular Buffer, Retention, 5MB localStorage-Limit, Überlauf-Prävention.

### 13. [Track & Trace Architecture](13-track-trace-architecture.md)
**Status:** Accepted | **Datum:** 2025-12-02  
Order-IDs vom Backend, Order-Type-Bestimmung, ERP-Fake-Daten, Event-Generierung.

### 14. [ORBIS CI Usage (Colors & Fonts)](14-orbis-ci-usage.md)
**Status:** Accepted  
Farben und Typografie aus CI-Palette; Open Sans; keine HR-spezifischen Schriften im Produkt-UI.

### 15. [Semver Versioning](15-semver-versioning.md)
**Status:** Accepted  
npm version + SemVer; Patch/Minor/Major; automatische Version-Injection in Builds.

### 16. [Direct-access pages outside tab navigation](16-direct-access-pages.md)
**Status:** Accepted  
Routen außerhalb der Tab-Navigation (z.B. Presentation, DSP-Animation); Dokumentation in Settings-Tab.

### 17. [TXT-Controller Deployment mit ROBO Pro Coding](17-txt-controller-deployment.md)
**Status:** Accepted | **Datum:** 2026-01-06  
ROBO Pro Coding als Deployment-Methode; alle OSF-Versionen in integrations/TXT-*/archives/ (ohne vendor).

### 18. [OSF-Erweiterungen – IP-Adressen und MQTT-Topics](18-osf-extensions-ip-and-mqtt-topics.md)
**Status:** Accepted | **Datum:** 2026-02-18  
IP-Range 192.168.0.91–99 für ORBIS Extensions; Topic-Schema `osf/arduino/<sensorTyp>/<deviceId>/*`.

### 19. [OSF-UI Deployment-Strategie](19-osf-ui-deployment-strategy.md)
**Status:** Accepted | **Datum:** 2026-02-18  
Deployment-Ziele (lokal, GitHub Pages, Docker/RPi); Betriebsmodi pro Ziel; ein Build für alle.

### 20. [APS-CCU OSF-Modifikationen – zentrale Dokumentation](20-aps-ccu-osf-modifications-documentation.md)
**Status:** Accepted | **Datum:** 2026-03-04  
Zentrale Dokumentation aller CCU-Abweichungen vom Fischertechnik-Original in `integrations/APS-CCU/OSF-MODIFICATIONS.md`. Phase-5-Kontext: MES/DSP-Steuerungsübernahme.

### 21. [CCU OSF-Versionierung](21-ccu-osf-versioning.md)
**Status:** Accepted | **Datum:** 2026-03-04  
package.json als Source of Truth, SemVer, Docker-Tags an Version gekoppelt. Selektives CCU-Build/Deploy als Standard.

### 22. [DSP Use-Cases – Konzept vs. Live Demo](22-dsp-use-case-konzept-live-demo.md)
**Status:** Accepted | **Datum:** 2026-03-10  
Ein Kachel pro Use-Case; Auswahl „Konzept“ oder „Live Demo“; UC-05 Live-Demo mit Gefahrensimulation; Quick Win vor UC-01-Refactoring. OSF-Zweck: Demo von DSP/MES-Funktionalität.

### 23. [RPi OSF-UI: Plattform armv7 (32-bit)](23-rpi-osf-ui-platform-armv7.md)
**Status:** Accepted | **Datum:** 2026-03-12  
RPi mit CCU-Stack nutzt 32-bit (armv7). OSF-UI muss armv7 bauen – arm64 führt zu Container-Crash (Exit 159). Deploy-Skript Default = armv7.

### 24. [Shopfloor-Highlight-Farben: Order-Tab vs. AGV-Tab](24-shopfloor-highlight-colors.md)
**Status:** Accepted | **Datum:** 2026-03-10  
Order-Tab: Aktives Modul und FTS auf Route in Grün (aktiver Schritt). AGV-1/2-Farben im AGV-Tab und Presentation-Tab.

---

## Template

Für neue Decision Records: [decision_template.md](decision_template.md)

---

*Letzte Aktualisierung: 2026-03-30*
