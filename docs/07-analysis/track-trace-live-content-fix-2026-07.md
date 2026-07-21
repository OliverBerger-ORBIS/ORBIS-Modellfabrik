# Track & Trace Live Demo – Inhaltliche Korrekturen (Arbeitsdokument)

**Status:** temporär · **Datum:** 21.07.2026 · **Sprint:** [26](../sprints/sprint_26.md)  
**Löschen:** nach Abarbeitung der Sprint-Tasks (A1/C1/B1, ggf. B3) bzw. Sprint-Closeout

**Arbeitsmodus:** HomeOffice / **Replay** ausreichend — Feldbetrieb nicht nötig. Verifikation mit Session-Replay + Track&Trace Live Demo (bzw. Fixture-Presets `track-trace-*`).

---

## Feldbefund (21.07.2026, Live)

Nach erfolgreichem NFC B-soft-Test und Live-Demo-UX:

1. **Auftragskontext:** nur **Lagerauftrag (STORAGE)** — kein getrennter **Produktionsauftrag**, obwohl Shopfloor-Events an MILL/AIQS laufen.
2. **Doppelmeldungen:** Station (MILL/AIQS) sendet PICK/PROCESS/DROP; FTS sendet dieselben Schritte zusätzlich (z. B. MILL-PICK). Dedup ist zweitrangig — **Publisher** (Device/Modul, FTS, ggf. CCU) muss klar sein.
3. **Zeit vs. Gruppierung:** chronologische Anordnung muss **höhere Prio** haben als Sub-Order-/Stations-Gruppen. Beispiel AIQS: zwei Sub-Order-Blöcke hintereinander, obwohl Timestamps ineinander greifen — fachlich nur **ein** Pick an der Station.

---

## Root Causes (Kurz)

### 1) Nur Lagerauftrag

| Ursache | Ort |
|--------|-----|
| `orders` werden einmal mit erstem FTS-`orderId` (meist STORAGE) angelegt | `workpiece-history.service.ts` (~Create History / `generateOrderContext`) |
| Spätere Updates patchen nur Daten, rufen `generateOrderContext` nicht mit neuem PRODUCTION-UUID auf | ~Map über `existingHistory.orders` |
| `generateOrderContext` filtert auf **einen** `ftsOrderId` | Skip wenn `orderId !== ftsOrderId` |
| Correlation-Refresh nutzt `orders[0]` / erstes Event-`orderId` | `refreshAllOrderContexts` |
| Event-`orderType` kann via Heuristik schon `PRODUCTION` sein, Panel liest nur `history.orders` | `determineOrderType` vs. UI |

DR-13 Multi-Order war bereits als offen markiert: [13-track-trace-architecture.md](../03-decision-records/13-track-trace-architecture.md).

### 2) Doppelmeldungen / Attribution

| Quelle | Eintrag | Inhalt |
|--------|---------|--------|
| FTS `fts/.../state` | `updateWorkpieceHistory` | An Fertigungsstationen in PRODUCTION: **synthetische** PICK→PROCESS→DROP |
| Modul `module/.../state` | `updateWorkpieceHistoryFromModule` | echte Stations-Events |

UI heute: `getEventPrimaryActor` = Station, `getEventTransportContext` = optional „via AGV“ — **kein Publisher-Feld**. Semantic Dedup (Sprint 21) kollabiert teils FTS↔Modul ohne Attribution; bei abweichenden Keys bleiben Duplikate.

### 3) Zeitstrahl vs. Sub-Order-Gruppen

- Flache `history.events`: chronologisch sortiert.
- UI: `groupEventsBySubOrder` sortiert Gruppen nach **numerischem Sub-Order-Suffix**, nicht nach `min(timestamp)`.
- `subOrderId`-Vergabe FTS vs. Modul kann **zwei Gruppen** für einen Stationsbesuch erzeugen.

---

## Optionen & Empfehlung

### (a) Order Context

| Opt | Idee | Empf. |
|-----|------|-------|
| **A1** | `orders` aus **allen** distinct `orderId`s in Events + CCU Match neu aufbauen | **ja (Phase 1)** |
| A2 | Eine Card umschalten STORAGE→PRODUCTION | nein (verliert Lager-Kontext) |
| A3 | Immer zwei Shells | nein (falsche UUIDs) |
| A4 | Volle CCU-Lifecycle-Anbindung | später |

### (b) Attribution / Duplikate

| Opt | Idee | Empf. |
|-----|------|-------|
| **B1** | `eventSource: 'FTS' \| 'MODULE'` (+ Badge) | **ja (Phase 1)** |
| B2 | Nur aus `moduleId` ableiten | fragil |
| **B3** | FTS-Synthese an Stationen abschalten; Modul = SoT für PICK/PROCESS/DROP | **Phase 2** |
| B4 | Zwei parallele Views | zu busy für Demo |

### (c) Chronologie

| Opt | Idee | Empf. |
|-----|------|-------|
| **C1** | Gruppen nach `min(timestamp)` sortieren | **ja (Phase 1)** |
| C2 | Flat timeline, Station nur Label | optional später |
| C4 | Einheitliche `subOrderId` pro Stationsbesuch | mit B3 |

---

## Umsetzungsplan (bei Implementierungs-Auftrag)

**Phase 1 (Replay / HomeOffice):**

1. **A1** – Multi-Order-Rebuild in `WorkpieceHistoryService`
2. **C1** – Sort in `groupEventsBySubOrder` (TrackTraceComponent)
3. **B1** – `eventSource` setzen + UI-Badge (EN i18n)
4. Unit-Tests + Replay-Verifikation (Session mit STORAGE→PRODUCTION, AIQS/MILL)

**Phase 2 (separater Task, höheres Risiko):**

- **B3** (+ ggf. **C4**): FTS nur Transport/DOCK/TURN; Stationen nur aus Modul-MQTT

**Nicht Teil dieses Tasks:** Persistenz (Option B bleibt Edge/Grafana, [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)).

---

## Relevante Dateien

- `osf/apps/osf-ui/src/app/services/workpiece-history.service.ts`
- `osf/apps/osf-ui/src/app/components/track-trace/track-trace.component.ts` / `.html`
- Fixtures: `osf/libs/testing-fixtures` Presets `track-trace-*`
- Architektur: [DR-13](../03-decision-records/13-track-trace-architecture.md)

---

## Abnahmekriterien (Phase 1)

- [ ] Auftragskontext zeigt STORAGE **und** PRODUCTION, wenn beide Order-IDs in der Historie vorkommen
- [ ] Event-Zeile zeigt Publisher (FTS vs. Modul/Device)
- [ ] Bei überlappenden Sub-Order-Timestamps an einer Station erscheint die Liste zeitlich korrekt (früheres Event weiter oben), nicht „ganzer Block A vor Block B“
- [ ] Verifizierbar im **Replay**-Modus ohne Shopfloor
