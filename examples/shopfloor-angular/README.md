# Angular Shopfloor Example - OMF3 Prototype

This standalone Angular example demonstrates the OMF3 Shopfloor layout architecture with ORBIS and DSP special cells. **Based on the actual OMF3 shopfloor-preview component**, it's designed for seamless integration into the main OMF3 application after approval.

## 🎯 Overview

This example implements:

- **OMF3-Based Architecture**: Uses the same JSON-based layout configuration as `omf3/apps/ccu-ui/src/app/components/shopfloor-preview`
- **Shopfloor Layout**: Absolute-positioned cells based on JSON configuration (`shopfloor_layout.json`)
- **ORBIS Cell (Company)**: Special cell with light blue background (`#cfe6ff`) showing consulting services, use cases, and incremental development methodology
- **DSP Cell (Software)**: Special cell with light blue background showing architecture and platform information
- **Dynamic Module Cells**: Clickable cells displaying simulated MQTT data (MILL, DRILL, AIQS, HBW, VGR, SLD, MPO, SSC, DPS)
- **Mock MQTT Service**: Simulates real-time data updates for demonstration purposes
- **Details Sidebar**: Slides in from the right to show detailed information about selected cells
- **Incremental Phases Component**: Interactive SVG diagram showing the 5 phases of incremental development

## 🏗️ Architecture

This example is based on the OMF3 shopfloor system:

### JSON-Based Layout Configuration
- **Configuration File**: `src/assets/shopfloor/shopfloor_layout.json`
- **Type Definitions**: `src/app/shopfloor-layout/shopfloor-layout.types.ts`
- **Cell Roles**: `module`, `company`, `software`
- **Background Color**: ORBIS and DSP use `#cfe6ff` (exact match to OMF3)

### Component Structure
- **Shopfloor Component**: Loads JSON config, renders cells with absolute positioning
- **Details Sidebar**: Shows cell-specific content (ORBIS, DSP, or dynamic MQTT data)
- **Incremental Component**: Interactive 5-phase development methodology diagram
- **MQTT Mock Service**: Observable-based simulation matching OMF3 patterns

## 📋 Features

### Shopfloor Layout
- JSON-configured cell positions and sizes
- Absolute positioning (800x600px canvas)
- Real-time status updates every 3 seconds (simulated)
- Color-coded cell borders based on status (running, idle, error, maintenance)
- Scalable viewport (0.8x default scale)
- OMF3-compatible cell structure

### ORBIS Cell Content
1. **Data Aggregation**
   - A) Business Process Data from ERP (order processing, customer orders)
   - B) Shopfloor Process Data (MILL, DRILL, AIQS)
   - C) Single-part specific information (NFC tag aggregation)
   - D) Environmental Sensor time-series data

2. **Track & Trace**
   - Object location tracking
   - Process data correlation
   - Sensor data integration
   - Quality impact analysis

3. **Predictive Maintenance**
   - Pattern recognition
   - Anomaly detection
   - Maintenance forecasting

4. **Incremental Development Methodology**
   - Interactive SVG diagram with 5 phases
   - Click on phases to see detailed activities
   - Visual representation of the development cycle

### DSP Cell Content (Distributed Shopfloor Processing)
- Interoperability: Bi-directional communication between systems
- Decentralized Control: Object-oriented process choreography
- Digital Twin: Real-time asset mapping
- Edge & Cloud Architecture: Local processing + centralized management
- Industry 4.0 capabilities (IIoT, AI, big data analytics)
- Links to ORBIS DSP resources

### Dynamic Cells
- Live status indicator
- Temperature readings
- Cycle time
- Parts produced counter
- Last update timestamp

## 🚀 Quick Start

### Prerequisites

- Node.js (v18 or higher)
- npm (v9 or higher)

### Installation

1. Navigate to the example directory:
```bash
cd examples/shopfloor-angular
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Open your browser and navigate to:
```
http://localhost:4200
```

The application will automatically reload when you make changes to the source files.

## 📁 Project Structure

```
examples/shopfloor-angular/
├── src/
│   ├── app/
│   │   ├── shopfloor/              # Main shopfloor grid component
│   │   │   ├── shopfloor.component.ts
│   │   │   ├── shopfloor.component.html
│   │   │   └── shopfloor.component.scss
│   │   ├── incremental/            # Incremental phases component
│   │   │   ├── incremental.component.ts
│   │   │   ├── incremental.component.html
│   │   │   └── incremental.component.scss
│   │   ├── details-sidebar/        # Sidebar for cell details
│   │   │   ├── details-sidebar.component.ts
│   │   │   ├── details-sidebar.component.html
│   │   │   └── details-sidebar.component.scss
│   │   ├── services/               # Services
│   │   │   └── mqtt-mock.service.ts
│   │   ├── app.component.ts
│   │   └── app.config.ts
│   ├── index.html
│   ├── main.ts
│   └── styles.scss
├── angular.json
├── package.json
├── tsconfig.json
├── tsconfig.app.json
└── README.md
```

## 🔧 Build for Production

To build the application for production:

```bash
npm run build
```

The build artifacts will be stored in the `dist/` directory.

## 🎨 Customization

### Styling

All styles are written in SCSS and are easily customizable:

- **Global styles**: `src/styles.scss`
- **Shopfloor grid**: `src/app/shopfloor/shopfloor.component.scss`
- **Sidebar**: `src/app/details-sidebar/details-sidebar.component.scss`
- **Incremental phases**: `src/app/incremental/incremental.component.scss`

### Colors

The ORBIS and DSP cells use a light blue gradient background defined in `shopfloor.component.scss`:

```scss
.cell-special {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-color: #2196f3;
}
```

Status colors for dynamic cells:
- Running: `#50C878` (green)
- Idle: `#FFA500` (orange)
- Error: `#E74C3C` (red)
- Maintenance: `#3498DB` (blue)

### Grid Layout

To modify the grid layout, edit the `cells` array in `shopfloor.component.ts`:

```typescript
readonly cells: ShopfloorCell[] = [
  { id: 'MILL', name: 'MILL', type: 'dynamic', row: 0, col: 0 },
  // ... add or modify cells
];
```

## 🔄 Integrating Real MQTT

The example uses `MqttMockService` to simulate MQTT data. To integrate with a real MQTT broker:

### 1. Install ngx-mqtt

```bash
npm install ngx-mqtt
```

### 2. Configure MQTT Connection

Update `app.config.ts`:

```typescript
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { IMqttServiceOptions, MqttModule } from 'ngx-mqtt';

export const MQTT_SERVICE_OPTIONS: IMqttServiceOptions = {
  hostname: '192.168.0.100',
  port: 9001,
  protocol: 'ws',
  path: '/mqtt'
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    // Add MQTT provider
  ]
};
```

### 3. Replace Mock Service

In `shopfloor.component.ts`, replace `MqttMockService` with the actual MQTT service:

```typescript
import { MqttService } from 'ngx-mqtt';

constructor(private mqttService: MqttService) {
  // Subscribe to topics
  this.mqttService.observe('shopfloor/+/status').subscribe(
    (message) => {
      // Handle MQTT message
      const payload = JSON.parse(message.payload.toString());
      // Update cell data
    }
  );
}
```

### 4. Topic Structure

Expected MQTT topic structure:
```
shopfloor/<cell-id>/status
shopfloor/<cell-id>/temperature
shopfloor/<cell-id>/production
```

Expected payload format:
```json
{
  "status": "running",
  "temperature": 45,
  "cycleTime": 120,
  "partsProduced": 234,
  "timestamp": "2025-11-20T22:00:00Z"
}
```

## 🔗 Integration into OMF3

This example is designed for **seamless integration** into OMF3:

### Architecture Compatibility

The example is based on OMF3's actual shopfloor system:
- Uses the same JSON configuration format as `omf3/apps/ccu-ui/public/shopfloor/shopfloor_layout.json`
- Implements the same type definitions as `omf3/apps/ccu-ui/src/app/components/shopfloor-preview/shopfloor-layout.types.ts`
- Uses `#cfe6ff` background color for ORBIS/DSP cells (exact match to OMF3 config)
- Cell roles: `module`, `company`, `software` match OMF3 types

### Integration Steps

1. **Extend Existing Shopfloor Component**: 
   - Add details sidebar functionality to `omf3/apps/ccu-ui/src/app/components/shopfloor-preview`
   - Add click handlers for `company` and `software` role cells
   - Integrate `IncrementalComponent` and `DetailsSidebarComponent`

2. **Update Layout Configuration**:
   - ORBIS and DSP cells are already in `omf3/apps/ccu-ui/public/shopfloor/shopfloor_layout.json`
   - Add `has_details: true` flag if needed
   - No structural changes required

3. **Add Components**:
   - Copy `incremental/` to `omf3/apps/ccu-ui/src/app/components/incremental/`
   - Copy `details-sidebar/` to `omf3/apps/ccu-ui/src/app/components/details-sidebar/`

4. **Replace Mock Service**:
   - The example uses Observable patterns compatible with OMF3's MQTT client
   - Replace `MqttMockService.getCellData()` with real MQTT subscriptions
   - Map serial numbers to MQTT topics

5. **Add Navigation** (Optional):
   - If creating a dedicated shopfloor page, add route in `app.routes.ts`
   - Or enhance existing Overview tab with sidebar functionality

### Why This Approach Works

- **Same Architecture**: Built on OMF3's actual shopfloor-preview component
- **JSON-Driven**: Uses the same layout configuration format
- **Type-Safe**: Shares type definitions with OMF3
- **Style-Compatible**: Uses OMF3's color scheme and styling patterns
- **Observable-Based**: MQTT mock service matches OMF3's reactive patterns

## 📚 Technologies Used

- **Angular 18**: Modern web framework
- **TypeScript 5.5**: Type-safe JavaScript
- **RxJS 7**: Reactive programming
- **SCSS**: Advanced CSS with variables and nesting
- **Standalone Components**: Modern Angular architecture

## 🎯 Acceptance Criteria

- ✅ Example app can be started locally with clear instructions
- ✅ ORBIS cell shows static consulting content and use cases
- ✅ ORBIS cell includes interactive incremental phases component
- ✅ DSP cell shows static architecture info and links
- ✅ Dynamic cells display simulated MQTT data
- ✅ Data updates periodically (every 3 seconds)
- ✅ Light blue background for ORBIS and DSP cells
- ✅ Clickable cells open detailed sidebar
- ✅ Clean, customizable SCSS styling
- ✅ Documentation for MQTT integration

## 📝 Notes

- This is a **prototype/example** designed for easy integration
- Mock data is used for demonstration purposes
- Production deployment would require:
  - Real MQTT broker connection
  - Topic mapping configuration
  - Authentication/authorization
  - Error handling and reconnection logic
  - Performance optimization

## 🤝 Contributing

This example is part of the ORBIS-Modellfabrik repository. For questions or contributions, please refer to the main repository documentation.

## 📄 License

MIT License - See main repository for details.

---

**Created as part of the OMF3 migration project**
