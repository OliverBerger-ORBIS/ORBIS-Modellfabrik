# FTS/AGV-Navigation: Wie funktioniert sie?

**Datum:** 2026-03-13 · **Überarbeitet:** 2026-03-31 (Supervisor-Sequenz → HBW + `clearLoadHandler` Live OK)  
**Quelle:** CCU-Code, VDA5050/Protocol, osf-ui AGV-Tab  
**Ziel:** Wer erstellt NAV-Anweisungen? Welche Topics und Payloads? Kann osf-ui manuell navigieren?

**Kurzfassung:** OSF **→ HBW** sendet eine FTS-**order** (CCU-kompatible IDs nach Anpassung). Nach **DOCK** am HBW bleibt das FTS oft mit **`waitingForLoadHandling`** — dann manuell **`clearLoadHandler`** per Instant Action (**Clear load handling** im AGV-Tab); **Live verifiziert** (Supervisor mit visueller Kontrolle). **Zwei Schritte:** erst Navigation, bei Bedarf zweiten Button — danach ist das Fahrzeug für CCU-NAV/Orders wieder „frei“. Start bisher v. a. **DPS**; andere Module über Start „Auto“/Dropdown noch gezielt testen.

---

## 1. Wer erstellt die NAV-Anweisung?

Die **CCU (Central Control Unit)** im APS-CCU-Backend.

**Code-Stellen:**
- `integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts`
  - `sendNavigationRequest()` – NAV für Production-/Storage-Orders
  - `sendClearModuleNodeNavigationRequest()` – NAV nach Quality-Fail (FTS vom blockierten Modul wegbewegen)
- `integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts`
  - Order-Management wählt FTS und Zielmodul
  - `retriggerFTSSteps()` – startet wartende NAV-Schritte anderer Orders

**Ablauf:** Order-Management → NavigatorService berechnet Pfad (Factory-Layout-Graph) → MQTT-Publish.

---

## 2. Topics und Payloads für FTS-Navigation

### 2.1 Order (VDA5050-Route)

| Thema | Format |
|-------|--------|
| **Topic** | `fts/v1/ff/{FTS-Serial}/order` |
| **Payload** | VDA5050-Order mit `nodes`, `edges`, `actions` |

**Illustration — bewusst getrennt:** Unten (Abschnitt 5) steht, **warum** OSF- und CCU-Payloads oft **nicht** zeichengleich sind. Kein fertiges Beispiel als „Ground Truth“ ohne Aufzeichnung vom Broker.

**OSF-Shopfloor (`shopfloor_layout.json`):** Knoten-Refs im Graphen sind `serial:SVR…` und `intersection:n`. Kanten tragen Layout-IDs wie `road_SVR4H73275_2`. Pfad: `AgvRouteService.findRoutePath` (BFS auf diesen Refs).

**CCU (`factory-layout.json` → Graph):** Modul-Knoten-ID ist die **reine Seriennummer** (`SVR3QA0022`, …). Kreuzungs-ID ist der JSON-Wert (`"1"`, `"2"`, … — **ohne** `intersection:`-Präfix). Kanten-IDs in der Order: **`fromId + '-' + toId`** (siehe `NavigatorService.convertPathToOrder`).

### 2.2 Instant Action (findPosition / findInitialDockPosition)

| Thema | Format |
|-------|--------|
| **Topic** | `fts/v1/ff/{FTS-Serial}/instantAction` |
| **Payload** | `serialNumber`, `timestamp`, `actions[]` |

**Beispiel (Dock zum DPS):**
```json
{
  "serialNumber": "5iO4",
  "timestamp": "2026-03-13T12:00:00.000Z",
  "actions": [{
    "actionId": "dock-xxx",
    "actionType": "findInitialDockPosition",
    "metadata": { "nodeId": "SVR4H73275" }
  }]
}
```

**findPosition:** Einige FTS/TXT-Firmware unterstützen `findPosition` mit `metadata.nodeId` – Ziel kann Modul-Serial oder Intersection-ID sein. Nicht in VDA-Protocol standardisiert.

---

## 3. osf-ui: Manuelle NAV von AIQS/DPS zu HBW

**Topic:** gleich wie CCU (`fts/v1/ff/{serial}/order`). **Payload:** siehe Abschnitt 5 — **kein** Garant für Byte-kompatibilität zur CCU.

### 3.1 Buttons (seit v0.8.12)

| Button | Voraussetzung | Topic | Ziel |
|--------|---------------|-------|------|
| **DPS → HBW** | AGV am DPS | `fts/v1/ff/{serial}/order` | SVR3QA0022 (HBW) |
| **AIQS → HBW** | AGV am AIQS | `fts/v1/ff/{serial}/order` | SVR3QA0022 (HBW) |
| **→ Intersection 2** | Bekannte AGV-Position | `fts/v1/ff/{serial}/order` | Layout-Ref `intersection:2` (nicht CCU-Knoten-ID `"2"`) |

**Serial:** Verwendet wird die aktuell ausgewählte AGV-Serial (`selectedAgvSerial$`) – also AGV-1 (5iO4) oder AGV-2 (leJ4) je nach Dropdown. Kein hart codiertes 5iO4 in den Command-Payloads.

### 3.2 Technische Umsetzung (`agv-tab.component.ts`)

- `buildOrderFromTo` baut `nodes` / `edges` aus `findRoutePath` und `findRoadBetween`.
- **Zwischenknoten (Kreuzungen):** wie CCU `inferIntersectionNodeAction` — gleiche Fahrtrichtung ein- und ausgehend → **`PASS`**, sonst **`TURN`** mit `metadata.direction` (`LEFT` / `RIGHT`, Regeln wie `NavigatorService.inferTurnDirectionFromRoadDirections`). Basis: `parsed_roads[].direction` und tatsächliche Laufrichtung entlang des Pfads.
- **Ziel HBW (`SVR3QA0022`):** letzter Knoten `DOCK` mit `getHbwDockMetadata()` (Load aus letztem FTS-State).
- **Sonstiges Ziel (z. B. Kreuzung):** letzter Knoten `STOP` (OSF), nicht zwingend dasselbe wie CCU-Ende.

---

## 4. CCU: `NavigatorService.convertPathToOrder` (Kernlogik)

**Code:** `integrations/APS-CCU/central-control/src/modules/fts/navigation/navigator-service.ts`

| Aspekt | CCU-Verhalten |
|--------|----------------|
| Zwischen **Kreuzungen** | `inferIntersectionNodeAction`: gleiche Kantenrichtung → **`PASS`**, sonst **`TURN`** mit `metadata.direction` (N/S/E/W gemäß `RoadDirection`). |
| **Modul als nächstes** im Pfad | Optionaler Knoten vor dem Modul (PASS/TURN), dann **`DOCK`** am Modul mit `action.id` = **vorgegebenes `actionId`** aus dem Order-/NAV-Workflow (kein beliebiges Nur-UI-UUID). |
| **Knoten-Reihenfolge** | Startknoten ohne Aktion; Aktionen nur an durchfahrenen Zwischenknoten + Dock am Zielmodul; Pfad bricht nach erstem anstehenden Modul ab (`break` nach DOCK). |
| **Kanten** | `id: startNode.id + '-' + endNode.id`; `linkedNodes` die Graph-IDs (reine Serials / `"1"`, `"2"`). |

Damit ist die frühere Vereinfachung „OSF sendet wie CCU nur PASS/DOCK“ **falsch**, sobald der geometrische Pfad Kurven braucht: die CCU sendet dann **`TURN`**-Schritte.

---

## 5. Checkliste: OSF-Order vs. CCU-Order (Debugging)

**Datenbasis (kein neues „Mitschneiden“ nötig):** Im Repo liegen zahlreiche MQTT-Session-Aufzeichnungen mit echten CCU-`order`-Publishs.

| Quelle | Inhalt |
|--------|--------|
| `data/osf-data/sessions/` | Roh-Logs je Szenario; Katalog und Eignung → [INVENTORY.md](../../data/osf-data/sessions/INVENTORY.md) |
| `data/osf-data/fts-analysis/` | Bereits extrahierte Messages u. a. `fts/v1/ff/…/order` pro Analyse-Lauf (`*_fts_order.json`, `*_all_fts_messages.json`) |

**Konkretes CCU-Beispiel DPS ↔ HBW** (Storage, funktionierender Ablauf): In `data/osf-data/fts-analysis/storage_order_white_20251110_181619_fts_order.json` ist u. a. eine Order **DPS → HBW** enthalten (`nodes`: `SVR4H73275` → `2` → `1` → `SVR3QA0022` mit `DOCK` am HBW; `edges`: `SVR4H73275-2`, `2-1`, `1-SVR3QA0022`; Zwischenaktionen dort **PASS** — der Pfad ist in diesem Layout gerade, ohne `TURN`). Diese Payload mit einer OSF-manuellen Order **Feld für Feld** vergleichen.

Bei fehlgeschlagener manueller Navigation:

1. **Knoten-IDs:** CCU = `SVR4H73275` / `2`; OSF = `serial:SVR4H73275` / `intersection:2`. Referenz aus passender Session/`fts-analysis`-Datei laden, mit OSF-Payload diffen.
2. **Kanten-IDs:** CCU `A-B`; OSF `road_…`. Gleiche Prüfung anhand gespeicherter Orders.
3. **Aktionstypen:** OSF (**Stand 2026-03**) sendet auf Kreuzungen **`PASS`** oder **`TURN`** wie CCU (s.o.). Bei Abweichung weiter mit Session-Referenz gleicher Route diffen.
4. **Letztes Modul:** HBW bei OSF = `DOCK` + Load-Metadaten aus UI-State; CCU = `DOCK` mit Workflow-`actionId` und Metadaten wie in den Session-Beispielen.
5. **Vorgehen:** Zuerst Referenz-`order` aus `sessions`/`fts-analysis` zum **gleichen Start/Ziel** wählen, dann OSF-Tab-Order (Message Monitor oder erneute kurze Aufnahme nur falls keine OSF-Seite im Log) gegenüberstellen. Live-Broker nur bei Bedarf.
6. **Nach manueller NAV mit DOCK am Modul:** Das Fahrzeug setzt oft `waitingForLoadHandling` bis Modul PICK/DROP oder bis **`clearLoadHandler`** per `fts/v1/ff/{serial}/instantAction` (siehe APS-CCU `agv.md`, `helper.sendClearLoadFtsInstantAction`). Im OSF-AGV-Tab: Button **Clear load handling** (nur wenn physikalisch unkritisch, z. B. leere Bays / kein laufender CCU-Lastprozess).

---

## 6. Referenzen

- [AGV-Position nach Order-Abschluss](agv-position-after-order-completion-2026-03.md)
- [APS-CCU Scenario Examples](../../integrations/APS-CCU/docs/10-scenario-examples.md) – VDA5050 order/instantAction Beispiele
- [navigation.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts)
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts)
- [navigator-service.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigator-service.ts) — `convertPathToOrder`, `inferIntersectionNodeAction`
- [factory-layout-service.ts](../../integrations/APS-CCU/central-control/src/modules/layout/factory-layout-service.ts) — Graph-Knoten-IDs (Serial / Kreuzung)
