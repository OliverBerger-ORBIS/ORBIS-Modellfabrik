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
| **Shopfloor-Tab** | Layout-Preview mit **AGV-Overlay** (`showFtsOverlay=true`), farbige Marker + Legende (AGV-1/AGV-2); Modul-Tabelle: **Name** wie Stationen im Format **Kurz (Lang)** (`id-full` via `ModuleNameService`) — für eingetragene FTS **`AGV-1 (Automated Guided Vehicle)`** / **`AGV-2 (…)`** (`getModuleFullName('FTS')`), nicht nur „AGV-1“ ohne Klammern |
| **Orders-Tab** | Aktive Karten: Multi-AGV-Overlays (orange/gelb) |
| **Gateway / Business** | `fts$` liefert nur **`fts/v1/.../state`** (kein `/order` im Stream) → `ftsStates$` bleibt pro Serial konsistent |
| **Track & Trace** | WorkpieceHistoryService dynamisch für beide Serials; Fixtures mit leJ4 |
| **Fixtures** | u. a. `storage_blue_agv2`, `storage_blue_parallel`; **Review Dual-AGV+Routes:** `production_blue_dual_agv_step15` / Preset `order-production-blue-dual-agv-step15` |
| **Layout** | `shopfloor_layout.json` – `fts[]`: **5iO4 (AGV-1)**, **leJ4 (AGV-2)**; erste `fts`-Position = orange, zweite = warmes Gelb |

---

## 2. Architektur (Kurz)

- **Business ftsStates$:** Key `ftsId ?? serialNumber` – beide AGVs; gebaut aus Gateway-**`fts$`**, das nur **`…/state`**-Topics mapped (Orders laufen nicht mehr durch `fts$`)
- **Topics:** Am Broker weiterhin `fts/v1/ff/<serial>/state` | `/order` | `/instantAction`; nur **`/state`** speist `fts$` / `ftsStates$`
- **Dock/Charge:** Topic bzw. Payload enthalten Serial – pro AGV korrekt adressiert

---

## 3. Offen / Optional

- **Shopfloor-Tabelle:** Modul-Status (READY/BUSY/…) auf AGV-Zeilen – Sprint 18 Follow-up (Namen ✓: `AGV-n` + `getModuleFullName('FTS')`; siehe §1)
- **E2E live** mit beiden AGVs (Mock-Fixture `production_blue_dual_agv_step15` verifiziert)
- **Order-Steps ↔ FTS (AGV-1/AGV-2):** [OSF-MODIFICATIONS.md](../../integrations/APS-CCU/OSF-MODIFICATIONS.md) **Mod 3** — optionales `serialNumber` in **NAVIGATION**-Steps ist **zurückgenommen** (2026-03); die CCU spiegelt die gewählte FTS-Seriennummer nicht in `ccu/order/active` / `completed` wider. **osf-ui:** Zuordnung `(orderId, stepId) → ftsSerial` über **`fts/v1/ff/<serial>/order`** ([`FtsOrderAssignmentService`](../../osf/apps/osf-ui/src/app/services/fts-order-assignment.service.ts)); **OrderCard** nutzt `step.serialNumber ?? getFtsSerialForStep(...)` (serverseitiges Feld bleibt optional/kompatibel). Details: [order-agv-mapping-without-mod3-2026-03.md](order-agv-mapping-without-mod3-2026-03.md).

---

## 4. Referenzen

- [sprint_17.md](../sprints/sprint_17.md) · [sprint_18.md](../sprints/sprint_18.md) – Messe / Dual-AGV-UI
- [order-agv-mapping-without-mod3-2026-03.md](order-agv-mapping-without-mod3-2026-03.md) – NAVIGATION ohne Mod 3, Option A (`fts/order`)
- [OSF-MODIFICATIONS.md](../../integrations/APS-CCU/OSF-MODIFICATIONS.md) – Mod 3 (NAVIGATION `serialNumber`) zurückgenommen
- [DR-24](../03-decision-records/24-shopfloor-highlight-colors.md) – Farben, beide AGVs, Gateway `fts$`
- [shopfloor_layout.json](../../osf/apps/osf-ui/public/shopfloor/shopfloor_layout.json) – `fts`-Array
- [Fischertechnik APS Add-On AGV](https://www.fischertechnik.de/en/industry-and-universities/technical-documents/simulate/agile-production-simulation) – Betriebsanleitung

---

*Konsolidiert aus second-agv-integration-analysis und second-agv-extensions-design. Historische Analysen mit Topic `fts/v1/ff/jp93/…` beziehen sich auf die frühere Hardware.*
