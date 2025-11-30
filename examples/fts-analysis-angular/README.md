# FTS Analysis Angular Example

A standalone Angular application demonstrating FTS/AGV (Automated Guided Vehicle) data visualization and analysis.

## 🎯 Features

### Dashboard
- **Battery Status**: Real-time battery voltage, percentage, and charging state visualization
- **AGV Status**: Current position, driving state, and order information
- **Load Information**: Display of workpieces currently loaded on the AGV
- **Route & Position**: Simplified shopfloor map showing current position and action timeline

### Track & Trace
- **Workpiece Tracking**: Follow individual workpieces through the production process
- **Event History**: Chronological view of all events for each workpiece
- **Location Labels**: Human-readable location names for module IDs

## 📁 Project Structure

```
examples/fts-analysis-angular/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── fts-battery/       # Battery status visualization
│   │   │   ├── fts-status/        # AGV status overview
│   │   │   ├── fts-loads/         # Load information display
│   │   │   ├── fts-route/         # Route & position map
│   │   │   └── track-trace/       # Workpiece tracking
│   │   ├── models/
│   │   │   └── fts.types.ts       # TypeScript types for FTS data
│   │   ├── services/
│   │   │   └── fts-mock.service.ts # Mock MQTT service
│   │   ├── app.component.*        # Main application component
│   │   └── app.config.ts          # Angular configuration
│   ├── styles.scss                # Global styles
│   ├── index.html                 # HTML entry point
│   └── main.ts                    # Application bootstrap
├── angular.json                   # Angular CLI configuration
├── package.json                   # Dependencies
├── tsconfig.json                  # TypeScript configuration
└── README.md                      # This file
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm 9+

### Installation

```bash
cd examples/fts-analysis-angular
npm install
```

### Development Server

```bash
npm start
```

Navigate to `http://localhost:4200/`. The application will automatically reload on file changes.

### Build

```bash
npm run build
```

Build artifacts are stored in the `dist/` directory.

## 📊 Data Source

This application uses mock data based on real FTS session recordings from:
- `data/omf-data/fts-analysis/production_order_bwr_20251110_182819_fts_state.json`
- `data/omf-data/fts-analysis/production_order_bwr_20251110_182819_fts_order.json`

The mock service simulates:
- Battery state changes (100% → 68%)
- Location transitions (HBW → DRILL → MILL → AIQS → DPS)
- Action state transitions (WAITING → INITIALIZING → RUNNING → FINISHED)
- Workpiece loading/unloading (BLUE, WHITE, RED)

## 🏗️ Architecture

### Components

| Component | Description |
|-----------|-------------|
| `FtsBatteryComponent` | Displays battery voltage, percentage, and charging status |
| `FtsStatusComponent` | Shows AGV status, position, and action states |
| `FtsLoadsComponent` | Lists workpieces currently on the AGV |
| `FtsRouteComponent` | Simplified shopfloor map with position overlay |
| `TrackTraceComponent` | Workpiece tracking with event history |

### Services

| Service | Description |
|---------|-------------|
| `FtsMockService` | Simulates MQTT data streams for development |

### Models

The `fts.types.ts` file contains TypeScript interfaces based on VDA5050 standard:

- `FtsState`: Complete AGV state from `fts/v1/ff/{serial}/state`
- `FtsBatteryState`: Battery information
- `FtsActionState`: Individual action state (DOCK, TURN, PASS, etc.)
- `FtsLoadInfo`: Workpiece information
- `FtsOrder`: Navigation order from `fts/v1/ff/{serial}/order`
- `WorkpieceHistory`: Track & trace data structure

## 🔄 Integration into OMF3

This example is designed to be easily integrated into the main OMF3 application:

1. **Copy Components**: Move components to `omf3/apps/ccu-ui/src/app/components/`
2. **Replace Mock Service**: Use `MessageMonitorService` for real MQTT data
3. **Add Tab**: Create `fts-tab.component.ts` in `omf3/apps/ccu-ui/src/app/tabs/`
4. **Shared Types**: Move types to `omf3/libs/entities/src/`

### MQTT Topics Used

- `fts/v1/ff/5iO4/state` - FTS state updates (position, battery, loads, actions)
- `fts/v1/ff/5iO4/order` - Navigation orders (VDA5050 format)
- `fts/v1/ff/5iO4/connection` - Connection status
- `ccu/order/active` - CCU order context

## 📝 Future Enhancements

- [ ] Real MQTT integration
- [ ] Shopfloor layout overlay on actual SVG
- [ ] ERP data integration (Purchase Orders, Customer Orders)
- [ ] Sensor data correlation (temperature, pressure)
- [ ] Historical data analysis
- [ ] Export/reporting features

## 🔗 Related Documentation

- [FTS Analysis PR Description](../../docs/pr-descriptions/fts-analysis-example-app.md)
- [Session Analysis Data](../../data/omf-data/fts-analysis/README.md)
- [VDA5050 Standard](https://github.com/VDA5050/VDA5050)
