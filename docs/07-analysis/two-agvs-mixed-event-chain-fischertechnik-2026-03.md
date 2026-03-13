# two-agvs-mixed: Event-getriebene Ursachenkette und Fischertechnik-Frage

**Datum:** 2026-03-12  
**Session:** `two-agvs-mixed_20260312_165108.log`

---

## 1. Zuordnung der Orders (orderId) und AGVs

| orderId (gekürzt) | Typ | AGV | Serial | Beschreibung |
|-------------------|-----|-----|--------|--------------|
| 94222604 | STORAGE WHITE | AGV-2 | jp93 | Einlagerung Weiß – erfolgreich abgeschlossen |
| fc14e7f5 | STORAGE RED | AGV-2 | jp93 | Einlagerung Rot – **Stillstand** (an DPS) |
| 4e98aff3 | PRODUCTION WHITE | AGV-1 | 5iO4 | Produktion Weiß – parallel; hat Werkstück von AIQS, soll zu DPS fahren |

**Konflikt:** AGV-1 (5iO4) hat das Werkstück vom AIQS-Modul geholt und soll zum DPS fahren (PICK = Auslieferung). Die DPS ist jedoch **belegt (busy)** durch AGV-2 (jp93) mit der Storage-RED-Order – jp93 steht an der DPS, DROP bleibt hängen (kein DROP FINISHED vom TXT).

---

## 2. Event-getriebene Ursachenkette

### Order A: STORAGE RED (fc14e7f5) – AGV-2 (jp93)

| Step | Typ | Modul | Status | Timestamp | Auslösendes MQTT-Event |
|------|-----|-------|--------|-----------|------------------------|
| 1 | NAVIGATION | START→DPS | FINISHED | 16:47:58 | `fts/v1/ff/jp93/state` → DOCK FINISHED |
| 2 | MANUFACTURE | DPS DROP | **IN_PROGRESS** | 16:47:58 | `module/v1/ff/SVR4H73275/order` (CCU sendet DROP) |
| 2 | MANUFACTURE | DPS DROP | **bleibt hängen** | – | **Fehlendes Event:** CCU wartet auf DROP FINISHED von `module/v1/ff/SVR4H73275/state` |
| 3 | NAVIGATION | DPS→HBW | ENQUEUED | – | Blockiert durch Step 2 |
| 4 | MANUFACTURE | HBW PICK | ENQUEUED | – | Blockiert durch Step 3 |

**Ereignis-Kette (nummeriert):**

| Nr | Zeit | Topic | actionState | Anmerkung |
|----|------|-------|-------------|-----------|
| 1 | 16:47:58 | `fts/v1/ff/jp93/state` | DOCK FINISHED | AGV-2 an DPS |
| 2 | 16:47:58 | `module/v1/ff/SVR4H73275/order` | – | CCU sendet DROP |
| 3 | 16:47:58 | `module/v1/ff/SVR4H73275/state` | (none) RUNNING | DROP gestartet |
| 3 | 16:47:58 | `module/v1/ff/NodeRed/SVR4H73275/state` | DROP RUNNING | |
| 4 | – | (physisch) | – | **DPS führt DROP aus – Werkstück liegt im AGV-2** |
| 5 | 16:48:11 | `module/v1/ff/NodeRed/SVR4H73275/state` | **DROP FINISHED** | NodeRed meldet Fertigstellung |
| 6 | 16:48:12 | `module/v1/ff/SVR4H73275/state` | **setStatusLED FINISHED** | TXT sendet nicht DROP FINISHED |

**Wichtige Info:** Das rote Werkstück ist **physisch gedropped** und liegt im AGV-2 (jp93). Die DPS hat die DROP-Order ausgeführt (Ereignis 4). NodeRed meldet DROP FINISHED (5). Der TXT sendet stattdessen setStatusLED FINISHED (6) – es fehlt DROP FINISHED auf `SVR4H73275/state`.

---

### Order B: PRODUCTION WHITE (4e98aff3) – AGV-1 (5iO4)

| Step | Typ | Modul | Status | Auslösendes MQTT-Event |
|------|-----|-------|--------|------------------------|
| … | … | … | … | … |
| AIQS | MANUFACTURE | AIQS CHECK_QUALITY, DROP | FINISHED | Werkstück an Bord |
| NAVIGATION | AIQS→DPS | ENQUEUED/blockiert | AGV-1 soll zum DPS fahren für PICK |
| – | – | **DPS belegt** | – | jp93 (Storage RED) blockiert die DPS |

**Konfliktsituation:**

| AGV | Serial | Order | Zustand |
|-----|--------|-------|---------|
| AGV-1 | 5iO4 | PRODUCTION WHITE | Hat Werkstück von AIQS, soll zu DPS für PICK – **DPS belegt** |
| AGV-2 | jp93 | STORAGE RED | Steht an DPS, Werkstück physisch im AGV, **kein DROP FINISHED** vom TXT |

---

### Vergleich: STORAGE WHITE (94222604) – funktionierender Ablauf

| Zeit | Topic | actionState | Wirkung |
|------|-------|-------------|---------|
| 16:46:07 | `module/v1/ff/SVR4H73275/state` | (none) RUNNING | DROP gestartet |
| 16:46:20 | `module/v1/ff/NodeRed/SVR4H73275/state` | DROP FINISHED | – |
| 16:46:21 | `module/v1/ff/SVR4H73275/state` | **DROP FINISHED** | CCU setzt Step 2 auf FINISHED, triggert Step 3 |

Hier sendet der TXT direkt auf `SVR4H73275/state` DROP FINISHED → funktioniert korrekt.

---

## 3. Frage an Fischertechnik

**Szenario:** Zwei AGVs im Mixed-Betrieb (Storage + Production parallel). AGV-2 (jp93) an DPS mit Storage-RED-Order. Die DPS hat die DROP-Order physisch ausgeführt (Werkstück liegt im AGV), sendet aber auf `module/v1/ff/SVR4H73275/state` setStatusLED FINISHED statt DROP FINISHED. NodeRed sendet DROP FINISHED auf dem NodeRed-Topic.

1. **Ist dieses Fehlverhalten bekannt?**
2. **Falls ja:** Soll man Szenarien vermeiden, in denen parallel mit zwei AGVs sowohl PRODUCTION- als auch STORAGE-Orders abgearbeitet werden?
3. **Falls ja:** Gibt es einen Bug-Fix oder Workaround?

---

*Erstellt: 2026-03-12*
