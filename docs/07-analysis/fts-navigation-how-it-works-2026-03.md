# FTS/AGV-Navigation: Wie funktioniert sie?

**Datum:** 2026-03-13  
**Quelle:** CCU-Code, VDA5050/Protocol, osf-ui AGV-Tab  
**Ziel:** Wer erstellt NAV-Anweisungen? Welche Topics und Payloads? Kann osf-ui manuell navigieren?

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

**Beispiel (DPS → HBW):**
```json
{
  "timestamp": "2026-03-13T12:00:00.000Z",
  "orderId": "uuid",
  "orderUpdateId": 0,
  "nodes": [
    { "id": "serial:SVR4H73275", "linkedEdges": ["..."], "action": null },
    { "id": "intersection:1", "linkedEdges": ["..."], "action": null },
    { "id": "serial:SVR3QA0022", "linkedEdges": ["..."], "action": { "type": "STOP", "id": "...", "metadata": {} } }
  ],
  "edges": [
    { "id": "road-id", "length": 360, "linkedNodes": ["serial:SVR4H73275", "intersection:1"] }
  ],
  "serialNumber": "5iO4",
  "metadata": { "requestedFrom": "SVR4H73275" }
}
```

**Node-IDs:** Layout nutzt `serial:SVR3QA0022` (HBW), `serial:SVR4H73275` (DPS), `serial:SVR4H76530` (AIQS), `intersection:1`, `intersection:2` usw. Der Pfad wird via `AgvRouteService.findRoutePath(start, target)` berechnet.

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

**Ja, möglich.** Der AGV-Tab publiziert dieselben Topics wie die CCU.

### 3.1 Buttons (seit v0.8.12)

| Button | Voraussetzung | Topic | Ziel |
|--------|---------------|-------|------|
| **DPS → HBW** | AGV am DPS | `fts/v1/ff/{serial}/order` | SVR3QA0022 (HBW) |
| **AIQS → HBW** | AGV am AIQS | `fts/v1/ff/{serial}/order` | SVR3QA0022 (HBW) |
| **→ Intersection 2** | Bekannte AGV-Position | `fts/v1/ff/{serial}/order` | 2 (Intersection 2) |

**Serial:** Verwendet wird die aktuell ausgewählte AGV-Serial (`selectedAgvSerial$`) – also AGV-1 (5iO4) oder AGV-2 (IeJ4) je nach Dropdown. Kein hart codiertes 5iO4 in den Command-Payloads.

### 3.2 Technische Umsetzung

- `buildOrderFromTo(startNodeId, targetNodeId)` baut VDA5050-Order aus Layout-Pfad
- `AgvRouteService.findRoutePath()` und `findRoadBetween()` für nodes/edges
- Buttons deaktiviert, wenn Startposition nicht passt (DPS→HBW nur wenn AGV am DPS usw.)

---

## 4. Referenzen

- [AGV-Position nach Order-Abschluss](agv-position-after-order-completion-2026-03.md)
- [APS-CCU Scenario Examples](../../integrations/APS-CCU/docs/10-scenario-examples.md) – VDA5050 order/instantAction Beispiele
- [navigation.ts](../../integrations/APS-CCU/central-control/src/modules/fts/navigation/navigation.ts)
- [order-management.ts](../../integrations/APS-CCU/central-control/src/modules/order/management/order-management.ts)
