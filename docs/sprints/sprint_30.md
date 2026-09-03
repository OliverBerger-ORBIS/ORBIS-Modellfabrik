# Sprint 30 – T&T sprachunabhängig, Dual-AGV Abnahme & Demo-Termine

**Zeitraum:** 04.09.2026 – 17.09.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 29](./sprint_29.md)

**Kurz:** Fokus **Track & Trace Live-Historie unabhängig vom Language-Reload**; Dual-AGV Serial-/NFC-first **Replay-Abnahme**; Demos **Bühler (14.09.)**, **Welcome Days (17.09.)**; Uni Magdeburg Deep-Dive SB (**21./22.09.**) vorbereiten.

---

## Externe Termine & Outreach

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **14.09.2026** | **Firma Bühler** — OSF-Präsentation **live** am Shopfloor | Kunden-Demo / Use-Case-Story |
| **17.09.2026** | **ORBIS Welcome Days** — OSF-Präsentation für neue ORBIS-Mitarbeiter | Onboarding / interne DSP-Story |
| **21.09.2026** *(bestätigt)* | **Uni Magdeburg / Dr. Reggelin** — **Ganztägiger Workshop Saarbrücken** Deep-Dive OSF/DSP; Termin-Einladung an **Kishitz** raus; **DSP-Team informiert**; NDA-Unterschrift **Frank Wilhelm** noch offen | Hochschulkooperation / DSP-Story |

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
- [ ] **T&T Dual-AGV Serial-/NFC-first Replay-Abnahme:** Code lokal (Transportgruppen nach Serial; NFC-first Phase bei fremder Step-`orderId`). Visuell: Reset + Replay `storage-wbr-dual-agv-rwb_20260903_094319` (AGV-2 vor MILL, AGV-1 MILL→AIQS). Danach Commit/Version/Deploy nach User-OK. *(Ursprung: Sprint 29)*

### Demo & Outreach

- [ ] **Bühler-Demo (14.09.):** Live Shopfloor; T&T/Grafana Story; Language vor Demo setzen (bis Fix oben).
- [ ] **Welcome Days (17.09.):** Interne OSF-Präsentation.
- [ ] **Uni Magdeburg SB (21./22.09.):** Deep-Dive vorbereiten; NDA Frank Wilhelm; DSP-Team.

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

- [Sprint 29](sprint_29.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md) · [test-coverage-status.md](../07-analysis/test-coverage-status.md) · [T&T Attribution / Language](../04-howto/osf-ui-track-trace-history-attribution.md)

---

*Stand: 03.09.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
