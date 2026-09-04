# Sprint 30 – T&T sprachunabhängig, Roadmap-Planung & Demo-Termine

**Zeitraum:** 04.09.2026 – 17.09.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 29](./sprint_29.md)

**Kurz:** Fokus **T&T Live-Historie sprachunabhängig** (Workaround: Sprache vor Demo); **Persistenz:** Architektur + Query-API V1 **da**, UC-01-DB in OSF-UI **offen**; Roadmap OD / SAP LM / Uni-MD; Demos **Bühler (14.09.)**, **Welcome Days (17.09.)**; Uni Magdeburg SB (**21./22.09.**). Dual-AGV Serial-/NFC-first **visuell abgenommen**.

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
| Aktuell | 04.09.2026 | 54.78% | 66.95% | 72.01% | 70.92% | 48 / 59 / 64 / 63 | +6.8 / +8.0 / +8.0 / +7.9 pp |

- **Messmethode:** `npm run test:coverage` (`--runInBand`) → `coverage/osf-ui/index.html`. Details: [test-coverage-status.md](../07-analysis/test-coverage-status.md).
- **Top-3 Gaps:**
  1. `shopfloor-tab` / `agv-tab` / `shopfloor-preview`
  2. DSP-/UC SVG-Generatoren (0 % Hotspots)
  3. Restzweige `workpiece-history` / große Tabs
- **Pflege:** Baseline unverändert; nach Messung nur **Aktuell** + Top-Gaps. Am Sprintende Pflicht-Messung vor Abschluss.

---

## Aufgaben (thematisch, mit Haken)

### Track & Trace / Dual-AGV *(Fokus)*

- [ ] **T&T Historie sprachunabhängig (Live-Demo):** Language-Wechsel = Full Reload, RAM-Genealogie weg (WAD). **Kein** Hotfix in diesem Sprint — Workaround: Sprache vor Demo setzen (Bühler/Welcome Days). Persistenz löst das erst mit UC-01-DB (siehe unten). WAD: [osf-ui-track-trace-history-attribution.md](../04-howto/osf-ui-track-trace-history-attribution.md) § Language-Wechsel. *(Ursprung: Sprint 29)*
- [x] **T&T Dual-AGV Serial-/NFC-first visuell abgenommen (03.09.2026):** Screenshots OK (`storage-wbr-dual-agv-rwb_*`); Serial-/NFC-first commit `1b56a33d`.

### Persistenz / UC-01 DB-Variante

- [x] **Architektur DSP-Tab vs. APS-Tabs (04.09.2026):** APS (Shopfloor/Orders/AGV/…) MQTT-Live; DSP-UCs Quelle je Story; **T&T = UC-01**. [dsp-tab-persistence-use-cases-2026-09.md](../07-analysis/dsp-tab-persistence-use-cases-2026-09.md).
- [x] **Lückenanalyse MQTT vs. `osf_edge` (04.09.2026):** V1 = FINISHED + Intake + Orders; nicht Sticky/Mitfahrt/ENV/Quality. [uc01-tt-persistence-gap-2026-09.md](../07-analysis/uc01-tt-persistence-gap-2026-09.md).
- [x] **Query-API V1 (04.09.2026):** `GET /v1/workpieces`, `GET /v1/workpieces/{nfc}/timeline`, Port **3081**. Lokal Replay-DB, Dual-AGV-NFCs `query-api-check-replay.sh --require`. How-to: [edge-persistence-query-api.md](../04-howto/deployment/edge-persistence-query-api.md).
- [ ] **UC-01 DB-Variante in OSF-UI:** Query-API parallel zur MQTT-T&T-Komponente (MQTT unangetastet). Dev: `http://localhost:3081` (`env.replay`). Kein Ersatz der Live-MQTT-Strecke in diesem Häppchen.
- [ ] **Visueller Check MQTT ↔ DB:** Replay Dual-AGV-Ref `storage-wbr-dual-agv-rwb_20260903_094319`; gleiche NFC; vergleichen Intake / Stationen / Reihenfolge. V1 **keine** Feature-Parität (Sticky, Mitfahrt, volle FTS-Ist-Spur). **Vor Commit der UI-Variante** — visuell durch Oliver.
- [ ] **Query-API auf `.201`:** Persistence-Image `--build` (`docker-compose.dsp.yml`), Port 3081; nachdem die lokale UI-Variante steht bzw. Uni-M Zugang braucht.

### Roadmap-Planung *(Konzept — keine Umsetzung in diesem Sprint)*

- [ ] **Object Detection / Visual-AI (BA Daniel Wonkam):** Konzeptskizze Integration in OSF — Datenpfad (Kamera → OD-App → MQTT/Facade → OSF-UI / T&T / Grafana), Abgrenzung zu Intake (`osf/workpiece/intake`, DR-30) und 3er-FTS-Stack. Ergebnis: kurze Analyse `docs/07-analysis/` + offene Entscheidungsfragen (kein Code).
- [ ] **SAP Logistic Management + Intralogistik:** Konzept, wie OSF die ORBIS/SAP-Lösung **Logistic Management** unterstützen kann (Lagerverwaltung, Intralogistik; Anbindung an STORAGE/HBW/DPS/FTS-Story). Optionaler **Showcase LogiMAT 2027 (16.–18.03.2027)**. Ergebnis: Optionen + Schnittstellen-Skizze (Phase-5-Richtung MES/SAP).
- [ ] **Uni Magdeburg — Manufacturing Knowledge Graph / Shopfloor-AI:** Konzept zur Kooperation (DSP + semantische KI-Schicht). PoC **additiv/lesend** auf Hub-DB `osf_edge` (nicht APS-Tabs). **Kshitiz** Technik, ORBIS Fachkontext/Zugang. Management Summary: [dsp-manufacturing-knowledge-graph-poc-2026-09.md](../07-analysis/dsp-manufacturing-knowledge-graph-poc-2026-09.md). Datenkante: [dsp-tab-persistence-use-cases-2026-09.md](../07-analysis/dsp-tab-persistence-use-cases-2026-09.md). Deep-Dive SB 21./22.09. nutzen. Query-API = lesender Schnitt (lokal jetzt, `.201` s. Persistenz-Thema).

### Demo & Outreach

- [ ] **Bühler-Demo (14.09.):** Live Shopfloor; T&T/Grafana Story; Language vor Demo setzen (bis Fix oben).
- [ ] **Welcome Days (17.09.):** Interne OSF-Präsentation.
- [ ] **Uni Magdeburg SB (21./22.09.):** Deep-Dive vorbereiten; NDA Frank Wilhelm; DSP-Team; Knowledge-Graph-PoC-Story (siehe Roadmap oben).

### Integration & Tests

- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Router / Netzwerk-Setup

- [x] **Netzwerk — IT-Antwort Dominik (04.09.2026):** P1 WAN · P2–3 LAN/Messe (md1 ohne VPN-Client) · P4–5 FT LAN; zwei getrennte Netze; IPSEC C2S am Omada. Doku + Portbild: [orbis-shopfloor-network-topology.md](../04-howto/setup/orbis-shopfloor-network-topology.md). *(Ursprung: Sprint 26)*
- [x] **FT-LAN Topologie nachgezogen (03.09.2026):** Mermaid Arduino/Grafana; Retest Kern OK; DHCP/SSID; Omada **ER605** Admin **`https://10.251.0.1/`** (Login-Seite OK; Passwort bei IT; `omadaer.net` FortiGuard-Block).
- [ ] **Netzwerk — Ist-Verkabelung vor Ort (KW nächste Woche):** Am Omada prüfen, ob weißer GL.iNet an **Port 4 oder 5 (FT LAN)** steckt (nicht Port 3 = LAN/Messe). Label am weißen GL historisch `PORT 3 TPLINK`; FT-Switch `FT PORT 4`. Bei Abweichung: umstecken + Labels korrigieren; Doku abhaken. Rückfrage an Dominik raus 04.09.2026. → [orbis-shopfloor-network-topology.md](../04-howto/setup/orbis-shopfloor-network-topology.md)
- *Rollen: GL.iNet weiß = DPS/FT-Gateway (Kabel+WLAN); GL.iNet grau = LTE→Omada WAN; Omada = WAN/LAN/FT-LAN + IPSEC C2S; Proxmox = DSP Edge im FT-LAN.*

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

- [Sprint 29](sprint_29.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md) · [test-coverage-status.md](../07-analysis/test-coverage-status.md) · [T&T Attribution / Language](../04-howto/osf-ui-track-trace-history-attribution.md) · [DSP-Tab Persistenz/UCs](../07-analysis/dsp-tab-persistence-use-cases-2026-09.md) · [UC-01 Persistenz-Lücken](../07-analysis/uc01-tt-persistence-gap-2026-09.md) · [Query-API V1](../04-howto/deployment/edge-persistence-query-api.md) · [Knowledge Graph PoC](../07-analysis/dsp-manufacturing-knowledge-graph-poc-2026-09.md)

---

*Stand: 04.09.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
