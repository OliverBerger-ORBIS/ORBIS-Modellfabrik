# Fixture-System Analyse und Verbesserungsvorschläge

## Aktueller Zustand

### Vorhandene Fixture-Typen

1. **Order Fixtures** (`OrderFixtureName`)
   - `white`, `white_step3`, `blue`, `red`, `mixed`, `storage`, `startup`
   - Topics: `ccu/order/#`
   - Verwendet in: Order Tab, Overview Tab, Process Tab

2. **Module/Pairing Fixtures** (`ModuleFixtureName`)
   - `default`, `white`, `blue`, `red`, `mixed`, `storage`, `startup`
   - Topics: `ccu/pairing/state`, `module/v1/#`
   - Verwendet in: Module Tab, Configuration Tab

3. **Stock Fixtures** (`StockFixtureName`)
   - `default`, `startup`
   - Topics: `warehouse/stock`
   - Verwendet in: Overview Tab (Inventory)

4. **Flow Fixtures** (`FlowFixtureName`)
   - `default`, `startup`
   - Topics: `ccu/state/flows`
   - Verwendet in: Process Tab

5. **Config Fixtures** (`ConfigFixtureName`)
   - `default`, `startup`
   - Topics: `ccu/state/config`
   - Verwendet in: Configuration Tab

6. **Sensor Fixtures** (`SensorFixtureName`)
   - `default`, `startup`
   - Topics: `/j1/txt/1/i/bme680`, `/j1/txt/1/i/ldr`, `/j1/txt/1/i/cam`
   - Verwendet in: Sensor Tab

7. **DSP Action Fixtures** (neu, nicht im Tab-System integriert)
   - Topics: `dsp/drill/action`
   - Verwendet in: DSP Action Tab, Configuration Tab (Drill Detail)

8. **Module Status Fixtures** (neu, nicht im Tab-System integriert)
   - Topics: `module/v1/ff/<serial>`, `fts/v1/ff/<serial>`
   - Verwendet in: Module Tab (Shopfloor Preview)

## Tab-zu-Fixture-Zuordnung

### Overview Tab
- **Relevante Fixtures**: Orders, Stock, FTS States
- **Aktuelles Verhalten**: Lädt alle Fixtures via `loadFixture()`
- **Empfohlen**: `loadTabFixture('overview-{scenario}')` mit Presets:
  - `overview-startup`: Orders (startup), Stock (startup), Modules (startup)
  - `overview-active`: Orders (mixed), Stock (default), Modules (default)

### Order Tab
- **Relevante Fixtures**: Orders (primär)
- **Aktuelles Verhalten**: Lädt alle Fixtures via `loadFixture()`
- **Empfohlen**: `loadTabFixture('order-{color}')` - bereits vorhanden
  - `order-white`, `order-blue`, `order-red`, `order-mixed`, `order-storage`

### Module Tab
- **Relevante Fixtures**: Modules/Pairing, Module Status (neu), FTS Position
- **Aktuelles Verhalten**: Lädt alle Fixtures + manuell `loadModuleStatusFixture()`
- **Empfohlen**: `loadTabFixture('module-{scenario}')` mit Presets:
  - `module-default`: Modules (default), Module Status (default)
  - `module-status-test`: Modules (default), Module Status (varied) - für Testing
  - `module-connection-test`: Modules (default), Module Status (connection variants)

### Process Tab
- **Relevante Fixtures**: Orders, Flows
- **Aktuelles Verhalten**: Lädt alle Fixtures via `loadFixture()`
- **Empfohlen**: `loadTabFixture('process-{scenario}')` mit Presets:
  - `process-active`: Orders (mixed), Flows (default)
  - `process-complete`: Orders (mixed), Flows (default)

### Sensor Tab
- **Relevante Fixtures**: Sensors (primär)
- **Aktuelles Verhalten**: Lädt alle Fixtures via `loadFixture()`
- **Empfohlen**: `loadTabFixture('sensor-{scenario}')` mit Presets:
  - `sensor-active`: Sensors (default)
  - `sensor-high-temp`: Sensors (high-temp) - wenn verfügbar

### Configuration Tab
- **Relevante Fixtures**: Config, Modules (für Details), DSP Actions (optional)
- **Aktuelles Verhalten**: Lädt alle Fixtures + manuell `loadDrillActionFixture()`
- **Empfohlen**: `loadTabFixture('config-{scenario}')` mit Presets:
  - `config-default`: Config (default), Modules (default)
  - `config-with-dsp`: Config (default), Modules (default), DSP Actions

### DSP Action Tab
- **Relevante Fixtures**: DSP Actions (primär)
- **Aktuelles Verhalten**: Manuell `loadDrillActionFixture()`
- **Empfohlen**: `loadTabFixture('dsp-action-{scenario}')` mit Presets:
  - `dsp-action-default`: DSP Actions (default)

### Message Monitor Tab
- **Relevante Fixtures**: Alle (für Debugging)
- **Aktuelles Verhalten**: Keine Fixture-Loading-Funktion
- **Empfohlen**: Kann alle Fixtures laden für Debugging

## Probleme im aktuellen System

1. **Inkonsistente Verwendung**: Einige Tabs nutzen `loadFixture()`, andere `loadTabFixture()`
2. **Fehlende Integration**: DSP Action und Module Status Fixtures sind nicht im Tab-System
3. **Redundanz**: Alle Tabs laden alle Fixtures, auch wenn sie nicht benötigt werden
4. **Manuelle Fixture-Loading**: Einige Tabs laden Fixtures manuell (z.B. `loadModuleStatusFixture()`)
5. **Keine Tab-spezifischen Presets**: Viele Tabs haben keine eigenen Presets

## Verbesserungsvorschläge

### 1. Erweiterte Tab-Fixture-Presets

```typescript
export const TAB_FIXTURE_PRESETS: Record<string, TabFixtureConfig> = {
  // ... existing presets ...
  
  // Overview Tab Presets
  'overview-startup': {
    orders: 'startup',
    modules: 'startup',
    stock: 'startup',
    flows: 'startup',
    config: 'startup',
    sensors: 'startup',
  },
  'overview-active': {
    orders: 'mixed',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  
  // Module Tab Presets (erweitert)
  'module-default': {
    orders: 'startup',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  'module-status-test': {
    orders: 'startup',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
    // Module Status wird separat geladen
  },
  
  // Process Tab Presets
  'process-active': {
    orders: 'mixed',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  
  // Configuration Tab Presets (erweitert)
  'config-default': {
    orders: 'startup',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
  },
  'config-with-dsp': {
    orders: 'startup',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
    // DSP Actions wird separat geladen
  },
  
  // DSP Action Tab Presets
  'dsp-action-default': {
    orders: 'startup',
    modules: 'default',
    stock: 'default',
    flows: 'default',
    config: 'default',
    sensors: 'default',
    // DSP Actions wird separat geladen
  },
};
```

### 2. Integration von DSP Action und Module Status Fixtures

**Option A: Als separate Fixture-Typen**
```typescript
export interface TabFixtureConfig {
  // ... existing ...
  dspActions?: 'default' | 'varied';
  moduleStatus?: 'default' | 'varied' | 'connection-test';
}
```

**Option B: Als "Custom Fixtures" (aktuell)**
- Beibehalten der manuellen Loading-Methode
- Aber: Standardisieren der Verwendung über Helper-Methoden

### 3. Standardisierte Fixture-Loading-Methode pro Tab

Jeder Tab sollte eine standardisierte Methode haben:

```typescript
// In jedem Tab-Component
async loadTabFixture(presetName: string): Promise<void> {
  if (!this.isMockMode) {
    return;
  }
  
  // Load main fixtures via dashboard
  await this.dashboard.loadTabFixture(presetName);
  
  // Load additional custom fixtures if needed
  await this.loadCustomFixtures(presetName);
}

private async loadCustomFixtures(presetName: string): Promise<void> {
  // Tab-spezifische Custom Fixtures
  // z.B. Module Tab: Module Status Fixtures
  // z.B. Configuration Tab: DSP Action Fixtures
}
```

### 4. Fixture-Management-Service (optional)

Ein zentraler Service für Fixture-Management:

```typescript
@Injectable({ providedIn: 'root' })
export class FixtureService {
  constructor(private dashboard: MockDashboardController) {}
  
  async loadTabFixture(tab: string, scenario: string): Promise<void> {
    const presetName = `${tab}-${scenario}`;
    await this.dashboard.loadTabFixture(presetName);
    
    // Load additional custom fixtures based on tab
    switch (tab) {
      case 'module':
        await this.loadModuleStatusFixtures(scenario);
        break;
      case 'configuration':
        if (scenario === 'with-dsp') {
          await this.loadDspActionFixtures();
        }
        break;
      // ...
    }
  }
}
```

## Empfohlene Implementierung

### Phase 1: TypeScript-Fehler beheben ✅
- [x] Module Status Fixtures Interface korrigieren
- [x] Stream-Funktion korrigieren

### Phase 2: Tab-Fixture-Presets erweitern
- [ ] Neue Presets für alle Tabs hinzufügen
- [ ] Module Status Fixtures in Tab-System integrieren
- [ ] DSP Action Fixtures in Tab-System integrieren

### Phase 3: Tabs migrieren
- [ ] Alle Tabs auf `loadTabFixture()` migrieren
- [ ] Standardisierte `loadTabFixture()` Methode pro Tab
- [ ] Custom Fixtures über Helper-Methoden laden

### Phase 4: Dokumentation
- [ ] Tab-zu-Fixture-Zuordnung dokumentieren
- [ ] Preset-Übersicht aktualisieren
- [ ] Migration-Guide erstellen

## Nächste Schritte

1. **Sofort**: TypeScript-Fehler beheben (✅ erledigt)
2. **Kurzfristig**: Tab-Fixture-Presets erweitern
3. **Mittelfristig**: Tabs auf neues System migrieren
4. **Langfristig**: Fixture-Management-Service (optional)

