# Sprint 19 – Sensor-Station, Backend/Grafana & Hannover-Vorbereitung

**Zeitraum:** 02.04.2026 – 15.04.2026 (2 Wochen) · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 18](./sprint_18.md)

**Kurz:** Arduino-Sensor-Station stärker in OSF integrieren (Steuerung, Konfiguration), physische Stabilisierung (24 V, Transportbox), Backend mit Persistenz und Grafana; Blog voranbringen; Hannover-Messe (Vogelperspektive, Konftel-20, OBS-Szenen) vorbereiten.

---

## Externe Termine

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **20–24.04.2026** | **Hannover Messe** | Großer Außenauftritt — **Vorbereitung** in diesem Sprint (Kamera, Halterung, OBS; Remote/Konftel-20) |
| **~Ende 04.2026** | **ORBIS Customer-Connect** | Folge-Meilenstein → [PROJECT_STATUS.md](../PROJECT_STATUS.md) |

---

## Aufgaben (thematisch, mit Haken)

### Arduino Sensor-Station & Hardware

- [ ] **24V Sensor-Station (Strompfad, ohne Löten):** Funduino **F23105924** (XL4005), Molex Mini-Fit Jr **Inline-Verlängerung + Tap**, Inline-Sicherung (**2 A** liegt vor), **12 V** auf Ampel + Arduino R4 **Barrel/VIN**; Acryl-Freifläche ca. **8×5 cm** vor Arduino auf **25×15 cm** Platte. Doku → [sensor-station-24v-bom-wiring.md](../05-hardware/sensor-station-24v-bom-wiring.md).
- [ ] **Sensor-Station-Box / Transport:** Deckel **25×15 cm** + 4 Seitenteile Höhe **28 cm** mit Winkelprofilverstärkung — **physische Stabilisierung** für Transport und Montage am Stand.
- [ ] **OSF-Einbindung Sensor-Station:** Bessere Darstellung/UX im **Sensor-Tab** und nachvollziehbare Anbindung an OSF-Story (Demo-tauglich).
- [ ] **ARDUINO-Steuerung (Schwellenwerte):** API/MQTT-Topics für Schwellenparameter; **OSF-UI** (z. B. Konfiguration-Tab oder dedizierte Sektion) — inkl. Prüfung **DAHEIM/ORBIS**-Wechsel ohne Flash (Timeout/Fallback). (Aus Sprint 18 übernommen.)
- [ ] **Shopfloor-Rotation 90° / 180° / 270° (Analyse):** Darstellung an **Monitor- und Laptop-Position** anpassen (inkl. **Konftel-20** / externe Kamera). **Variante A:** Rotation in **OSF**. **Variante B:** Ausrichtung primär über **OBS** — Optionen dokumentieren; Verweis [obs-video-presentation-setup.md](../04-howto/presentation/obs-video-presentation-setup.md).

### Backend, Persistenz & Grafana

- [ ] **Backend OSF Service:** Persistenz der Daten (Prozess, Shopfloor, Umwelt) mit dem Ziel **Analyse**; Zielbild: Dienst auf **RPi** mit **Grafana**-Anbindung; **Interface** so wählen, dass später **DSP-DISC** o. ä. austauschbar bleibt (siehe Backlog Sprint 18). Grobe Architektur ggf. DR/Analyse.

### Blog & Organisation

- [ ] **Blog:** Reviews A1, A2, A3 vorantreiben.
- [ ] **Azure DevOps:** Repo + Boards von GitHub umziehen.

### Hannover Messe 2026 – Vorbereitung

- [ ] **Vogelperspektive / Kamera:** Halterung, Bildausschnitt, Tests mit OSF/OBS.
- [ ] **OBS-Szenen:** Szenen für **Hannover**-Setup vorbereiten (analog [obs-video-presentation-setup.md](../04-howto/presentation/obs-video-presentation-setup.md)).
- [ ] **Konftel-20:** Fernsteuerung / Remote-Setup für **Szenen** oder Kameraeinstellungen (Hersteller-Oberfläche, Netzwerk) — **ohne** Blockieren der Demo-Pipeline; mit Windows-Präsentationsrechner validieren.

### OSF-UI – SVG-Diagramme (Konzept / Presentation / generiert)

- [ ] **SVG systematisch je Diagramm & Spalte/Lane:** Prinzip wie UC-00 DSP-Column auf **alle** relevanten OSF-UI-SVGs; [osf-ui-svg-label-text-conventions.md](../04-howto/osf-ui-svg-label-text-conventions.md); visuelles Gate wo Shopfloor betroffen.

### Integration & Tests (E2E)

- [ ] **Session-Aufzeichnung (Analysen):** Shopfloor-Sessions **zwei AGVs** (Mixed-Betrieb); Session Manager **Topic-Filter / Preset** (DR-25) — Arduino/BME680/Kamera aus Record optional.
- [ ] **dsp/correlation/info:** E2E Request/Response dokumentieren / durchführen.
- [ ] **ccu/order/request:** E2E Ersatzauftrag nach Quality-Fail; OSF zeigt neue Order wenn MES reagiert.

### Presentation & Shopfloor-UX (Übernahme aus Sprint 18)

- [ ] **Navigation:** **Back** (oder gleichwertig), damit Nutzer bei **per Link geöffneten Tabs** zur Ausgangssicht zurückkommen.
- [ ] **Einheitliche Diagramm-/Layout-Größe:** Zentrale Steuerung der UC-/Shopfloor-Skalierung bei typischer Browser-/Monitor-Größe (Konzept + Aufwand).

### Sprint-Wechsel (am Ende von Sprint 19 abarbeiten)

- [ ] Sprint 19: Status **Abgeschlossen**, Abschlussdatum eintragen.
- [ ] Sprint 20: aus [sprint_template.md](./sprint_template.md), offene **`[ ]`** übernehmen.
- [ ] **PROJECT_STATUS** und **Roadmap** kurz prüfen.

---

## Später (Backlog, nicht zum Abhaken im Sprint)

- **Produkt WHITE „2× Bohren“:** MES/CCU/Station/Kamera-Kette — wenn priorisiert.
- **Netzsch:** eigene Customer-Config `NETZSCH_CONFIG`.
- **Arduino:** optionales 7-Segment (TM1637/MAX7219).
- **Tests:** optionales UI-Test-Framework → [test-framework-replay-comparison-2026-03.md](../07-analysis/test-framework-replay-comparison-2026-03.md)
- **Info:** Analyse Stillstand zwei AGVs im Mixed-Betrieb — nur Einordnung.

---

## Links

- [DR-25 Session-Logs & Topic-Filter](../03-decision-records/25-session-log-topic-filters.md) · [Arduino Multi-Sensor](../05-hardware/arduino-r4-multisensor.md) · [Use-Case-Bibliothek](../02-architecture/use-case-library.md)

---

*Stand: 02.04.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
