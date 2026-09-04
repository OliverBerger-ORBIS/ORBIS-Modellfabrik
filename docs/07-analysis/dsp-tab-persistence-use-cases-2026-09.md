# DSP-Tab: Präsentation vs. APS-Live — Persistenz in Use-Case-Demos

**Stand:** 2026-09-04  
**Sprint:** [sprint_30.md](../sprints/sprint_30.md) — Roadmap-Konzept (keine Tab-Umbauten)  
**Bezug:** [DR-22](../03-decision-records/22-dsp-use-case-konzept-live-demo.md) · [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md) · [Use-Case-Bibliothek](../02-architecture/use-case-library.md) · [Knowledge Graph PoC](dsp-manufacturing-knowledge-graph-poc-2026-09.md)

---

## Entscheidung (geschärft)

OSF-UI enthält **zwei verschiedene Produkte in einer Shell**:

| Bereich | Charakter | Daten | Paradigmen |
|---------|-----------|-------|------------|
| **APS-Tabs** (Shopfloor, Orders, AGV, Stationen, Sensoren, …) | Fischertechnik-Modellfabrik, operativ | **Nur Live / MQTT** | bleiben: MessageMonitor, RAM, keine Edge-DB |
| **DSP-Tab + Kinder** (Use-Cases **inkl. UC-01 Track & Trace**, Architecture, Customer) | **Präsentationsfläche für DSP** — Inhalte sind sonst schwer erklärbar | **pro Use-Case:** MQTT und/oder Hub-DB | **dürfen brechen** |

**Track & Trace ist ein DSP-Use-Case**, kein APS-Tab. Die Nav-Kachel „T&T“ in der Shell ist dieselbe UC-Oberfläche (heute MQTT/RAM) — nicht eine zweite Fischertechnik-Wahrheit, die dauerhaft MQTT-only bleiben muss. **Langfristig kommt UC-01 aus der Hub-Persistenz.**

Der DSP-Tab ist **herauslösbar**: APS-Tabs funktionieren ohne ihn. Language-Reload der **APS-Live-Tabs** bleibt Workaround. Für T&T ist Persistenz der eigentliche Weg, nicht ein SQL-Hydrate der Shopfloor-Ansicht.

**Wer schreibt** MQTT→DB (heute OSF Persistence-Service, Ziel DSP/DISC) ist **sekundär**. Stabil muss der **Lese-Vertrag** sein — denselben nutzen Grafana, DSP-Use-Case-Demos und Uni Magdeburg.

---

## Zwei Welten

```
APS-Tabs (Fischertechnik-Live): Shopfloor, Orders, AGV, Stationen, Sensoren
  MQTT .100  →  MessageMonitor
  Kein SQL.

DSP-Tab (Präsentation / Demo), inkl. UC-01 T&T
  Concept = SVG-Story
  Demo    = je UC die passende Quelle:
              MQTT  wenn Realtime die Story ist (z. B. Anomaly / UC-07)
              SQL   wenn Historie / Korrelation / KPI die Story ist (z. B. T&T / UC-01)
              beides, wenn die Story beides braucht
```

**Heute (Übergang):** UC-01 „Live Demo“ und die Shell-Kachel T&T nutzen dieselbe MQTT/RAM-Komponente (`TrackTraceTab` / `WorkpieceHistoryService`). Das ist die aktuelle Live-Demo, **nicht** das Zielbild. Ziel: dieselbe T&T-Oberfläche (DSP-UC) **aus `osf_edge`**, MQTT höchstens als Live-Ergänzung — analog „Historie ist die DSP-Story“.

---

## Persistenz gehört zum DSP-Hub

DSP-Edge-Komponente **Database** (plus DISI/DISC) ist der Integrations-Hub. Auf `.201` läuft bereits SQL Server; OSF schreibt in die DB `osf_edge` auf **derselben Instanz**. DSP-Runtime (Agent, DISI, DISC) bleibt unberührt.

- **Schreiber heute:** `osf-edge-persistence` (MQTT read-only → SQL). Platzhalter, austauschbar.
- **Schreiber Ziel:** DSP-Komponente (DISC o. ä.) — Sprint-18-Backlog, unverändert gültig.
- **Engine:** SQL Server reicht für Demo-/PoC-Volumen. Timescale war ein Mai-Entwurf; August-Wechsel auf MSSQL war die **Annäherung an DSP**, kein Rückschritt. Eigene Timeseries-DB nur bei nachgewiesenem Bedarf (Uni-M / Volumen).

Leser (gleiche Tabellen, unterschiedliche UI):

| Leser | Zweck |
|-------|--------|
| Grafana `:3000` | Analytics, Ingest-Beweis (ist da) |
| DSP Use-Case-Demos in OSF-UI | erklärbare DSP-Story (nächste Arbeit) |
| Uni Magdeburg Knowledge Graph | lesender PoC, additiv (21./22.09.) |

---

## Quelle je Use-Case (Empfehlung)

Nicht ein History-Backend für alles. **Pro UC die Quelle, die die Story trägt.**

| UC | Story | Primärquelle Demo | Ist heute |
|----|--------|-------------------|-----------|
| **UC-00** Interoperability | Event→Prozess, Konzept | Concept-SVG; DB später für Event-Ketten | nur Concept |
| **UC-01** Track & Trace | Genealogie über Zeit, NFC | **DB** (`workpiece`, `shopfloor_event`, `shopfloor_order`) — Zielbild | MQTT/RAM-Komponente (Shell-Tab + UC Live Demo); Persistenz noch nicht angebunden |
| **UC-02** Three Data Pools | Aggregation Shopfloor/Umwelt/(Biz) | **DB** (unprefixed Shopfloor + `env_*`) | nur Concept |
| **UC-03** AI Lifecycle | später KG / Uni-M | DB + Graph (Folge) | nur Concept |
| **UC-04** Closed Loop Quality | Qualität über Aufträge | **DB** (AIQS/Quality-Events) | nur Concept |
| **UC-05** Predictive Maintenance | Datenbasis + Prognose-Story; Alarm-Simulation extra | **DB** für Zeitreihe/Kontext; MQTT nur für Demo-Trigger (besteht) | Concept + MQTT `simulateDanger` |
| **UC-06** Process Optimization | KPI→Aktion | **DB** / Grafana-KPIs | nur Concept |
| **UC-07** Anomaly Detection | akuter Alarm → DSP → CRM | **MQTT (Realtime)** | Concept; Live-Button noch `disabled` |

Entwicklung: **MQTT-Variante bleibt**, DB-Variante **parallel** (siehe Lückenanalyse). Langfristig kann die UC-01-Quelle die Hub-DB sein; kein Ersatz der Live-MQTT-Strecke vor V1-Vergleich.

---

## Lese-Vertrag (Hub-DB `osf_edge`)

Kein Grafana-JSON als UI-API. Feste Tabellen, später dünne Read-API auf `.201` (Schreiber austauschbar).

| Tabelle | Für |
|---------|-----|
| `workpiece` | NFC-Identität, Typ, last seen |
| `shopfloor_event` | Ist-Events (Station/FTS, `workpiece_id`, `order_id`, `action`) |
| `shopfloor_order` | STORAGE/PRODUCTION, State |
| `production_step` | Soll-Schritte |
| `env_sensor_snapshot` | Umwelt/Arduino, `reason` EVENT/INTERVAL/THRESHOLD |
| `mqtt_raw_message` | Roharchiv / Debug, nicht erste Demo-Quelle |

Korrelation: **NFC** (`workpiece_id`) wie DR-28/DR-30. Sensor↔Werkstück query-time (as-of), nicht beim Ingest.

Transport für OSF-UI Use-Cases: erstes Häppchen eine **read-only Query-API** (HTTP) gegen `.201`, nicht Direct-SQL aus dem Browser. Replay lokal analog (`env.replay` / Dev-SQL), Live nur `.201`.

---

## Uni Magdeburg

Gleicher Lese-Schnitt, nicht die APS-Tabs.

- PoC **additiv/lesend**; Knowledge Graph liegt **auf** Events/Werkstücken/Sensoren, ersetzt sie nicht.
- Erster Schnitt: `shopfloor_event` + `workpiece` + `env_sensor_snapshot` (gleiche Reihenfolge wie UC-01 / UC-05).
- MQTT nur wo Realtime nötig ist (Alarm-Story) — analog UC-07.
- Rollen: Kshitiz Technik; ORBIS Fachkontext + Zugang zur Hub-DB / API.

---

## Bewusst nicht

- Shopfloor / Orders / AGV aus SQL hydrieren (bleiben MQTT-Live).
- T&T dauerhaft als „APS-MQTT-Tab“ festschreiben — das wäre die falsche Zuordnung.
- MQTT-T&T abschalten, bevor die DB-Variante am gleichen NFC verglichen wurde.
- Timescale als Muss.

---

## Nächste Schritte (Umsetzung = Folge-Sprints)

1. ~~Lückenanalyse UC-01~~ → [uc01-tt-persistence-gap-2026-09.md](uc01-tt-persistence-gap-2026-09.md)
2. Dünne Read-API auf `.201` — **V1 umgesetzt (04.09.2026):** Persistence-Container Port **3081**, `GET /v1/workpieces`, `GET /v1/workpieces/{nfc}/timeline`. How-to: [edge-persistence-query-api.md](../04-howto/deployment/edge-persistence-query-api.md). Deploy: Persistence-Image auf VE neu bauen.
3. UC-01 **DB-Variante parallel** zur MQTT-Variante (V1-Timeline)
4. UC-05: Sensor-Zeitreihe aus DB; MQTT-Trigger behalten
5. UC-07: Live-Alarm über MQTT
6. Ingest-Schreiber OSF → DSP erst nach stabilem Lese-Vertrag (kein Demo-Thema)

Sprint 30: dieses Papier; Demos Bühler/Welcome Days mit APS-Live + Grafana; Uni-MD 21./22.09. mit Hub-DB-Story.
