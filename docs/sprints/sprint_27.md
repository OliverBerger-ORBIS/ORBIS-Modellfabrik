# Sprint 27 – Grafana-Dashboard-Analyse & Track&Trace

**Zeitraum:** 24.07.2026 – 06.08.2026 · **Status:** Laufend · **Vorheriger Sprint:** [Sprint 26](./sprint_26.md)

**Kurz:** Fokus **Grafana-Dashboard-Analyse** (Modus A / Panels / Persistenz-Pfad) in Kombination mit offenen **Track&Trace**-Tasks (Live-Demo Inhalt, Edge-Persistenz Option B); Carry-over Netzwerk, FTS Nr. 2, Blog A3/A4 und Integrations-Nachweise.

---

## Externe Termine & Outreach

*Kundentermine, Demos und Blog-Artikel — externe Wirkung / Umsatz-relevante OSF-Nutzung. Bei Sprint-Abschluss auch in [PROJECT_STATUS](../PROJECT_STATUS.md) → Spalte **Externe Events**.*

| Datum | Event | Nutzen fuer OSF |
|--------|--------|----------------|
| **23.07.2026** | **Blog A2** veröffentlicht — [Track und Trace in der Fertigung](https://www.orbis-group.com/de-de/blog/branchen/manufacturing/track-und-trace-in-der-fertigung/) | Storytelling-Serie A2 live *(Sprint 26)* |
| **geplant** | **Hochschulkooperation** — Kshitiz Bohara (Doktorand, Uni Magdeburg): GenAI / Agentic AI im Umfeld SmartFactory, MES, DSP | Möglicher erster Use Case: semantisch gestützte Analyse von Track-&-Trace- und Qualitätsereignissen. **Offen:** strategische Abstimmung innerhalb ORBIS nach dem ersten Kennenlerngespräch |
| **14.08.2026** | **Kundentermin Musashi** | Erstverifikation Router-/Netzwerk-Setup und Windows-Desktop-Praesentation (Follow-up LOM-Day; verschoben von 14.07.) |

---

## Aufgaben (thematisch, mit Haken)

### Grafana Dashboard *(Fokus)*

- [ ] **Modus A (Replay + Session):** Grafana `localhost:3000` mit Session-Replay erneut pruefen — Orders/Daten sichtbar; Abweichungen in Troubleshooting dokumentieren. *(Ursprung: Sprint 22; Nachfolger „keine orders“; siehe [runtime-modes-matrix.md](../04-howto/helper_apps/session-manager/runtime-modes-matrix.md))*
- [ ] Grafana-Dashboards ausbauen (fachliche Panels schaerfen, offene Visualisierungs-/Abnahmepunkte systematisch schliessen). *(Ursprung: Sprint 22)*
- [ ] Deployment vorbereiten: Grafana + Persistence-Stack auf DSP-Docker lauffaehig machen (neben local-dev als naechster Zielpfad). *(Ursprung: Sprint 22)*
- [ ] **Track&Trace Persistenz (Option B):** UI-Historie bleibt session-/RAM-scoped; längere NFC-Spuren über Edge/Grafana (`osf-edge-persistence`, [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)) — kein Browser-localStorage. *(Entscheidung 21.07.2026; Ursprung: Sprint 26)*

### Track&Trace *(Fokus)*

- [x] **Track&Trace A1 Multi-Order (28.07.2026):** `WorkpieceHistoryService` rebuildet Auftragskontexte aus **allen** Event-Order-UUIDs → STORAGE **und** PRODUCTION als Business-Klammern. Unit-Tests grün. Verifikation: Replay `*-storage-production_20260728_*.log` + Live Demo (Hard-Reload).
- [x] **Track&Trace Live Demo Inhalt Phase 1 B1+C1+S1 (28.07.2026):** Publisher-Badge FTS/Module; Sub-Order-Gruppen nach `min(timestamp)`; STORAGE-Sensor an DPS DROP + HBW PICK. Replay-Check: `*-storage-production_20260728_*`.
- [x] **Track&Trace Modul-Events erweitern (Antwort A, 28.07.2026):** Color/NFC; DRILL/MILL/CHECK_QUALITY als Event-Namen (nicht generisches PROCESS); HBW-Position als „Position in HBW: A1“. Fixes 28.07. abends: Color chronologisch zuerst, kein doppeltes NFC, Flush nur bei RGB_NFC.
- [x] **Track&Trace Live Demo Inhalt Phase 2 B3 (28.07.2026):** FTS-Stationssynthese ab; Modul = SoT für PICK/DRILL/MILL/DROP. UI: Spalten **Station | Transport**; DPS-Besuch eine Gruppe; Order Context max. 1× STORAGE + 1× PRODUCTION.
- [x] **Sensor-Matrix STORAGE korrigieren (28.07.2026):** Umwelt-Snapshots an **DPS DROP** + **HBW PICK** (S1 mit Phase-1-Bundle).
- [x] **Track&Trace Phase 3 (29.07.2026):** Sensor-Matrix PRODUCTION erweitert: **HBW DROP** + **DPS PICK** → Environment-Snapshot. Transport-Events: **Intersection N**-Label + Location-Icon vor Position; Bucket-Slot mit Werkstück-Farbe (`Position: 1 (BLUE)`). `intersectionNumber` aus `AgvRouteService.resolveNodeRef` in FTS-Event-Details persistiert. CHECK_QUALITY: **Ergebnis-Badge** (OK/FAILED) aus `details.result` im Timeline-Event. Unit-Tests 77/77 grün.
- [x] **Session Manager Replay Speed 10x/max (29.07.2026):** Replay Station Geschwindigkeit um **10x** und **max** (ohne Wartezeit) erweitert; Timeshift bleibt load-time (`now + ts_rel`), Speed skaliert nur Wall-Clock-Wartezeit. Version **1.8.0** (`session_manager/__init__.py`). Tag nach Commit: `session-manager-v1.8.0`.
- [x] **Session Manager Replay Speed Fix/Diagnose (29.07.2026):** Speed wirkte nicht 10× — Ursachen: Selectbox/Rerun instabil + MQTT-QoS1-Backpressure (Burst dann ~50–80 msg/10s). Fix: stabile Speed-Labels, ab ≥5×/max **QoS0**, Queue/Retry, Publish-Rate-Diagnose in UI. Version **1.8.1**. **1.8.2:** zusätzlich **Gesamtzeit** (aktiv/Wanduhr) + **Ø-Rate** über den ganzen Lauf (Momentan-Rate schwankt bei V=1 stark).
- [x] **Replay-Referenz-Sessions aufgenommen (28.07.2026):** `white|red|blue-storage-production_20260728_*.log`. Alte Single-Color-`20260303`-Paare **gelöscht** (28.07.). Parallel-Production (`production-wr-*`) ohne Storage in derselben Session ausreichend für Multi-AGV-Herausforderungen, sobald Multi-Order an den drei Referenzen steht.
- *Hinweis Demo: Capture läuft in Live/Replay nach MQTT-Connect auch ohne offenen Tab; Header-Refresh leert die Historie — dazwischen nicht unnötig refreshen.*
- *Replay-Hinweis (28.07.): `mixed-pw-…` zu komplex für Erstanalyse; `od_white_1` unvollständig (nur STORAGE). Details in Arbeitsdoku.*

### Shopfloor / Message Monitor

- [x] **Module/AGV-Filter an Layout-Registry (28.07.2026):** Message-Monitor Dropdown aus `shopfloor_layout` (Serial→Typ); FTS als **AGV-1/AGV-2** + FTS-Langname; Live ohne `HBW-DEMO`/`*-MISSING`; case-insensitive Serial-Lookup. Verifikation: localhost Live + RPi Hard-Reload.
- [x] **Layout-Cache-Bust (28.07.2026):** RPi zeigte keine FTS trotz Layout mit `fts[]` — nginx `application/json` max-age ~10y. Fix: nginx epoch + `shopfloor_layout.json?v=<VERSION>` (v1.1.12). **Verifiziert RPi Hard-Reload:** Shopfloor + Message-Monitor zeigen AGV-1/AGV-2.

### Router / Netzwerk-Setup

- [ ] **Netzwerk-Topologie/Verkabelung (Rest):** ORBIS-LAN-Adressliste + MES-Pfad mit Netzwerk-Kollegen (**nur mit ORBIS-VPN testbar**); Omada Admin-URL/Modell; ggf. HTML neu exportieren. *(Ursprung: Sprint 26)*
- *Rollen: GL.iNet weiß = DPS/FT-Gateway; GL.iNet grau = LTE→Omada WAN; Omada = WLAN + Port-Hub; Proxmox = DSP Edge im FT-LAN. How-to: [orbis-shopfloor-network-topology.md](../04-howto/setup/orbis-shopfloor-network-topology.md).*

### ORBIS Feldbetrieb / Hardware

- [ ] **Kontrolle FTS Nr. 2 (Folgeprüfungen):** RoboPro-Schnittstellen-Test (23.07.) → Multimeter-Test **27.07.2026**: **Encoder-Motor defekt** (nicht Kabelbruch). Nächster Schritt: **Ersatzteile oder Reparatur**, Rücksprache bei **fischertechnik**. *(Ursprung: Sprint 26; TXT-Projekte lokal unter `integrations/`)*

### Integration & Tests

- [ ] **UI-Test-Framework (Fortsetzung):** von 2 Pilot-Tests zu stabiler Abdeckung kritischer Flows mit Tier A + Tier B Nachweisen ausbauen. *(Ursprung: Sprint 21)*
- [ ] **dsp/correlation/info** E2E (BLOCKED bis Team-Setup aktiv): End-to-End-Nachweis (Topic-Eingang + UI-Kontext) dokumentieren. *(Ursprung: Sprint 18)*
- [ ] **ccu/order/request** E2E (Ersatzauftrag nach Quality-Fail, BLOCKED bis Team-Setup aktiv): E2E-Nachweis mit klarer Ereigniskette dokumentieren. *(Ursprung: Sprint 18)*

### Blog & Organisation

- [ ] Blog: Review A3 *(Von Daten zu belastbaren KPIs)* *(Ursprung: Sprint 19 / 26)*
- [ ] Blog: Review A4 *(Von Erkenntnissen zu Aktionen)* *(Ursprung: Sprint 19 / 26)*
- [ ] Azure DevOps: Repo/Boards von GitHub *(Ursprung: Sprint 19)*

### Sprint-Wechsel (am Ende des Sprints abarbeiten)

- [ ] Sprint 27: Status Abgeschlossen, Datum *(Ursprung: Sprint 27)*
- [ ] Sprint 28 anlegen, offene `[ ]` uebernehmen *(Ursprung: Sprint 27)*
- [ ] PROJECT_STATUS / Roadmap kurz *(Ursprung: Sprint 27)*

---

## Links

- [Sprint 26](sprint_26.md) · [PROJECT_STATUS.md](../PROJECT_STATUS.md) · [sprints_README.md](sprints_README.md)

---

*Stand: 29.07.2026* · Doku-Workflow: [sprints_README.md](sprints_README.md)
