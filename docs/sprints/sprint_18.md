# Sprint 18 – LogiMAT-Messe Durchführung

**Zeitraum:** 19.03.2026 - 01.04.2026 (2 Wochen)  
**Status:** Laufend

**Vorgänger:** [Sprint 17](./sprint_17.md)

**Stakeholder-Update:** Fokus auf LogiMAT-Durchführung, kritische Bugfixes und Hardware-Demo-Stabilität.

**Kurz vor Messe (wenig Zeit, kein Fix-Roulette):** [osf-ui-logimat-smoke-checklist.md](../04-howto/osf-ui-logimat-smoke-checklist.md)

**Release:** Build + Messe-Version **`v1.0.0` / `v1.0.x`** erst **nach** allen Fixes ([Checkliste](../04-howto/osf-ui-logimat-smoke-checklist.md#release-und-messe-version-nach-allen-fixes)).

---

## 🎯 Ziele

### Priorität 1: Kritische Bugs (LogiMAT)

- [x] **Message Monitor (Messe):** Doppelte Topic-Anzeige – **Ursache analysiert**, **Konsole-Debug dokumentiert** (`osf.debug`), damit Messe-Debugging möglich ist. **Analyse:** [message-monitor-duplicate-topics-2026-03.md](../07-analysis/message-monitor-duplicate-topics-2026-03.md). **How-to:** [osf-ui-console-debug.md](../04-howto/osf-ui-console-debug.md). *Technischer Fix (kein Doppel-Ingest mehr) → Abschnitt „Nach LogiMAT (Refactoring)“ unten.*
- [ ] **Camera Image (Sensor-Tab):** Bild wird nicht angezeigt ("Camera Image Loading…" bleibt). **Nur Live-Modus** (aktuell schwer testbar). **Analyse (Ursachen / keine automatische „Fix“ durch Message-Monitor-Änderungen):** [sensor-tab-camera-live-loading-2026-03.md](../07-analysis/sensor-tab-camera-live-loading-2026-03.md).
- [x] **AGV-Tab NAV-Buttons:** Manuell „→ HBW“ / Intersection-2: Payload folgt CCU-Muster (`PASS`/`DOCK`, nicht `STOP`). **→ HBW** nutzt Routenstart wie „Start“-Dropdown (Auto = `lastNodeId`). Session-Analyse: `data/osf-data/sessions/storage-*.log` (`fts/v1/ff/.../order`).
- [x] **FTS Route-Overlay / Order-Tab Route:** SCSS-Regression (v0.9.3): Route-`<line>`-Styles lagen unter `.preview__fts-layer` statt `.preview__route-overlay` → Linie unsichtbar. **Fix:** Styles wieder unter `.preview__route-overlay`. **Pflicht ab jetzt:** visuelle Checks vor Merge → [osf-ui-shopfloor-route-agv-visual-gate.md](../04-howto/osf-ui-shopfloor-route-agv-visual-gate.md). Optional weiter: RPi vs. localhost.
- [x] **Customer LogiMAT:** Darstellung DSP-Architecture mit LogiMAT Business Apps (ORBIS-MES EWM (SAP)...)

### Nach LogiMAT (Refactoring, noch Sprint 18)

- [ ] **Message Monitor:** Code-Fix – doppelte Topic-/Nachrichten-Anzeige **beheben** (Root Cause: doppelte `addMessage`-Pfade im Mock; siehe Analyse §2). **Analyse:** [message-monitor-duplicate-topics-2026-03.md](../07-analysis/message-monitor-duplicate-topics-2026-03.md). *Nach Messe, Umsetzung noch Sprint 18. Ergänzt den abgehakten Messe-Task „Message Monitor (Messe)“ oben.*

### Priorität 2: Übernommen aus Sprint 17

- [x] **Vibrationssensor-Station:** Fertigstellung messetaugliche Platte und Transportsicherung (Arduino R4 + MPU-6050 + SW-420 + DHT11 + Flamme + MQ-2 + Ampel + Sirene). Verdrahtung, Konfiguration, Doku konsolidiert ([arduino-r4-multisensor.md](../05-hardware/arduino-r4-multisensor.md)), alle Sensoren getestet.
- [x] **Fixture-Playback im Mock:** Fixtures in Production-Build aufgenommen (project.json). Mock-Fixture-Playback funktioniert auf RPi – Demo ohne Hardware, vorbereitete Sessions. Live-Modus unverändert. DR-19 ergänzt.
- [x] **Flammensensor-Anzeige (Sensor-Tab):** Darstellung von linearer auf logarithmische Skala umstellen.
- [ ] **Flammensensor Alarm-Werte:** Verifikation der angezeigten Werte im Alarm-Fall (Live-Test).
- [ ] **Arduino Sketch Deployment:** OSF_MultiSensor_R4WiFi v1.1.0 auf Arduino R4 flashen. SKETCH_VERSION im Header prüfen, Serial Monitor „Sketch v1.1.0“, MQTT-Heartbeat 5 s. Doku: [arduino-r4-multisensor.md](../05-hardware/arduino-r4-multisensor.md) §4.
- [x] **UC-05 Live-Demo (Gefahrensimulation):** ~~Umsetzbar wie vorgestellt~~ – **CCU-Limitation:** `ccu/set/park` + `ccu/order/cancel` erreichen *keinen* vollständigen Sofort-Stop. IN_PROGRESS-Orders laufen weiter, laufende Stationen (z.B. AIQS) werden nicht abgebrochen. **Nach Stopp zwingend:** Reset + AGV-dock (manual-intervention). Button „Gefahr simulieren“ sendet Park+Cancel+FTS-Reset – Demo zeigt Sent Events; echter Prozess-Anhalt nur bei ENQUEUED. Siehe [alarm-fabrik-stop](../07-analysis/alarm-fabrik-stop-ccu-commands-2026-03.md).
- [x] **UC-01 Anpassung:** Zusammenführung der Track-&-Trace-Kacheln (Konzept/Live) gemäß DR-22 – `TrackTraceUseCaseComponent`, nur `dsp/use-case/track-trace` mit `?tab=concept` / `?tab=live` (keine `…-genealogy`-Route mehr), DSP-Liste „Concept“ / „Live Demo“.

### Organisatorisches

- [ ] **Azure DevOps Migration:** Von Github zu Azure Devops (Repo + Boards).
- [ ] **Blog-Serie:** Review A1 (Marketing), A2 (Track & Trace), A3 (Überarbeitung).

### E2E-Tests & Verifikation

- [ ] **dsp/correlation/info:** End-to-End Test mit Request/Response Szenario finalisieren.
- [ ] **ccu/order/request von MES/DSP:** Simulierter Ersatzauftrag nach Quality-Fail; osf-ui zeigt neue Order.

### Sprint-Abschluss (Vorbereitung Sprint 19)

*Erledigung vor Start Sprint 19.*

- [ ] Sprint-Dokument [Sprint 18]: Status → „Abgeschlossen“, Abschlussdatum setzen
- [ ] Neuer Sprint [Sprint 19]: Aus Template anlegen, offene `[ ]` übernehmen
- [ ] PROJECT_STATUS: Neue Zeile für Sprint 19 anlegen
- [ ] Roadmap prüfen: Phasen/Daten noch stimmig?

---

## 📋 Backlog (Optional / Prio 2)

### EPIC: Prozess-Anpassung "2-mal Bohren" (Product WHITE)
*Ziel: Das Produkt "Weiß" soll an der Bohrstation eine abweichende Bearbeitung (2 Löcher statt 1) erhalten. Dies erfordert Anpassungen durch die gesamte Kette.*

- **Story 1 (MES/DSP):** Definition des Produkts "WHITE" mit speziellem Workplan-Parameter (z.B. `drill_count: 2`) im MES-Auftrag.
- **Story 2 (CCU/Logic):** Anpassung der `OrderManager`-Logik, um den Parameter auszuwerten. Entweder Generierung zweier separater Bohr-Steps im Workplan (`Drill -> Drill`) oder Erweiterung des Kommandos an die Station.
- **Story 3 (Station/Hardware):** Anpassung der Bohrstation (TXT-Controller), um differenzierte Kommandos ("1x Bohren" vs. "2x Bohren") zu verstehen und physikalisch auszuführen.
- **Story 4 (AI/OSF-AIQS):** Neues ML-Modell trainieren. Erweiterung der Klassifikation um den Zustand "2 Löcher" (vs. "1 Loch" vs. "kein Loch").
- **Story 5 (Hardware/Prep):** Anpassung der Werkstücke (Produkt WHITE) mit Aufklebern/Folien, um das Bohrergebnis "2 Löcher" visuell für die Kamera zu simulieren.

- **Customer Architecture Netzsch:** Neue DSP-Customer-Config `NETZSCH_CONFIG` anlegen – Vorlage: `osf/apps/osf-ui/.../customer/ecme/` und `customer-selector-page.component.ts`.

### Sensor-Erweiterung Arduino (Backlog)

*Siehe [Arduino R4 Multi-Sensor](../05-hardware/arduino-r4-multisensor.md).* Backlog: TM1637/MAX7219 Display für 4-stelliges 7-Segment.

### OSF-UI: Gemeinsamer SVG-/Label-Umbruch & Breiten-Heuristik (Backlog)

*Refactoring / Wartbarkeit – nicht LogiMAT-kritisch; nach Messe oder Sprint 19 priorisieren.*

**Ausgang:** UC-01 Partitur (`uc-01-svg-generator.service.ts`) enthält feste Box-Schrift, Wortumbruch, deutsche Komposita-Suffixe und Silbentrennung mit Bindestrich – **nur** für dieses Diagramm.

**Bereits ähnliche Logik (dupliziert / andere Heuristik):**

| Ort | Inhalt (Kurz) |
|-----|----------------|
| `dsp-architecture.component.ts` | `getWrappedLabelLines()` – `charWidth ≈ fontSize * 0.6`, `maxCharsPerLine`, nur `device`-Container, **max. 2 Zeilen**, Wort-für-Wort |
| `dsp-animation.component.ts` | `getWrappedLabelLines()` – u. a. `fontSize * 0.58`, Break-Hints (`" / "`), lange Tokens; Tests: `dsp-animation.component.label-wrapping.spec.ts` |
| UC-01 SVG-Generator | String→SVG, feste 18px, DE-Suffixe, `Teil - teil` / `Teil-` + Rest |

**Ziel:** Einen **gemeinsamen, injizierbaren Service** (oder `osf`-Lib-Utility) für **Zeilenumbruch in SVG-Boxen** evaluieren und ggf. einführen: einheitliche **Zeichenbreiten-Heuristik**, optionale **Strategien** (Sprache/Locale, Break-Hints, max. Zeilen, Bindestrich-Trennung), **keine** Copy-Paste-Weiterentwicklung pro Diagramm.

**Akzeptanz (Richtung):** UC-01 und DSP-Architecture (mindestens) können den Service nutzen oder dünne Wrapper behalten; bestehende Tests (DSP Animation Label-Wrapping) als Referenz für Regression.

### EPIC: Aufbau eines Test-Frameworks für osf-ui (Backlog)

*Siehe [Test-Framework vs. Replay – Analyse](../07-analysis/test-framework-replay-comparison-2026-03.md).* Optionale Ergänzung zum Replay-Workflow: Framework-Evaluierung (Playwright/Cypress), Fixture-Anbindung, Pilot-Tests für kritische Szenarien.

### Kurz / Info (Backlog)

- **Analyse Stillstand bei zwei AGVs im mixed-Modus:** Zur Info. Nicht messerelevant für LogiMAT.

---

## 🔗 Entscheidungen

- [DR-22](../03-decision-records/22-dsp-use-case-konzept-live-demo.md), [Alarm → Fabrik-Stop](../07-analysis/alarm-fabrik-stop-ccu-commands-2026-03.md)

---

## 📎 Referenzen

- [Arduino R4 Multi-Sensor](../05-hardware/arduino-r4-multisensor.md)
- [Use-Case Bibliothek](../02-architecture/use-case-library.md)
- [Zweites AGV (jp93)](../07-analysis/second-agv-2026-03.md)

---

*Letzte Aktualisierung: 22.03.2026 (Backlog: Reihenfolge OSF-UI SVG-Umbruch vor Test-Framework-EPIC; Kurz/Info AGV)*
