# start-osf Session-Analyse

**Session:** `start-osf_20260303_075408.log`  
**Zeitraum:** 07:50:23 – 07:54:08 (~4 min)  
**Datum:** 2026-03-03

---

## Übersicht

| Metrik | Wert |
|--------|------|
| Zeilen | 764 |
| Erste Message | ccu/state/version-mismatch (retained) |
| Letzte Message | module/v1/ff/SVR4H73275/instantAction |

---

## DPS (SVR4H73275) – Message-Sequenz

### State-Messages (direkt auf `module/v1/ff/SVR4H73275/state`)

| Zeit | actionState | loads |
|------|-------------|-------|
| 07:50:23 | FINISHED factsheetRequest | 0 |
| 07:50:30 | FINISHED factsheetRequest | 0 |

**Nur diese 2 State-Messages** in der gesamten Session. Danach: nur Connection (~alle 15 s) und instantAction (LED-Updates).

### Ablauf

1. **07:50:23** – NodeRed + TXT melden sich:
   - NodeRed/SVR4H73275/connection, state (factsheetRequest FINISHED), factsheet
   - SVR4H73275/state, connection, factsheet (direkt vom TXT)

2. **07:50:30** – Wiederholung (Heartbeat/Retry)

3. **07:50:36 – 07:54:07** – Nur noch:
   - SVR4H73275/connection alle ~15 s
   - SVR4H73275/instantAction (LED-Updates, setStatusLED)

4. **Kein weiterer State** in diesen ~4 Minuten.

---

## Pairing-State am Ende

```
DPS: READY SVR4H73275
```

Die beiden State-Messages mit `factsheetRequest FINISHED` und `loads: 0` reichen aus, damit `handleModuleAvailability` den DPS auf READY setzt. Danach bleibt er READY, weil kein Reset erfolgt.

---

## Bewertung

**Normale Session** – korrekter Statuswechsel, keine Blockade. Die beiden State-Messages mit `factsheetRequest FINISHED` reichen für READY; danach Connection/instantAction. Siehe auch [start-problems-session-2026-03.md](start-problems-session-2026-03.md) für Ablauf nach Reset.

---

*Erstellt: 2026-03-12*
