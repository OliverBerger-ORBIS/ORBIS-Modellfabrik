# Sprint 18 – LogiMAT-Messe Durchführung

**Zeitraum:** 19.03.2026 – 01.04.2026 · **Status:** Abgeschlossen · **Vorheriger Sprint:** [Sprint 17](./sprint_17.md) · **Nachfolger:** [Sprint 19](./sprint_19.md)

**Kurz:** Messe stabil halten, Bugs fixen, Demo-Hardware zuverlässig.

---

## Messe-Ergebnis: LogiMAT 2026 (24.–26.03.)

- **Demo:** **Erfolgreich** — SmartFactory-Demo mit **zwei AGVs** auf der Messe gefahren.
- **WLAN:** **Instabilitäten** im Messebetrieb; zulässig war **nur 2,4 GHz** (kein 5 GHz). Das Umfeld war **vorher bekannt** risikobehaftet. Unter dieser **ortsbedingten Einschränkung** ist **kaum mit einer robusten technischen „Lösung“** zu rechnen (Kanalüberlast, Störungen, viele parallele Netze) — vielmehr **Risiko/Erwartungsmanagement** für **künftige Messen** und vergleichbare Locations.

---

## Externe Termine (nach LogiMAT, vor Hannover)

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **02.04.2026** | **ORBIS-intern: Vertriebsmeeting** — Präsentation **OSF** | Vertrieb soll zeigen können, **wie OSF genutzt wird**, um **ORBIS-Produkte** (**DSP**, **MES**, **SmartFactory-Konzept**) zu vermitteln — nicht Messe-Publikum, sondern eigener Vertrieb. |
| *Fälligkeit* | Termin liegt auf dem **ersten Tag von Sprint 19** (Sprint 18 endet 01.04.) | **Vorbereitung** (OBS-Durchlauf, Inhalt, Technik) soll **Ende Sprint 18** starten bzw. abgeschlossen sein; siehe Tasks unten **Presentation & Vertrieb**. |

**Hinweis:** Parallel **Hannover Messe** (20–24.04.2026) bleibt separater Meilenstein → [PROJECT_STATUS.md](../PROJECT_STATUS.md) § Wichtige Events.

### Live-Rehearsal ORBIS (Windows: OBS + Kamera)

**Zweck:** Einmal **vor Ort** mit dem **Windows-Präsentationsrechner** durchspielen — gleiche **URL/Env** wie am **Vertriebstermin 02.04.2026**. Die Punkte spiegeln den Sprint-Block **Presentation, OBS & Shopfloor-UX** (Checkliste unten).

1. **Inhalt & Story:** Wie Vertrieb **DSP / MES / SmartFactory** mit OSF erklärt — Fahrplan oder Slides, **wer führt** (Task: *Vertriebsmeeting … inhaltlich abstimmen*).
2. **OBS — Komplettlauf:** Szenen und Quellen (**Browser-Fenster**, **Kamera**), Ausgabe auf Beamer/Display; im Browser OSF mit **Fixtures** und **kritischen Routen** ohne Abbrüche (Task: *OBS-Präsentation*).
3. **Shopfloor / Kamera / Konftel:** Bildausrichtung für Publikum konsistent — primär **OBS** (spiegeln/drehen) vs. später OSF (Task: *Shopfloor-Rotation …*); **Kamera** in OBS und ggf. **Sensor-Tab** nur prüfen, wenn **Publisher** da ist (nicht raten).
4. **Navigation:** Rückweg bei **per Link geöffneten Tabs** — *Back* oder gleichwertig; bei Problemen **Hard-Reload** kennen (Task: *Navigation*).
5. **Layout / Zoom:** Eine **typische** Zielauflösung für den Termin festlegen; UC- und Shopfloor-Skalierung probeweise prüfen (Task: *Einheitliche Diagramm-/Layout-Größe*).
6. **Technik Windows:** Energiesparen/Fullscreen; **OBS-Hotkeys**; **Reserve** (z. B. zweite Szene oder direkter Browser-Tab ohne OBS), falls Capture oder Grafiktreiber zicken.

Abweichungen nach dem Lauf als **Follow-up in Sprint 19** einplanen (wie in den offenen Sprint-Tasks beschrieben).

---

## Releases (Überblick)

| Version | Datum | Inhalt (kurz) |
|---------|--------|----------------|
| v1.0.4 | 03-25 | AGV-2 **`leJ4`**, Shopfloor nur Layout-FTS, RPi **`orbis-osf-ui:1.0.4`** |
| v1.0.3 | 03-25 | Tests / Registry-Texte |
| v1.0.2 | 03-25 | DSP Action live, Arduino Messe-WLAN-Doku |
| v1.0.1 | 03-23 | DHT/UI, Verifikation |
| v1.0.0 | — | Messe-Referenz |

---

## Vor der Messe (Kurzablauf, kein Extra-Dokument)

- Vor Demo: aktuellen **Git-Stand** notieren.
- **Mock:** OSF starten → Shopfloor (Fixture) → Sensor (Mock) → Message Monitor; bei Fehlern **Hard-Reload**.
- **Live:** Broker verbunden; Kamera nur prüfen, wenn Publisher da ist (nicht raten).
- **Nicht starten bis nach Messe:** Message-Monitor-**Code**-Fix (nur Analyse erledigt), große Refactorings, Kamera-UI ohne MQTT-Repro.
- Debug: `osf.debug` = `1` → [osf-ui-console-debug.md](../04-howto/osf-ui-console-debug.md)

---

## Aufgaben (thematisch, mit Haken)

Hier alle Sprint-Punkte **in Themenblöcken**. Erledigt = `[x]`, offen = `[ ]`.

### OSF-UI – Shopfloor & AGV

- [x] **AGV-Tab:** NAV-Buttons (→ HBW etc.); Order aus Shopfloor-Pfad (CCU-kompatible Knoten-/Kanten-IDs; Kreuzungen **`PASS`/`TURN`** aus Streckenrichtung wie `NavigatorService` — [fts-navigation-how-it-works-2026-03.md](../07-analysis/fts-navigation-how-it-works-2026-03.md)).
- [x] **AGV Supervisor (US):** Als Supervisor das AGV von **beliebigem Start** (Auto = gemeldete Position oder manuelles Start-Modul) zum **HBW** steuern; nach Ankunft sollen **CCU-Flows** (z. B. `ccu/order/request`, Ladefahrt) wieder möglich sein. **Umsetzung OSF:** Block „Supervisor navigation“ — Route **von/bis**, Readiness-Badge; **`clearLoadHandler`**-Button (**Clear load handling**), wenn `waitingForLoadHandling` (Freigabe für neue NAV/CCU nach DOCK ohne Modul-Handshake). Siehe [fts-navigation-how-it-works-2026-03.md](../07-analysis/fts-navigation-how-it-works-2026-03.md) §5.
- [x] **Shopfloor:** Route-Linie im Preview wieder sichtbar (Styles unter `.preview__route-overlay`). Visuell prüfen vor Merge → [osf-ui-shopfloor-route-agv-visual-gate.md](../04-howto/osf-ui-shopfloor-route-agv-visual-gate.md)
- [x] **AGV Supervisor-Sequenz (Live):** **→ HBW** dann bei Bedarf **Clear load handling** — verifiziert (Nach `waitingForLoadHandling`: CCU kann wieder; visuelle Kontrolle sinnvoll). **DPS → HBW** getestet; **weitere Startpunkte** (Auto/DRILL/…) noch gezielt live prüfen. Doku: [fts-navigation-how-it-works-2026-03.md](../07-analysis/fts-navigation-how-it-works-2026-03.md) §5–6.
- [x] **AGV:** Vergleich mit Fischertechnik: **Dock** sowie **Laden** / **Laden beenden** sollen abhängig vom **FTS-/AGV-Zustand** nur angezeigt werden bzw. nur **aktiv** sein, wenn der Zustand das erlaubt (nicht nur „Initialzustand“). Betrifft **Shopfloor-Tab** und **AGV-Tab**; Kriterien an `fts/.../state` (z. B. `lastNodeId`, `lastModuleSerialNumber`, `driving`, `paused`, `waitingForLoadHandling`, `batteryState.charging`, Ladestation) und ggf. CCU/Factsheet abstimmen.
- [x] **AGV-Anzeige (Dual-Farben, beide Fahrzeuge auf der Karte):** Erstes Element in `fts[]` orange, zweites warmes Gelb (`getAgvColor`); Label **AGV-1/AGV-2** aus Layout (`getAgvLabel`). **AGV-Tab** „Route & Position“ und **Presentation** zeigen beide AGVs und getrennte Routen (Farben pro AGV), sobald State/Order da sind; **Orders**- und **Shopfloor**-Preview mit farbigen Overlays und Legende. Gateway: `fts$` nur Topics **`…/state`** (Orders überschreiben `ftsStates$` nicht mehr). Fixture **`production_blue_dual_agv_step15`** / Preset `order-production-blue-dual-agv-step15` — **Mock-Test OK** (März 2026). Z-Index/Overlay-Reihenfolge und **Routen-Berechnung** unverändert gelassen. **Follow-up (optional):** Modul-Status (READY/BUSY/…) auf AGV-Zeilen — siehe [DR-24](../03-decision-records/24-shopfloor-highlight-colors.md).
- [x] **Shopfloor-Tab – Modul-Tabelle:** Feste Reihenfolge **DRILL → HBW → MILL → AIQS → DPS → CHRG → AGV-1 → AGV-2** via `getShopfloorTableRowSerialOrder()`; Spalte **Registry Active** entfernt — in Spalte **ID** **✓/✗** + Serial. **Name** für AGV-Zeilen wie Stationen: **`Kurz (Lang)`** — z. B. **`AGV-1 (Automated Guided Vehicle)`** (`getAgvLabel` + `getModuleFullName('FTS')`); **`fts[]`:** **5iO4 = AGV-1**, **leJ4 = AGV-2**.

### Message Monitor

- [x] **Doppelte Topics:** Ursache dokumentiert, Konsole `osf.debug` beschrieben → [message-monitor-duplicate-topics-2026-03.md](../07-analysis/message-monitor-duplicate-topics-2026-03.md)
- [x] **Doppelte Topics:** **Code-Fix** im Mock (doppelte `addMessage`-Pfade) — Shopfloor nur `injectMessage`; **DSP-Action-Tab** Fixture über `injectMessage` wie [message-monitor-duplicate-topics-2026-03.md](../07-analysis/message-monitor-duplicate-topics-2026-03.md) Option A.

### Sensor & Kamera

- [x] **Kamera Live:** Keine frischen Bilder auf `/j1/txt/1/i/cam` – Defekt in DPS Station in SPS (Fehler-Anzeige)Camera Bilder wurden am 24.03 gepublished am 25.03 kammen keine mehr. prüfen → [sensor-tab-camera-live-loading-2026-03.md](../07-analysis/sensor-tab-camera-live-loading-2026-03.md)
- [x] **Flammensensor:** Anzeige **logarithmisch** statt linear (Sensor-Tab).
- [x] **Flammensensor:** Alarm / Sirene mit UC-05 in Live-WLAN geprüft.

### Arduino & Hardware-Station

- [x] **Vibrationssensor-Station:** Platte, Transport, Verdrahtung, Tests → [arduino-r4-multisensor.md](../05-hardware/arduino-r4-multisensor.md)
- [x] **Sketch v1.1.2:** Messe-WLAN `ORBIS-4C57`, Broker `192.168.0.100` → Doku §4, [credentials.md](../credentials.md)
- [x] **Mock-Fixtures:** Playback im Production-Build, Demo auf RPi ohne Hardware (DR-19).
- [x] **Arduino MQTT (Warn/Alarm-Telemetrie + UTC-Timestamps):** Sketch **v1.1.6** — wie v1.1.5, **Payload-`timestamp`** mit **Millisekunden** (`YYYY-MM-DDThh:mm:ss.sssZ`). Siehe [arduino-r4-multisensor.md](../05-hardware/arduino-r4-multisensor.md); OSF/Session Manager: [DR-26](../03-decision-records/26-utc-iso-timestamp-ms-convention.md).
- [x] **Arduino ORBIS NTP (Shopfloor-RPi):** Sketch **v1.1.7** — in **`WIFI_MODE_ORBIS`** **NTP** zuerst **`192.168.0.100`** (RPi **chrony**); Payload-Format unverändert. **How-to:** [rpi-chrony-ntp-server.md](../04-howto/rpi-chrony-ntp-server.md).
- [ ] **24V Sensor-Station (Strompfad, ohne Löten):** Funduino **F23105924** (XL4005), Molex Mini-Fit Jr **Inline-Verlängerung + Tap**, Inline-Sicherung (**2 A** liegt vor), **12 V** auf Ampel + Arduino R4 **Barrel/VIN**; Acryl-Freifläche ca. **8×5 cm** vor Arduino auf **25×15 cm** Platte. Doku & Verbindungsgrafik → [sensor-station-24v-bom-wiring.md](../05-hardware/sensor-station-24v-bom-wiring.md).
- [ ] **Sensor-Station-Box:** Deckel: 25×15 cm + 4 Seitenteile Höhe 28 cm mit Winkelprofilverstärkung.
- [ ] **ARDUINO-API:** API zur Steuerung der Schwellenwerte der Sensoren (vermutlich über MQTT-Topics"). Erweiterung der OSF-UI um ARDUINO-Steuerung an geeigneter Stelle z.B Konfiguration-Tab Parameter für Arduino. (Prüfen ob WIFI-Setup Parallel betrieben werden kann, default ORBIS Fallback daheim, wenn nach n Sekunden keine Verbindung aufgebaut wurde, dann müssen wir nicht den Sketch neu Laden wenn bei ORBIS oder DAHEIM im Wechsel)

### DSP / LogiMAT-Inhalt

- [x] **Customer-Ansicht:** DSP-Architecture mit LogiMAT Business Apps (z. B. ORBIS-MES EWM).
- [x] **UC-01:** Track & Trace eine Kachel, Tabs Konzept / Live (DR-22).
- [x] **UC-05:** Gefahren-Button; Grenzen CCU dokumentiert → [alarm-fabrik-stop-ccu-commands-2026-03.md](../07-analysis/alarm-fabrik-stop-ccu-commands-2026-03.md)

### OSF-UI – SVG-Diagramme (Konzept / Presentation / generiert)

- [ ] **SVG systematisch je Diagramm & Spalte/Lane:** Das mit UC-00 DSP-Column **durchürbte Prinzip** auf **alle** relevanten OSF-UI-SVGs ausrollen: pro **Diagramm** (z. B. UC-00 … UC-06 Konzept-Tab, DSP-Architecture, DSP-Animation, weitere Presentation-SVGs) und darin **der Reihe nach** jede **Spalte, Lane oder gleichartige Box-Gruppe**. **Vorgehen (Orientierung):** (1) **Inventar** — welche Komponenten/Services liefern welches SVG (`*-svg-generator.service`, `dsp-architecture`, `dsp-animation`, …); Verweis [osf-ui-svg-label-text-conventions.md](../04-howto/osf-ui-svg-label-text-conventions.md). (2) **Priorität** — Messe/Demo-Routen und zuerst Bereiche mit Fließtext in **fixen Boxen**. (3) **Pro Bereich** — kurze i18n-Strings; wo nötig **explizite Mehrzeiligkeit** (mehrere Keys statt heuristischem Wrap); max. Zeilen und Abstände **festschreiben**; Kontrast (nicht nur `.muted` auf Weiß); kein horizontaler Überlauf, keine Überlagerung Titel/Body. (4) **Visuelles Gate** wo Shopfloor/Route betroffen — analog zu bestehenden How-tos. Optional danach: weitere Generatoren konsequent auf `escapeXmlForSvgText` / gemeinsame Helper, wo sinnvoll.

### Integration & Tests (E2E)

- [ ] **Session-Aufzeichnung (Analysen):** Neue **Shopfloor-Sessions mit zwei AGVs** (Mixed-Betrieb) erfassen und unter `data/osf-data/sessions/` ablegen. Im **Session Manager** konfigurierbare **Topic-Filter / Preset** (z. B. „Analyse“), damit beim Record **keine** MQTT-Messages zu **Arduino-Sensordaten** (`osf/arduino/…`), **BME680** (`/j1/txt/1/i/bme680`) und **Kamera** (`/j1/txt/1/i/cam`) geschrieben werden — Volumen/Noise reduzieren, ohne FTS/CCU-Kerntopics zu verlieren. Policy: [DR-25](../03-decision-records/25-session-log-topic-filters.md).
- [x] **OSF / Session Manager — UTC-Zeitstempel:** Kanonisch **`utcIsoTimestampMs`** (`@osf/entities`) bzw. **`utc_iso_timestamp_ms()`** (Python) — ISO-8601 UTC mit Millisekunden (`YYYY-MM-DDThh:mm:ss.sssZ`), abgestimmt mit Arduino **v1.1.6** (CCU/TXT unverändert). Formal: [DR-26](../03-decision-records/26-utc-iso-timestamp-ms-convention.md).
- [ ] **dsp/correlation/info:** E2E Request/Response abgeschlossen dokumentieren / durchführen.
- [ ] **ccu/order/request:** E2E Ersatzauftrag nach Quality-Fail; OSF zeigt neue Order wenn MES neue Order anlegt als reaktion auf Fail (Voraussetzung)

### Presentation, OBS & Shopfloor-UX (Vertrieb 02.04.)

- [x] **Vertriebsmeeting 02.04.2026:** OSF-Präsentation inhaltlich **abstimmen** (Story: wie Vertrieb **DSP / MES / SmartFactory** mit OSF erklärt); Slides oder OSF-Fahrplan dokumentieren, wer **führt**.
- [x] **OBS-Präsentation:** **Komplettlauf** testen (Browser, Fixtures, kritische Routen) **vor** dem Termin; Abweichungen/Mängel als Follow-up in **Sprint 19** einplanen.
- [ ] **Shopfloor-Rotation 90° / 180° / 270° (Analyse):** Darstellung an **Monitor- und Laptop-Position** anpassen (inkl. **Konftel-50** / externer Kamera). **Variante A:** Rotation in **OSF** (betrifft u. a. Tab **Shopfloor**, **Orders**, **Konfiguration**, **AGV**, **Presentation**). **Variante B:** Ausrichtung primär über **OBS** spiegeln/drehen, damit Bild zu Konftel konsistent ist — Optionen dokumentieren, ggf. in **DR/Analyse** auslagern; Umsetzung kann eigener Sprint-19-Task werden.
- [ ] **Navigation:** **Back** (oder gleichwertig), damit Nutzer bei **per Link geöffneten Tabs** zur Ausgangssicht zurückkommen.
- [ ] **Einheitliche Diagramm-/Layout-Größe:** Heute **mehrere** Stellen für **Shopfloor-Layout-** und **UC-Diagramm-**Skalierung; bei **typisch fester** Browser-/Monitor-Größe **eine zentrale** Steuerung anstreben, die **alle** relevanten UC-/Shopfloor-Darstellungen mitzieht (Konzept + Aufwand klären).

### Organisation

- [ ] **Azure DevOps:** Repo + Boards von GitHub umziehen.
- [ ] **Blog:** Reviews A1, A2, A3.

### Sprint-Wechsel (wenn Sprint 18 zu Ende ist)

- [x] Sprint 18: Status **Abgeschlossen**, Abschlussdatum **02.04.2026**.
- [x] Sprint 19: Datei neu aus [sprint_template.md](./sprint_template.md), **alle noch offenen `[ ]`** von hier übernommen — **inkl.** offener Punkte unter **Presentation, OBS & Shopfloor-UX** (nicht erledigt: Rotation, Navigation, Layout).
- [x] **PROJECT_STATUS:** neue Zeile Sprint 19; **Externe Events** ergänzt.
- [x] **Roadmap** kurz gegenlesen.

---

## Später (Backlog, nicht zum Abhaken im Sprint)

- **Produkt WHITE „2× Bohren“:** MES/CCU/Station/Kamera-Kette – siehe frühere Epic-Aufzählung; angehen, wenn priorisiert.
- **Netzsch:** eigene Customer-Config `NETZSCH_CONFIG`.
- **Arduino:** optionales 7-Segment (TM1637/MAX7219).
- **Tests:** optionales UI-Test-Framework → [test-framework-replay-comparison-2026-03.md](../07-analysis/test-framework-replay-comparison-2026-03.md)
- **Info:** Analyse Stillstand zwei AGVs im Mixed-Betrieb – nur zur Einordnung.
- **Backend OSF Service:** Persistenz der Daten (Prozess, Shopfloor, Umwelt) mit dem Ziel der Analyse (in der cloud, Ziel: Backend auf RPI mit Grafana Dashboard; oder später backend ersetzen durch DSP-Komponente DISC; wichtig: Interface für Grafana damit OSF-Backend und DSP-DISC ausgetauscht werden können)

---

## Links (Entscheidungen & Tiefe)

- [DR-22](../03-decision-records/22-dsp-use-case-konzept-live-demo.md) · [DR-25 Session-Logs & Topic-Filter](../03-decision-records/25-session-log-topic-filters.md) · [Zweites AGV leJ4](../07-analysis/second-agv-2026-03.md) · [Use-Case-Bibliothek](../02-architecture/use-case-library.md)

---

*Stand: 02.04.2026*
