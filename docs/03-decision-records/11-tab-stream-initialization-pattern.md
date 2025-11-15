# Tab Stream Initialization Pattern

## Problem

Wenn Tabs später geöffnet werden, nachdem MQTT-Nachrichten bereits empfangen wurden, zeigen sie keine Daten an, weil die Dashboard-Streams bereits emittiert haben und mit `refCount: true` beendet wurden, wenn keine Subscriber vorhanden waren.

## Lösung: Hybrid Pattern

Wir verwenden ein zweistufiges Pattern, abhängig davon, ob der Gateway-Stream `startWith` hat:

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

### Pattern 2: Streams ohne `startWith` in Gateway-Layer

**Anwendbar auf:**
- `inventoryOverview$` (kommt von `gateway.stockSnapshots$`, kein `startWith` in Gateway)
- `flows$` (kommt direkt von `gateway.flows$`, kein `startWith` in Gateway)
- `config$` (kommt direkt von `gateway.config$`, kein `startWith` in Gateway)

**Implementierung:**
```typescript
// Hole letzten Wert aus MessageMonitorService
const lastValue = this.messageMonitor.getLastMessage<PayloadType>('topic/name').pipe(
  filter((msg) => msg !== null && msg.valid),
  map((msg) => msg!.payload),
  startWith(defaultValue)
);

// Merge mit Dashboard-Stream für Echtzeit-Updates
this.stream$ = merge(lastValue, this.dashboard.streams.stream$).pipe(
  shareReplay({ bufferSize: 1, refCount: false })
);
```

**Warum:**
- Gateway-Streams ohne `startWith` emittieren erst, wenn eine Nachricht ankommt
- Wenn die Nachricht bereits empfangen wurde, bevor der Tab geöffnet wird, ist der Stream bereits beendet
- MessageMonitorService speichert alle empfangenen Nachrichten, daher können wir den letzten Wert sofort abrufen
- Merge mit Dashboard-Stream stellt sicher, dass wir weiterhin Echtzeit-Updates erhalten

### Spezialfall: Transformation erforderlich

**Für `inventoryOverview$`:**
- MessageMonitorService speichert rohe `StockSnapshot` Payloads
- Business-Layer transformiert `StockSnapshot` zu `InventoryOverviewState`
- Wir müssen die Transformation im Tab durchführen:

```typescript
const lastInventory = this.messageMonitor.getLastMessage<StockSnapshot>('ccu/state/stock').pipe(
  filter((msg) => msg !== null && msg.valid),
  map((msg) => this.buildInventoryOverviewFromSnapshot(msg!.payload)),
  startWith(defaultInventoryOverview)
);
```

## Regeln

1. **Immer `refCount: false` verwenden** in Tab-Komponenten, um Streams aktiv zu halten
2. **Prüfe Gateway-Streams** auf `startWith` - wenn vorhanden, Pattern 1 verwenden
3. **Wenn kein `startWith`** in Gateway-Layer, Pattern 2 verwenden
4. **Bei Transformation erforderlich**, Transformationslogik im Tab implementieren
5. **Konsistentes Pattern** in allen Tabs anwenden

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

