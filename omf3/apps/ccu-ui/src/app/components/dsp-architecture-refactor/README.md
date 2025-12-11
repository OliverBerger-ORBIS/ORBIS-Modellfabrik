# DSP Architecture Refactor Component

A refactored implementation of the ORBIS DSP (Distributed Shopfloor Processing) architecture visualization component with enhanced features, animations, and configurability.

## Features

- **Three-Layer Architecture**: Business, DSP, and Shopfloor (Systems & Devices)
- **Multiple View Modes**: Functional, Component, and Deployment perspectives
- **Interactive Animations**: Scene-based animation engine with multiple action types
- **SVG Arrows**: Configurable connections with L-shaped, straight, or curved paths
- **Zoom Controls**: Zoom in/out and reset functionality
- **Responsive Design**: Adapts to different screen sizes
- **Customer Configurable**: Support for custom layer configurations
- **Event Emitters**: BoxClick and StepChange events for integration

## Installation & Usage

### Basic Usage

```typescript
import { DspArchitectureRefactorComponent } from './components/dsp-architecture-refactor/dsp-architecture-refactor.component';

@Component({
  selector: 'app-my-page',
  standalone: true,
  imports: [DspArchitectureRefactorComponent],
  template: `
    <app-dsp-architecture-refactor
      [viewMode]="'functional'"
      [animationEnabled]="true"
      (boxClick)="onBoxClick($event)"
      (stepChange)="onStepChange($event)">
    </app-dsp-architecture-refactor>
  `
})
export class MyPageComponent {
  onBoxClick(event: BoxClickEvent) {
    console.log('Box clicked:', event);
  }

  onStepChange(event: StepChangeEvent) {
    console.log('Animation step:', event);
  }
}
```

### Component Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `viewMode` | `'functional' \| 'component' \| 'deployment'` | `'functional'` | Architecture view perspective |
| `animationEnabled` | `boolean` | `true` | Enable/disable animation controls |
| `customConfig` | `Partial<ArchitectureConfig>` | `undefined` | Override default configuration |

### Component Outputs

| Output | Type | Description |
|--------|------|-------------|
| `boxClick` | `EventEmitter<BoxClickEvent>` | Emitted when a box is clicked |
| `stepChange` | `EventEmitter<StepChangeEvent>` | Emitted when animation step changes |

## View Modes

### Functional View
Shows high-level functional capabilities across all layers:
- Business: ERP, SCM, Analytics
- DSP: SmartFactory Dashboard, Edge, Management Cockpit
- Shopfloor Systems: MES, Warehouse, AGV, SCADA
- Shopfloor Devices: Mill, Drill, AIQS, HBW, DPS, Charger

### Component View
Shows detailed DSP component architecture:
- Business: ERP System, Cloud Applications
- DSP Components: Dashboard, Connectivity, Digital Twin, Analytics, Workflow, Cockpit
- Shopfloor Systems: Factory, Warehouse, AGV
- Shopfloor Devices: Mill, Drill, AIQS, HBW, DPS

### Deployment View
Shows infrastructure and deployment architecture:
- Cloud/On-Premise: SAP S/4HANA, Azure Cloud, Data Lake
- DSP Platform: Dashboard Container, Edge Runtime (Docker/K8s), Cockpit Container
- Shopfloor IT: MES Server, PLC Network
- Devices/Hardware: Mill PLC, Drill PLC, HBW PLC, DPS PLC

## Configuration

### Custom Layer Configuration

You can override default configurations for customer-specific requirements:

```typescript
const customConfig: Partial<ArchitectureConfig> = {
  layers: [
    // Custom layer definitions
    {
      id: 'business-layer',
      type: 'business',
      label: 'Customer Business Layer',
      backgroundColor: '#FFFFFF',
      heightRatio: 1,
      boxes: [
        {
          id: 'bp-custom-1',
          label: 'Custom System',
          widthRatio: 1/2,
          layer: 'business',
          position: 0,
          clickable: true,
        },
        // ... more boxes
      ],
    },
    // ... more layers
  ],
  arrows: [
    // Custom arrow definitions
    {
      id: 'custom-arrow-1',
      from: 'bp-custom-1',
      to: 'dsp-edge',
      type: 'l-shaped',
      color: '#154194',
      strokeWidth: 2,
      visible: true,
    },
  ],
};

// Use in component
<app-dsp-architecture-refactor
  [customConfig]="customConfig">
</app-dsp-architecture-refactor>
```

## Animation System

The component includes a powerful scene-based animation engine.

### Animation Actions

| Action Type | Description | Parameters |
|-------------|-------------|------------|
| `highlight` | Highlight specific boxes | `targets: string[]`, `color?: string` |
| `fadeothers` | Fade non-highlighted boxes | - |
| `connect` | Show specific arrows | `targets: string[]` |
| `disconnect` | Hide specific arrows | `targets: string[]` |
| `show` | Reveal hidden boxes | `targets: string[]` |
| `hide` | Conceal boxes | `targets: string[]` |
| `focus` | Zoom/focus on area | `targets: string[]` |
| `text` | Display overlay text | `text: string` |

### Custom Animation Scene

```typescript
const customScene: AnimationScene = {
  id: 'my-custom-scene',
  name: 'Custom Animation',
  description: 'Demonstrates custom flow',
  viewMode: 'functional',
  steps: [
    {
      id: 'step-1',
      label: 'Initialize',
      actions: [
        {
          type: 'highlight',
          targets: ['bp-1', 'bp-2'],
          color: '#154194',
        },
        {
          type: 'text',
          text: 'Starting data flow from business systems',
        },
      ],
      duration: 3000,
    },
    // ... more steps
  ],
};
```

## Styling & Theming

### Color Palette

The component uses the ORBIS corporate color palette:
- Business Layer: `#FFFFFF` (white)
- DSP Layer: `#E6F0FA` (light blue)
- Shopfloor Layer: `#F3F3F3` (light gray)

### Custom Styling

Override component styles using CSS custom properties or SCSS:

```scss
app-dsp-architecture-refactor {
  --box-border-color: #154194;
  --box-hover-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  --arrow-highlight-color: #5071af;
}
```

## Box IDs Reference

### Business Layer
- `bp-1`, `bp-2`, `bp-3`, `bp-4`, `bp-5`, `bp-6`

### DSP Layer
- `dsp-smartfactory-dashboard`
- `dsp-edge`
- `dsp-management-cockpit`
- Edge components: `edge-connectivity`, `edge-digital-twin`, `edge-process-logic`, `edge-analytics`, `edge-buffering`, `edge-data-storage`, `edge-workflow`

### Shopfloor Systems
- `sf-system-1`, `sf-system-2`, `sf-system-3`, `sf-system-4`

### Shopfloor Devices
- `sf-device-mill`
- `sf-device-drill`
- `sf-device-aiqs`
- `sf-device-hbw`
- `sf-device-dps`
- `sf-device-chrg`

## Icon Mapping

Icons are automatically mapped from the existing icon registry:
- Business icons: `ICONS.business.*`
- DSP icons: `ICONS.dsp.architecture.*` and `ICONS.dsp.functions.*`
- Shopfloor icons: `ICONS.shopfloor.systems.*` and `ICONS.shopfloor.stations.*`

See `icons.config.ts` for the complete mapping.

## Accessibility

The component follows accessibility best practices:
- Keyboard navigation support
- ARIA labels on interactive controls
- High contrast mode support
- Screen reader friendly

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Demo

Visit `/en/refactor-demo` or `/en/refactor` to see the component in action with interactive controls and event logging.

## Files Structure

```
dsp-architecture-refactor/
├── types.ts                              # Type definitions
├── layout.config.ts                      # Layout configurations for all views
├── animation.config.ts                   # Animation scenes
├── icons.config.ts                       # Icon mappings
├── dsp-architecture-refactor.component.ts    # Main component
├── dsp-architecture-refactor.component.html  # Template
├── dsp-architecture-refactor.component.scss  # Styles
└── README.md                             # This file
```

## Contributing

When extending this component:
1. Add new box IDs to the appropriate layer in `layout.config.ts`
2. Map icons in `icons.config.ts`
3. Create animation scenes in `animation.config.ts`
4. Update type definitions in `types.ts` if needed
5. Follow ORBIS color palette guidelines

## License

© ORBIS SE - All rights reserved
