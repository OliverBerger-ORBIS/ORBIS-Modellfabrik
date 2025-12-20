# Beispiel: Tab-spezifische Fixtures verwenden

## Grundlegendes Beispiel - Order Tab

```typescript
import { Component } from '@angular/core';
import { getDashboardController } from '../mock-dashboard';

@Component({
  selector: 'app-order-tab',
  // ...
})
export class OrderTabComponent {
  private readonly dashboard = getDashboardController();
  
  // Preset-Optionen für Order Tab
  readonly fixturePresets = [
    { value: 'order-white', label: 'White Production Order' },
    { value: 'order-blue', label: 'Blue Production Order' },
    { value: 'order-red', label: 'Red Production Order' },
    { value: 'order-mixed', label: 'Mixed Orders' },
    { value: 'order-storage', label: 'Storage Orders' },
  ];
  
  activePreset = 'order-white';
  
  // Lade tab-spezifisches Fixture
  async loadTabFixture(preset: string) {
    console.log(`Loading tab fixture: ${preset}`);
    await this.dashboard.loadTabFixture(preset, {
      intervalMs: 25,
      loop: true
    });
    this.activePreset = preset;
  }
  
  ngOnInit() {
    // Lade initial fixture
    void this.loadTabFixture(this.activePreset);
  }
}
```

## HTML Template

```html
<div class="fixture-selector">
  <label>Order Scenario:</label>
  <select [(ngModel)]="activePreset" (change)="loadTabFixture(activePreset)">
    <option *ngFor="let preset of fixturePresets" 
            [value]="preset.value">
      {{ preset.label }}
    </option>
  </select>
</div>

<!-- Order content -->
<div class="orders">
  <!-- Order cards, etc. -->
</div>
```

## Sensor Tab Beispiel

```typescript
import { Component } from '@angular/core';
import { getDashboardController } from '../mock-dashboard';

@Component({
  selector: 'app-sensor-tab',
  // ...
})
export class SensorTabComponent {
  private readonly dashboard = getDashboardController();
  
  // Sensor Tab lädt nur sensor-relevante Fixtures
  async loadSensorData() {
    await this.dashboard.loadTabFixture('sensor-active', {
      intervalMs: 50,  // Schnelleres Update für Sensordaten
      loop: true
    });
  }
  
  ngOnInit() {
    void this.loadSensorData();
  }
}
```

## Module Tab Beispiel

```typescript
import { Component } from '@angular/core';
import { getDashboardController } from '../mock-dashboard';

@Component({
  selector: 'app-module-tab',
  // ...
})
export class ModuleTabComponent {
  private readonly dashboard = getDashboardController();
  
  // Module Tab lädt modul-fokussierte Fixtures
  async loadModuleData() {
    await this.dashboard.loadTabFixture('module-default', {
      intervalMs: 25,
      loop: true
    });
  }
  
  ngOnInit() {
    void this.loadModuleData();
  }
}
```

## Erweiterte Verwendung - Mehrere Szenarien

```typescript
import { Component } from '@angular/core';
import { getDashboardController } from '../mock-dashboard';

@Component({
  selector: 'app-order-tab',
  // ...
})
export class OrderTabComponent {
  private readonly dashboard = getDashboardController();
  
  scenarios = {
    normal: 'order-mixed',
    whiteOnly: 'order-white',
    blueOnly: 'order-blue',
    redOnly: 'order-red',
    storage: 'order-storage',
  };
  
  async loadScenario(scenarioKey: keyof typeof this.scenarios) {
    const preset = this.scenarios[scenarioKey];
    await this.dashboard.loadTabFixture(preset, {
      intervalMs: 25,
      loop: true
    });
  }
  
  // Schnellzugriff auf häufige Szenarien
  async loadNormalProduction() {
    await this.loadScenario('normal');
  }
  
  async loadWhiteProduction() {
    await this.loadScenario('whiteOnly');
  }
  
  async loadStorageOrders() {
    await this.loadScenario('storage');
  }
}
```

## Migration von alter zu neuer Methode

### Vorher (alte Methode)

```typescript
async loadFixture(fixture: OrderFixtureName) {
  await this.dashboard.loadFixture(fixture);
}
```

### Nachher (neue Methode)

```typescript
async loadFixture(fixture: OrderFixtureName) {
  // Map zu tab-spezifischem Preset
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

## Vorteile

1. **Unabhängigkeit**: Jeder Tab kann seine eigenen Fixtures laden ohne andere Tabs zu beeinflussen
2. **Flexibilität**: Einfaches Hinzufügen neuer Szenarien pro Tab
3. **Performance**: Nur relevante Topics werden geladen
4. **Wartbarkeit**: Klare Trennung zwischen Tab-spezifischen Fixtures
5. **Testbarkeit**: Einfaches Testen verschiedener Szenarien pro Tab

## Siehe auch

- [Tab Fixtures Documentation](../../../libs/testing-fixtures/TAB-FIXTURES.md)
- [testing-fixtures README](../../../libs/testing-fixtures/README.md)
- [Mock Dashboard](../mock-dashboard.ts)
