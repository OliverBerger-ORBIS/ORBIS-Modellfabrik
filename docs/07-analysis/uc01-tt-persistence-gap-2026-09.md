# UC-01 Track & Trace — Lückenanalyse MQTT/RAM vs. Hub-DB `osf_edge`

**Stand:** 2026-09-04  
**Sprint:** [sprint_30.md](../sprints/sprint_30.md)  
**Code geprüft:** `WorkpieceHistoryService` / `TrackTraceEvent`, Attribution-How-to, Persistence `normalizer.ts` / `nfc.ts` / `topics.ts`, Schema `db/mssql/002_schema.sql`, Grafana `workpiece-trace.json`  
**Rahmen:** [dsp-tab-persistence-use-cases-2026-09.md](dsp-tab-persistence-use-cases-2026-09.md)

Keine Umsetzung in diesem Dokument. Bühler-Demo unverändert (MQTT-T&T + Grafana).

---

## 1. Zwei Varianten (Entwicklung)

| Variante | Quelle | Rolle |
|----------|--------|--------|
| **A — MQTT** | `WorkpieceHistoryService` wie heute | bleibt; Live-Demo, Bühler, volle Heuristik |
| **B — DB** | Read-API auf `osf_edge` | parallel neu; Historie / DSP-UC / Uni-M |

Kein Ersatz von A durch B in Sprint 30. Langfristig kann B die UC-01-Quelle werden; bis dahin zwei Pfade.

---

## 2. Was die MQTT-Variante wirklich baut

T&T speichert **keine** MQTT-Rohzeilen. Der Service **leitet Genealogie ab**:

| Ableitung | Regel (kurz) | Wo |
|-----------|----------------|-----|
| Nur Modul-**FINISHED** | RUNNING wird verworfen | `updateWorkpieceHistoryFromModule` |
| FTS-Transport | Location-Wechsel **oder** Same-Node-DOCK; TURN-Remap an Intersection | `shouldEmitTransport` |
| NFC-first | Event gehört zum `loadId`; fremde FTS-`orderId` → `coPassenger` / `IST_ONLY` | Attribution §3, Dual-AGV 03.09. |
| Serial-first (Anzeige) | Transportgruppen nach FTS-Serial (`AGV-1`/`AGV-2`) | Attribution § Dual-AGV |
| Sticky loads | transient `loadId=null` auffüllen | Attribution § Sticky |
| HBW-Regal | Einlagerung vs. Auslagerung (`result` vs. Rest-`loads[]`) | Attribution § HBW |
| Intake | `osf/workpiece/intake` → Color + NFC-Zeilen; APS-RGB_NFC nicht | DR-30 |
| SOLL-Kette | **hardcoded** nach Farbe (BLUE DRILL→MILL→AIQS, …) + STORAGE/PRODUCTION | `getPlannedStationChain` |
| ENV | RAM-Snapshot nur an Anker-Events | Attribution §5 |
| Quality-Bild | Topic `/j1/txt/1/i/quality_check` (zeitlich um AIQS FINISHED) | `QUALITY_CHECK_TOPIC` |
| ERP-Felder | Process-Tab / Fake-IDs | `ErpOrderDataService` |

B3: Station-Spalte = Modul-MQTT; Transport-Spalte = FTS. Keine synthetisierten Stations-PICK/DROP vom FTS.

---

## 3. Was die Hub-DB wirklich speichert

Schreiber: `osf-edge-persistence` (MQTT subscribe → SQL). **Stateless** — kein Sticky, kein `coPassenger`, keine SOLL-Checklist.

### 3.1 Tabellen vs. T&T-Bedarf

| Tabelle | Inhalt | Für UC-01 |
|---------|--------|-----------|
| `workpiece` | NFC, Typ, last seen | Kachel-Liste |
| `shopfloor_event` | projizierte MQTT-Events + volles `payload_json` | Kern der Timeline |
| `shopfloor_order` | STORAGE/PRODUCTION, State, NFC | Order Context (ohne ERP-Fake) |
| `production_step` | CCU-Steps aus **completed** (nur bekannte `orderId`) | SOLL-Ist-Abgleich später; nicht die UI-Checklist |
| `env_sensor_snapshot` | Arduino/TXT, **ohne** NFC beim Ingest | ENV query-time (as-of) |
| `mqtt_raw_message` | Roharchiv | Debug, nicht erste Demo-Quelle |

### 3.2 Ingest-Verhalten (wichtig)

- **Jede** passende `module/…/state`, `fts/…/state`, `connection`, `order` erzeugt Zeilen — inkl. **RUNNING** und häufiger FTS-Positions-Ticks. Grafana filtert für Workpiece Trace auf `action_state = FINISHED`.
- NFC: `resolveWorkpieceId` (Intake `nfc`, CCU `workpieceId`, RGB_NFC/PICK/DROP `result`, einzelnes `loadId`). **Multi-Load FTS:** ein Event **pro** NFC in `load[]` — gut. **Kein Sticky:** `loadId=null` → oft **keine** NFC-Zeile.
- Intake: `event_type = WORKPIECE_INTAKE`, `action = intake` — **eine** DB-Zeile. UI macht daraus **zwei** Zeilen (Color + NFC).
- `fts/…/order` und `module/…/order` liegen in `shopfloor_event` (`payload_json` enthält TURN-Richtung).
- **Nicht subscribed:** `/j1/txt/1/i/quality_check`, `dsp/correlation/info`. Kamera ausgeschlossen (DR-28).

### 3.3 Grafana (Ist-Beweis, nicht T&T-Parität)

Dashboard Workpiece Trace: NFC + Farbe, nur **FINISHED**, Topics `module/%` / `fts/%` / completed MANUFACTURE, Station-Label aus Serial-Map (dieselbe wie `moduleSerialMap.ts`). Keine Mitfahrt, kein SOLL, kein ENV am Event, keine AGV-Buckets, kein Intake-Color/NFC-Split.

---

## 4. Lücken (MQTT-Genealogie − DB)

Schwere: **B** = Blocker für eine brauchbare UC-01-Historie · **V1** = erste DB-Variante darf fehlen · **L** = später / Uni-M.

| # | MQTT/UI | In der DB? | Schwere | Bemerkung |
|---|---------|------------|---------|-----------|
| 1 | Modul-Ist PICK/DRILL/MILL/CHECK_QUALITY/DROP FINISHED | ja, plus RUNNING-Rauschen | — | Filter `action_state = FINISHED` + `source = module` |
| 2 | Intake Color + NFC | ja, 1 Zeile `WORKPIECE_INTAKE` | V1 | API/UI splittet analog Bridge-Payload (`productRaw`, `nfc`) |
| 3 | Order-Typ STORAGE/PRODUCTION | `shopfloor_order.order_type` | — | Join über `order_id` |
| 4 | NFC-Liste / Kacheln | `workpiece` | — | |
| 5 | FTS-Transport (Location-Pfad, Intersections) | Roh-`fts/…/state` inkl. Ticks | **B** für volle Ist-Spur | UI filtert auf Location-Wechsel; Grafana-FINISHED-only **verliert** PASS/I-Nodes, wenn nicht FINISHED. V1: entweder FINISHED-DOCK/PASS/TURN **oder** Ableitung in der API (Location-Diff über sortierte FTS-Rows) |
| 6 | Sticky `loadId` | nein | V1 | Multi-Load-Lücken in der DB-Spur; MQTT-Variante bleibt Referenz |
| 7 | `coPassenger` / `visitKind` | nein | V1 | braucht CCU-`order.type` vs. Slot-Farbe + Workflow — Ableitung in API/UI, nicht Ingest |
| 8 | Serial-first Gruppen / AGV-Label | `module_serial` am Event | V1 | Layout-Map `5iO4`/`xkI4` bleibt Client oder API |
| 9 | TURN LEFT/RIGHT, DOCK@I→TURN | in `payload_json` / `fts/…/order` | V1 | Logik heute im Service; DB-Variante nachziehen oder erst ohne Richtung |
| 10 | HBW-Mini-Matrix | `payload_json.loads` | V1 | gleiche Attribution wie UI (Ein- vs. Auslagerung) — nicht im Normalizer |
| 11 | SOLL-Checklist | hardcoded UI | V1 | ohne DB rekonstruierbar (`order_type` + Farbe) |
| 12 | ENV am Anker | `env_sensor_snapshot`, NFC leer | V1 | Query-time as-of (SQL existiert Postgres-legacy; **T-SQL-Port offen**) |
| 13 | Quality-Bild | **nicht ingestiert** | L | Topic fehlt in `SUBSCRIBE_TOPICS` |
| 14 | ERP-PO/CO Fake | nein | L | Demo-Process-Tab; nicht Hub-SoT |
| 15 | `dsp/correlation/info` | nein | L | E2E weiter blocked |
| 16 | Dual-Wahrheit Heuristik | Ja: UI ≠ Normalizer | **B** für Parität | Ziel V1: **DB-Spur zeigen**, nicht 1:1 `WorkpieceHistoryService` nachbauen |

---

## 5. Empfohlene erste DB-Variante (Schnitt, nicht Code)

**Zielbild V1:** NFC wählen → Timeline **Station-Ist + Intake + Order-Klammern**, vergleichbar Grafana Workpiece Trace, in der OSF-UC-01-Oberfläche (eigene Quelle, MQTT-Komponente unangetastet).

**Lesen (API später, Vertrag jetzt):**

1. `GET /workpieces?from&to` → aus `workpiece` / distinct `shopfloor_event.workpiece_id`
2. `GET /workpieces/{nfc}/timeline?from&to` → `shopfloor_event` mit  
   `workpiece_id = nfc`  
   und (`event_type = WORKPIECE_INTAKE` **oder** (`action_state = FINISHED` und Topic `module/%` oder `fts/%`))  
   plus Join `shopfloor_order` für `order_type`
3. Mapping auf ein **schlankes** Event-DTO (nicht volles `TrackTraceEvent`): `ts`, `nfc`, `color`, `station`, `action`, `actionState`, `orderId`, `orderType`, `moduleSerial`, `eventSource` (`osf`/`module`/`fts`/`ccu`), `payload` optional

**Bewusst nicht in V1:** Sticky, Mitfahrt-Badges, ENV, Quality-Bild, ERP, Location-Diff-Transport in voller Attribution-Tiefe.

**Als Nächstes nach V1 (wenn MQTT-Referenz und DB-Spur am gleichen NFC verglichen wurden):** FTS-Location-Diff in der API **oder** Mitfahrt-Ableitung — erst nach empirischem Diff (Replay-Session mit bekanntem NFC, z. B. Dual-AGV-Ref `storage-wbr-dual-agv-rwb_20260903_094319`).

---

## 6. Read-API (V1, 04.09.2026)

Im Persistence-Service (HTTP, Port **3081**). How-to: [edge-persistence-query-api.md](../04-howto/deployment/edge-persistence-query-api.md).

**V1 lokal:** Replay → lokale SQL (`env.replay`) → Query-API `localhost:3081`. Referenz-Session `storage-wbr-dual-agv-rwb_20260903_094319`. How-to: [edge-persistence-query-api.md](../04-howto/deployment/edge-persistence-query-api.md). Check: `bash osf-edge-persistence/scripts/query-api-check-replay.sh --require`.

---

## 7. Was „Ingest an DSP übergeben“ nicht ist

Nicht Teil von UC-01 und nicht terminrelevant für Bühler/Uni-M-Workshop.

Heute schreibt **OSF** MQTT→`osf_edge`. DSP hat auf `.201` bereits SQL + DISI/DISC, schreibt `osf_edge` aber nicht. **Übergabe des Schreibers** (OSF-Service → DSP-Komponente) erst, wenn der **Lese-Vertrag** (Tabellen + API) steht — sonst bricht Grafana/UI/Uni-M beim Wechsel. Wer schreibt, ändert die Use-Case-Demos nicht, solange Schema und Queries gleich bleiben.

---

## 8. Offene Prüfungen (nicht raten)

- Live-`.201`: Anteil `FINISHED` vs. RUNNING/connection in `shopfloor_event` (Volumen).
- Ob FTS-PASS an Intersections als FINISHED ankommen (sonst V1-Transport dünn).
- T-SQL-Port `sensor_around_ist` vor ENV in der UI.

---

*Quellen: Attribution-How-to 03.09.2026 · DR-28/DR-30 · `normalizer.ts` 04.09.2026*
