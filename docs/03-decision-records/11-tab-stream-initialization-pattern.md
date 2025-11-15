# Tab Stream Initialization Pattern

## Problem

Wenn Tabs später geöffnet werden, nachdem MQTT-Nachrichten bereits empfangen wurden, zeigen sie keine Daten an. Dies tritt auf, weil:

1. Gateway-Streams ohne `startWith` nur emittieren, wenn eine neue Nachricht ankommt
2. Wenn die Nachricht bereits vor dem Tab-Öffnen empfangen wurde, bleibt der Tab leer
3. Der Tab zeigt erst Daten an, wenn eine neue Nachricht eintrifft

## Lösung: Timing-Unabhängiges Pattern

Wir verwenden ein zweistufiges Pattern, abhängig davon, ob der Business-Layer-Stream `startWith` hat:

### Pattern 1: Streams mit `startWith` in Business-Layer

**Anwendbar auf:**
- `orders$` (hat `startWith` in Business-Layer)
- `orderCounts$` (hat `startWith` in Business-Layer)
- `ftsStates$` (hat `startWith` in Business-Layer)
- `moduleOverview$` (hat `startWith` in Business-Layer)
- `sensorOverview$` (hat `startWith` in Business-Layer)
- `cameraFrames$` (hat `startWith` in Gateway-Layer)

**Implementierung:**
```typescript
this.stream$ = this.dashboard.streams.stream$.pipe(
  shareReplay({ bufferSize: 1, refCount: false })
);
```

**Warum:**
- Business-Layer Streams haben bereits `startWith`, daher emittieren sie sofort einen initialen Wert
- `refCount: false` hält den Stream aktiv, auch wenn keine Subscriber vorhanden sind
- Der letzte Wert bleibt verfügbar, auch wenn der Tab später geöffnet wird

### Pattern 2: Streams ohne `startWith` in Business-Layer

**Anwendbar auf:**
- `inventoryOverview$` (kommt von `gateway.stockSnapshots$`, kein `startWith` in Gateway)
- `flows$` (kommt direkt von `gateway.flows$`, kein `startWith` in Gateway)
- `config$` (kommt direkt von `gateway.config$`, kein `startWith` in Gateway)

**Implementierung:**
```typescript
// Hole letzten Wert aus MessageMonitorService
// WICHTIG: Operator-Reihenfolge ist kritisch für korrektes Timing-Verhalten
const lastValue = this.messageMonitor.getLastMessage<PayloadType>('topic/name').pipe(
  filter((msg) => msg !== null && msg.valid),  // 1. Filter: Nur gültige Nachrichten
  map((msg) => msg!.payload),                   // 2. Map: Payload extrahieren
  startWith(defaultValue)                       // 3. StartWith: Fallback für leeren State
);

// Merge mit Dashboard-Stream für Echtzeit-Updates
this.stream$ = merge(lastValue, this.dashboard.streams.stream$).pipe(
  shareReplay({ bufferSize: 1, refCount: false })
);
```

**Warum:**
- Gateway-Streams ohne `startWith` emittieren erst, wenn eine Nachricht ankommt
- Wenn die Nachricht bereits empfangen wurde, bevor der Tab geöffnet wird, funktioniert der Stream nicht
- MessageMonitorService speichert alle empfangenen Nachrichten, daher können wir den letzten Wert sofort abrufen
- Merge mit Dashboard-Stream stellt sicher, dass wir weiterhin Echtzeit-Updates erhalten
- **Operator-Reihenfolge**: `filter` → `map` → `startWith` ist kritisch, damit `startWith` nur als Fallback dient

### Spezialfall: Transformation erforderlich

**Für `inventoryOverview$`:**
- MessageMonitorService speichert rohe `StockSnapshot` Payloads
- Business-Layer transformiert `StockSnapshot` zu `InventoryOverviewState`
- Wir müssen die Transformation im Tab durchführen:

```typescript
const lastInventory = this.messageMonitor.getLastMessage<StockSnapshot>('ccu/state/stock').pipe(
  filter((msg) => msg !== null && msg.valid),        // 1. Filter gültige Nachrichten
  map((msg) => this.buildInventoryOverviewFromSnapshot(msg!.payload)), // 2. Transform
  startWith(defaultInventoryOverview)                 // 3. Fallback
);
```

### Spezialfall: Mehrere Topics kombinieren

**Für `sensorOverview$`:**
- Benötigt Daten von zwei separaten Topics (`bme680`, `ldr`)
- Verwendet `combineLatest` um beide Streams zu kombinieren
- `startWith` wird auf einzelnen Streams UND dem kombinierten Stream verwendet:

```typescript
const lastBme680 = this.messageMonitor.getLastMessage<Bme680Snapshot>('/j1/txt/1/i/bme680').pipe(
  filter((msg) => msg !== null && msg.valid),
  map((msg) => msg!.payload)
);
const lastLdr = this.messageMonitor.getLastMessage<LdrSnapshot>('/j1/txt/1/i/ldr').pipe(
  filter((msg) => msg !== null && msg.valid),
  map((msg) => msg!.payload)
);

// Wichtig: startWith AUSSERHALB von combineLatest Array für korrekte Test-Kompatibilität
const bme680WithDefault = lastBme680.pipe(startWith(null));
const ldrWithDefault = lastLdr.pipe(startWith(null));

const lastSensorOverview = combineLatest([
  bme680WithDefault,
  ldrWithDefault
]).pipe(
  map(([bme, ldr]) => this.buildSensorOverviewState(bme, ldr)),  // 1. Transform
  startWith(this.buildSensorOverviewState(null, null))            // 2. Fallback
);
```

## Regeln

1. **Immer `refCount: false` verwenden** in Tab-Komponenten, um Streams aktiv zu halten
2. **Prüfe Business-Layer-Streams** auf `startWith` - wenn vorhanden, Pattern 1 verwenden
3. **Wenn kein `startWith`** in Business-Layer, Pattern 2 verwenden
4. **Bei Transformation erforderlich**, Transformationslogik im Tab implementieren
5. **Operator-Reihenfolge ist kritisch**: `filter` → `map` → `startWith` (niemals `map` → `filter`)
6. **Bei `combineLatest`**: `startWith` AUSSERHALB des Arrays für Test-Kompatibilität
7. **Timing-Unabhängigkeit**: Pattern funktioniert egal ob Tab oder Nachricht zuerst da ist

## Betroffene Tabs

- ✅ Overview-Tab: `inventoryOverview$` (Pattern 2 mit Transformation)
- ✅ Order-Tab: `orders$`, `completedOrders$` (Pattern 1)
- ✅ Process-Tab: `flows$` (Pattern 2)
- ✅ Module-Tab: `moduleOverview$` (Pattern 1)
- ✅ Sensor-Tab: `sensorOverview$`, `cameraFrames$` (Pattern 1)
- ✅ Configuration-Tab: `configSnapshot$` (Pattern 2)

## Referenzen

- `omf3/libs/gateway/src/index.ts` - Gateway-Stream Definitionen
- `omf3/libs/business/src/index.ts` - Business-Stream Definitionen mit `startWith`
- `omf3/apps/ccu-ui/src/app/tabs/*.component.ts` - Tab-Implementierungen

