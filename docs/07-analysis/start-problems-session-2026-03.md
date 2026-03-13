# start-problems Session-Analyse

**Session:** `start-problems_20260312_175942.log`  
**Zeitraum:** 17:51:42 – 17:59:42 (~8 min)  
**Datum:** 2026-03-12

---

## Kontext

User hat 2× Factory Reset ausgelöst. **Verhalten war normal** – alle Module melden sich mit ready/available zurück.

Beim zweiten Reset lief gerade ein **Storage-Order** (Werkstück an DPS). Ergebnis:
- DPS verarbeitet den Storage-Order nicht weiter und **verwirft das Werkstück**
- Nach dem Reset geht es **ordentlich und normal** weiter
- Der abgebrochene Storage-Order hat **keine Spuren hinterlassen**

---

## Übersicht

| Metrik | Wert |
|--------|------|
| Resets | 2 (17:54:26, 17:57:12) |
| DPS Recovery | Nach jedem Reset: ~27 Sek BLOCKED/BUSY, danach READY |
| Ergebnis | Alle Module READY am Ende |

---

## Ablauf nach Reset 2 (17:57:12)

### DPS State-Messages (direkt `module/v1/ff/SVR4H73275/state`)

| Zeit | actionState | active_loads | CCU → Availability |
|------|-------------|--------------|--------------------|
| 17:57:12.133 | null | 1 (RED) | BLOCKED (Reset) → BUSY |
| 17:57:13 – 17:57:38 | null | 1 | BUSY |
| 17:57:39.106 | null | 0 | **READY** |

**Zeit bis READY:** ~27 Sekunden nach Reset.

### Wichtig

1. Der **TXT publiziert State** auf dem direkten Topic – nicht nur Connection.
2. Die ersten States haben **Load, kein actionState** → `handleModuleAvailability` setzt BUSY (DPS-Sonderfall: Load ohne actionState).
3. Sobald **kein aktiver Load** mehr gemeldet wird, setzt die CCU den DPS auf READY.

---

## Bewertung

**Normale Session** – korrekter Statuswechsel, keine Blockade. Beide Sessions (start-osf, start-problems) sind valide.

Der TXT publiziert State auf dem direkten Topic; nach ~27 s (bis Load freigegeben) setzt die CCU die DPS auf READY. Reset mitten im Storage-Order wird sauber abgebrochen, keine Rückstände.

---

## Architektur (Recap)

- **CCU abonniert:** `module/v1/ff/+/state` → trifft nur `SVR4H73275/state`, **nicht** `NodeRed/SVR4H73275/state`.
- **DPS State-Quellen:**
  - TXT direkt → `module/v1/ff/SVR4H73275/state`
  - NodeRed → `module/v1/ff/NodeRed/SVR4H73275/state` (CCU erhält das nicht)

---

*Erstellt: 2026-03-12*
