# Sprint 28 – Sessions komplettieren, 2. AGV & Grafana

**Zeitraum:** 07.08.2026 – 20.08.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 27](./sprint_27.md)

**Kurz:** Fokus **Referenz-Sessions** (Quality-Matrix, Multi-Load-Lücken, **2-AGV** nach FTS-2) und **Grafana** (Modus A / Panels / Persistenz). Arbeitszeit verkürzt durch **Urlaub 11.–14.08.**; Musashi-Vorführung durch **Sven Horras**.

**Kapazität:** Urlaub Oliver **11.–14.08.2026** → weniger Umsetzungstage; Priorität auf Sessions + Grafana, Carry-over nur bei Bedarf anfassen.

---

## Externe Termine & Outreach

*Kundentermine, Demos und Blog-Artikel — externe Wirkung / Umsatz-relevante OSF-Nutzung. Bei Sprint-Abschluss auch in [PROJECT_STATUS](../PROJECT_STATUS.md) → Spalte **Externe Events**.*

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **07.08.2026** | **Hochschulkontakt Kaiserslautern** — Herr **Nussbaum** (genaue Uni-/Hochschulbezeichnung folgt); Bachelorarbeit **Danil Wonkam** zu **Object Detection** | Abstimmung / Einordnung der BA im OSF-/Shopfloor-Kontext (OD; Anknüpfung an AI-HUB-/Session-Manager-OD-Pfad) |
| **11.–14.08.2026** | **Urlaub Oliver** | Reduzierte Sprint-Kapazität |
| **14.08.2026** | **Kundentermin Musashi** — Vorführung **Sven Horras** | Erstverifikation Router-/Netzwerk-Setup und Windows-Desktop-Praesentation (Follow-up LOM-Day); Oliver abwesend |
| *(offen)* | Hochschulkooperation — Kshitiz Proposal (Graph-DB Edge/DSP/KI) | Follow-up Teams 03.08. *(Sprint 27)* |

---

## Coverage Standing

| Stand | Datum | Branches | Functions | Lines | Statements | Gates (B/F/L/S) | Gate-Margin (B/F/L/S) |
|--------|--------|----------|-----------|-------|------------|------------------|------------------------|
| Sprint-Start (Baseline aus Sprint-27-Endmessung) | 06.08.2026 | 46.42% | 52.82% | 52.66% | 51.78% | 30 / 42 / 47 / 46 | +16.42 / +10.82 / +5.66 / +5.78 pp |
| Aktuell | 06.08.2026 | 49.75% | 61.25% | 66.67% | 65.58% | 42 / 52 / 58 / 58 | +7.75 / +9.25 / +8.67 / +7.58 pp |

- **Messmethode:** `npm run test:coverage` (seit 06.08.2026 mit `--runInBand`) → `coverage/osf-ui/index.html`. Details: [test-coverage-status.md](../07-analysis/test-coverage-status.md).
- **Top-3 Gaps (nach Option D):**
  1. `shopfloor-tab` — ~50 % Lines (noch größter Tab-Hotspot; DPS/Preview-Helfer ergänzt)
  2. DSP-/Customer-Pages — weiterhin oft **0 %**
  3. Einzelne UI-Komponenten mit niedriger Abdeckung
- **Pflege:** Baseline unverändert; nach Messung nur **Aktuell** + Top-Gaps aktualisieren. Am Sprintende Pflicht-Messung vor Abschluss.
- **Hinweis:** Jest-Gates 06.08. auf **42 / 52 / 58 / 58** angehoben; Langziel Lines 60 %+ weiter übertroffen.

---

## Aufgaben (thematisch, mit Haken)

### Sessions / Track&Trace-Referenz *(Fokus)*

- [x] **OSF-UI Deploy RPi (v1.2.2):** Image `orbis-osf-ui:1.2.2` auf Shopfloor-RPi (`npm run docker:osf-ui:deploy -- ff22@192.168.0.100`). How-to: [rpi-deployment.md](../04-howto/deployment/rpi-deployment.md). *(deployed 10.08.2026; `osf-ui-prod` Up, Compose `orbis-osf-ui:1.2.2`, http://192.168.0.100:8080 → 302)*
- [x] **T&T Replay-Abnahme (v1.2.2, 10.08.2026):** Quality-Check-Bild an `CHECK_QUALITY`; Session-Matrix Single/NOK/ml-* bei Replay **v=10** visuell OK (SM Fail=0). Matrix: [track-trace-heuristic-session-matrix-2026-08.md](../07-analysis/track-trace-heuristic-session-matrix-2026-08.md).
- [x] **Neue T&T-Sessions (Arduino-Schwellwerte + Aug-Set, 07./10.08.2026):** Vibration/ENV-Schwellwerte am Arduino hochgesetzt (kein Dauer-WARN). Single-Color **Pass+NOK W/R/B** und Multi-Load `ml-*_20260807_*` im Repo; Juli-Single-Color-Duplikate entfernt. Inventar: [INVENTORY.md](../../data/osf-data/sessions/INVENTORY.md); Matrix: [track-trace-heuristic-session-matrix-2026-08.md](../07-analysis/track-trace-heuristic-session-matrix-2026-08.md). *`ml-wrb_114227` bleibt als unvollständige Aufnahme dokumentiert — Abnahme über `ml-wbr_*`.*
- [x] **Teil B – 2-AGV T&T-Abnahme (Replay, 10.08.2026):** Interim-Sessions `two-agvs-mixed_20260312_165108` / `production-wr-agv2-b-agv1-clean_20260513_135600` — Darstellung plausibel, **beide AGVs erkannt und richtig zugeordnet**. Neue Aufnahme mit eindeutiger NFC **blockiert**: AGV-2 dockt trotz Motortausch M2/C2 (06.08.) und positivem Schnittstellentest **nicht an DPS** → **Reklamation an Fischertechnik**. *(Ursprung: Sprint 27)*
- *Hinweis Demo: Capture läuft in Live/Replay nach MQTT-Connect auch ohne offenen Tab; Header-Refresh leert die Historie — dazwischen nicht unnötig refreshen.*

### Grafana Dashboard *(Fokus)*

- [ ] **Modus A (Replay + Session):** Grafana `localhost:3000` mit Session-Replay erneut pruefen — Orders/Daten sichtbar; Abweichungen in Troubleshooting dokumentieren. *(Ursprung: Sprint 22; siehe [runtime-modes-matrix.md](../04-howto/helper_apps/session-manager/runtime-modes-matrix.md))*
- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad). *(Ursprung: Sprint 22)*
- [ ] **Track&Trace Persistenz (Option B):** UI-Historie bleibt session-/RAM-scoped; längere NFC-Spuren über Edge/Grafana (`osf-edge-persistence`, [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)) — kein Browser-localStorage. *(Entscheidung 21.07.2026; Ursprung: Sprint 26)*

### Integration & Tests

- [x] **Use-Case-SVG/Pages — erste Specs (kein Fokus-Thema):** Smoke-/Unit-Tests für `applyStepToSvg`, UC-01…05/07 SVG-Generatoren, BaseUseCase via Interoperability, UseCaseControls, Selector-Page. Coverage runInBand 06.08.: Lines **64.65 %** (Baseline 52.66 %). *(Sprint 28; [test-coverage-status.md](../07-analysis/test-coverage-status.md))*
- [x] **Coverage Option D (06.08.2026):** Jest-Gates → **42/52/58/58**; Shopfloor-Tab DPS/Preview-Helfer; Track&Trace-UC-Shell + UC-02 Lanes. Messung: Lines **66.67 %**, Branches **49.75 %**. *(Sprint 28)*
- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### ORBIS Feldbetrieb / Hardware

- [x] **Kontrolle FTS Nr. 2 — Motortausch (06.08.2026):** Rechter Vorderradantrieb **M2/C2** ausgefallen (langsam → Totalausfall); Mechanik OK; ~8 V am Kabel; Ersatzmotor vor Einbau am M2-Kabel OK → Tausch. Schnittstellentest: **alle 4 Antriebe** laufen. **Nachtest (10.08.):** Andocken an DPS weiterhin **nicht** möglich → AGV-2 zur **Reklamation an Fischertechnik**. How-to: [fts-agv-encoder-motor-replacement.md](../05-hardware/fts-agv-encoder-motor-replacement.md). *(Ursprung: Sprint 26)*

### Router / Netzwerk-Setup

- [ ] **Netzwerk-Topologie/Verkabelung (Rest):** ORBIS-LAN-Adressliste + MES-Pfad mit Netzwerk-Kollegen (**nur mit ORBIS-VPN testbar**); Omada Admin-URL/Modell; ggf. HTML neu exportieren. *(Ursprung: Sprint 26)*
- *Rollen: GL.iNet weiß = DPS/FT-Gateway; GL.iNet grau = LTE→Omada WAN; Omada = WLAN + Port-Hub; Proxmox = DSP Edge im FT-LAN. How-to: [orbis-shopfloor-network-topology.md](../04-howto/setup/orbis-shopfloor-network-topology.md).*

### Blog & Organisation

- [ ] Blog: Review A3 *(Von Daten zu belastbaren KPIs)* *(Ursprung: Sprint 19 / 26)*
- [ ] Blog: Review A4 *(Von Erkenntnissen zu Aktionen)* *(Ursprung: Sprint 19 / 26)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] **Coverage Standing:** Endmessung (`npm run test:coverage`) → `Aktuell` + Top-Gaps; Analyse-Doku bei Bedarf aktualisieren *(Pflicht vor Abschluss)*
- [ ] Sprint 28: Status Abgeschlossen, Datum
- [ ] Sprint 29 anlegen, offene `[ ]` uebernehmen; Coverage-Baseline = Endmessung Sprint 28
- [ ] PROJECT_STATUS / Roadmap kurz

---

## Links

- [Sprint 27](sprint_27.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md) · [test-coverage-status.md](../07-analysis/test-coverage-status.md)

---

*Stand: 06.08.2026 (FTS-2 Motor OK)* · Doku-Workflow: [sprints_README.md](sprints_README.md)
