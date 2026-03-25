# Zweites AGV (leJ4) – Implementierung & Referenz

**Sprint:** 17 | **Stand:** März 2026  
**Kontext:** LogiMAT-Vorbereitung, zweites FTS mit MQTT-Serial **`leJ4`** (Ersatzgerät; zuvor jp93).

**Serial-Schreibweise:** Offiziell **`leJ4`** – erstes Zeichen = **kleines L** (`U+006C`), nicht großes **I** (`U+0049`). Fälschlich **`IeJ4`** in Layout/Pairing führt zu keinem Match mit `fts/v1/ff/leJ4/…` und Placeholder-Zeilen in der UI.

---

## 1. Umgesetzt

| Bereich | Inhalt |
|---------|--------|
| **AGV-Tab** | Dropdown AGV-1/AGV-2; beide AGVs im Shopfloor sichtbar; Status/Battery/Loads/Commands pro ausgewähltem AGV |
| **Shopfloor** | Beide AGVs mit Farben (AGV-1 orange, AGV-2 gelb) – im AGV-Tab und Presentation-Tab (DR-24) |
| **Shopfloor-Tab** | Layout-Section ohne AGV-Overlay (`showFtsOverlay=false`); Transport-Rows pro AGV mit Dock/Charge |
| **Track & Trace** | WorkpieceHistoryService dynamisch für beide Serials; Fixtures mit leJ4 |
| **Fixtures** | `storage_blue_agv2` (nur leJ4), `storage_blue_parallel` (beide AGVs) |
| **Layout** | `shopfloor_layout.json` – `fts`-Array mit 5iO4 (AGV-1), leJ4 (AGV-2) |

---

## 2. Architektur (Kurz)

- **Business ftsStates$:** Key `ftsId ?? serialNumber` – beide AGVs
- **Topics:** `fts/v1/ff/<serial>/state`, `/order`, `/instantAction`
- **Dock/Charge:** Topic bzw. Payload enthalten Serial – pro AGV korrekt adressiert

---

## 3. Offen / Optional

- **E2E-Test** mit AGV-2 (Fixtures nutzbar)
- **CCU-Erweiterung:** ✅ Umgesetzt (v1.3.0-osf.2). Optionales `serialNumber` in NAVIGATION-Steps in `ccu/order/active` / `completed`. OSF-UI vorbereitet.

---

## 4. Referenzen

- [sprint_17.md](../sprints/sprint_17.md) – LogiMAT Vorbereitung
- [shopfloor_layout.json](../../osf/apps/osf-ui/public/shopfloor/shopfloor_layout.json) – `fts`-Array
- [Fischertechnik APS Add-On AGV](https://www.fischertechnik.de/en/industry-and-universities/technical-documents/simulate/agile-production-simulation) – Betriebsanleitung

---

*Konsolidiert aus second-agv-integration-analysis und second-agv-extensions-design. Historische Analysen mit Topic `fts/v1/ff/jp93/…` beziehen sich auf die frühere Hardware.*
