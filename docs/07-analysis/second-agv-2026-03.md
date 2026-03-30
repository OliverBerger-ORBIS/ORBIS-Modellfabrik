# Zweites AGV (leJ4) – Implementierung & Referenz

**Sprint:** 17 → 18 | **Stand:** 30.03.2026  
**Kontext:** LogiMAT-Vorbereitung, zweites FTS mit MQTT-Serial **`leJ4`** (Ersatzgerät; zuvor jp93).

**Serial-Schreibweise:** Offiziell **`leJ4`** – erstes Zeichen = **kleines L** (`U+006C`), nicht großes **I** (`U+0049`). Fälschlich **`IeJ4`** in Layout/Pairing führt zu keinem Match mit `fts/v1/ff/leJ4/…` und Placeholder-Zeilen in der UI.

---

## 1. Umgesetzt

| Bereich | Inhalt |
|---------|--------|
| **AGV-Tab** | Dropdown AGV-1/AGV-2; Status/Battery/Loads/Commands pro Auswahl; **Route & Position** mit beiden AGVs und Routen in AGV-Farben; Legende Route (AGV-1)/(AGV-2) |
| **Presentation** | Gleiche `app-agv-tab`-Karte wie AGV-Tab (beide AGVs + Routen) |
| **Shopfloor-Tab** | Layout-Preview mit **AGV-Overlay** (`showFtsOverlay=true`), farbige Marker + Legende (AGV-1/AGV-2); Transport-Rows pro AGV mit Dock/Charge |
| **Orders-Tab** | Aktive Karten: Multi-AGV-Overlays (orange/gelb) |
| **Gateway / Business** | `fts$` liefert nur **`fts/v1/.../state`** (kein `/order` im Stream) → `ftsStates$` bleibt pro Serial konsistent |
| **Track & Trace** | WorkpieceHistoryService dynamisch für beide Serials; Fixtures mit leJ4 |
| **Fixtures** | u. a. `storage_blue_agv2`, `storage_blue_parallel`; **Review Dual-AGV+Routes:** `production_blue_dual_agv_step15` / Preset `order-production-blue-dual-agv-step15` |
| **Layout** | `shopfloor_layout.json` – `fts`-Array mit 5iO4 (AGV-1), leJ4 (AGV-2) |

---

## 2. Architektur (Kurz)

- **Business ftsStates$:** Key `ftsId ?? serialNumber` – beide AGVs; gebaut aus Gateway-**`fts$`**, das nur **`…/state`**-Topics mapped (Orders laufen nicht mehr durch `fts$`)
- **Topics:** Am Broker weiterhin `fts/v1/ff/<serial>/state` | `/order` | `/instantAction`; nur **`/state`** speist `fts$` / `ftsStates$`
- **Dock/Charge:** Topic bzw. Payload enthalten Serial – pro AGV korrekt adressiert

---

## 3. Offen / Optional

- **Shopfloor-Tabelle:** AGV-2 ggf. noch generisches „FTS …“ statt Layout-Label; Modul-Status auf AGV-Zeilen prüfen (Sprint 18 Follow-up)
- **E2E live** mit beiden AGVs (Mock-Fixture `production_blue_dual_agv_step15` verifiziert)
- **CCU-Erweiterung:** ✅ Umgesetzt (v1.3.0-osf.2). Optionales `serialNumber` in NAVIGATION-Steps in `ccu/order/active` / `completed`. OSF-UI vorbereitet.

---

## 4. Referenzen

- [sprint_17.md](../sprints/sprint_17.md) · [sprint_18.md](../sprints/sprint_18.md) – Messe / Dual-AGV-UI
- [DR-24](../03-decision-records/24-shopfloor-highlight-colors.md) – Farben, beide AGVs, Gateway `fts$`
- [shopfloor_layout.json](../../osf/apps/osf-ui/public/shopfloor/shopfloor_layout.json) – `fts`-Array
- [Fischertechnik APS Add-On AGV](https://www.fischertechnik.de/en/industry-and-universities/technical-documents/simulate/agile-production-simulation) – Betriebsanleitung

---

*Konsolidiert aus second-agv-integration-analysis und second-agv-extensions-design. Historische Analysen mit Topic `fts/v1/ff/jp93/…` beziehen sich auf die frühere Hardware.*
