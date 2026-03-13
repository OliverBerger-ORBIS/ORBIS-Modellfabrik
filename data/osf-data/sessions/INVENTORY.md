# Session Log Inventory

Übersicht aller Session-Logs für die Auswahl geeigneter Aufzeichnungen für Analysen, Fixtures und Tests.

**Ziel:** Anhand der Abläufe entscheiden, ob eine Session für Start-up, Production, Storage oder Mixed-Analyse geeignet ist.

---

## Schnellübersicht

| Session | Start-up | Production | Storage | Mixed | AGVs | Besonderheiten |
|---------|:--------:|:----------:|:-------:|:-----:|:----:|----------------|
| start-osf_20260303_075408 | ✓ | | | | 1 | FTS-State, Layout, Config – minimal Orders |
| start-problems_20260312_175942 | | | ✓ | | 1 | Sehr viele Storage-Orders (475 active), hohe Last |
| two-agvs_20260312_085306 | | | ✓ | | 2 | Beide AGVs, vorwiegend Storage |
| two-agvs-mixed_20260312_101514 | | ✓ | ✓ | ✓ | 2 | Beide AGVs, Prod+Storage parallel |
| two-agvs-mixed_20260312_165108 | | ✓ | ✓ | ✓ | 2 | **Stillstand:** DPS DROP hängt, TXT sendet setStatusLED statt DROP FINISHED |
| agv-1-simple_20260312_113627 | | | | | 1 | Viele Orders (96), nur AGV-1 |
| agv-1-mixed_20260312_103130 | | | | | 1 | Kurz (3 min), wenige Orders |
| agv-1-mixed_20260312_133313 | | ✓ | ✓ | ✓ | 1 | Prod+Storage, AGV-1 |
| agv-2-mixed_20260312_134156 | | ✓ | ✓ | ✓ | 2 | Prod+Storage, beide AGVs |
| agv-2-mixed_20260312_164447 | | ✓ | ✓ | ✓ | 2 | Prod+Storage, beide AGVs |
| production-blue_20260303_090705 | | ✓ | | | 1 | Reine Produktion Blau |
| production-red_20260303_081525 | | ✓ | ✓ | ✓ | 1 | Prod überwiegend, wenig Storage |
| production-white_20260303_081127 | | ✓ | ✓ | ✓ | 1 | Prod überwiegend, wenig Storage |
| production-blue-part1_20260303_082030 | | ✓ | ✓ | ✓ | 1 | Prod Blau Teil 1 |
| production-blue-part2_20260303_090117 | | ✓ | ✓ | ✓ | 1 | Prod Blau Teil 2 |
| storage-blue_20260303_080705 | | | ✓ | | 1 | Reine Einlagerung Blau |
| storage-red_20260303_080428 | | | ✓ | | 1 | Reine Einlagerung Rot |
| storage-white_20260303_075954 | | | ✓ | | 1 | Reine Einlagerung Weiß |
| storage-red234_20260303_094003 | | ✓ | ✓ | ✓ | 1 | Storage überwiegend, wenig Prod |
| mixed-pw-pr-sw-pb-sr-sb_20260303_092241 | | ✓ | ✓ | ✓ | 1 | Gemischt: White, Red, Blue Prod+Storage |
| mixed-sw-pw-sw-pwnok-pw_20260303_093559 | | ✓ | ✓ | ✓ | 1 | **Quality-Fail:** White prnok (CHECK_QUALITY FAILED), Ersatzauftrag |
| mixed-sr-pr-prnok_20260305_121602 | | ✓ | ✓ | ✓ | 1 | **Quality-Fail:** Fixture mixed_pr_prnok |
| calibrate_dps_1_20251202_101939 | | | ✓ | | 1 | DPS-Kalibrierung, Storage |
| vibration-sw420_20260303_094240 | | ✓ | ✓ | ✓ | 1 | Kurz, SW-420 Vibrationssensor im Kontext |
| auftrag-blau_1.log | | ✓ | | | 0 | Mock/Synthetisch, keine FTS-Events |
| auftrag-rot_1.log | | ✓ | | | 0 | Mock/Synthetisch, keine FTS-Events |
| auftrag-weiss_1.log | | ✓ | | | 1 | Älteres Format, wenig FTS |

---

## Besondere Topics

| Topic | Sessions mit Vorkommen | Zweck |
|-------|------------------------|-------|
| ccu/set/park | *(keine in aktuellen Logs)* | Fabrik-Park-Befehl (z.B. UC-05 Gefahrensimulation) |
| ccu/order/cancel | *(bei Bedarf prüfen)* | Order-Abbruch |
| fts/v1/ff/5iO4/state, fts/v1/ff/jp93/state | two-agvs*, agv-2*, agv-1* | AGV-1 (5iO4), AGV-2 (jp93) |

---

## Versionen (aus Logs/Factsheets)

- **CCU:** 1.3.0 (typisch in pairing/state)
- **Module:** 1.3.0 (HBW, DRILL, MILL, AIQS), DPS 1.6.0
- **osf-ui:** Nicht in Logs – Aufnahmezeitpunkt als Proxy (z.B. 2026-03-12 = v0.8.8/0.8.9)

---

## Detaillierte Abläufe (Auswahl)

### Start-up

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **start-osf** | CCU state (layout, config, flows, stock), pairing, wenig Orders, FTS-State. Kurzer Zeitraum (~4 min). | Gut für Start-up/Preload-Tests, wenig Order-Traffic |
| **start-problems** | Sehr viele Storage-Orders (475 active, 460 completed), sehr hohe Message-Rate. | Last-Test, nicht für saubere Ablauf-Analyse |

### Production (ein AGV)

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **production-blue** | Reine Produktion Blau: DRILL→MILL→AIQS→DPS. Ein AGV. | Ideal für Production-Only-Analyse |
| **production-red** | Produktion Rot überwiegend, minimal Storage. | Prod-fokussiert |
| **production-white** | Produktion Weiß überwiegend, minimal Storage. | Prod-fokussiert |
| **production-blue-part1/2** | Produktion Blau in zwei Phasen. | Längere Prod-Sequenz |

### Storage (ein AGV)

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **storage-blue** | Reine Einlagerung Blau. HBW→DPS. | Ideal für Storage-Only |
| **storage-red** | Reine Einlagerung Rot. | Storage-Only |
| **storage-white** | Reine Einlagerung Weiß. | Storage-Only |
| **calibrate_dps** | DPS-Kalibrierung, Storage-Orders. | Speziell DPS/Calibration |
| **two-agvs** | Beide AGVs, vorwiegend Storage (3 Orders). | Zwei-AGV Storage, wenig Last |

### Mixed (Production + Storage, ein oder zwei AGVs)

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **mixed-pw-pr-sw-pb-sr-sb** | Gemischte Folge: White, Red, Blue – Prod und Storage. Ein AGV. | Typisches Mixed-Szenario |
| **mixed-sw-pw-sw-pwnok-pw** | White Prod, Quality-Fail (prnok), Ersatzauftrag. | Quality-Fail, Order ERROR, Ersatzauftrag |
| **mixed-sr-pr-prnok** | Red+Purple Prod, Quality-Fail. Fixture `mixed_pr_prnok`. | Quality-Fail-Analyse |
| **agv-1-mixed** (133313) | AGV-1, Prod+Storage parallel. | Ein-AGV Mixed |
| **agv-2-mixed** | AGV-1 und AGV-2, Prod+Storage parallel. | Zwei-AGV Mixed |
| **two-agvs-mixed** (101514) | Beide AGVs, Prod+Storage. | Zwei-AGV Mixed, früher am Tag |
| **two-agvs-mixed** (165108) | Beide AGVs, Prod+Storage. **Stillstand:** AGV-2 an DPS, DROP hängt (TXT sendet setStatusLED statt DROP FINISHED), AGV-1 blockiert. | **Analyse Stillstand zwei AGVs** – siehe [two-agvs-mixed-event-chain](../07-analysis/two-agvs-mixed-event-chain-fischertechnik-2026-03.md) |

### Sonstige

| Session | Ablauf | Eignung |
|---------|--------|---------|
| **vibration-sw420** | Kurze Aufnahme, Vibrationssensor SW-420, gemischter Kontext. | Sensor-Kontext |
| **auftrag-*** | Mock/Synthetisch, keine echten FTS/Module-Events. | Ältere Testdaten |

---

## Referenzen

- [two-agvs-mixed-event-chain-fischertechnik-2026-03.md](../../docs/07-analysis/two-agvs-mixed-event-chain-fischertechnik-2026-03.md) – Stillstand-Analyse two-agvs-mixed_165108
- [mixed-sr-pr-prnok](../../osf/testing/fixtures/) – Fixture für Quality-Fail
- [order-agv-mapping-without-mod3](../../docs/07-analysis/order-agv-mapping-without-mod3-2026-03.md) – Order↔AGV-Zuordnung

---

*Stand: 2026-03-13. Bei neuen Sessions: Ablauf kurz beschreiben, in Schnellübersicht einordnen, Besonderheiten (Stillstand, ccu/set/park, etc.) vermerken.*
