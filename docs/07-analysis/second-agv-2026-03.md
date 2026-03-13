# Zweites AGV (jp93) – Implementierung & Referenz

**Sprint:** 17 | **Stand:** März 2026  
**Kontext:** LogiMAT-Vorbereitung, zweites FTS mit Serial jp93

---

## 1. Umgesetzt

| Bereich | Inhalt |
|---------|--------|
| **AGV-Tab** | Dropdown AGV-1/AGV-2; beide AGVs im Shopfloor sichtbar; Status/Battery/Loads/Commands pro ausgewähltem AGV |
| **Shopfloor** | Beide AGVs mit Farben (AGV-1 orange, AGV-2 gelb); Hervorhebung (Schatten, Glow, Ring) AGV-spezifisch |
| **Shopfloor-Tab** | Layout-Section ohne AGV-Overlay (`showFtsOverlay=false`); Transport-Rows pro AGV mit Dock/Charge |
| **Track & Trace** | WorkpieceHistoryService dynamisch für beide Serials; Fixtures mit jp93 |
| **Fixtures** | `storage_blue_agv2` (nur jp93), `storage_blue_parallel` (beide AGVs) |
| **Layout** | `shopfloor_layout.json` – `fts`-Array mit 5iO4 (AGV-1), jp93 (AGV-2) |

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

*Konsolidiert aus second-agv-integration-analysis und second-agv-extensions-design*
