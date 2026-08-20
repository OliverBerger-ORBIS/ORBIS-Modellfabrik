# Sprint 29 – Grafana/Persistenz, Intake-Bridge live & OD-Anbindung

**Zeitraum:** 21.08.2026 – 03.09.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 28](./sprint_28.md)

**Kurz:** Fokus **Grafana / Edge-Persistenz** und **Workpiece-Intake live** (Bridge auf RPi + optional OSF-UI-Subscribe); Carry-over Netzwerk/Blog/E2E; Vorbereitung Uni Magdeburg Deep-Dive SB (**21./22.09.**).

---

## Externe Termine & Outreach

| Datum | Event | Nutzen für OSF |
|--------|--------|----------------|
| **21./22.09.2026** *(geplant)* | **Uni Magdeburg / Dr. Reggelin** — Meeting Saarbrücken Deep-Dive OSF/DSP; Kishitz; NDA-Unterschrift **Frank Wilhelm** noch offen | Hochschulkooperation / DSP-Story |
| *(offen)* | Abstimmung DSP-Truppe für SB-Termin | Terminfixierung Deep-Dive |
| *(Follow-up)* | **Daniel Wonkam** (OD) — Intake-Topic nutzen; Workpiece-Tracking 3er-Stack | Partner über `osf/workpiece/intake` |

---

## Coverage Standing

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline = Sprint-28-Ende) | 20.08.2026 | 49.8% | 61.3% | 66.5% | 65.5% | 42 / 52 / 58 / 58 | +7.8 / +9.3 / +8.5 / +7.5 pp |
| Aktuell | 20.08.2026 | 49.8% | 61.3% | 66.5% | 65.5% | 42 / 52 / 58 / 58 | +7.8 / +9.3 / +8.5 / +7.5 pp |

- **Messmethode:** `npm run test:coverage` (`--runInBand`; bei Nx-Daemon-Fehler: `npx nx reset` + `NX_DAEMON=false`) → `coverage/osf-ui/index.html`. Details: [test-coverage-status.md](../07-analysis/test-coverage-status.md).
- **Top-3 Gaps:**
  1. `shopfloor-tab` / `shopfloor-preview`
  2. DSP-/Customer-Pages
  3. `agv-tab` / `workpiece-history`
- **Pflege:** Baseline unverändert; nach Messung nur **Aktuell** + Top-Gaps. Am Sprintende Pflicht-Messung vor Abschluss.

---

## Aufgaben (thematisch, mit Haken)

### Grafana / Edge-Persistenz *(Fokus)*

- [ ] **Modus A (Replay + Session):** Grafana `localhost:3000` mit Session-Replay erneut prüfen — Orders/Daten sichtbar; Abweichungen in Troubleshooting dokumentieren. *(Ursprung: Sprint 22; [runtime-modes-matrix.md](../04-howto/helper_apps/session-manager/runtime-modes-matrix.md))*
- [ ] Grafana-Dashboards ausbauen (fachliche Panels schärfen, offene Visualisierungs-/Abnahmepunkte systematisch schließen). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffähig machen (neben local-dev als nächster Zielpfad). *(Ursprung: Sprint 22)*
- [ ] **Track&Trace Persistenz (Option B):** UI-Historie bleibt session-/RAM-scoped; längere NFC-Spuren über Edge/Grafana (`osf-edge-persistence`, [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)) — kein Browser-localStorage. *(Entscheidung 21.07.2026; Ursprung: Sprint 26)*

### Workpiece-Intake / Object Detection *(Fokus)*

- [ ] **Intake-Bridge auf RPi deployen:** `npm run docker:workpiece-intake-bridge:deploy -- ff22@192.168.0.100` (FT-LAN); Verifikation Topic `osf/workpiece/intake`. How-to: [workpiece-intake-bridge-rpi.md](../04-howto/deployment/workpiece-intake-bridge-rpi.md). *(Sprint 28: Image gebaut, Deploy ausstehend)*
- [ ] **OSF-UI subscribe `osf/workpiece/intake`:** optionale Nutzung für OD-View / NFC-Einstieg (Folge nach Bridge live). *(Ursprung: Sprint 28; [DR-30](../03-decision-records/30-workpiece-intake-mqtt-facade.md))*
- *Partner-Hinweis an Daniel:* [workpiece-intake-event-partner.md](../04-howto/integrations/workpiece-intake-event-partner.md)

### Integration & Tests

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
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
- [ ] Sprint 29: Status Abgeschlossen, Datum
- [ ] Sprint 30 anlegen, offene `[ ]` übernehmen; Coverage-Baseline = Endmessung Sprint 29
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Links

- [Sprint 28](sprint_28.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md) · [test-coverage-status.md](../07-analysis/test-coverage-status.md) · [DR-30 Intake](../03-decision-records/30-workpiece-intake-mqtt-facade.md)

---

*Stand: 20.08.2026 (Sprintwechsel)* · Doku-Workflow: [sprints_README.md](sprints_README.md)
