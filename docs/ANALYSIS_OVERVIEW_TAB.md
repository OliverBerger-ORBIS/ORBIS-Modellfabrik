# Analyse: Overview-Tab Funktionalität und Migration

**Datum:** 20.12.2025  
**Status:** ✅ **Overview-Tab wurde entfernt** (20.12.2025)  
**Zweck:** Prüfung welche Funktionalität noch ausschließlich im Overview-Tab vorhanden ist und ob Update-Patterns konsistent sind.

## Zusammenfassung

Nach dem Rebranding und der Migration von Overview-Tab Features zu Process-Tab und Module-Tab (Shopfloor) gibt es noch **3 Features, die ausschließlich im Overview-Tab vorhanden sind**:

1. **OrdersViewComponent** - Zeigt aktive Orders mit Status-Badges (Running/Queued/Completed)
2. **AgvViewComponent** - Zeigt AGV Fleet Status (FTS States)
3. **Inventory Grid (A1-C3)** - Visuelle Darstellung aller Inventory-Slots (nicht nur HBW)

## Feature-Vergleich

### ✅ Migriert zu Process-Tab

| Feature | Overview-Tab | Process-Tab | Status |
|---------|--------------|-------------|--------|
| Purchase Orders | ✅ | ✅ | Migriert |
| Customer Orders | ✅ | ✅ | Migriert |
| Order Raw Material Button | ✅ | ✅ | Migriert |
| Order Workpiece Button | ✅ | ✅ | Migriert |
| Inventory State Service | ✅ | ✅ | Gleiche Logik |
| ERP Info Box | ❌ | ✅ | Neu hinzugefügt |

### ✅ Migriert zu Module-Tab (Shopfloor)

| Feature | Overview-Tab | Module-Tab | Status |
|---------|--------------|------------|--------|
| HBW Stock Information | ✅ (Inventory Grid) | ✅ (HBW Stock Grid) | Migriert |
| Module Status | ❌ | ✅ | Neu hinzugefügt |
| Shopfloor Preview | ❌ | ✅ | Neu hinzugefügt |

### ❌ Nur im Overview-Tab

| Feature | Beschreibung | Verwendung |
|---------|--------------|------------|
| **OrdersViewComponent** | Zeigt Liste aller aktiven Orders mit Status-Badges (Running/Queued/Completed) | Nur im Overview-Tab |
| **AgvViewComponent** | Zeigt AGV Fleet Status (FTS States) mit Positionen | Nur im Overview-Tab |
| **Inventory Grid (A1-C3)** | Visuelle Darstellung aller 9 Inventory-Slots (A1, A2, A3, B1, B2, B3, C1, C2, C3) | Nur im Overview-Tab |

## Update-Patterns Analyse

### Konsistenz-Check: RxJS Stream Patterns

#### Overview-Tab
```typescript
// Persistente Streams (refCount: false)
this.orders$ = this.dashboard.streams.orders$.pipe(
  shareReplay({ bufferSize: 1, refCount: false })
);

// Inventory State Service (refCount: true)
const inventory$ = this.inventoryState.getState$(envKey).pipe(
  shareReplay({ bufferSize: 1, refCount: true })
);

// MessageMonitor Pattern (refCount: false)
const lastInventory = this.messageMonitor.getLastMessage<StockSnapshot>('ccu/state/stock').pipe(
  filter((msg) => msg !== null && msg.valid),
  map((msg) => this.buildInventoryOverviewFromSnapshot(msg!.payload)),
  startWith(initialState)
);
return merge(lastInventory, this.dashboard.streams.inventoryOverview$).pipe(
  shareReplay({ bufferSize: 1, refCount: false })
);
```

#### Process-Tab
```typescript
// Persistente Streams (refCount: false) ✅ KONSISTENT
this.flows$ = merge(lastFlows, this.dashboard.streams.flows$).pipe(
  shareReplay({ bufferSize: 1, refCount: false })
);

// Inventory State Service (refCount: true) ✅ KONSISTENT
const inventory$ = this.inventoryState.getState$(envKey).pipe(
  shareReplay({ bufferSize: 1, refCount: true })
);

// MessageMonitor Pattern (refCount: false) ✅ KONSISTENT
const lastInventory = this.messageMonitor.getLastMessage<StockSnapshot>('ccu/state/stock').pipe(
  filter((msg) => msg !== null && msg.valid),
  map((msg) => this.buildInventoryOverviewFromSnapshot(msg!.payload)),
  startWith(initialState)
);
return merge(lastInventory, this.dashboard.streams.inventoryOverview$).pipe(
  shareReplay({ bufferSize: 1, refCount: false })
);
```

#### Module-Tab
```typescript
// Persistente Streams (refCount: false) ✅ KONSISTENT
this.moduleOverview$ = merge(lastModuleOverview, this.dashboard.streams.moduleOverview$).pipe(
  shareReplay({ bufferSize: 1, refCount: false })
);
```

**Ergebnis:** ✅ **Update-Patterns sind konsistent** - alle Tabs verwenden:
- `shareReplay({ bufferSize: 1, refCount: false })` für persistente Dashboard-Streams
- `shareReplay({ bufferSize: 1, refCount: true })` für State-Service-Streams
- MessageMonitorService Pattern mit `getLastMessage()` + `merge()` + `startWith()`

## Fixture-Verwendung Analyse

### Overview-Tab Fixtures
```typescript
const presetMap: Partial<Record<OrderFixtureName, string>> = {
  startup: 'overview-startup',
  white: 'overview-active',
  white_step3: 'overview-active',
  blue: 'overview-active',
  red: 'overview-active',
  mixed: 'overview-active',
  storage: 'overview-active',
};
```

**Verwendete Presets:**
- `overview-startup` - Startup-Zustand
- `overview-active` - Aktive Orders (orders: 'mixed', modules: 'default', stock: 'default')

### Process-Tab Fixtures
```typescript
const presetMap: Partial<Record<OrderFixtureName, string>> = {
  startup: 'process-startup',
  white: 'order-white',
  white_step3: 'order-white-step3',
  blue: 'order-blue',
  red: 'order-red',
  mixed: 'order-mixed',
  storage: 'order-storage',
};
```

**Verwendete Presets:**
- `process-startup` - Startup-Zustand
- `order-*` - Order-spezifische Fixtures (verwendet auch von Order-Tab)

### Module-Tab Fixtures
```typescript
// Verwendet module-default, shopfloor-status
```

**Verwendete Presets:**
- `module-default` - Default Module States
- `shopfloor-status` - Shopfloor Status Fixture

### Fixture-Konsistenz

**Problem:** Overview-Tab verwendet **tab-spezifische Fixtures** (`overview-startup`, `overview-active`), die nur für Overview-Tab definiert sind.

**Empfehlung:**
- ✅ Process-Tab verwendet `order-*` Fixtures (konsistent mit Order-Tab)
- ✅ Module-Tab verwendet `module-*` Fixtures (konsistent)
- ⚠️ Overview-Tab verwendet `overview-*` Fixtures (nur für Overview)

**Lösung:** Wenn Overview-Tab entfernt wird, können `overview-startup` und `overview-active` Presets aus `tab-fixtures.ts` entfernt werden.

## Empfehlungen

### 1. OrdersViewComponent & AgvViewComponent

**Option A:** In andere Tabs integrieren
- OrdersViewComponent → Process-Tab oder Order-Tab
- AgvViewComponent → AGV-Tab

**Option B:** Als separate Komponenten behalten
- Können in anderen Tabs wiederverwendet werden, wenn benötigt

**Option C:** Entfernen, wenn nicht mehr benötigt
- Prüfen ob die Informationen bereits in anderen Tabs verfügbar sind

### 2. Inventory Grid (A1-C3)

**Aktueller Stand:**
- Overview-Tab: Zeigt alle 9 Slots (A1-C3) visuell
- Module-Tab: Zeigt nur HBW Stock Grid (wenn HBW-Modul ausgewählt)

**Empfehlung:**
- ✅ HBW Stock Grid im Module-Tab ist ausreichend für die meisten Use Cases
- ⚠️ Inventory Grid könnte nützlich sein für Gesamtübersicht
- **Entscheidung:** Soll das Inventory Grid beibehalten werden oder ist HBW Stock Grid ausreichend?

### 3. Fixtures

**Empfehlung:**
- Wenn Overview-Tab entfernt wird: `overview-startup` und `overview-active` aus `tab-fixtures.ts` entfernen
- Process-Tab und Module-Tab verwenden bereits konsistente Fixtures

## Fazit

✅ **Update-Patterns sind konsistent** - alle Tabs verwenden die gleichen RxJS Patterns  
✅ **Meiste Features wurden migriert** - Purchase/Customer Orders → Process-Tab, HBW Info → Module-Tab  
⚠️ **3 Features nur im Overview-Tab** - OrdersViewComponent, AgvViewComponent, Inventory Grid  
⚠️ **Tab-spezifische Fixtures** - `overview-*` Fixtures nur für Overview-Tab

## ✅ Durchgeführte Maßnahmen (20.12.2025)

1. ✅ **Process-Tab Fixtures aktualisiert:** `overview-*` → `process-startup` / `order-*`
2. ✅ **Overview-Tab entfernt:** Component, HTML, SCSS gelöscht
3. ✅ **Route entfernt:** `app.routes.ts` bereinigt
4. ✅ **OrdersViewComponent & AgvViewComponent entfernt:** Komponenten und Tests gelöscht
5. ✅ **overview-* Presets entfernt:** Aus `tab-fixtures.ts` und README entfernt
6. ✅ **Referenzen aktualisiert:** 
   - `language.service.ts`: Fallback von `'overview'` → `'dsp'`
   - `app.component.ts`: Navigation Label entfernt
   - `app.component.spec.ts`: Test-Routes aktualisiert
   - `language.service.spec.ts`: Alle Test-URLs aktualisiert
   - `tab-stream-pattern.spec.ts`: OverviewTab Tests entfernt
   - `process-tab.component.ts`: Kommentare aktualisiert

**Ergebnis:** Overview-Tab wurde vollständig entfernt. Alle Features wurden zu Process-Tab und Module-Tab migriert.

