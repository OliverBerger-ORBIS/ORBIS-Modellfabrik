# Track & Trace: Historie-Attribution (Ist + SOLL + ENV)

**Stand:** 2026-07-30  
**Scope:** Live-Demo Track & Trace (`WorkpieceHistoryService` + `TrackTraceComponent`)  
**Architektur-Basis:** [DR-13 Track & Trace Architecture](../03-decision-records/13-track-trace-architecture.md)  
**Code:** `osf/apps/osf-ui/src/app/services/workpiece-history.service.ts`,  
`osf/apps/osf-ui/src/app/components/track-trace/`

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
| FTS State | `fts/v1/ff/<serial>/state` | Pro beladenem Slot (`loadId` + `loadType`) Transport-Events |
| Modul State | `module/v1/ff/<serial>/state` (+ NodeRed) | PICK / DRILL / MILL / CHECK_QUALITY / DROP / Color / NFC |
| Orders | `ccu/order/active` (+ completed) | Order-Kontext; Feld **`type`** = Werkstückfarbe (BLUE/WHITE/RED) |
| Umwelt | Arduino / BME / LDR Streams | Globaler Snapshot → an Events angehängt (Matrix) |

Serial→Station-Fallback (ohne Layout): `SVR4H76449`→DRILL, `SVR3QA2098`→MILL, `SVR4H76530`→AIQS, `SVR3QA0022`→HBW, `SVR4H73275`→DPS.

**Produktions-Workflows (SOLL-Kern):**

| Farbe | Fertigungsstationen |
|-------|---------------------|
| BLUE | DRILL → MILL → AIQS |
| WHITE | DRILL → AIQS |
| RED | MILL → AIQS (kein DRILL) |

Vollständige Kette im UI: `HBW` + Workflow + `DPS` (STORAGE: `DPS` → `HBW`).

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

### Multi-Load-Anzeige

Wenn `agvLoads.length >= 1`: einheitliche Zeilen  
`Position N (COLOR)` mit Werkstück-Icon (`getTransportLoadRows`).  
Intersection-Meta getrennt (`getTransportMetaLabel`).

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

Globaler Sensor-Stand (`TrackTraceEnvironmentService`) wird angehängt, wenn `shouldCaptureEnvironmentSnapshot` true ist:

| Order | Station | Event-Typen |
|-------|---------|-------------|
| PRODUCTION | DRILL / MILL / AIQS | PROCESS, DRILL, MILL, CHECK_QUALITY, **DOCK** |
| PRODUCTION | HBW | PICK, DROP |
| PRODUCTION | DPS | PICK, DROP |
| STORAGE | DPS | DROP |
| STORAGE | HBW | PICK |

**Nicht:** PASS/TURN, DRILL-PICK, Intersection-only.  
Sensoren sind vorerst **global** (Näherung); Location-Bezug später.

Mitfahrer: ENV hängt am **FTS-DOCK**-Event (Ist-Stop), nicht am fremden Modul-Prozess.

---

## 6. UI-Struktur

| Bereich | Inhalt |
|---------|--------|
| Order Context | Status, ERP-Felder, Route, **SOLL-Checklist** ✓/○ (`getPlannedStationChecklist` / Flow-Anker) |
| Business flow | Chip nur bei SOLL-Stationsbesuch (Modul-Anker) |
| Station | Modul-Events (+ Intake Color/NFC) |
| Transport | FTS DOCK/PASS/TURN (+ Ist-stop Badge) |
| Environment | Snapshot @ Event |

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
| Multi-Load unsichtbar | `agvLoads` fehlt / UI nur Single-Path | FTS `details.agvLoads`, `getTransportLoadRows` |
| Multi-Load: alle FTS-Events bei einem Werkstück | Mapping `loadId`→Historie fehlerhaft (FTS liefert alle IDs) | `updateWorkpieceHistory` forEach; Regression `storage-production-ml-wrb|wbr_*` |
| Doppelte Modul-Zeilen | NodeRed + Direct | Dedup `actionId` |
| Station-Namen null | Layout noch nicht geladen | `MODULE_SERIAL_TYPES` Fallback |
| „Wilde“ / doppelte Spuren über Sessions hinweg | NFC-TAGs wiederverwendet (vor eindeutigen Reads) | Neue Aufnahmen; alte Mixed-Logs nur begrenzt nutzen |

**Empfohlene Replay-Sessions:**

- Referenz Storage→Production (eindeutige NFC, Arduino): `*-storage-production_20260728_*.log`
- **Multi-Load 1 AGV (04.08.2026, eindeutige NFC):** `ml-wrb_…114227`, `ml-wbr_…115849`, `ml-brw_…121835` (Charge+RED-Fail), `ml-bwr_…131822` (OK), `ml-bwr_…130016` (Störfall DPS/FTS, behalten). **`ml-rrr_…133245`**, **`ml-bbb_…134700`**. Inventar-Cleanup 05.08.: alte vergleichbare Logs entfernt; **2-AGV-Lücke** bis AGV-2-Reparatur (Interim: Stillstand + ein osf.4-WR).
- Parallel WR/RW/WB+R (Mai 2026): für Mitfahrt/Multi-AGV geeignet, aber **NFC-IDs können wiederverwendet** sein → Spuren teils „wild“
- Alte Mixed-Logs (`mixed-pw-*`, ältere `two-agvs-*`) nur noch begrenzt für Attribution nutzen

Unit-Regression: Specs `module attribution (no Blue steal)`, `FTS Ist stops`, ENV-Matrix, Multi-Load Position-Rows; **offen:** Multi-Load FTS je `loadId`.

---

## 8. Was bewusst nicht wieder eingeführt wird

- FTS-Synthese von Stations-PICK/PROCESS/DROP (widerspricht B3)
- Modul-Events dem Mitfahrer zuordnen, nur weil er „auch an der Station war“
- ENV an jedem PASS/Intersection (Rauschen)

Neue Sonderfälle: zuerst hier dokumentieren (Symptom → Regel → Test), dann Code.

---

## Referenzen

- [DR-13 Track & Trace Architecture](../03-decision-records/13-track-trace-architecture.md)
- Temporäre Inhalts-Analyse: [track-trace-live-content-fix-2026-07.md](../07-analysis/track-trace-live-content-fix-2026-07.md)
- Session-Inventar: `data/osf-data/sessions/INVENTORY.md`
- Sprint 27 Track&Trace-Themen: [sprint_27.md](../sprints/sprint_27.md)
