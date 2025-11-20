# Tab-Specific Fixture Loading

## Overview

Das Tab-spezifische Fixture-Loading-System ermöglicht es jedem Tab, unabhängig verschiedene Fixtures mit relevanten Topics zu laden. Dies verbessert die Mock-Umgebung, indem jeder Tab genau die Daten erhält, die er zum Testen benötigt.

## Verwendung

### Grundlegende Verwendung in Tabs

Jeder Tab kann jetzt entweder die alte `loadFixture()`-Methode oder die neue `loadTabFixture()`-Methode verwenden:

```typescript
// Alt: Globales Fixture für alle Streams
await this.dashboard.loadFixture('white');

// Neu: Tab-spezifisches Fixture-Preset
await this.dashboard.loadTabFixture('order-white');
```

### Verfügbare Presets

Die folgenden vorkonfigurierten Presets sind verfügbar:

#### Startup/Default
- **`startup`**: Initialer Zustand mit allen Grunddaten

#### Order Tab Presets
- **`order-white`**: White production order
- **`order-blue`**: Blue production order  
- **`order-red`**: Red production order
- **`order-mixed`**: Mixed production orders
- **`order-storage`**: Storage orders

#### Module Tab Presets
- **`module-default`**: Standard-Modulstatus

#### Process/Flow Tab Presets
- **`process-active`**: Aktive Produktionsflows

#### Sensor Tab Presets
- **`sensor-active`**: Aktive Sensordaten

#### Configuration Tab Presets
- **`config-default`**: Standard-Konfiguration

### Preset-Struktur

Jedes Preset definiert, welche Fixture-Typen geladen werden:

```typescript
{
  orders: 'white',      // Order fixtures
  modules: 'white',     // Module/pairing fixtures
  stock: 'default',     // Stock/inventory fixtures
  flows: 'default',     // Production flow fixtures
  config: 'default',    // Configuration fixtures
  sensors: 'default'    // Sensor fixtures (BME680, LDR, camera)
}
```

## Beispiele

### Order Tab mit verschiedenen Szenarien

```typescript
export class OrderTabComponent {
  private readonly dashboard = getDashboardController();

  // White orders
  async loadWhiteOrders() {
    await this.dashboard.loadTabFixture('order-white');
  }

  // Blue orders
  async loadBlueOrders() {
    await this.dashboard.loadTabFixture('order-blue');
  }

  // Mixed scenario
  async loadMixedOrders() {
    await this.dashboard.loadTabFixture('order-mixed');
  }

  // Storage orders
  async loadStorageOrders() {
    await this.dashboard.loadTabFixture('order-storage');
  }
}
```

### Sensor Tab mit spezifischen Sensordaten

```typescript
export class SensorTabComponent {
  private readonly dashboard = getDashboardController();

  async loadSensorFixture() {
    // Lädt nur sensor-relevante Fixtures
    await this.dashboard.loadTabFixture('sensor-active');
  }
}
```

### Module Tab mit Modul-fokussierten Daten

```typescript
export class ModuleTabComponent {
  private readonly dashboard = getDashboardController();

  async loadModuleFixture() {
    // Lädt nur modul-relevante Fixtures
    await this.dashboard.loadTabFixture('module-default');
  }
}
```

## Eigene Fixture-Presets erstellen

### 1. Neues Preset in tab-fixtures.ts definieren

```typescript
export const TAB_FIXTURE_PRESETS: Record<string, TabFixtureConfig> = {
  // ... existing presets ...
  
  'order-error': {
    orders: 'mixed',      // Use mixed orders
    modules: 'default',   // Default modules
    stock: 'default',     // Default stock
    flows: 'default',     // Default flows
    config: 'default',    // Default config
    sensors: 'default'    // Default sensors
  },
};
```

### 2. Neue Fixture-Dateien erstellen

Erstelle neue `.log`-Dateien in den entsprechenden Verzeichnissen:

```bash
omf3/testing/fixtures/
├── orders/
│   ├── white/orders.log
│   ├── blue/orders.log
│   ├── error/orders.log      # Neu: Error-Szenario
│   └── ...
├── modules/
│   ├── default.log
│   ├── calibration.log        # Neu: Kalibrierungs-Szenario
│   └── ...
└── sensors/
    ├── default.log
    ├── high-temp.log          # Neu: Hohe Temperatur
    └── ...
```

### 3. Fixture-Namen-Typen erweitern

Falls neue Fixture-Varianten hinzugefügt werden:

```typescript
// In omf3/libs/testing-fixtures/src/index.ts

export type OrderFixtureName =
  | 'white'
  | 'blue'
  | 'red'
  | 'mixed'
  | 'storage'
  | 'startup'
  | 'error';  // Neu

export type SensorFixtureName = 
  | 'default' 
  | 'startup'
  | 'high-temp'  // Neu
  | 'error';     // Neu
```

### 4. Fixture-Pfade registrieren

```typescript
// In omf3/libs/testing-fixtures/src/index.ts

const FIXTURE_PATHS: Record<OrderFixtureName, string> = {
  // ... existing paths ...
  error: 'error/orders.log',  // Neu
};

const SENSOR_FIXTURE_PATHS: Record<SensorFixtureName, string> = {
  // ... existing paths ...
  'high-temp': 'high-temp.log',  // Neu
  error: 'error.log',             // Neu
};
```

## Programmatische Verwendung

### Custom Fixture Config

Für noch mehr Kontrolle kann eine benutzerdefinierte Konfiguration verwendet werden:

```typescript
import { createCustomTabFixture } from '@omf3/testing-fixtures';

// Nur spezifische Fixture-Typen laden
const customStream$ = createCustomTabFixture({
  orders: 'white',
  sensors: 'default',
  // modules, stock, flows, config werden nicht geladen
}, {
  intervalMs: 25,
  loop: true
});

// Subscribe to the stream
customStream$.subscribe((message) => {
  console.log('Received:', message.topic, message.payload);
});
```

### Direkter Zugriff auf Fixture-Stream

```typescript
import { createTabFixtureStream } from '@omf3/testing-fixtures';

const tabFixtureConfig = {
  orders: 'blue',
  modules: 'default',
  stock: 'default',
  flows: 'default',
  config: 'default',
  sensors: 'default'
};

const stream$ = createTabFixtureStream(tabFixtureConfig, {
  intervalMs: 50,
  loop: false
});
```

## Migration

### Von globalem loadFixture() zu tab-spezifischem loadTabFixture()

**Vorher:**
```typescript
async loadFixture(fixture: OrderFixtureName) {
  await this.dashboard.loadFixture(fixture);
}
```

**Nachher:**
```typescript
async loadFixture(fixture: OrderFixtureName) {
  // Map OrderFixtureName to tab preset
  const presetMap: Record<OrderFixtureName, string> = {
    startup: 'startup',
    white: 'order-white',
    white_step3: 'order-white',
    blue: 'order-blue',
    red: 'order-red',
    mixed: 'order-mixed',
    storage: 'order-storage',
  };
  
  const preset = presetMap[fixture] || 'startup';
  await this.dashboard.loadTabFixture(preset);
}
```

## Best Practices

1. **Minimale Fixtures**: Lade nur die Fixture-Typen, die der Tab wirklich benötigt
2. **Konsistente Benennung**: Nutze ein konsistentes Naming-Schema für Presets (z.B. `{tab}-{scenario}`)
3. **Dokumentation**: Dokumentiere neue Presets und Fixture-Szenarien
4. **Realistische Daten**: Fixtures sollten realistische Produktionsszenarien abbilden
5. **Test-Coverage**: Erstelle Fixtures für Edge-Cases und Fehlerszenarien

## Troubleshooting

### Fixtures werden nicht geladen

Prüfe:
1. Existiert die Fixture-Datei im richtigen Verzeichnis?
2. Ist der Fixture-Name in den Typ-Definitionen vorhanden?
3. Ist der Pfad korrekt in `FIXTURE_PATHS` registriert?
4. Browser-Konsole auf Fehler prüfen

### Falsche Daten im Tab

Prüfe:
1. Ist das richtige Preset ausgewählt?
2. Enthält das Preset die richtigen Fixture-Typen?
3. Sind die Fixture-Dateien korrekt formatiert (JSON Lines)?

### Performance-Probleme

1. Reduziere `intervalMs` für schnelleres Replay
2. Verwende `loop: false` für Single-Shot-Tests
3. Lade nur notwendige Fixture-Typen

## Siehe auch

- [testing-fixtures README](./README.md)
- [Mock Dashboard](../../apps/ccu-ui/src/app/mock-dashboard.ts)
- [Session Replay Script](../../../scripts/README-replay.md)
