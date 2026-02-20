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

1. ~~**ERP-Integration:** Wie sollen echte ERP-IDs integriert werden?~~ ✅ **Gelöst (2025-12-20):** `ErpOrderDataService` Integration implementiert, ERP-Daten werden aus Process-Tab übernommen
2. ~~**Order-Historie:** Sollen auch abgeschlossene Orders (`ccu/order/completed`) berücksichtigt werden?~~ ✅ **Gelöst (2025-12-20):** Beide Streams (`ccu/order/active` und `ccu/order/completed`) werden abonniert, Status wird korrekt angezeigt
3. **Multi-Order:** Was passiert, wenn ein Workpiece mehrere Orders durchläuft? (Zukünftige Aufgabe - aktuell wird nur die erste passende Order verwendet)

## Referenzen

- `osf/apps/osf-ui/src/app/services/workpiece-history.service.ts`
- `docs/07-analysis/production-order-analysis-results.md`
- *(Schema/Topics: OMF2 registry entfernt – Referenz in `docs/06-integrations/00-REFERENCE/`)*

## Aktueller Status (2025-12-20)

### Fixture System

**Status:** ✅ Vollständig funktionsfähig

**Verfügbare Fixtures:**
- `production_bwr`: Production BWR Szenario (1478 Messages, 34 FTS Messages mit loadId)
- `production_white`: Production White Szenario (977 Messages, 9 FTS Messages mit loadId)
- `storage_blue`: Storage Blue Szenario (371 Messages, 18 FTS Messages mit loadId)

**UI-Konsistenz:**
- Alle Tabs verwenden einheitliches Fixture-UI-Pattern (basierend auf Module-Tab)
- Track & Trace Tab bietet 3 Fixture-Optionen: Production BWR, Production White, Storage Blue
- AGV-Tab bietet erweiterte Fixture-Optionen: `startup`, `white`, `blue`, `red`, `mixed`, `storage`, `production_bwr`, `production_white`, `storage_blue`

**Dokumentation:**
- Hauptdokumentation: `osf/libs/testing-fixtures/README.md`
- Tab-spezifische Presets: `osf/libs/testing-fixtures/src/tab-fixtures.ts`

## Erweiterte Features (2025-12-20)

### 1. TURN LEFT/RIGHT Icons

**Problem:** FTS TURN Events wurden bisher nur mit einem generischen Turn-Icon angezeigt, ohne Unterscheidung zwischen Links- und Rechtskurven.

**Lösung:**
- **FTS Order Stream Integration:** Der `WorkpieceHistoryService` abonniert den `ccu/order/fts` Topic, um TURN-Richtungen zu extrahieren
- **Direction Mapping:** TURN-Actions werden mit ihrer Richtung (`LEFT` oder `RIGHT`) aus dem Order-Stream gemappt (`turnDirectionByActionId`)
- **Event Details:** Die Richtung wird in `event.details['direction']` gespeichert
- **Icon Selection:** `TrackTraceComponent.getEventIcon()` prüft die Richtung und verwendet:
  - `ICONS.shopfloor.shared.turnLeftEvent` für TURN LEFT
  - `ICONS.shopfloor.shared.turnRightEvent` für TURN RIGHT
  - `ICONS.shopfloor.shared.turnEvent` als Fallback
- **Label Display:** `getEventLabel()` zeigt "TURN LEFT" oder "TURN RIGHT" an

**Implementierung:**
```typescript
// In WorkpieceHistoryService
private readonly turnDirectionByActionId = new Map<string, 'LEFT' | 'RIGHT' | string>();

// Subscribe to FTS order stream
const ftsOrder$ = this.messageMonitor.getLastMessage('ccu/order/fts').pipe(...);
ftsOrder$.subscribe((order: any) => {
  if (Array.isArray(order.nodes)) {
    order.nodes.forEach((node: any) => {
      const action = node?.action;
      if (action?.type === 'TURN' && action?.id && action?.metadata?.direction) {
        this.turnDirectionByActionId.set(action.id, action.metadata.direction);
      }
    });
  }
});

// In event generation
if (eventType === 'TURN') {
  const actionStateMeta = (state.actionState as any)?.metadata;
  if (actionStateMeta?.direction) {
    turnDirection = actionStateMeta.direction;
  } else {
    turnDirection = this.turnDirectionByActionId.get(state.actionState.id);
  }
  details.direction = turnDirection;
}
```

### 2. Order Status (Active/Completed)

**Problem:** Der Order Context zeigte keine Information darüber, ob eine Order aktuell aktiv oder bereits abgeschlossen ist.

**Lösung:**
- **Dual Order Stream:** `WorkpieceHistoryService` abonniert sowohl `ccu/order/active` als auch `ccu/order/completed`
- **Status Determination:** `generateOrderContext()` prüft, ob eine Order-ID in `completed` Orders vorhanden ist
- **Status Field:** `OrderContext` Interface erweitert um `status?: 'ACTIVE' | 'COMPLETED'`
- **UI Display:** Track-Trace Template zeigt Status mit farblicher Hervorhebung (grün für Active, grau für Completed)

**Implementierung:**
```typescript
// In generateOrderContext()
const normalizedOrders = {
  active: activeOrders || {},
  completed: completedOrders || {}
};

const isCompleted = normalizedOrders.completed[orderId] !== undefined;
const orderStatus: 'ACTIVE' | 'COMPLETED' = isCompleted ? 'COMPLETED' : 'ACTIVE';

contexts.push({
  ...orderData,
  status: orderStatus,
});
```

### 3. ERP-Daten Verknüpfung

**Problem:** ERP-Daten (Purchase Orders, Customer Orders) aus dem Process-Tab wurden nicht mit den Track-Trace Order Contexts verknüpft.

**Lösung:**
- **ErpOrderDataService Integration:** `WorkpieceHistoryService` verwendet `ErpOrderDataService` um ERP-Daten abzurufen
- **Storage Orders:** Für Storage Orders wird `popPurchaseOrderForWorkpieceType(workpieceType)` aufgerufen
- **Production Orders:** Für Production Orders wird `popCustomerOrder()` aufgerufen
- **Priority:** ERP-Daten haben Priorität über generierte Fake-IDs, aber Fallback auf Fake-IDs bleibt bestehen

**Implementierung:**
```typescript
// In generateOrderContext() for STORAGE orders
const workpieceTypeUpper = workpieceType.toUpperCase() as 'BLUE' | 'WHITE' | 'RED';
const erpPurchaseData = this.erpOrderDataService.popPurchaseOrderForWorkpieceType(workpieceTypeUpper);

contexts.push({
  orderId,
  orderType: 'STORAGE',
  purchaseOrderId: purchaseOrderId || erpPurchaseData?.purchaseOrderId || generatePurchaseOrderId(),
  supplierId: erpPurchaseData?.supplierId || generateSupplierId(),
  orderDate: erpPurchaseData?.orderDate || orderDate,
  rawMaterialOrderDate: erpPurchaseData?.orderDate,
  // ...
});

// In generateOrderContext() for PRODUCTION orders
const erpCustomerData = this.erpOrderDataService.popCustomerOrder();

contexts.push({
  orderId,
  orderType: 'PRODUCTION',
  customerOrderId: customerOrderId || erpCustomerData?.customerOrderId || generateCustomerOrderId(),
  customerId: erpCustomerData?.customerId || generateCustomerId(),
  orderDate: erpCustomerData?.orderDate || orderDate,
  customerOrderDate: erpCustomerData?.orderDate,
  // ...
});
```

### 4. Zusätzliche Datenfelder

**Problem:** Der Order Context zeigte nur grundlegende Daten (Order Date, Start/End Time), aber keine spezifischen Meilensteine wie Lieferung, Storage, Produktions-Start, etc.

**Lösung:**
- **Event Analysis:** `extractDatesFromEvents()` analysiert die Event-Historie eines Workpieces
- **Date Extraction:** Spezifische Daten werden aus Events extrahiert:
  - **Storage Orders:**
    - `deliveryDate`: Erstes DPS-Event (Lieferung-Datum - wann angeliefert im DPS)
    - `storageDate`: Erstes HBW-Event (Storage-Datum - wann im HBW eingelagert)
  - **Production Orders:**
    - `productionStartDate`: Letztes HBW-Event vor erstem Manufacturing-Event (Produktions-Start - Auslagerung aus HBW)
    - `deliveryEndDate`: Letztes DPS-Event (Auslieferungs-Datum - Production-Ende im DPS)
- **OrderContext Interface:** Erweitert um zusätzliche optionale Felder:
  - `rawMaterialOrderDate?: string` - Bestellung-Datum RAW-Material (aus ERP)
  - `deliveryDate?: string` - Lieferung-Datum (aus Events)
  - `storageDate?: string` - Storage-Datum (aus Events)
  - `customerOrderDate?: string` - Bestellung-Datum Customer-Order (aus ERP)
  - `productionStartDate?: string` - Produktions-Start (aus Events)
  - `deliveryEndDate?: string` - Auslieferungs-Datum (aus Events)

**Implementierung:**
```typescript
private extractDatesFromEvents(
  events: TrackTraceEvent[],
  orderType: 'STORAGE' | 'PRODUCTION'
): {
  deliveryDate?: string;
  storageDate?: string;
  productionStartDate?: string;
  deliveryEndDate?: string;
} {
  const dpsId = 'SVR4H73275';
  const hbwId = 'SVR3QA0022';
  
  const result = {};
  
  // Find first DPS event (delivery date for storage orders)
  if (orderType === 'STORAGE') {
    const firstDpsEvent = events.find(e => e.location === dpsId || e.moduleId === dpsId);
    if (firstDpsEvent) {
      result.deliveryDate = firstDpsEvent.timestamp;
    }
  }
  
  // Find first HBW event (storage date)
  const firstHbwEvent = events.find(e => e.location === hbwId || e.moduleId === hbwId);
  if (firstHbwEvent) {
    result.storageDate = firstHbwEvent.timestamp;
  }
  
  // Find last HBW event before production (production start)
  if (orderType === 'PRODUCTION') {
    const manufacturingEvents = events.filter(e => 
      e.stationId === 'DRILL' || e.stationId === 'MILL' || e.stationId === 'AIQS'
    );
    if (manufacturingEvents.length > 0) {
      const firstManufacturingEvent = manufacturingEvents[0];
      const hbwEventsBeforeProduction = events.filter(e => 
        (e.location === hbwId || e.moduleId === hbwId) &&
        new Date(e.timestamp).getTime() < new Date(firstManufacturingEvent.timestamp).getTime()
      );
      if (hbwEventsBeforeProduction.length > 0) {
        const lastHbwEvent = hbwEventsBeforeProduction[hbwEventsBeforeProduction.length - 1];
        result.productionStartDate = lastHbwEvent.timestamp;
      }
    }
  }
  
  // Find last DPS event (delivery end date for production orders)
  if (orderType === 'PRODUCTION') {
    const dpsEvents = events.filter(e => e.location === dpsId || e.moduleId === dpsId);
    if (dpsEvents.length > 0) {
      const lastDpsEvent = dpsEvents[dpsEvents.length - 1];
      result.deliveryEndDate = lastDpsEvent.timestamp;
    }
  }
  
  return result;
}
```

### 5. Internationalization (i18n)

**Problem:** Die neuen Datenfelder hatten deutsche Begriffe als Default-Texte im Template.

**Lösung:**
- **Default Language:** Alle Template-Texte auf Englisch geändert
- **I18n Keys:** Neue Keys hinzugefügt für alle Datenfelder:
  - `@@trackTraceOrderStatus`, `@@trackTraceOrderStatusActive`, `@@trackTraceOrderStatusCompleted`
  - `@@trackTraceRawMaterialOrderDate` - "Raw Material Order Date:"
  - `@@trackTraceDeliveryDate` - "Delivery Date:"
  - `@@trackTraceStorageDate` - "Storage Date:"
  - `@@trackTraceCustomerOrderDate` - "Customer Order Date:"
  - `@@trackTraceProductionStartDate` - "Production Start:"
  - `@@trackTraceDeliveryEndDate` - "Delivery Date:"
- **DE/FR Translations:** Vollständige Übersetzungen in `messages.de.json` und `messages.fr.json`

**Dateien:**
- `osf/apps/osf-ui/src/app/components/track-trace/track-trace.component.html` - Template mit englischen Defaults
- `osf/apps/osf-ui/src/locale/messages.de.json` - Deutsche Übersetzungen
- `osf/apps/osf-ui/src/locale/messages.fr.json` - Französische Übersetzungen

## Referenzen

- `osf/apps/osf-ui/src/app/services/workpiece-history.service.ts` - Hauptservice für Track & Trace
- `osf/apps/osf-ui/src/app/components/track-trace/track-trace.component.ts` - UI-Komponente
- `osf/apps/osf-ui/src/app/services/erp-order-data.service.ts` - ERP-Daten Service
- `osf/apps/osf-ui/src/app/tabs/fts-tab.component.ts` - Referenz für TURN LEFT/RIGHT Logik
- `docs/07-analysis/production-order-analysis-results.md`
- *(Schema/Topics: OMF2 registry entfernt – Referenz in `docs/06-integrations/00-REFERENCE/`)*
