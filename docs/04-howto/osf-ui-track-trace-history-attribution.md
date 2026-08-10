# Track & Trace: Historie-Attribution (Ist + SOLL + ENV)

**Stand:** 2026-08-06  
**Scope:** Live-Demo Track & Trace (`WorkpieceHistoryService` + `TrackTraceComponent`)  
**Architektur-Basis:** [DR-13 Track & Trace Architecture](../03-decision-records/13-track-trace-architecture.md)  
**Code:** `osf/apps/osf-ui/src/app/services/workpiece-history.service.ts`,  
`osf/apps/osf-ui/src/app/components/track-trace/`  
**SOLL-Checklisten je Farbe (visueller Test):** [osf-ui-track-trace-soll-by-color.md](osf-ui-track-trace-soll-by-color.md)

Dieses How-to beschreibt die **aktuellen Regeln**, damit spätere Sonderfälle (Mitfahrt, leere `loads[]`, Multi-AGV) nicht „neu erfunden“ werden. Bei Fixes: Regeln hier und Unit-Tests unter `workpiece-history.service.spec.ts` / `track-trace.component.spec.ts` mitziehen.

---

## 1. Leitprinzip: beides, nicht entweder-oder

| Spur | Bedeutung | Quelle der Wahrheit |
|------|-----------|---------------------|
| **SOLL** | Geplante Produktions-/Lagerkette des Werkstücks | Hardcoded Workflows → `plannedStationChain`; **Bearbeitung** nur aus **Modul-MQTT** |
| **Ist** | Tatsächlicher Weg inkl. Mitfahrer-Stops | **FTS** `load[]` → DOCK/PASS/TURN; fremde Stationen bleiben sichtbar |

**B3-Regel:** FTS **synthetisiert keine** Stations-PICK/PROCESS/DROP mehr. Station-Spalte = Modul-Events; Transport-Spalte = FTS.

---

## 2. Datenquellen (kurz)

| Stream | Topic-Muster | Was landet in der Historie |
|--------|--------------|----------------------------|
| FTS State | `fts/v1/ff/<serial>/state` | Pro beladenem Slot (`loadId` + Sticky) Transport-Events |
| Modul State | `module/v1/ff/<serial>/state` (+ NodeRed) | PICK / DRILL / MILL / CHECK_QUALITY / DROP / Color / NFC |
| Orders | **`ccu/order/active`** (+ completed) | **Phase** `orderType` STORAGE\|PRODUCTION je `orderId`; Feld **`type`** = Farbe; oft `workpieceId` = NFC |
| Umwelt | Arduino / BME / LDR Streams | Globaler Snapshot → an Events angehängt (Matrix) |

**Phase (Golden Path):** Event-`orderType` kommt primär aus CCU (`resolveCcuOrderType` / `orderId`).  
Location-Heuristik (`wasAtHbw`) nur Fallback — vermeidet Doppel-Lagerauftrag-Karten.

### Golden Path (Referenz: `*-storage-production_20260807_*` Pass; Fail: `*-storage-production-nok_20260807_*`)

**Storage:** DPS Color → DPS NFC (NFC = Historie-ID) → DPS DROP → FTS (DPS → Intersections → HBW) → HBW PICK  
**Production:** HBW DROP → FTS → Modul PICK/PROCESS/DROP (DRILL/MILL/AIQS je Farbe) → FTS → DPS PICK  

Dieselbe Systematik für alle Farben; Multi-Load = Spur **parallel je NFC**.

Serial→Station-Fallback (ohne Layout): `SVR4H76449`→DRILL, `SVR3QA2098`→MILL, `SVR4H76530`→AIQS, `SVR3QA0022`→HBW, `SVR4H73275`→DPS.

**Produktions-Workflows (SOLL-Kern):**

| Farbe | Fertigungsstationen |
|-------|---------------------|
| BLUE | DRILL → MILL → AIQS |
| WHITE | DRILL → AIQS |
| RED | MILL → AIQS (kein DRILL) |

Vollständige Kette im UI: `HBW` + Workflow + `DPS` (STORAGE: `DPS` → `HBW`).

Schritt-für-Schritt inkl. UI-/gap-/session-Markern: **[SOLL by color](osf-ui-track-trace-soll-by-color.md)**.

**Planned-Stations-Haken (Auftragskontext):** Modul-Flow-Anker auf der eigenen `orderId`. Zusätzlich für PRODUCTION **DRILL/MILL/AIQS**: realer **FTS-DOCK** am Werkstück (auch Mitfahrt) = physisch da — **kein** erfundenes MODULE/Quality.

---

## 3. FTS-Transport (Ist-Spur)

### Wann wird emittiert?

1. **Location-Wechsel** (`lastNodeId` geändert), oder  
2. **Same-Node DOCK** nach anderem Command (z. B. PASS → DOCK am gleichen Node) — damit „angedockt an Station X“ nicht verloren geht.

### Details auf dem Event

| Feld | Zweck |
|------|--------|
| `eventSource: 'FTS'` | Transport-Spalte |
| `details.loadPosition` | Slot dieses Werkstücks |
| `details.agvLoads` | **Alle** befüllten Slots `{ loadId, loadType, loadPosition }` |
| `details.intersectionNumber` | Intersection-Label (aus `AgvRouteService.resolveNodeRef`) |
| `details.visitKind` | `PLANNED` \| `IST_ONLY` |
| `details.coPassenger` | `true` bei Mitfahrt / fremder Order |

### Mitfahrt / Ist-only

`IST_ONLY` + `coPassenger`, wenn:

- Fertigungsstation **nicht** in der eigenen Workflow-Farbe liegt (z. B. RED @ DRILL), **oder**
- CCU-Order-`type` zur FTS-`orderId` **≠** `loadType` dieses Slots (z. B. BLUE auf AGV mit aktiver **RED**-Order @ MILL).

UI: Badge **Ist stop** (`getIstVisitBadge`). Location bleibt sichtbar; **kein** Modul-Prozess für den Mitfahrer.

### Multi-Load-Anzeige (AGV-Buckets)

Sobald MQTT mindestens einen befüllten Slot liefert (`agvLoads` oder Legacy-`loadPosition`): UI zeigt **immer Pos 1–3** horizontal (`getTransportLoadRows`). Fehlende Slots = **EMPTY** (`wp-slot-empty`).  
DOCK ohne jegliche Load-Info → keine Buckets. Intersection-Meta getrennt (`getTransportMetaLabel`).

FTS-Events: **zweispaltig** — links Load-Array, rechts kompakte Shopfloor-Preview (`getAgvEventShopfloorMiniMap`: Straßennetz + AGV-Punkt in AGV-Farbe).

### DOCK an Intersection → TURN

MQTT meldet oft `DOCK`, während `lastNodeId` noch I1–I4 ist (Anfahrt/Ausrichtung vor Rückwärts-Dock an die Station). Intersections können nicht docken → Historie speichert **TURN** (`remappedFromDockAtIntersection`, `originalCommand: DOCK`), **nur wenn** an dieser Intersection noch kein TURN existiert. Folge-`DOCK@I*` nach TURN wird unterdrückt (kein Doppel-TURN).

Gleicher TURN-`actionId` bei wechselndem `lastNodeId` (Fahrt nach der Drehung) wird nicht erneut emittiert; neuer TURN an derselben Node bei neuem `actionId` + `FINISHED` schon.

Drehrichtung LEFT/RIGHT kommt aus `fts/v1/ff/<serial>/order` (und optional `ccu/order/fts`) → `details.direction` → Icons `turnLeftEvent` / `turnRightEvent`.

### HBW Mini-Matrix

Bei MODULE **HBW PICK/DROP**: 3×3-Grid A1–C3 aus `details.hbwShelf` (Service speichert MQTT-`loads[]`-Snapshot; bei leerem DROP-FINISHED ggf. Last-Known-Shelf). Aktiver Slot (`loadPosition`) hervorgehoben; Text-`Position:`-Label entfällt.

### Sticky Slot-Occupancy (Ist, Multi-Load)

FTS liefert oft transient `loadId=null` bei weiterhin belegtem Slot (dabei bleibt `loadType` oft gesetzt).  
Service merkt sich letzte bekannte Identity je `(Environment, FTS-Serial, loadPosition)` und füllt **nur fehlende `loadId`**, wenn `loadType` noch passt.

| Situation | Verhalten |
|-----------|-----------|
| `loadId` + `loadType` gesetzt | Sticky lernen / ersetzen |
| `loadType` gesetzt, `loadId` null | Sticky-`loadId` gleicher Farbe → Event |
| Slot `(null, null)` | Sticky für Position **löschen**, **kein** Event |
| Slot fehlt in späterem nicht-leerem `load[]` | Sticky löschen |
| MODULE **HBW PICK** / **DPS PICK** FINISHED | Sticky für dieses NFC **überall** löschen |

**Nicht** mehr: leere Slots mit alter NFC weiterattributieren („prefer too many“) — das erzeugte bei Multi-Load Fake-FTS nach HBW-Abladung und falsche Co-Passenger-Anzeige.

### HBW Einlagerung / Auslagerung (Multi-Shelf)

| Vorgang | Fachlogik | MQTT | Attribution |
|---------|-----------|------|-------------|
| **Einlagerung** (STORAGE PICK) | erste freie Position A1…C3 | `loads[]` = ganzes Regal; oft **kein** `result` | CCU `order.workpieceId` / `order.type` — **nicht** erste `loadId` im Regal |
| **Auslagerung** (PRODUCTION DROP) | FIFO **pro Farbe** | `actionState.result` = bewegte NFC; `loads[]` = **Rest** im Regal | **`result` zuerst**; Position aus eigenem HBW-PICK / gemerktem Slot — **nie** Restregal-`loadPosition` |

### CHRG (Ladestation)

- Bestandteil des Shopfloors (`CHRG0`), **kein** Modul-MQTT.
- Sichtbar nur über **FTS** `lastNodeId` (typisch `DOCK @ CHRG0`).
- Immer **`visitKind: IST_ONLY`** (außerplanmäßig, nicht in SOLL-Kette).
- UI: Station-Icon `chrg-station.svg` in Location-Zeile / `getStationIcon('CHRG')`.

---

## 4. Modul-Attribution (SOLL-Bearbeitung)

Priorität beim Zuordnen eines Modul-Events zu einem Workpiece:

```
1) Explizite NFC in loads[] / metadata / RGB_NFC-Result
   → Historie für diese ID (anlegen falls nötig)
   → NIEMALS durch OrderId-Fallback überschreiben

2) loads[].loadType + passende History mit gleicher orderId

3) Leere loads[] (typisch DROP / Prozessende):
   a) CCU order.type zur module.orderId (Order-Farbe)
   b) findWorkpieceDockedAtModule:
      FTS-DOCK am Modul-Serial + gleiche orderId
      Prefer: nicht-coPassenger → planned Station → neuester DOCK
   c) sonst erster History-Treffer mit orderId (+ optional Type-Filter)
```

**Warum Order-Farbe?** Mitfahrer teilen oft dieselbe FTS-`orderId`. BLUE und RED haben beide MILL in der SOLL-Kette — ohne `order.type` würde Map-Reihenfolge / „beide planned“ Blue fälschlich Modul-MILL geben.

**Dedup:** gleiche `actionId` + Station + Workpiece (NodeRed vs. Direct Module) → ein Event.

---

## 5. ENV-Snapshots

Globaler Sensor-Stand (`TrackTraceEnvironmentService`) wird angehängt, wenn `shouldCaptureEnvironmentSnapshot` true ist — **nur Anker-Events**:

| Order | Station | Event-Typen |
|-------|---------|-------------|
| PRODUCTION | DRILL / MILL / AIQS | **DOCK**, **CHECK_QUALITY** |
| PRODUCTION | HBW | PICK, DROP |
| PRODUCTION | DPS | PICK, DROP |
| STORAGE | DPS | DROP |
| STORAGE | HBW | PICK |

**Nicht:** PASS/TURN, PROCESS/DRILL/MILL, Station-PICK an DRILL/MILL/AIQS, Intersection-only.  
UI zeigt ENV nur für `DOCK|PICK|DROP|CHECK_QUALITY` (`shouldDisplayEnvironmentSnapshot`); Default **kollabiert** (`Env · OK/WARN/ALARM · Zeit`), Expand → volle Sensor-Rows.

Mitfahrer: ENV hängt am **FTS-DOCK**-Event (Ist-Stop), nicht am fremden Modul-Prozess.

---

## 6. UI-Struktur

| Bereich | Inhalt |
|---------|--------|
| Order Context | Status, ERP-Felder, Route, **SOLL-Checklist** ✓/○ (`getPlannedStationChecklist` / Flow-Anker) |
| Business flow | SOLL-Chip (solid); ungeplante Ist-Stops als **dashed Chip** |
| Station | Modul-Events (+ Intake Color/NFC) |
| Transport | FTS zwischen geplanten Stationen **gruppiert** (Default kollabiert: `AGV · N · HBW→MILL`) |
| Environment | Snapshot @ Anker-Event (kollabiert) |

Flow-Anker (Checklist „visited“): z. B. PRODUCTION HBW←DROP, DRILL←DRILL/PROCESS, … — siehe `isFlowAnchorEvent`.

---

## 7. Bekannte Sonderfälle (Checkliste bei Bugs)

| Symptom | Wahrscheinliche Ursache | Wo schauen |
|---------|-------------------------|------------|
| Alles landet bei einer Farbe (oft Blue) | OrderId-Fallback / Map-Order ohne `order.type` | `findWorkpieceDockedAtModule`, `resolveOrderWorkpieceType` |
| White/Red nur AIQS, Rest fehlt | Modul-Events ohne NFC; Attribution falsch | empty `loads[]` Pfad |
| Extra SOLL-Station (z. B. MILL vor DRILL bei Blue) | Mitfahrt-Modul dem Co-Passenger zugeordnet | `coPassenger` + Order-Farbe |
| DOCK fehlt nach PASS | nur Location-Change emittiert | Same-Node-DOCK-Zweig |
| Kein ENV am Ist-Stop | Matrix ohne DOCK | `shouldCaptureEnvironmentSnapshot` |
| Multi-Load unsichtbar | `agvLoads` fehlt / UI nur Single-Path | FTS `details.agvLoads`, `getTransportLoadRows` (3 Buckets) |
| DOCK an Intersection | MQTT `DOCK` bei `lastNodeId` I1–I4 | Remap → TURN (`remappedFromDockAtIntersection`) |
| HBW ohne Regal-Übersicht | `hbwShelf` fehlt / UI nur Text-Position | MODULE `details.hbwShelf`, `getHbwMiniGrid` |
| Multi-Load: alle FTS-Events bei einem Werkstück | Sticky füllt leere Slots mit alter NFC | Sticky nur bei Type-only; Clear bei `(null,null)` / HBW\|DPS PICK |
| FTS nach HBW-Abladung in Storage | Sticky nicht geleert nach PICK / empty | `clearFtsStickyForLoadId` + empty-slot clear |
| HBW DROP/PICK bei falscher Farbe | `loads[]` = Regal-Rest; `result` ignoriert | `result` / `order.workpieceId` vor multi-shelf `loadId` |
| Storage-Transport fehlt (nur Type, kein Id) | FTS ohne `loadId` im Transit | Sticky bei gleichem `loadType` |
| CHRG ohne Icon / als „unbekannt“ | kein Modul-MQTT; Serial `CHRG0` | `MODULE_SERIAL_TYPES` + `getStationIcon('CHRG')` |
| Pflicht-Action fehlt trotz Shopfloor | Message fehlt in Session-Log (≠ Prozess) | Log/Message-Monitor; nicht als UI-Attribution werten |
| 2× Lagerauftrag / Prod dazwischen | Location-Heuristik `wasAtHbw` statt CCU-`orderType` | `resolveEventOrderType` + `toOrderIdMap(ccu/order/active)` |
| Doppelte Modul-Zeilen | NodeRed + Direct | Dedup `actionId` |
| Station-Namen null | Layout noch nicht geladen | `MODULE_SERIAL_TYPES` Fallback |
| „Wilde“ / doppelte Spuren über Sessions hinweg | NFC-TAGs wiederverwendet (vor eindeutigen Reads) | Neue Aufnahmen; alte Mixed-Logs nur begrenzt nutzen |
| Production-Stationen fehlen trotz Pass-Lauf | Session ohne `DRILL`/`MILL`/`AIQS` `/state` (Aufnahme-Lücke) | Inventar prüfen; z. B. `ml-wrb_114227` unvollständig → Replay `ml-wbr_*` |

**Abnahme-Regel (Pass, kein Quality-Fail):**  
Pro Farbe sollen `storage-production-ml-*` / `ml-*` Sessions **mindestens** so viele Station- und Transport-Events je Werkstück zeigen wie die Pass-Referenzen `*-storage-production_20260807_*`. Zu viele Ist-Events (Mitfahrt) sind ok; zu wenige nicht.

- Referenz Storage→Production Pass: `white|red|blue-storage-production_20260807_*.log`
- Referenz Storage→Production Fail: `white|red|blue-storage-production-nok_20260807_*.log`

**Empfohlene Replay-Sessions:**

- Referenz Storage→Production (eindeutige NFC, Arduino, Aug 2026): `*-storage-production_20260807_*.log` (Pass); `*-storage-production-nok_20260807_*.log` (Fail)
- **Multi-Load 1 AGV (07.08.2026):** `ml-wbr_…125133` (Pass), `ml-wrb-red-nok_…`, `ml-rbw-blue-nok_…`, `ml-wrb-chrg-blue-nok_…`
- **Multi-Load 1 AGV (04.08.2026, eindeutige NFC):** `ml-wbr_…115849` (Pass, vollständige Mfg-States — bevorzugte Mapping-Abnahme), `ml-wrb_…114227` (**unvollständig:** kaum DRILL/MILL/AIQS `/state`), `ml-brw_…121835` (Charge+RED-Fail), `ml-bwr_…131822` (OK), `ml-bwr_…130016` (Störfall DPS/FTS, behalten). **`ml-rrr_…133245`**, **`ml-bbb_…134700`**. Juli-Single-Color-Refs entfernt 10.08.2026; **2-AGV-Lücke** bis AGV-2-Reparatur (Interim: Stillstand + ein osf.4-WR).
- Parallel WR/RW/WB+R (Mai 2026): für Mitfahrt/Multi-AGV geeignet, aber **NFC-IDs können wiederverwendet** sein → Spuren teils „wild“
- Alte Mixed-Logs (`mixed-pw-*`, ältere `two-agvs-*`) nur noch begrenzt für Attribution nutzen

Unit-Regression: Specs `module attribution (no Blue steal)`, `FTS Ist stops`, ENV-Matrix, Multi-Load sticky (`loadId` omit mit Type; empty clear; HBW PICK clear).

---

## 8. Was bewusst nicht wieder eingeführt wird

- FTS-Synthese von Stations-PICK/PROCESS/DROP (widerspricht B3)
- Modul-Events dem Mitfahrer zuordnen, nur weil er „auch an der Station war“
- ENV an jedem PASS/Intersection (Rauschen)

Neue Sonderfälle: zuerst hier dokumentieren (Symptom → Regel → Test), dann Code.

---

## Referenzen

- [DR-13 Track & Trace Architecture](../03-decision-records/13-track-trace-architecture.md)
- [SOLL by color (visual / replay test)](osf-ui-track-trace-soll-by-color.md)
- Temporäre Inhalts-Analyse: [track-trace-live-content-fix-2026-07.md](../07-analysis/track-trace-live-content-fix-2026-07.md)
- Session-Inventar: `data/osf-data/sessions/INVENTORY.md`
- Sprint 27 Track&Trace-Themen: [sprint_27.md](../sprints/sprint_27.md)
