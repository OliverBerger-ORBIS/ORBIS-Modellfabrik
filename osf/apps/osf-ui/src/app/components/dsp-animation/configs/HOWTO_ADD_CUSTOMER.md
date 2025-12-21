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
mkdir -p osf/apps/osf-ui/src/app/components/dsp-animation/configs/<customer-id>
mkdir -p osf/apps/osf-ui/src/app/pages/dsp/customer/<customer-id>
```

**Beispiel:**
```bash
mkdir -p osf/apps/osf-ui/src/app/components/dsp-animation/configs/acme
mkdir -p osf/apps/osf-ui/src/app/pages/dsp/customer/acme
```

## Schritt 2: Konfigurationsdatei erstellen

**WICHTIG - Template verwenden:**
- Verwenden Sie **FMF_CONFIG** (`fmf-config.ts`) als Template für neue Customer-Configs
- Die Default-Config ist nur ein Fallback für Tests/Entwicklung, nicht für neue Customers

Erstellen Sie die Konfigurationsdatei `osf/apps/osf-ui/src/app/components/dsp-animation/configs/<customer-id>/<customer-id>-config.ts`:

**Tipp:** Kopieren Sie `fmf-config.ts` als Basis und passen Sie die Werte an.

**WICHTIG - SVG-Nomenklatur:**
- **Devices:** Alle Device-SVGs müssen `*-station.svg` heißen (z.B. `drill-station.svg`, `mill-station.svg`)
- **Systems:** Alle System-SVGs müssen `*-system.svg` heißen (z.B. `warehouse-system.svg`, `agv-system.svg`)
- **Business:** Alle Business-SVGs müssen `*-application.svg` heißen (z.B. `erp-application.svg`, `mes-application.svg`)

```typescript
/**
 * ACME Customer Configuration
 * Beschreibung des Kunden und seiner Anforderungen
 */
import type { CustomerDspConfig } from '../types';

export const ACME_CONFIG: CustomerDspConfig = {
  customerKey: 'acme',
  customerName: 'ACME Corporation',
  
  // Shopfloor devices - Liste der Devices mit semantischen IDs
  sfDevices: [
    {
      id: 'sf-device-cnc',  // Semantische ID: Der Teil nach "sf-device-" wird für das SVG verwendet
      label: $localize`:@@deviceCNC:CNC / Station`,  // I18n-Label mit Umbruch-Hinweis " / "
      iconKey: 'cnc-station',  // Entspricht cnc-station.svg im Ordner shopfloor/stations/
    },
    {
      id: 'sf-device-laser',
      label: $localize`:@@deviceLaser:Laser / Station`,
      iconKey: 'laser-station',  // Entspricht laser-station.svg
    },
    // ... weitere Devices (z.B. sf-device-mill → iconKey: 'mill-station')
  ],
  
  // Shopfloor systems - Liste der Systeme mit semantischen IDs
  sfSystems: [
    {
      id: 'sf-system-scada',  // Semantische ID: Der Teil nach "sf-system-" wird für das SVG verwendet
      label: $localize`:@@dspArchLabelScada:SCADA / System`,
      iconKey: 'scada-system',  // Entspricht scada-system.svg im Ordner shopfloor/systems/
    },
    // ... weitere Systems (z.B. sf-system-warehouse → iconKey: 'warehouse-system')
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

**WICHTIG - SVG-Nomenklatur:**
- **Devices:** Alle SVGs in `src/assets/svg/shopfloor/stations/` müssen `*-station.svg` heißen
- **Systems:** Alle SVGs in `src/assets/svg/shopfloor/systems/` müssen `*-system.svg` heißen
- **Business:** Alle SVGs in `src/assets/svg/business/` müssen `*-application.svg` heißen

**Devices (Shopfloor Stations):**
- `drill` - Drill Station
- `mill` - Mill Station
- `oven` - Oven Station
- `laser` - Laser Station
- `cnc` - CNC Station
- `printer-3d` - 3D Printer Station
- `hydraulic` - Hydraulic Station
- `weight` - Weight Station
- `robot-arm` - Robotic Arm Station
- `conveyor` - Conveyor Station
- `warehouse` - Warehouse Device
- `agv` - AGV Device (wird zu `dps` gemappt)
- `dps` - DPS Station
- `hbw` - HBW Station
- `hbw` - HBW (High Bay Warehouse)
- `dps` - DPS (Distribution & Picking System) - **NEU**
- `aiqs` - AIQS (AI Quality System) - **NEU**

**Systems (Shopfloor Systems):**
- `warehouse-system` - Warehouse System
- `scada` - SCADA System
- `industrial-process` - Industrial Process System
- `cargo` - Cargo System
- `pump` - Pump System
- `agv` - AGV System (wird zu `agv-system` gemappt, verwendet `shopfloor-fts` Icon)
- `agv-system` - AGV System (explizit) - **NEU**

**Business Processes:**
- `erp` - ERP Applications
- `mes` - MES Applications
- `cloud` - Cloud Applications
- `analytics` - Analytics Applications
- `scm` - SCM Applications (Supply Chain Management)
- `crm` - CRM Applications (Customer Relationship Management)

**Brand Logos:**
- `sap` - SAP Logo
- `alpha-x` - Alpha-X Logo
- `aws` - AWS Logo
- `azure` - Azure Logo
- `powerbi` - PowerBI Logo
- `grafana` - Grafana Logo
- `googlecloud` - Google Cloud Logo
- `alpha-x` - Alpha-X Logo
- `aws` - AWS Logo
- `azure` - Azure Logo
- `powerbi` - PowerBI Logo
- `grafana` - Grafana Logo
- `google-cloud` - Google Cloud Logo - **NEU** (als `google-cloud-logo` in Icon-Registry)

## Schritt 3: I18n-Übersetzungen hinzufügen

Fügen Sie die Übersetzungen zu allen I18n-Dateien hinzu:

**Deutsch (`osf/apps/osf-ui/src/locale/messages.de.json`):**
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

**Französisch (`osf/apps/osf-ui/src/locale/messages.fr.json`):**
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

**Wichtig:** Aktualisieren Sie auch die Dateien in `osf/apps/osf-ui/public/locale/`!

## Schritt 4: Customer Page Component erstellen

Erstellen Sie die Page Component `osf/apps/osf-ui/src/app/pages/dsp/customer/<customer-id>/<customer-id>-dsp-page.component.ts`:

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

Fügen Sie die Route zu `osf/apps/osf-ui/src/app/app.routes.ts` hinzu:

```typescript
{
  path: 'dsp/customer/acme',
  loadComponent: () =>
    import('./pages/dsp/customer/acme/acme-dsp-page.component').then((m) => m.AcmeDspPageComponent),
},
```

**Hinweis:** Die Customer-Seite wird automatisch in der zentralen Customer-Auswahlseite (`/dsp/customer`) angezeigt, sobald die Route hinzugefügt wurde. Die Customer-Auswahlseite listet alle verfügbaren Customers auf und ermöglicht die Navigation zu den einzelnen Customer-Seiten.

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

1. Erstellen Sie das Verzeichnis: `osf/apps/osf-ui/src/assets/customers/<customer-id>/`
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

### Semantische IDs (empfohlen)

Verwenden Sie semantische IDs für Devices und Systems. Die ID bestimmt den SVG-Dateinamen:

- **Devices**: `sf-device-xyz` → `iconKey: 'xyz-station'` → `xyz-station.svg` (im Ordner `shopfloor/stations/`)
- **Systems**: `sf-system-xyz` → `iconKey: 'xyz-system'` → `xyz-system.svg` (im Ordner `shopfloor/systems/`)

Falls das entsprechende SVG nicht existiert, wird automatisch ein Fallback verwendet (z.B. `any-system.svg` für Systems, `any-station.svg` für Devices).

### Konkrete IDs (nur wenn nötig)

Für Business Processes verwenden Sie konkrete IDs:
- `bp-erp`, `bp-mes`, `bp-cloud`, `bp-analytics`, `bp-data-lake`, `bp-scm`, `bp-crm`

## Best Practices

1. **Labels**: Verwenden Sie immer I18n-Übersetzungen mit `$localize`
2. **Icons**: Nutzen Sie zunächst generische Icon Keys, fügen Sie nur bei Bedarf `customIconPath` hinzu
3. **Tests**: Erstellen Sie Tests für die Config und die Component
4. **Dokumentation**: Aktualisieren Sie `README.md` mit dem neuen Kunden
5. **Konsistenz**: Folgen Sie den bestehenden Beispielen (FMF, ECME)
6. **Template**: Verwenden Sie FMF_CONFIG als Template (nicht die Default-Config)

## Troubleshooting

### Labels werden nicht angezeigt
- Prüfen Sie, ob die I18n-Übersetzungen in allen Dateien (`src/locale/` und `public/locale/`) vorhanden sind
- Prüfen Sie, ob die `$localize`-IDs korrekt sind

### Icons werden nicht angezeigt
- Prüfen Sie, ob der `iconKey` in `types.ts` definiert ist
- Prüfen Sie, ob das Icon in `icon.registry.ts` registriert ist
- Prüfen Sie, ob der `customIconPath` in `icon-registry.ts` existiert (falls verwendet)
- **Prüfen Sie die SVG-Nomenklatur:** 
  - Devices müssen `*-station.svg` heißen (z.B. `drill-station.svg`)
  - Systems müssen `*-system.svg` heißen (z.B. `warehouse-system.svg`)
  - Business müssen `*-application.svg` heißen (z.B. `erp-application.svg`)

### Route funktioniert nicht
- Prüfen Sie, ob die Route in `app.routes.ts` korrekt hinzugefügt wurde
- Prüfen Sie, ob der Component-Import-Pfad korrekt ist
- Prüfen Sie, ob der Component korrekt exportiert ist

## Weitere Informationen

- Siehe [README.md](./README.md) für allgemeine Informationen zum Configuration System
- Siehe [SVG_GUIDE.md](./SVG_GUIDE.md) für Informationen zum Hinzufügen neuer SVG-Icons
- Siehe [types.ts](./types.ts) für TypeScript-Typdefinitionen
