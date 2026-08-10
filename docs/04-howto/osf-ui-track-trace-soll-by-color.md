# Track & Trace: SOLL by color (visual / replay test)

**Stand:** 2026-08-06  
**Scope:** Live-Demo Track & Trace — erwartete Event-Abfolge je Werkstückfarbe  
**Companion:** Attribution-Regeln → [osf-ui-track-trace-history-attribution.md](osf-ui-track-trace-history-attribution.md)  
**Code:** `WorkpieceHistoryService`, `TrackTraceComponent`

Dieses How-to ist die **kanonische SOLL-Checkliste** für visuelle Replay-Tests (Single-Color Pass und Multi-Load `ml-*`). Agents und Tester sollen hier nachschlagen, was die UI **ableiten kann**, wenn MQTT die Events liefert — und was bewusst **fehlt**, wenn Shopfloor/CCU nichts publiziert.

---

## Leitprinzip (verbindlich)

| Regel | Bedeutung |
|-------|-----------|
| **MQTT-treu** | Track & Trace ist eine **Ableitung** aus realen FTS-/Modul-/CCU-Messages. Keine erfundenen Stationsbesuche. |
| **Fehlende Events** | Wenn MQTT Color/NFC/PICK/DOCK nicht liefert, bleibt die Spur lückenhaft — das ist korrektes Verhalten, kein UI-Bug. |
| **SOLL vs Ist** | **SOLL** = geplante Kette (`plannedStationChain` + Modul-Anker). **Ist** = FTS-DOCK/PASS/TURN inkl. Mitfahrt. |
| **Keine FTS-Stations-Synthese** | FTS erzeugt keine Modul-PICK/PROCESS/DROP (B3). |

**Legende in den Listen**

| Mark | Bedeutung |
|------|-----------|
| **UI** | UI stellt dar, sobald MQTT/Attribution das Event liefert |
| **gap** | Fachlich gewünscht, aber **kein** zuverlässiges MQTT / nicht implementiert |
| **session** | In manchen `ml-*`-Aufnahmen beobachtet fehlend (Shopfloor/CCU), nicht spekulativ füllen |
| **dense** | Einzelne PASS/TURN können in der UI zu einer **Transport-Gruppe** (`AGV · N · A→B`) zusammengefasst sein |

**Gemeinsame UI-Darstellung (alle Farben)**

- AGV-Loads: immer **Pos 1–3** (fehlende Slots = `EMPTY`)
- HBW PICK/DROP: **3×3-Mini-Grid** wenn Slot bekannt
- ENV: nur an Matrix-Events (DOCK/PICK/DROP/CHECK_QUALITY); Status aus Sensor-**Row**-Variante
- Planned-Stations-Haken: Modul-Flow-Anker auf der **eigenen** `orderId`; zusätzlich PRODUCTION **DRILL/MILL/AIQS**, wenn auf dem Werkstück ein **FTS-DOCK** an der Station existiert (auch Mitfahrt — physischer Stop, kein erfundenes Quality)
- **CHRG:** nur Ist (FTS `lastNodeId` CHRG0), **nur mit Sticky-Load**; leerer AGV @ CHRG → kein Event auf einer NFC-Historie
- **DPS Read NFC** am Production-Ende: siehe unten → **gap**

---

## DPS Read NFC (Production-Ende) — gap

SOLL-Schritt am Ende jeder Production-Kette:

> DPS Pick → **DPS Read NFC** (gleiche NFC wie Order / Historie-ID)

**Ist-Stand 2026-08-06:** DPS Production-Ende liefert in Sessions typischerweise Modul-`PICK` mit `result: PASSED` (Qualitäts-Token), **nicht** erneut `RGB_NFC`. Ein separates „Read NFC“-Event gibt es in MQTT derzeit **nicht** zuverlässig → in den Listen als **gap** markiert. Nicht synthetisieren.

---

## WHITE — SOLL

**Workflow Production:** `HBW → DRILL → AIQS → DPS`  
**Referenz Pass:** `white-storage-production_20260807_*` · Multi-Load: `ml-*` NFC White

### STORAGE

| # | Event | Mark | Hinweis |
|---|--------|------|---------|
| 1 | DPS Color (`INPUT_RGB`) | UI | Oft ohne Type bis NFC |
| 2 | DPS NFC (`RGB_NFC`) | UI | NFC = Historie-ID |
| 3 | DPS DROP | UI | |
| 4 | AGV Loads (Pos1 WHITE, Pos2/3 EMPTY) | UI | Sticky / `agvLoads` |
| 5 | AGV Intersection 2 PASS | UI / dense | |
| 6 | AGV Intersection 1 PASS oder TURN | UI / dense | |
| 7 | AGV HBW DOCK | UI | |
| 8 | HBW PICK + 3×3-Matrix | UI | |

### PRODUCTION

| # | Event | Mark | Hinweis |
|---|--------|------|---------|
| 1 | HBW DROP + Matrix | UI | |
| 2 | AGV Loads | UI | |
| 3–4 | AGV TURN an Intersection 1 / 3 | UI / dense | Richtung aus FTS-Order wenn vorhanden |
| 5 | AGV DOCK DRILL | UI | |
| 6–8 | DRILL PICK → DRILL → DROP | UI | Dauer ~15 s |
| 9–11 | AGV TURN / Transport → AIQS | UI / dense | |
| 12 | AGV DOCK AIQS | UI | |
| 13–15 | AIQS PICK → CHECK_QUALITY → DROP | UI | |
| 16–17 | AGV Transport → DPS | UI / dense | |
| 18 | AGV DOCK DPS | UI | |
| 19 | DPS PICK | UI | oft `result: PASSED` |
| 20 | DPS Read NFC | **gap** | kein zuverlässiges MQTT |

---

## RED — SOLL

**Workflow Production:** `HBW → MILL → AIQS → DPS` (**kein** DRILL)  
**Referenz Pass:** `red-storage-production_20260807_*` · Multi-Load: `ml-*` NFC Red

### STORAGE

| # | Event | Mark | Hinweis |
|---|--------|------|---------|
| 1 | DPS Color | UI / **session** | In manchen `ml-*` **kein** `INPUT_RGB`/`RGB_NFC` für Red → Spur startet erst bei DROP |
| 2 | DPS NFC | UI / **session** | wie Color |
| 3 | DPS DROP | UI | |
| 4 | AGV Loads (RED in Slot) | UI | |
| 5–6 | Intersections PASS/TURN | UI / dense | |
| 7 | AGV HBW DOCK | UI | |
| 8 | HBW PICK + Matrix | UI | |

### PRODUCTION

| # | Event | Mark | Hinweis |
|---|--------|------|---------|
| 1 | HBW DROP + Matrix | UI | |
| 2 | AGV Loads | UI | |
| 3–4 | AGV TURN Intersections | UI / dense | |
| 5 | AGV DOCK MILL | UI | |
| 6–8 | MILL PICK → MILL → DROP | UI | Dauer ~20 s |
| 9–11 | AGV → AIQS | UI / dense | |
| 12 | AGV DOCK AIQS | UI | |
| 13–15 | AIQS PICK → CHECK_QUALITY → DROP | UI | |
| 16–17 | AGV → DPS | UI / dense | |
| 18 | AGV DOCK DPS | UI / **session** | in manchen `ml-*` fehlt Production-DOCK @ DPS für Red |
| 19 | DPS PICK | UI / **session** | nur wenn Modul oder (DOCK+completed)-Ableitung greift |
| 20 | DPS Read NFC | **gap** | |

---

## BLUE — SOLL

**Workflow Production:** `HBW → DRILL → MILL → AIQS → DPS`  
**Referenz Fail:** `blue-storage-production-nok_20260807_*` · Multi-Load: `ml-*` NFC Blue  
**Referenz Pass:** `blue-storage-production_20260807_*`

### STORAGE

| # | Event | Mark | Hinweis |
|---|--------|------|---------|
| 1 | DPS Color | UI | |
| 2 | DPS NFC | UI | |
| 3 | DPS DROP | UI | |
| 4 | AGV Loads (BLUE in Slot) | UI | |
| 5–6 | Intersections PASS/TURN | UI / dense / **session** | in manchen `ml-*` kein FTS mit Blue-Load DPS→HBW |
| 7 | AGV HBW DOCK | UI / **session** | |
| 8 | HBW PICK + Matrix | UI / **session** | PICK kann unter **fremder** Storage-`orderId` laufen → Blue-Storage-Checklist ○ HBW |

### PRODUCTION

| # | Event | Mark | Hinweis |
|---|--------|------|---------|
| 1 | HBW DROP + Matrix | UI | |
| 2 | AGV Loads | UI | |
| 3–4 | AGV TURN Intersections | UI / dense | |
| 5 | AGV DOCK DRILL | UI | |
| 6–8 | DRILL PICK → DRILL → DROP | UI | |
| 9–11 | AGV → MILL | UI / dense | |
| 12 | AGV DOCK MILL | UI | |
| 13–15 | MILL PICK → MILL → DROP | UI | |
| 16–18 | AGV → AIQS | UI / dense | |
| 19 | AGV DOCK AIQS | UI | Mitfahrt-DOCK zählt für Planned-Haken; MODULE Quality nur wenn CCU/Modul für **diese** Order |
| 20–22 | AIQS PICK → CHECK_QUALITY → DROP | UI / **session** | CCU kann Blue ohne Modul-AIQS completed melden |
| 23–24 | AGV → DPS | UI / dense | |
| 25 | AGV DOCK DPS | UI | |
| 26 | DPS PICK | UI | |
| 27 | DPS Read NFC | **gap** | |

---

## Bekannte Multi-Load-Gaps (`ml-*`, Stand 2026-08-06)

Empirie an `storage-production-ml-wbr_*` u. a. — **nicht** durch UI-Spekulation schließen:

| Symptom | Typische Ursache |
|---------|------------------|
| Red ohne Color/NFC | Session publiziert kein `RGB_NFC` für Red |
| Blue Storage ohne Transport/HBW-PICK | Kein FTS-Load Blue DPS→HBW; HBW-PICK unter fremder Order |
| Blue Production ○ AIQS (früher) / ohne MODULE-AIQS | Mitfahrt-DOCK ≠ Modul-Quality; CCU completed ohne AIQS-Step |
| Red Production ohne DPS-Ende | Kein FTS-DOCK @ DPS / kein Modul-PICK für Red-Order |
| CHRG fehlt in NFC-Historie | DOCK @ CHRG0 mit **leerem** AGV |
| ENV durchgängig WARN | Sensorlage (z. B. MPU `yellow`) in der Aufnahme — kein Sticky-UI-Bug |

Single-Color Pass-Sessions (`*-storage-production_20260807_*`) bleiben die sauberste SOLL-Referenz.

---

## Visuelle Abnahme (kurz)

1. Replay gewählte Session → Track & Trace Live Demo  
2. Pro NFC: STORAGE- und PRODUCTION-Karte, Planned-Stations-Haken vs. Timeline  
3. Fehlende Stationszeilen nur akzeptieren, wenn MQTT/Session-Gap (diese Doku) — sonst Attribution-Bug  
4. Attribution-Details: [osf-ui-track-trace-history-attribution.md](osf-ui-track-trace-history-attribution.md)

---

## Referenzen

- [DR-13 Track & Trace Architecture](../03-decision-records/13-track-trace-architecture.md)
- Sessions: `data/osf-data/sessions/INVENTORY.md`
- Arbeitsnotizen (veraltet, Stub): `tmp/TrackAndTrace-*.md` → zeigen auf dieses How-to
