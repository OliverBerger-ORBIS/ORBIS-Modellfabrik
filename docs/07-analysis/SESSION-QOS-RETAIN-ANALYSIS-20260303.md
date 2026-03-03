# Session-Log-Analyse: QoS/Retained – Empirische Verifizierung

**Datum:** 03.03.2026  
**Quelle:** Neuaufnahmen an realer Fischertechnik-Modellfabrik (ORBIS Smart Factory)  
**Session Recorder:** v1.2+ (speichert qos/retain in `.log`)  
**Script:** `scripts/analyze_retain_in_logs.py`

**Kontext:** [AS-IS vs. Fischertechnik](../07-analysis/AS-IS-FISCHERTECHNIK-COMPARISON.md) – Die Fischertechnik-Referenz dokumentiert State/connection/factsheet als retained. Diese Analyse verifiziert die tatsächliche Verteilung an der realen APS.

**Aufnahme-Kontext:** Die 13 Sessions wurden **ohne Reconnect** aufgezeichnet (nicht notwendig). Retained Messages kamen von **Connect** (start-osf) und **Resubscribe** (subscribe beim Start jeder Folgesession – Verbindung blieb offen).

> **Merksatz:** Die Nachrichten, die die UI zum Aufbau der Seiten benötigt (layout, state, connection, factsheet, stock, order/active, order/completed), liegen im Broker als **retained Messages**. Bei **Connect** oder **Reconnect** ist die notwendige Info sofort verfügbar – keine Leer-Anzeige, kein Warten auf Live-Updates.

---

## 1. Zusammenfassung

| Metrik | Ergebnis |
|--------|----------|
| **Sessions analysiert** | 13 |
| **Alle mit qos/retain** | ✅ 100 % |
| **Factsheet** | Überwiegend retained (8–24 pro Session) |
| **Connection** | Mix: retained (8–24) + non_retained (45–260) |
| **State** | Mix: retained (9–27) + non_retained (17–1224) |

**Fazit:** Die Fischertechnik-Implementierung publiziert State-, Connection- und Factsheet-Topics sowohl als **retained** (initial/LWT) als auch als **non_retained** (Live-Updates). Factsheets sind nahezu ausschließlich retained. State und Connection haben retained-Einträge bei Broker-Connect/Subscribe; die häufigen Updates (1Hz oder on-change) sind non_retained.

---

## 2. Detailergebnisse pro Session

| Session | Total | state retained | state non_ret | connection ret | connection non | factsheet ret | factsheet non |
|---------|-------|----------------|---------------|----------------|----------------|---------------|---------------|
| start-osf | 764 | 16 | 172 | 14 | 76 | 14 | 1 |
| storage-white | 502 | 9 | 121 | 8 | 45 | 8 | 0 |
| storage-red | 513 | 9 | 123 | 8 | 45 | 8 | 0 |
| storage-blue | 510 | 9 | 121 | 8 | 45 | 8 | 0 |
| production-white | 897 | 9 | 248 | 8 | 75 | 8 | 0 |
| production-red | 840 | 9 | 231 | 8 | 70 | 8 | 0 |
| production-blue-part1 | 1170 | 9 | 357 | 8 | 95 | 8 | 0 |
| production-blue-part2 | 1457 | 27 | 322 | 24 | 135 | 24 | 2 |
| production-blue | 1065 | 9 | 305 | 8 | 85 | 8 | 0 |
| mixed-pw-pr-sw-pb-sr-sb | 3630 | 9 | 1224 | 8 | 260 | 8 | 0 |
| mixed-sw-pw-sw-pwnok-pw | 3200 | 9 | 1048 | 8 | 240 | 8 | 0 |
| storage-red234 | 845 | 9 | 228 | 8 | 70 | 8 | 0 |
| vibration-sw420 | 139 | 9 | 17 | 8 | 15 | 8 | 0 |

---

## 3. Interpretation

### 3.1 Factsheet
- **Retained:** 8–24 pro Session (je nach Modulanzahl/FTS)
- **Non_retained:** 0–2 (Ausnahme: production-blue-part2 nach Resubscribe)
- **Bewertung:** ✅ Entspricht Fischertechnik-Doku – Factsheets werden retained publiziert.

### 3.2 Connection
- **Retained:** 8–24 (Standard: 8 für 5 Module + FTS + ggf. NodeRed)
- **Non_retained:** 45–260 (häufige Connection-Updates/LWT-Nachrichten)
- **Bewertung:** ✅ Retained vorhanden (LWT/Will); Live-Updates erhöhen non_retained während langer Sessions.

### 3.3 State
- **Retained:** 9–27 (initial/baseline bei Connect oder Resubscribe)
- **Non_retained:** 17–1224 (1Hz-Updates oder event-driven)
- **Bewertung:** ✅ State-Topics werden retained publiziert; der Großteil des Traffics sind non_retained Updates (konsistent mit „reduces traffic“ bei event-driven).

### 3.4 Start-Session vs. Folgesessions
- **start-osf:** Höhere retained-Zahlen (16 state, 14 connection, 14 factsheet) – frischer Connect, alle retained vom Broker
- **Folgesessions:** Weniger retained (9/8/8) – Resubscribe liefert nur einen Teil; Broker sendet retained beim Subscribe

---

## 4. Vergleich mit Fischertechnik-Referenz

| Thema | Fischertechnik | Empirisch (ORBIS APS) |
|-------|----------------|------------------------|
| State retained | Ja (UI-Persistenz) | ✅ Ja – retained vorhanden |
| Connection retained | Ja (LWT) | ✅ Ja – retained vorhanden |
| Factsheet retained | Ja (on startup) | ✅ Ja – nahezu ausschließlich retained |
| State 1Hz/on-change | Non_retained Updates | ✅ Überwiegend non_retained |
| QoS | 1–2 für State | qos in Logs (0/1) – weitere Auswertung optional |

---

## 5. Relevanz für OSF-UI

- **Connect/Reconnect:** Die UI benötigt retained Messages zum Aufbau der Seiten. Bei Connect oder Reconnect liefert der Broker diese sofort – keine Leer-Anzeige, kein Warten auf den nächsten Live-Update.
- **Replay:** Sessions mit retained-Einträgen am Anfang ermöglichen vollständigen Replay inkl. Fabrik-Setup.
- **Session Recorder:** „Aufnahme vor Verbinden“ (frischer Connect) oder Resubscribe beim Session-Start erfasst retained Messages zuverlässig.

---

## 6. Referenzen

- [Session-Log-Analyse Anleitung](../04-howto/session-log-analyse.md)
- [AS-IS vs. Fischertechnik](../07-analysis/AS-IS-FISCHERTECHNIK-COMPARISON.md)
- [Fischertechnik 05-message-structure](../06-integrations/fischertechnik-official/05-message-structure.md)
- [mqtt-topic-conventions](../06-integrations/00-REFERENCE/mqtt-topic-conventions.md)
