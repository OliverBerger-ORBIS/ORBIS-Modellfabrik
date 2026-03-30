# two-agvs-mixed: Welche Daten liegen in den Sessions vor?

**Datum:** 2026-03-30  
**Kontext:** Empirische Grundlage für UI-/Business-Auswertung (z. B. AGV-Farben, Modul-Status, FTS-Zustand).  
**Referenz-Sessions:** `two-agvs-mixed_20260312_101514`, `two-agvs-mixed_20260312_165108` (siehe [INVENTORY.md](../../data/osf-data/sessions/INVENTORY.md)).

---

## 1. Rohdaten im Repo

Session-Logs liegen unter `data/osf-data/sessions/` als **JSON-Zeilen** (`*.log`: `topic`, `payload`, `timestamp`). Sie können **versioniert** im Repo liegen oder nur lokal; **`.cursorignore`** sollte MQTT-Sessions **nicht** global ausschließen, sonst sind sie für die KI-Indexierung unsichtbar.

**Praxis:** Auswertung z. B. mit `rg`/`jq` oder Python über alle Zeilen (siehe [sessions/README.md](../../data/osf-data/sessions/README.md)). Die **INVENTORY**-Tabelle listet bekannte Aufnahmen: [INVENTORY.md](../../data/osf-data/sessions/INVENTORY.md).

---

## 2. Serial-Mapping AGV-2: `jp93` (historisch) → `leJ4` (aktuell)

| Rolle   | MQTT-Serial | Zeitraum / Quelle |
|---------|-------------|-------------------|
| AGV-1   | `5iO4`      | Erstes `fts[]`-Element im Layout; Label **AGV-1** (orange) |
| AGV-2   | `leJ4`      | Zweites `fts[]`-Element; seit Hardware-Austausch / Messe statt `jp93` |
| AGV-2   | `jp93`      | Sessions **2026-03-12** unter diesem Topic-Segment (historisch) |

**Topics:** Struktur `fts/v1/ff/<serial>/state|order|…` ist für beide Serien gleich — bei Literatur/älteren Logs **`jp93` durch `leJ4` ersetzen**, wenn es um aktuelle OSF-Konfiguration geht.

---

## 3. Empirische Auswertung: `two-agvs-mixed_20260312_165108.log`

**Stand:** 2026-03-30 · **1 626** JSON-Zeilen · **37** eindeutige Topics.

### 3.1 Topic-Histogramm (Auszug)

| Topic | Anzahl | Anmerkung |
|-------|--------|-----------|
| `/j1/txt/1/i/cam` | 678 | Kamera-JPEG in `payload` — dominiert das Volumen |
| `ccu/pairing/state` | 279 | |
| `module/v1/ff/SVR4H73275/instantAction` | 278 | DPS; sehr hohe Rate (ggf. Heartbeat/Spam prüfen) |
| `fts/v1/ff/5iO4/state` | 89 | AGV-1 |
| `fts/v1/ff/jp93/state` | 30 | AGV-2 (aktuell: `leJ4`) |
| `fts/v1/ff/5iO4/order` | 5 | |
| `fts/v1/ff/jp93/order` | 3 | u. a. STORAGE WHITE, STORAGE RED |
| `module/v1/ff/SVR4H73275/state` | 10 | DPS direkt |
| `module/v1/ff/NodeRed/SVR4H73275/state` | 18 | DPS Node-RED |
| `ccu/order/active` | 19 | Payload = **Liste** von Orders |
| `ccu/order/request` | 3 | |
| `ccu/order/response` | 3 | |
| `ccu/order/completed` | 2 | |

Die frühere Stichprobe „46 / 25“ für `fts/.../state` (siehe §4) stammt aus einer **anderen** Session; **165108** hat **89 / 30** — mehr Updates für 5iO4 im erfassten Fenster.

### 3.2 FTS-`state`: Union aller Keys in dieser Datei

Über alle `fts/v1/ff/*/state`-Nachrichten:

`actionState`, `actionStates`, `batteryState`, `driving`, `edgeStates`, `errors`, `headerId`, `lastCode`, `lastNodeId`, `lastNodeSequenceId`, `load`, `nodeStates`, `orderId`, `orderUpdateId`, `paused`, `serialNumber`, `timestamp`, `waitingForLoadHandling`

**Befund:** **`lastModuleSerialNumber` kommt in 165108 in keiner FTS-State-Zeile vor** (0×). Logik, die ausschließlich darauf setzt, erhält in diesem Recording **keinen** MQTT-Wert dafür.

### 3.3 Letzte Zustände (Ende Log) — Kurz

| Serial | `lastNodeId` | `waitingForLoadHandling` | Kontext |
|--------|--------------|---------------------------|---------|
| `jp93` | `SVR4H73275` (DPS) | `true` | ROT geladen, DOCK FINISHED, Order `fc14e7f5-…` |
| `5iO4` | `SVR3QA0022` (HBW) | `false` | andere Order-ID |

---

## 4. Topic-Vorkommen (ältere Stichprobe „two-agvs“)

Aus [storage-order-rejection-two-agvs-2026-03.md](storage-order-rejection-two-agvs-2026-03.md) (Abschnitt „Topic-Übersicht (two-agvs Session)“ — Stichprobe, nicht mixed-spezifisch):

| Topic | Anzahl (Beispiel-Session) | Rolle |
|-------|---------------------------|--------|
| `fts/v1/ff/5iO4/state` | 46 | AGV-1 Live-Zustand |
| `fts/v1/ff/jp93/state` | 25 | AGV-2 Live-Zustand (historischer Serial) |
| `module/v1/ff/SVR4H73275/state` | 17 | DPS (direktes Modul-Topic) |
| `module/v1/ff/NodeRed/SVR4H73275/state` | 26 | DPS über Node-RED |
| `module/v1/ff/SVR3QA0022/state` | 2 | HBW (u. a. loads) |
| `module/v1/ff/SVR3QA0022/factsheet` | 2 | HBW Factsheet |
| `ccu/state/stock` | 2 | Lagerübersicht |
| `ccu/order/request` | 3 | u. a. UNKNOWN-Typen im untersuchten Ausschnitt |

**two-agvs-mixed_101514** (Zeitachse und DPS-Fehlerbild): siehe [storage-order-rejection-two-agvs-2026-03.md](storage-order-rejection-two-agvs-2026-03.md) ab „Session-Analyse 2“ — u. a. `loads`, `errors`, fehlender INPUT_RGB-Flow.

**two-agvs-mixed_165108** (Stillstand, parallele Orders): siehe [two-agvs-mixed-event-chain-fischertechnik-2026-03.md](two-agvs-mixed-event-chain-fischertechnik-2026-03.md) und [two-agvs-mixed-agv2-dps-busy-2026-03.md](two-agvs-mixed-agv2-dps-busy-2026-03.md) — Kette aus `fts/.../state`, `module/.../order`, `module/.../state` (DROP vs. setStatusLED). Rohdaten-Histogramm: **§3**.

---

## 5. FTS-State: Felder, die in den Log-Analysen tatsächlich verwendet wurden

Aus den Event-Ketten (nicht erschöpfend, aber für „was könnte OSF nutzen“ relevant):

| Feld / Konzept | Beispiel / Nutzen in der Session |
|----------------|----------------------------------|
| Fahrzeug an Knoten | `lastNodeId` z. B. `SVR4H73275` (DPS) |
| Docking | `actionState` mit **DOCK FINISHED** (`fts/v1/ff/jp93/state`) |
| Last / Load | Werkstücktyp / Position (z. B. ROT geladen, `loadPosition`) |
| Wartestatus | `waitingForLoadHandling: true` (letzter jp93-State in 165108) |
| Orders | `fts/v1/ff/jp93/order` — Route, Schritte NAVIGATION |

Parallel **CCU-Orders** (`ccu/order/active`, Order-Steps) und **Modul-States** (DPS DROP RUNNING / FINISHED, Abweichung TXT vs. Node-RED) erklären Stillstände — OSF-„Modul-Status“ für Stationen kommt aus `module/v1/ff/+/state`, für FTS primär aus `fts/v1/ff/<serial>/state`.

---

## 6. Mapping OSF-Datenmodell (Kurz)

- **Transport-/Pairing-Zeilen** pro FTS-Serial: aus Registry/Pairing + `fts$`-Stream; Felder wie `connected`, `lastUpdate`, `charging`, `waitingForLoadHandling` setzen sich aus MQTT-Auswertung zusammen (siehe `@osf/business` Merge mit FTS-State).
- **Anzeige „AGV-1“ / „AGV-2“:** `fts[]` (`label` + `serial`) im Layout; Shopfloor-Spalte **Name** wie bei Stationen im Format **Kurz (Langbezeichnung)** — z. B. `AGV-1 (Automated Guided Vehicle)` aus Layout-Label + `ModuleNameService.getModuleFullName('FTS')`; ohne Layout-Zuordnung Fallback `FTS (Automated Guided Vehicle)` (`getModuleDisplayText('FTS','id-full')`).

---

## 7. Empfehlung für Folge-Analysen

1. **Log-Datei** unter `data/osf-data/sessions/` (Repo oder lokal) und Topic-Histogramm erzeugen (`rg '^.*"topic":"' … | sort | uniq -c`).
2. **Pro FTS-Serial** die letzten N `…/state`-Payloads diffen (Battery, `driving`, `paused`, `errors`, `orderId`).
3. Bei **AGV-2-Umstellung** alte Docs mit `jp93` als historischen Bezug lesen, neue Sessions mit **`leJ4`** referenzieren.

---

## Referenzen

- [two-agvs-mixed-event-chain-fischertechnik-2026-03.md](two-agvs-mixed-event-chain-fischertechnik-2026-03.md)
- [two-agvs-mixed-agv2-dps-busy-2026-03.md](two-agvs-mixed-agv2-dps-busy-2026-03.md)
- [storage-order-rejection-two-agvs-2026-03.md](storage-order-rejection-two-agvs-2026-03.md)
- [agv-2-mixed-standstill-2026-03.md](agv-2-mixed-standstill-2026-03.md)
- [second-agv-2026-03.md](second-agv-2026-03.md)
