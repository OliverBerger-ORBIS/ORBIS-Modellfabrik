# How to Add a New Customer Configuration

Diese Anleitung beschreibt Schritt für Schritt, wie Sie eine neue Kundenkonfiguration für die DSP-Animation hinzufügen.

## Übersicht

Eine Kundenkonfiguration besteht aus:
- **Shopfloor Devices (sf-devices)**: Geräte auf dem Shopfloor (z.B. CNC-Station, Laser-Station)
- **Shopfloor Systems (sf-systems)**: Systeme auf dem Shopfloor (z.B. SCADA-System, AGV-System)
- **Business Processes (bp-processes)**: Geschäftsprozesse (z.B. ERP, MES, Analytics)
- **Customer Logo**: Optionales Kundenlogo

## Schritt 1: Verzeichnisstruktur erstellen

Erstellen Sie ein neues Verzeichnis für den Kunden:

```bash
mkdir -p omf3/apps/ccu-ui/src/app/components/dsp-animation/configs/<customer-id>
mkdir -p omf3/apps/ccu-ui/src/app/pages/dsp/customer/<customer-id>
```

**Beispiel:**
```bash
mkdir -p omf3/apps/ccu-ui/src/app/components/dsp-animation/configs/acme
mkdir -p omf3/apps/ccu-ui/src/app/pages/dsp/customer/acme
```

## Schritt 2: Konfigurationsdatei erstellen

Erstellen Sie die Konfigurationsdatei `omf3/apps/ccu-ui/src/app/components/dsp-animation/configs/<customer-id>/<customer-id>-config.ts`:

```typescript
/**
 * ACME Customer Configuration
 * Beschreibung des Kunden und seiner Anforderungen
 */
import type { CustomerDspConfig } from '../types';

export const ACME_CONFIG: CustomerDspConfig = {
  customerKey: 'acme',
  customerName: 'ACME Corporation',
  
  // Shopfloor devices - Liste der Geräte
  sfDevices: [
    {
      id: 'sf-device-1',  // Abstract ID (sf-device-1 bis sf-device-5)
      label: $localize`:@@deviceCNC:CNC / Station`,  // I18n-Label mit Umbruch-Hinweis " / "
      iconKey: 'cnc',  // Generic Icon Key (siehe types.ts)
      customIconPath: 'device-cnc',  // Optional: Spezifischer Icon-Pfad
    },
    {
      id: 'sf-device-2',
      label: $localize`:@@deviceLaser:Laser / Station`,
      iconKey: 'laser',
      customIconPath: 'device-laser',
    },
    // ... weitere Devices
  ],
  
  // Shopfloor systems - Liste der Systeme
  sfSystems: [
    {
      id: 'sf-system-1',  // Abstract ID (sf-system-1 bis sf-system-4)
      label: $localize`:@@dspArchLabelScada:SCADA / System`,
      iconKey: 'scada',  // Generic Icon Key
      customIconPath: 'shopfloor-scada',  // Optional: Spezifischer Icon-Pfad
    },
    // ... weitere Systems
  ],
  
  // Business processes - Liste der Geschäftsprozesse
  bpProcesses: [
    {
      id: 'bp-erp',  // Konkrete ID (bp-erp, bp-mes, bp-analytics, bp-data-lake)
      label: $localize`:@@dspArchLabelERP:ERP Applications`,
      iconKey: 'erp',
      brandLogoKey: 'sap',  // Brand Logo (sap, alpha-x, aws, azure, powerbi, grafana)
    },
    {
      id: 'bp-mes',
      label: $localize`:@@dspArchLabelMESApp:MES Applications`,
      iconKey: 'mes',
      brandLogoKey: 'sap',
    },
    {
      id: 'bp-analytics',
      label: $localize`:@@dspArchLabelAnalytics:Analytical\nApplications`,
      iconKey: 'analytics',
      brandLogoKey: 'powerbi',
    },
    {
      id: 'bp-data-lake',
      label: $localize`:@@dspArchLabelDataLake:Data Lake`,
      iconKey: 'cloud',
      customIconPath: 'bp-data-lake',  // Optional: Spezifischer Icon-Pfad
      brandLogoKey: 'azure',
    },
  ],
  
  // Optional: Kundenlogo
  customerLogoPath: 'assets/customers/acme/logo.svg',
};
```

### Wichtige Hinweise zu Labels

- **Umbruch-Hinweise**: Verwenden Sie ` / ` (Leerzeichen-Slash-Leerzeichen) als Umbruch-Hinweis in Labels
  - Beispiel: `"CNC / Station"` wird bei Platzmangel zu zwei Zeilen: "CNC" und "Station"
  - Wenn genug Platz vorhanden ist, wird es zu einer Zeile: "CNCStation" (ohne Leerzeichen)
- **I18n**: Verwenden Sie `$localize` mit eindeutigen IDs (`@@deviceCNC`, `@@dspArchLabelScada`, etc.)
- **Hyphen bei Umbrüchen**: Wenn ein Label umgebrochen wird, wird automatisch ein Bindestrich hinzugefügt (z.B. "CNC-" und "Station")

### Verfügbare Icon Keys

**Devices:**
- `drill`, `mill`, `oven`, `laser`, `cnc`, `printer-3d`
- `hydraulic`, `weight`
- `robot-arm`, `conveyor`, `warehouse`, `agv`, `hbw`

**Systems:**
- `warehouse-system`, `scada`, `industrial-process`, `cargo`, `pump`
- `erp`, `mes`, `cloud`, `analytics`

**Brand Logos:**
- `sap`, `alpha-x`, `aws`, `azure`, `powerbi`, `grafana`

## Schritt 3: I18n-Übersetzungen hinzufügen

Fügen Sie die Übersetzungen zu allen I18n-Dateien hinzu:

**Deutsch (`omf3/apps/ccu-ui/src/locale/messages.de.json`):**
```json
{
  "locale": "de",
  "translations": {
    "@@deviceCNC": "CNC / Station",
    "@@deviceLaser": "Laser / Station",
    "@@dspArchLabelScada": "SCADA / System",
    // ... weitere Übersetzungen
  }
}
```

**Französisch (`omf3/apps/ccu-ui/src/locale/messages.fr.json`):**
```json
{
  "locale": "fr",
  "translations": {
    "@@deviceCNC": "CNC / Station",
    "@@deviceLaser": "Laser / Station",
    "@@dspArchLabelScada": "SCADA / Système",
    // ... weitere Übersetzungen
  }
}
```

**Wichtig:** Aktualisieren Sie auch die Dateien in `omf3/apps/ccu-ui/public/locale/`!

## Schritt 4: Customer Page Component erstellen

Erstellen Sie die Page Component `omf3/apps/ccu-ui/src/app/pages/dsp/customer/<customer-id>/<customer-id>-dsp-page.component.ts`:

```typescript
import { Component, ChangeDetectionStrategy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { ACME_CONFIG } from '../../../../components/dsp-animation/configs/acme/acme-config';
import { VIEW_MODES } from '../shared/view-modes.const';
import { CUSTOMER_PAGE_STYLES } from '../shared/customer-page.styles';
import type { ViewMode } from '../../../../components/dsp-animation/types';

/**
 * ACME DSP Architecture Page
 * Displays DSP architecture customized for ACME's equipment and systems
 * Supports functional, component, and deployment view modes
 */
@Component({
  standalone: true,
  selector: 'app-acme-dsp-page',
  imports: [CommonModule, DspAnimationComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="customer-dsp-page">
      <header class="customer-header">
        <h1>{{ config.customerName }} - DSP Architecture</h1>
        <p class="subtitle">Interactive demonstration of DSP architecture tailored for {{ config.customerName }}</p>
        
        <div class="view-mode-selector">
          <button 
            *ngFor="let mode of viewModes"
            [class.active]="currentViewMode() === mode.value"
            (click)="setViewMode(mode.value)"
            class="view-mode-btn"
          >
            {{ mode.label }}
          </button>
        </div>
      </header>
      <app-dsp-animation
        [viewMode]="currentViewMode()"
        [customerConfig]="config"
      ></app-dsp-animation>
    </div>
  `,
  styles: [CUSTOMER_PAGE_STYLES],
})
export class AcmeDspPageComponent {
  config = ACME_CONFIG;
  currentViewMode = signal<ViewMode>('functional');
  viewModes = VIEW_MODES;
  
  setViewMode(mode: ViewMode): void {
    this.currentViewMode.set(mode);
  }
}
```

## Schritt 5: Route hinzufügen

Fügen Sie die Route zu `omf3/apps/ccu-ui/src/app/app.routes.ts` hinzu:

```typescript
{
  path: 'dsp/customer/acme',
  loadComponent: () =>
    import('./pages/dsp/customer/acme/acme-dsp-page.component').then((m) => m.AcmeDspPageComponent),
},
```

## Schritt 6: Tests erstellen

Erstellen Sie Test-Dateien:

**Config Test (`<customer-id>-config.spec.ts`):**
```typescript
import { ACME_CONFIG } from './acme-config';

describe('ACME_CONFIG', () => {
  it('should be defined', () => {
    expect(ACME_CONFIG).toBeDefined();
  });

  it('should have correct customer key', () => {
    expect(ACME_CONFIG.customerKey).toBe('acme');
  });

  // ... weitere Tests
});
```

**Component Test (`<customer-id>-dsp-page.component.spec.ts`):**
```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AcmeDspPageComponent } from './acme-dsp-page.component';
// ... weitere Imports

describe('AcmeDspPageComponent', () => {
  // ... Tests
});
```

## Schritt 7: Kundenlogo hinzufügen (optional)

Wenn Sie ein Kundenlogo verwenden möchten:

1. Erstellen Sie das Verzeichnis: `omf3/apps/ccu-ui/src/assets/customers/<customer-id>/`
2. Legen Sie das Logo als `logo.svg` ab
3. Setzen Sie `customerLogoPath: 'assets/customers/<customer-id>/logo.svg'` in der Config

## Schritt 8: Ergebnis prüfen

Nach dem Hinzufügen können Sie die Kundenkonfiguration unter folgender URL aufrufen:

```
http://localhost:4200/dsp/customer/<customer-id>
```

**Beispiel:**
- `http://localhost:4200/dsp/customer/acme`
- `http://localhost:4200/dsp/customer/fmf`
- `http://localhost:4200/dsp/customer/ecme`

## Container ID Strategie

### Abstract IDs (empfohlen)

Verwenden Sie abstract IDs für Devices und Systems, um Flexibilität zu gewährleisten:

- **Devices**: `sf-device-1`, `sf-device-2`, ..., `sf-device-5`
- **Systems**: `sf-system-1`, `sf-system-2`, ..., `sf-system-4`

### Konkrete IDs (nur wenn nötig)

Für Business Processes verwenden Sie konkrete IDs:
- `bp-erp`, `bp-mes`, `bp-analytics`, `bp-data-lake`, `bp-cloud`

## Best Practices

1. **Labels**: Verwenden Sie immer I18n-Übersetzungen mit `$localize`
2. **Icons**: Nutzen Sie zunächst generische Icon Keys, fügen Sie nur bei Bedarf `customIconPath` hinzu
3. **Tests**: Erstellen Sie Tests für die Config und die Component
4. **Dokumentation**: Aktualisieren Sie `README.md` mit dem neuen Kunden
5. **Konsistenz**: Folgen Sie den bestehenden Beispielen (FMF, ECME)

## Troubleshooting

### Labels werden nicht angezeigt
- Prüfen Sie, ob die I18n-Übersetzungen in allen Dateien (`src/locale/` und `public/locale/`) vorhanden sind
- Prüfen Sie, ob die `$localize`-IDs korrekt sind

### Icons werden nicht angezeigt
- Prüfen Sie, ob der `iconKey` in `types.ts` definiert ist
- Prüfen Sie, ob das Icon in `icon.registry.ts` registriert ist
- Prüfen Sie, ob der `customIconPath` in `icon-registry.ts` existiert (falls verwendet)

### Route funktioniert nicht
- Prüfen Sie, ob die Route in `app.routes.ts` korrekt hinzugefügt wurde
- Prüfen Sie, ob der Component-Import-Pfad korrekt ist
- Prüfen Sie, ob der Component korrekt exportiert ist

## Weitere Informationen

- Siehe [README.md](./README.md) für allgemeine Informationen zum Configuration System
- Siehe [SVG_GUIDE.md](./SVG_GUIDE.md) für Informationen zum Hinzufügen neuer SVG-Icons
- Siehe [types.ts](./types.ts) für TypeScript-Typdefinitionen
