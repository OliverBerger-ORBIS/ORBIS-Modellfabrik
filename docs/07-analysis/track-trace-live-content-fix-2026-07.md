# Track & Trace Live Demo – Inhaltliche Korrekturen (Arbeitsdokument)

**Status:** temporär · **Datum:** 21.07.2026 (Update 29.07.2026) · **Sprint:** [27](../sprints/sprint_27.md)  
**Löschen:** nach Abarbeitung der Sprint-Tasks (A1/C1/B1, Sensor-Matrix, ggf. B3) bzw. Sprint-Closeout

**Arbeitsmodus:** HomeOffice / **Replay** ausreichend — Feldbetrieb nicht nötig. Verifikation mit Session-Replay + Track&Trace Live Demo (bzw. Fixture-Presets `track-trace-*`).

---

## Feldbefund (21.07.2026, Live)

Nach erfolgreichem NFC B-soft-Test und Live-Demo-UX:

1. **Auftragskontext:** nur **Lagerauftrag (STORAGE)** — kein getrennter **Produktionsauftrag**, obwohl Shopfloor-Events an MILL/AIQS laufen.
2. **Doppelmeldungen:** Station (MILL/AIQS) sendet PICK/PROCESS/DROP; FTS sendet dieselben Schritte zusätzlich (z. B. MILL-PICK). Dedup ist zweitrangig — **Publisher** (Device/Modul, FTS, ggf. CCU) muss klar sein.
3. **Zeit vs. Gruppierung:** chronologische Anordnung muss **höhere Prio** haben als Sub-Order-/Stations-Gruppen. Beispiel AIQS: zwei Sub-Order-Blöcke hintereinander, obwohl Timestamps ineinander greifen — fachlich nur **ein** Pick an der Station.

---

## Replay-Befund (28.07.2026)

### Session-Eignung

| Session | Bewertung |
|---------|-----------|
| `mixed-pw-pr-sw-pb-sr-sb_20260303_092241.log` | Zu komplex für Erstanalyse (Multi-Farbe, parallele Orders) — Fremd-Events in Weiß-Historie, doppelter Produktionsauftrag-Header |
| `storage-white` + `production-white` (`20260303`) | **gelöscht 28.07.** — ersetzt durch `*-storage-production_20260728_*` |
| `object-detection/od_white_1` | Nur STORAGE live; Capture unvollständig (kein PRODUCTION) |
| **`white|red-storage-production_20260728_*.log`** | **Referenz Pass** für A1: je 1× STORAGE + 1× PRODUCTION, Sensorik vollständig |
| **`blue-storage-production-nok_20260728_100418.log`** | **Referenz Fail:** BLUE AIQS `CHECK_QUALITY` FAILED (umbenannt 05.08.2026) |
| **`production-wr-*` / `production-wb-*`** | Parallel-Production **ohne** Storage — ausreichend für Multi-AGV-/Parallel-Attribution, nachdem Multi-Order an den drei Referenzen verifiziert ist |

### Kernbefund Live/Replay: Events ok, Production-Klammer fehlt

**Beobachtung:** Im Track&Trace Live Demo werden Shopfloor-Events dem richtigen Werkstück zugeordnet. Es fehlt aber die Business-Überschrift / Auftragskontext-Karte **Production**.

**Warum Events trotzdem am Werkstück hängen:** FTS `load[].loadId` = NFC/`workpieceId`. Darauf baut `WorkpieceHistoryService` die Historie.

**Warum Production-Request oft ohne `workpieceId` startet:** OSF sendet Production farbbasiert (`type` + `orderType: PRODUCTION`, ohne `workpieceId`) — siehe `osf/libs/business` `requestProduction`. Das ist der Startzustand.

**CCU-Verhalten (in den neuen Sessions gemessen):**

| Phase | `workpieceId` |
|-------|----------------|
| STORAGE request/active/response | sofort gesetzt (z. B. White `2b2c6dd469a47a`) |
| PRODUCTION request + erste active/response | **fehlt** |
| PRODUCTION active ab ~HBW-PICK (~1 min später) | **gesetzt** — gleiche ID wie Storage |

→ Die NFC-Identität geht **nicht verloren**; CCU bindet sie nachträglich an die Production-Order. Für die fehlende UI-Klammer ist das aber **nicht** die Ursache.

**Root Cause der fehlenden Production-Klammer (A1):**

1. Historie wird mit erstem FTS-`orderId` angelegt → meist **STORAGE**.
2. `generateOrderContext(..., ftsOrderId, ...)` filtert auf **genau diese eine** Order-UUID.
3. Spätere Updates patchen nur Daten in `existingHistory.orders`, rufen **keinen** Rebuild mit der neuen PRODUCTION-UUID.
4. UI (`groupEventsByOrder`) sucht Header in `history.orders` → ohne PRODUCTION-Eintrag keine Production-Klammer, obwohl Events `orderType: PRODUCTION` tragen können.

Relevant: `workpiece-history.service.ts` (`generateOrderContext`, `updateWorkpieceHistory` Order-Patch, `refreshAllOrderContexts` nutzt `orders[0]`).

### Konkrete UI-Abweichungen (mixed-pw, Weiß `04798eca341290`)

1. **Produktionsauftrag 2×** mit gleicher Order-UUID — pro Werkstück nur ein PRODUCTION-Block.
2. **Bohrstation 2×** — sehr wahrscheinlich FTS-Synthese („via AGV“) vs. Modul-Events (ggf. plus Fremd-Werkstück in Mixed-Session).
3. **DPS dann MILL** mit wechselnden Order-UUID-Präfixen — Fremdaufträge in der Historie / falsche Zuordnung.
4. **AIQS erst am Schluss** — Timeline durch Vermischung unplausibel.

### Storage-only (historisch `storage-white`; heute `*-storage-production_20260728_*`)

- Shopfloor-Events **logisch** (DPS → HBW).
- **Sensor-Spalte leer:** Trigger-Matrix STORAGE erwartet DPS **PICK** / HBW **DROP**, real sind DPS **DROP** / HBW **PICK**.
- Nice-to-have: DPS-Meldung mit Farbe + NFC (nicht Blocker).
---

## Root Causes (Kurz)

### 1) Nur Lagerauftrag / doppelter Order-Header

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

### 4) Sensor-Matrix STORAGE (28.07.)

- `shouldCaptureEnvironmentSnapshot` in `workpiece-history.service.ts`: STORAGE → DPS PICK / HBW DROP.
- Realer Storage-Ablauf: DPS DROP / HBW PICK → keine Snapshots an den sichtbaren Events.
- Session `storage-white` (historisch) hatte zudem nur BME680+LDR; die `20260728`-Referenzen enthalten volles Arduino-Set — Matrix-Mismatch bleibt (S1).

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

### (d) Sensor-Matrix

| Opt | Idee | Empf. |
|-----|------|-------|
| **S1** | STORAGE: Snapshot an **DPS DROP** + **HBW PICK**; Unit-Test-Matrix anpassen | **ja** |
| S2 | Nice-to-have DPS Farbe/NFC in Event-Zeile | optional später |

---

## Umsetzungsplan (bei Implementierungs-Auftrag)

**Vorbereitung:** drei Referenz-Sessions Storage→Production gleiches Werkstück (W/R/B) aufnehmen.

**Phase 1 (Replay / HomeOffice):**

1. **A1** – Multi-Order-Rebuild — **erledigt 28.07.2026**
2. **C1** – Gruppen nach `min(timestamp)` — **erledigt 28.07.2026**
3. **B1** – `eventSource` + Badge — **erledigt 28.07.2026**
4. **S1** – STORAGE-Sensor DPS DROP + HBW PICK — **erledigt 28.07.2026**
5. **Antwort A Modul-Events** — Color/NFC + DRILL/MILL als Event-Namen + Position in HBW — **erledigt 28.07.2026**
6. Unit-Tests + Replay-Verifikation

**Phase 2 (28.07.2026 abends):**

- **B3** — FTS nur Transport/DOCK/TURN; Stationen nur Modul-MQTT
- UI: Spalten **Station | Transport**; ein Stations-Header pro Besuch (DPS Color/NFC/DROP)
- Order Context: max. **1× STORAGE + 1× PRODUCTION** (UUID-Shells mergen)

**Nicht Teil dieses Tasks:** Persistenz (Option B bleibt Edge/Grafana, [DR-28](../03-decision-records/28-edge-persistence-stack-and-metrics-model.md)).

---

## Relevante Dateien

- `osf/apps/osf-ui/src/app/services/workpiece-history.service.ts` (`shouldCaptureEnvironmentSnapshot`, Multi-Order)
- `osf/apps/osf-ui/src/app/components/track-trace/track-trace.component.ts` / `.html`
- Fixtures: `osf/libs/testing-fixtures` Presets `track-trace-*`
- Architektur: [DR-13](../03-decision-records/13-track-trace-architecture.md)

---

## Abnahmekriterien (Phase 1)

- [x] Auftragskontext zeigt STORAGE **und** PRODUCTION, wenn beide Order-IDs in der Historie vorkommen *(A1 Code 28.07.2026; Live/Replay-Check noch ausstehend)*
- [x] Event-Zeile zeigt Publisher (FTS vs. Modul/Device) *(B1 28.07.2026)*
- [x] Bei überlappenden Sub-Order-Timestamps an einer Station erscheint die Liste zeitlich korrekt (früheres Event weiter oben), nicht „ganzer Block A vor Block B“ *(C1 28.07.2026)*
- [x] STORAGE-Sensor-Snapshots an DPS DROP + HBW PICK *(S1 28.07.2026)*
- [x] PRODUCTION-Sensor-Snapshots erweitert: **HBW DROP + DPS PICK** *(Phase 3, 29.07.2026)*
- [x] Transport-Events: **Intersection N**-Label + Location-Icon; Bucket-Slot mit Farbe *(Phase 3, 29.07.2026)*
- [x] CHECK_QUALITY: **Ergebnis-Badge** (OK/FAILED) inline im Event *(Phase 3, 29.07.2026)*
- [ ] Verifizierbar im **Replay**-Modus ohne Shopfloor (idealerweise neue W/R/B-Referenz-Sessions)
