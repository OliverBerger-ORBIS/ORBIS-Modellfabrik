# Sprint 30 – T&T sprachunabhängig, Roadmap-Planung & Demo-Termine

**Zeitraum:** 04.09.2026 – 17.09.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 29](./sprint_29.md)

**Kurz:** Fokus **T&T Live-Historie sprachunabhängig**; **Roadmap-Konzept** (Object Detection, SAP Logistic Management / LogiMAT 2027, Persistenz↔OSF-UI, **Uni Magdeburg Knowledge Graph / Shopfloor-AI**); Demos **Bühler (14.09.)**, **Welcome Days (17.09.)**; Uni Magdeburg Deep-Dive SB (**21./22.09.**). Dual-AGV Serial-/NFC-first **visuell abgenommen**.

---

## Externe Termine & Outreach

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **14.09.2026** | **Firma Bühler** — OSF-Präsentation **live** am Shopfloor | Kunden-Demo / Use-Case-Story |
| **17.09.2026** | **ORBIS Welcome Days** — OSF-Präsentation für neue ORBIS-Mitarbeiter | Onboarding / interne DSP-Story |
| **21.09.2026** *(bestätigt)* | **Uni Magdeburg / Dr. Reggelin** — **Ganztägiger Workshop Saarbrücken** Deep-Dive OSF/DSP; **Kshitiz**; **DSP-Team informiert**; NDA **Frank Wilhelm** noch offen | Hochschulkooperation / Manufacturing Knowledge Graph PoC |
| **16.–18.03.2027** *(Ausblick)* | **LogiMAT 2027** — möglicher Showcase **SAP Logistic Management** + OSF Shopfloor | Messe-Story Intralogistik / ORBIS–SAP |

---

## Coverage Standing

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline = Sprint-29-Ende) | 03.09.2026 | 54.77% | 66.87% | 71.97% | 70.89% | 48 / 59 / 64 / 63 | +6.8 / +7.9 / +8.0 / +7.9 pp |
| Aktuell | 03.09.2026 | 54.77% | 66.87% | 71.97% | 70.89% | 48 / 59 / 64 / 63 | +6.8 / +7.9 / +8.0 / +7.9 pp |

- **Messmethode:** `npm run test:coverage` (`--runInBand`) → `coverage/osf-ui/index.html`. Details: [test-coverage-status.md](../07-analysis/test-coverage-status.md).
- **Top-3 Gaps:**
  1. `shopfloor-tab` / `agv-tab` / `shopfloor-preview`
  2. DSP-/UC SVG-Generatoren (0 % Hotspots)
  3. Restzweige `workpiece-history` / große Tabs
- **Pflege:** Baseline unverändert; nach Messung nur **Aktuell** + Top-Gaps. Am Sprintende Pflicht-Messung vor Abschluss.

---

## Aufgaben (thematisch, mit Haken)

### Track & Trace / Dual-AGV *(Fokus)*

- [ ] **T&T Historie sprachunabhängig (Live-Demo):** Language-Wechsel (`window.location.assign` → Locale-Build-Reload) verwirft RAM-Genealogie; AGV-Events fehlen → wirkt wie Bug. Ziel: vollständige/konsistente T&T-Daten unabhängig von Language-Wahl (Design zuerst, Live priorisieren). WAD-Doku: [osf-ui-track-trace-history-attribution.md](../04-howto/osf-ui-track-trace-history-attribution.md) § Language-Wechsel. *(Ursprung: Sprint 29)*
- [x] **T&T Dual-AGV Serial-/NFC-first visuell abgenommen (03.09.2026):** Screenshots OK (`storage-wbr-dual-agv-rwb_*`); Serial-/NFC-first commit `1b56a33d`. Offen nur Language-Reload (siehe oben).

### Roadmap-Planung *(Konzept — keine Umsetzung in diesem Sprint)*

- [ ] **Object Detection / Visual-AI (BA Daniel Wonkam):** Konzeptskizze Integration in OSF — Datenpfad (Kamera → OD-App → MQTT/Facade → OSF-UI / T&T / Grafana), Abgrenzung zu Intake (`osf/workpiece/intake`, DR-30) und 3er-FTS-Stack. Ergebnis: kurze Analyse `docs/07-analysis/` + offene Entscheidungsfragen (kein Code).
- [ ] **SAP Logistic Management + Intralogistik:** Konzept, wie OSF die ORBIS/SAP-Lösung **Logistic Management** unterstützen kann (Lagerverwaltung, Intralogistik; Anbindung an STORAGE/HBW/DPS/FTS-Story). Optionaler **Showcase LogiMAT 2027 (16.–18.03.2027)**. Ergebnis: Optionen + Schnittstellen-Skizze (Phase-5-Richtung MES/SAP).
- [ ] **Persistenz Messages/Events ↔ OSF-UI:** Design — Historie für T&T und weitere **Live**-Use-Cases aus Edge-Persistenz (DR-28 / `.201`) statt RAM/MessageMonitor? Welche Umbau-Tiefe (nur T&T vs. generisches History-Backend)? Brücke zum Language-Reload-Problem. Ergebnis: Design-Optionen, Live priorisieren.
- [ ] **Uni Magdeburg — Manufacturing Knowledge Graph / Shopfloor-AI:** Konzept zur Kooperation (DSP + semantische KI-Schicht). DSP bleibt Integrations-/Prozessschicht; Knowledge Graph verknüpft Shopfloor/MES/SAP/Sensorik für nachvollziehbare LLM-Abfragen; PoC **additiv/lesend** auf OSF ohne Kundendaten; **Kshitiz** Technik, ORBIS Fachkontext/Zugang. T&T perspektivisch → erklärbare Ursachenanalyse. Management Summary: [dsp-manufacturing-knowledge-graph-poc-2026-09.md](../07-analysis/dsp-manufacturing-knowledge-graph-poc-2026-09.md). Deep-Dive SB 21./22.09. nutzen.

### Demo & Outreach

- [ ] **Bühler-Demo (14.09.):** Live Shopfloor; T&T/Grafana Story; Language vor Demo setzen (bis Fix oben).
- [ ] **Welcome Days (17.09.):** Interne OSF-Präsentation.
- [ ] **Uni Magdeburg SB (21./22.09.):** Deep-Dive vorbereiten; NDA Frank Wilhelm; DSP-Team; Knowledge-Graph-PoC-Story (siehe Roadmap oben).

### Integration & Tests

- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Router / Netzwerk-Setup

- [ ] **Netzwerk-Topologie/Verkabelung (Rest):** ORBIS-LAN-Adressliste + MES-Pfad mit Netzwerk-Kollegen (**nur mit ORBIS-VPN testbar**); Omada Admin-URL/Modell; ggf. HTML neu exportieren. *(Ursprung: Sprint 26)*
- *Rollen: GL.iNet weiß = DPS/FT-Gateway; GL.iNet grau = LTE→Omada WAN; Omada = WLAN + Port-Hub; Proxmox = DSP Edge im FT-LAN. How-to: [orbis-shopfloor-network-topology.md](../04-howto/setup/orbis-shopfloor-network-topology.md).*

### Blog & Organisation

- [ ] Blog: Review A3 *(Von Daten zu belastbaren KPIs)* *(Ursprung: Sprint 19 / 26)*
- [ ] Blog: Review A4 *(Von Erkenntnissen zu Aktionen)* *(Ursprung: Sprint 19 / 26)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] **Coverage Standing:** Endmessung (`npm run test:coverage`) → `Aktuell` + Top-Gaps; bei Bedarf [test-coverage-status.md](../07-analysis/test-coverage-status.md) aktualisieren
- [ ] Sprint 30: Status Abgeschlossen, Datum
- [ ] Sprint 31 anlegen, offene `[ ]` übernehmen; Coverage-Baseline = Endmessung Sprint 30
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Links

- [Sprint 29](sprint_29.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md) · [test-coverage-status.md](../07-analysis/test-coverage-status.md) · [T&T Attribution / Language](../04-howto/osf-ui-track-trace-history-attribution.md) · [Knowledge Graph PoC](../07-analysis/dsp-manufacturing-knowledge-graph-poc-2026-09.md)

---

*Stand: 03.09.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md) · Roadmap-Konzepte → Umsetzung Folge-Sprints
