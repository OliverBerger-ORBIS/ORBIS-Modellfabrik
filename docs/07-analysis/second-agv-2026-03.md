# Zweites AGV (xkI4) – Implementierung & Referenz

**Sprint:** 17 → 18 | **Stand:** 01.09.2026  
**Kontext:** Zweites FTS; MQTT-Serial-Kette **jp93** (historisch) → **leJ4** (LogiMAT-Ersatz) → **xkI4** (FT-Reset 01.09.2026, zweites FTS zurückgesendet).

**Serial-Schreibweise (AGV-2 aktuell):** **`xkI4`** — drittes Zeichen = **großes I** (`U+0049`), **nicht** kleines **l** (`U+006C`). Visuell oft nicht von `xkl4` unterscheidbar → kanonisch aus MQTT-Topic oder Message-Monitor `serialNumber` kopieren, nicht abtippen.

**Vorgänger leJ4:** erstes Zeichen = **kleines L** (`U+006C`) — gleiche I/l-Falle, anderes Zeichen.

---

## 1. Umgesetzt

| Bereich | Inhalt |
|---------|--------|
| **AGV-Tab** | Dropdown AGV-1/AGV-2; Status/Battery/Loads/Commands pro Auswahl; **Route & Position** mit beiden AGVs und Routen in AGV-Farben; Legende Route (AGV-1)/(AGV-2) |
| **Presentation** | Gleiche `app-agv-tab`-Karte wie AGV-Tab (beide AGVs + Routen) |
| **Shopfloor-Tab** | Layout-Preview mit **AGV-Overlay** (`showFtsOverlay=true`), farbige Marker + Legende (AGV-1/AGV-2); Modul-Tabelle: **Name** wie Stationen im Format **Kurz (Lang)** |
| **Orders-Tab** | Aktive Karten: Multi-AGV-Overlays (orange/gelb) |
| **Gateway / Business** | `fts$` liefert nur **`fts/v1/.../state`** (kein `/order` im Stream) → `ftsStates$` bleibt pro Serial konsistent |
| **Track & Trace** | WorkpieceHistoryService dynamisch für beide Serials |
| **Layout** | `shopfloor_layout.json` – `fts[]`: **5iO4 (AGV-1)**, **xkI4 (AGV-2)**; erste `fts`-Position = orange, zweite = warmes Gelb |

---

## 2. Architektur (Kurz)

- **Business ftsStates$:** Key `ftsId ?? serialNumber` – beide AGVs; gebaut aus Gateway-**`fts$`**, das nur **`…/state`**-Topics mapped (Orders laufen nicht mehr durch `fts$`)
- **Topics:** Am Broker `fts/v1/ff/<serial>/state` | `/order` | `/instantAction`
- **Dock/Charge:** Topic bzw. Payload enthalten Serial – pro AGV korrekt adressiert

---

## 3. Offen / Optional

- **Shopfloor-Tabelle:** Modul-Status (READY/BUSY/…) auf AGV-Zeilen – Sprint 18 Follow-up
- **Fixtures / Sessions:** Alte Logs mit `jp93` oder `leJ4` bleiben historisch; Replay nutzt Topic-Serial aus der Session, nicht das aktuelle Layout

---

## 4. Verifikation Serial

```bash
# Broker (RPi): exakte Topic-Segmente
docker exec mqtt-broker-prod mosquitto_sub -h localhost -u default -P default \
  -t 'fts/v1/ff/+/connection' -v -W 30
```

Oder OSF-UI **Message Monitor** → `fts/v1/ff/xkI4/…` → `"serialNumber": "xkI4"`.

---

*Historische Analysen mit `jp93` / `leJ4`: nur als Session-Bezug lesen; aktuelles Layout = **5iO4** / **xkI4**.*
