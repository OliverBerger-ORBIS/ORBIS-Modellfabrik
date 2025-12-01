# Track & Trace Architecture

**Datum:** 2025-12-02  
**Status:** Entscheidung getroffen  
**Kontext:** Integration von Track & Trace Funktionalität in OMF3

## Problemstellung

Track & Trace soll die komplette Historie eines Workpieces (Rohmaterial → Produktion → Fertigprodukt) nachverfolgen. Die Order-IDs müssen vom APS-CCU Backend kommen, nicht künstlich generiert werden.

## Architektur-Übersicht

### Datenquellen

1. **FTS State Messages** (`fts/v1/ff/5iO4/state`)
   - Enthält: `orderId` (UUID vom CCU-Backend), `orderUpdateId`, `load[]` (Workpiece-IDs), `lastNodeId`, `actionState`
   - **Kritisch:** `orderId` ist die echte UUID vom CCU-Backend, nicht generiert!

2. **CCU Order Active** (`ccu/order/active`)
   - Enthält: Array von aktiven Orders mit `orderId`, `orderType` (STORAGE/PRODUCTION), `productionSteps`, `startedAt`, `workpieceId`
   - **Kritisch:** `orderType` bestimmt, ob es eine Storage- oder Production-Order ist

3. **Module State Messages** (`module/v1/ff/<serial>/state`)
   - Enthält: Module-spezifische States für PROCESS-Events (Dauer, etc.)

### Track & Trace Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. FTS State Message empfangen                                │
│    - orderId: "8e79e45c-f4dc-4e2a-b7b9-8f56c3238c52" (UUID) │
│    - load: [{ loadId: "047389ca341291", loadType: "BLUE" }] │
│    - lastNodeId: "SVR4H76530"                                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Order-Type bestimmen                                      │
│    - Match orderId mit ccu/order/active                     │
│    - Wenn Match: orderType aus ccu/order/active verwenden   │
│    - Wenn kein Match: orderType aus Location/Events ableiten │
│      (HBW/Manufacturing Stations → PRODUCTION)              │
│      (DPS ohne HBW → STORAGE)                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Event generieren                                          │
│    - Event mit orderId (echte UUID!)                        │
│    - Event mit orderType (STORAGE oder PRODUCTION)           │
│    - Event mit subOrderId (orderId + Sequenznummer)         │
│    - Event mit actionId (aus actionState.id)                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Order Context generieren                                  │
│    - orderId: Echte UUID aus FTS State                      │
│    - orderType: Aus ccu/order/active oder abgeleitet       │
│    - ERP-IDs: Nur wenn nicht verfügbar → Fake (ERP-PO-...) │
│      (Purchase Order ID, Customer Order ID, Supplier ID,    │
│       Customer ID, Order Date)                              │
└─────────────────────────────────────────────────────────────┘
```

## Entscheidungen

### 1. Order-IDs müssen vom Backend kommen

**Problem:** Aktuell werden künstliche Order-IDs generiert (`storage-blue-${Date.now()}`), wenn keine Orders aus `ccu/order/active` gefunden werden.

**Lösung:**
- **Order-IDs** kommen IMMER aus `state.orderId` (FTS State)
- **Order-Type** wird aus `ccu/order/active` gematcht (Order-ID → Order-Type)
- Wenn kein Match: Order-Type wird aus Location/Events abgeleitet, aber Order-ID bleibt die echte UUID

### 2. Order-Type Bestimmung

**Priorität:**
1. **Match mit `ccu/order/active`**: Wenn `state.orderId` in `ccu/order/active` gefunden wird, verwende `order.orderType`
2. **Ableitung aus Events/Location**: 
   - Wenn Workpiece an HBW oder Manufacturing Stations (MILL, DRILL, AIQS) war → PRODUCTION
   - Wenn Workpiece nur an DPS war und nie an HBW/Manufacturing Stations → STORAGE

### 3. ERP-IDs sind optional (Fake wenn nicht verfügbar)

**ERP-IDs werden nur generiert, wenn sie nicht im Backend verfügbar sind:**
- `purchaseOrderId`: `ERP-PO-XXXXXX` (nur für STORAGE Orders)
- `customerOrderId`: `ERP-CO-XXXXXX` (nur für PRODUCTION Orders)
- `supplierId`: `SUP-XXXX` (nur für STORAGE Orders)
- `customerId`: `CUST-XXXX` (nur für PRODUCTION Orders)
- `orderDate`: `startedAt` aus `ccu/order/active` oder aktuelles Datum

**Wichtig:** Diese sind "Fake"-Daten für Demo-Zwecke. In einer echten Integration würden diese vom ERP-System kommen.

### 4. Event-Generierung

**Events werden generiert für:**
- Jede Location-Änderung (FTS bewegt sich)
- Jede Action (DOCK, PICK, PROCESS, DROP, TURN, PASS)
- Jede Station (HBW, DPS, MILL, DRILL, AIQS)

**Event-Struktur:**
```typescript
{
  timestamp: string;
  workpieceId: string;
  workpieceType: 'BLUE' | 'WHITE' | 'RED';
  location: string; // Node ID (z.B. "SVR4H76530")
  moduleId: string; // Serial ID (z.B. "SVR4H76530")
  moduleName: string; // Display Name (z.B. "AIQS")
  orderId: string; // Echte UUID vom CCU-Backend
  orderType: 'STORAGE' | 'PRODUCTION';
  orderUpdateId: number; // Aus FTS State
  subOrderId: string; // `${orderId}-${sequenznummer}`
  actionId: string; // Aus actionState.id
  eventType: 'DOCK' | 'PICK' | 'DROP' | 'TRANSPORT' | 'PROCESS' | 'TURN' | 'PASS';
}
```

## Implementierung

### WorkpieceHistoryService

**Kritische Änderungen:**

1. **Order-IDs aus FTS State verwenden:**
   ```typescript
   // In updateWorkpieceHistory()
   const orderId = state.orderId; // Echte UUID, nicht generiert!
   ```

2. **Order-Type matchen:**
   ```typescript
   // Match orderId mit ccu/order/active
   const matchedOrder = activeOrders?.find(o => o.orderId === state.orderId);
   const orderType = matchedOrder?.orderType || this.determineOrderType(...);
   ```

3. **Order Context generieren:**
   ```typescript
   // generateOrderContext() sollte:
   // - orderId aus FTS State verwenden (nicht generieren!)
   // - orderType aus ccu/order/active matchen
   // - Nur ERP-IDs generieren, wenn nicht verfügbar
   ```

## Offene Fragen

1. **ERP-Integration:** Wie sollen echte ERP-IDs integriert werden? (Zukünftige Aufgabe)
2. **Order-Historie:** Sollen auch abgeschlossene Orders (`ccu/order/completed`) berücksichtigt werden?
3. **Multi-Order:** Was passiert, wenn ein Workpiece mehrere Orders durchläuft?

## Referenzen

- `omf3/apps/ccu-ui/src/app/services/workpiece-history.service.ts`
- `docs/07-analysis/production-order-analysis-results.md`
- `omf2/registry/schemas/ccu_order_active.schema.json`
- `omf2/registry/topics/ccu.yml`

## Aktueller Status & Bekannte Probleme (2025-12-02)

### Fixture Loading Issue

**Problem:**
- Track & Trace Tab zeigt Fixture-Button, aber beim Klicken werden keine Workpieces angezeigt
- `WorkpieceHistoryService` wird bereits im `TrackTraceComponent.ngOnInit()` initialisiert
- Beim Fixture-Load wird `clear()` und `initialize()` aufgerufen, aber der Service reagiert nicht auf neue Messages

**Aktuelle Implementierung:**
- `TrackTraceTabComponent.loadFixture()` ruft `clear()` und dann `initialize()` auf
- `clear()` löscht die Subscription, danach kann `initialize()` erneut aufgerufen werden
- Service sollte auf neue Messages vom Fixture reagieren über `MessageMonitorService.getLastMessage()`

**Status:** In Testing - Fixture-Load funktioniert, aber Workpieces werden nicht angezeigt

**Nächste Schritte:**
- Debugging: Prüfen ob Messages vom Fixture korrekt an `MessageMonitorService` weitergegeben werden
- Prüfen ob `WorkpieceHistoryService` korrekt auf neue Messages subscribed
- Falls nicht: Eventuell `getLastMessage()` durch direkten Stream-Subscription ersetzen

