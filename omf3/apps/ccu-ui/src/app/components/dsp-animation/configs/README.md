# DSP Animation Customer Configuration System

This directory contains customer-specific configurations for the DSP animation component. The system allows different customers to have customized labels, icons, and branding while using the same core animation logic.

## Overview

The customer configuration system enables:
- **Customizable labels**: Each customer can use their own terminology for devices and systems
- **Generic icon library**: Reusable SVG icons that can be shared across customers
- **Brand flexibility**: Support for different ERP, MES, and cloud providers
- **No code duplication**: Single animation component supports multiple customers

## Directory Structure

```
configs/
├── README.md              # This file
├── types.ts              # TypeScript type definitions
├── fmf/
│   └── fmf-config.ts     # FMF (Fischertechnik) customer config
└── ecme/
    └── ecme-config.ts    # ECME (European Company Manufacturing Everything) customer config
```

## Generic Icon Library

Generic icons are stored in `omf3/apps/ccu-ui/src/assets/svg/` and organized by category:

- **shopfloor/stations/**: Generic device icons (drill, mill, laser, cnc, etc.)
- **shopfloor/systems/**: Generic system icons (agv-system, any-system, warehouse-system, etc.)
- **shopfloor/shared/**: Shared icons used for both devices and systems
- **business/**: Business application icons (erp, mes, cloud, analytics, etc.)
- **brand/**: Brand/provider logos (sap, alpha-x, aws, azure, powerbi, grafana)

**📖 Detaillierte Anleitung:** Siehe [SVG_GUIDE.md](./SVG_GUIDE.md) für:
- Wie neue Device-SVGs hinzugefügt werden
- Wie Duplikate vermieden werden
- Namenskonventionen
- Best Practices

## Creating a New Customer Configuration

### 1. Create Customer Config File

Create a new directory and config file:

```typescript
// configs/my-customer/my-customer-config.ts
import type { CustomerDspConfig } from '../types';

export const MY_CUSTOMER_CONFIG: CustomerDspConfig = {
  customerKey: 'my-customer',
  customerName: 'My Customer Name',
  
  sfDevices: [
    {
      id: 'sf-device-mill',  // Reuse existing container ID
      label: 'My Custom Device Name',
      iconKey: 'cnc',  // Reference to generic icon
    },
    // ... more devices
  ],
  
  sfSystems: [
    {
      id: 'sf-system-any',
      label: 'My Custom System',
      iconKey: 'warehouse-system',
    },
    // ... more systems
  ],
  
  bpProcesses: [
    {
      id: 'bp-erp',
      label: 'My ERP System',
      iconKey: 'erp',
      brandLogoKey: 'sap',  // or 'alpha-x', 'aws', etc.
    },
    // ... more processes
  ],
  
  customerLogoPath: 'assets/customers/my-customer/logo.svg',
};
```

### 2. Create Customer Page Component

Create a page component to display the customized animation:

```typescript
// pages/dsp/customer/my-customer/my-customer-dsp-page.component.ts
import { Component } from '@angular/core';
import { DspAnimationComponent } from '../../../../components/dsp-animation/dsp-animation.component';
import { MY_CUSTOMER_CONFIG } from '../../../../components/dsp-animation/configs/my-customer/my-customer-config';

@Component({
  standalone: true,
  selector: 'app-my-customer-dsp-page',
  imports: [DspAnimationComponent],
  template: `
    <div class="customer-dsp-page">
      <header class="customer-header">
        <h1>{{ config.customerName }} - DSP Architecture</h1>
      </header>
      <app-dsp-animation
        [viewMode]="'functional'"
        [customerConfig]="config"
      ></app-dsp-animation>
    </div>
  `,
  styles: [`/* your styles */`],
})
export class MyCustomerDspPageComponent {
  config = MY_CUSTOMER_CONFIG;
}
```

### 3. Add Route

Update `app.routes.ts`:

```typescript
{
  path: 'dsp/customer/my-customer',
  loadComponent: () =>
    import('./pages/dsp/customer/my-customer/my-customer-dsp-page.component')
      .then((m) => m.MyCustomerDspPageComponent),
},
```

## Container ID Mapping Strategy

The system reuses existing container IDs to avoid breaking changes:

| Container Type | IDs Available | Notes |
|---------------|---------------|-------|
| Devices | `sf-device-mill`, `sf-device-drill`, `sf-device-aiqs`, `sf-device-hbw`, `sf-device-dps`, `sf-device-chrg`, `sf-device-conveyor`, `sf-device-stone-oven` | 8 device slots |
| Systems | `sf-system-any`, `sf-system-fts`, `sf-system-warehouse`, `sf-system-factory` | 4 system slots |
| Business Processes | `bp-erp`, `bp-mes`, `bp-cloud`, `bp-analytics`, `bp-data-lake` | 5 BP slots |

## Examples

### FMF Configuration

The FMF (Fischertechnik Modellfabrik) configuration demonstrates a factory with Fischertechnik equipment:
- German terminology (Frässtation, Bohrstation, etc.)
- SAP ERP and MES
- AWS cloud services
- Grafana analytics

### ECME Configuration

The ECME (European Company Manufacturing Everything) configuration shows a different facility:
- English terminology
- New SVG icons for devices (CNC, Hydraulic, 3D Printer, Weight, Laser)
- New SVG icons for systems (SCADA, Industrial Process, Cargo, Pump)
- Alpha-X ERP and MES
- Azure cloud services
- PowerBI analytics

## Generic Icon Keys

### Device Icons
- `drill`, `mill`, `oven`, `laser`, `cnc`, `printer-3d`
- `hydraulic`, `weight`
- `robot-arm`, `conveyor`, `warehouse`, `agv`, `hbw`

### System Icons
- `warehouse-system`, `scada`, `industrial-process`, `cargo`, `pump`
- `erp`, `mes`, `cloud`, `analytics`

### Brand Icons
- `sap`, `alpha-x`, `aws`, `azure`, `powerbi`, `grafana`

## Custom Icons

If you need custom icons not available in the generic library:

```typescript
{
  id: 'sf-device-mill',
  label: 'Special Machine',
  iconKey: 'mill',  // Still required as fallback
  customIconPath: 'assets/customers/my-customer/special-machine.svg',
}
```

## TypeScript Types

All configuration types are defined in `types.ts`:

- `GenericIconKey`: Union type of all available generic icons
- `DeviceMapping`: Configuration for a shopfloor device
- `SystemMapping`: Configuration for a shopfloor system
- `BusinessProcessMapping`: Configuration for a business process
- `CustomerDspConfig`: Complete customer configuration

## Technical Notes

- Customer configurations are applied after the base configuration is loaded
- Labels override the default i18n labels
- Icons override the default icon paths
- The same animation steps work for all customers (using abstract container IDs)
- No changes to the core animation logic are required when adding new customers
