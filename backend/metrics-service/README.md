# OMF Metrics Service

MQTT to InfluxDB metrics collection service for the ORBIS Modellfabrik.

## Overview

This service subscribes to MQTT topics from the factory floor (CCU, FTS, modules, sensors) and writes time-series data to InfluxDB for visualization in Grafana.

## Architecture

```
MQTT Broker (Mosquitto)
    ↓
Metrics Service (Node.js + TypeScript)
    ↓
InfluxDB 2.x
    ↓
Grafana Dashboards
```

## Prerequisites

- Node.js 18+ and npm
- MQTT broker (Mosquitto) running on localhost:1883 or configured IP
- InfluxDB 2.x instance (can be started via Docker Compose)
- Grafana (optional, for visualization)

## Quick Start

### 1. Install Dependencies

```bash
cd backend/metrics-service
npm install
```

### 2. Configure Environment

Create a `.env` file or set environment variables:

```bash
# MQTT Configuration
MQTT_URL=mqtt://localhost:1883
MQTT_CLIENT_ID=omf-metrics-service

# InfluxDB Configuration
INFLUX_URL=http://localhost:8086
INFLUX_TOKEN=dev-token-please-change
INFLUX_ORG=orbis
INFLUX_BUCKET=omf-metrics
```

### 3. Start InfluxDB + Grafana (via Docker Compose)

```bash
cd ../../deploy
docker compose -f docker-compose.metrics.yml up -d
```

This starts:
- **InfluxDB** on http://localhost:8086
  - Username: `admin`
  - Password: `adminpassword`
  - Token: `dev-token-please-change`
  - Organization: `orbis`
  - Bucket: `omf-metrics`
- **Grafana** on http://localhost:3000
  - Username: `admin`
  - Password: `admin`

### 4. Run the Metrics Service

**Development mode (with auto-reload):**
```bash
npm run dev
```

**Production mode:**
```bash
npm run build
npm start
```

## Configuration for Trade Fair / Demo

To switch from localhost to a trade fair IP (e.g., `192.168.0.100`):

```bash
export MQTT_URL=mqtt://192.168.0.100:1883
export INFLUX_URL=http://192.168.0.100:8086
npm run dev
```

Or update the `.env` file accordingly.

## MQTT Topics Subscribed

The service subscribes to the following topics:

### Order Management
- `ccu/order/completed` - Completed production orders
- `ccu/order/active` - Active orders

### FTS (Automated Guided Vehicle)
- `fts/v1/ff/+/state` - FTS state updates (VDA 5050)
- `fts/v1/ff/+/connection` - FTS connection status
- `fts/v1/ff/+/order` - FTS orders
- `fts/v1/ff/+/instantAction` - FTS instant actions
- `fts/v1/ff/+/factsheet` - FTS capabilities

### Production Modules
- `module/v1/ff/+/state` - Module states (DRILL, MILL, HBW, etc.)
- `module/v1/ff/NodeRed/+/state` - NodeRed-enriched module states

### Sensors
- `/j1/txt/1/i/bme680` - Environment sensor (temperature, humidity, IAQ)
- `/j1/txt/1/f/i/stock` - Warehouse stock levels

## InfluxDB Measurements

The service creates the following measurements:

### `order_durations`
Order completion times and production metrics.
- **Tags**: `order_id`, `type` (color), `order_type`, `workpiece_id`
- **Fields**: `duration_s`, `steps_count`
- **Time**: Order completion timestamp

### `production_step_durations`
Individual production step durations.
- **Tags**: `order_id`, `step_id`, `step_type`, `step_state`, `module_type`, `serial_number`, `command`
- **Fields**: `duration_s`

### `fts_state`
FTS vehicle state and battery level.
- **Tags**: `fts_id`, `action_state`, `motion_state`, `order_id`
- **Fields**: `battery_level`, `is_driving`, `is_idle`, `has_errors`, `load_count`, `order_update_id`

### `fts_connection`
FTS connection status.
- **Tags**: `fts_id`, `connection_state`
- **Fields**: `connected` (0/1)

### `fts_orders`
FTS order tracking.
- **Tags**: `fts_id`, `order_id`, `order_type`, `load_type`
- **Fields**: `order_count`, `order_update_id`, `node_count`, `edge_count`

### `fts_instant_actions`
FTS instant actions (calibration, etc.).
- **Tags**: `fts_id`, `action_id`, `action_type`
- **Fields**: `action_count`

### `module_state`
Production module states.
- **Tags**: `module_id`, `state`, `module_type`, `is_node_red`, `order_id`, `serial_number`
- **Fields**: `active` (1 for MANUFACTURE, 0 otherwise), `has_order`

### `environment`
Environmental sensor data (BME680).
- **Tags**: `sensor_id`, `sensor_type`
- **Fields**: `temperature`, `humidity`, `iaq`, `pressure`, `gas_resistance`

### `stock_levels`
Warehouse inventory per location.
- **Tags**: `hbw`, `location`, `workpiece_type`, `workpiece_state`, `workpiece_id`
- **Fields**: `stock_count`, `has_workpiece`

### `stock_aggregate`
Aggregate warehouse statistics.
- **Tags**: `hbw`
- **Fields**: `total_items`, `raw_items`, `processed_items`, `empty_locations`

## Grafana Dashboard Examples

Once data is flowing into InfluxDB, you can create Grafana dashboards to visualize:

### Order & Production KPIs
- **Order Throughput**: Orders completed per hour
- **Average Order Duration**: Mean time from start to finish
- **Production Step Analysis**: Which steps take longest?
- **Order Type Distribution**: Breakdown by color (RED, BLUE, WHITE)

### FTS Vehicle Metrics
- **FTS Utilization**: Percentage of time driving vs. idle
- **Battery Level Trends**: Monitor battery health
- **Trip Counter**: Number of navigation tasks completed
- **FTS Availability**: Connection uptime

### Module Performance
- **Module Utilization**: Time in MANUFACTURE state
- **Module Availability**: Connection status over time
- **Order Distribution by Module**: Which modules are busiest?

### Environment & Quality
- **Temperature & Humidity Trends**: Climate monitoring
- **Indoor Air Quality (IAQ)**: Track air quality over time
- **Stock Levels**: Real-time inventory visualization
- **Workpiece Location Heatmap**: Where are workpieces located?

## Development

### Project Structure

```
backend/metrics-service/
├── src/
│   ├── handlers/          # Topic-specific message handlers
│   │   ├── orderCompletedHandler.ts
│   │   ├── ftsStateHandler.ts
│   │   ├── ftsConnectionHandler.ts
│   │   ├── ftsOrderHandler.ts
│   │   ├── ftsInstantActionHandler.ts
│   │   ├── moduleStateHandler.ts
│   │   ├── environmentHandler.ts
│   │   └── stockHandler.ts
│   ├── config.ts          # Configuration management
│   ├── index.ts           # Main entry point
│   ├── influxWriter.ts    # InfluxDB client wrapper
│   ├── logger.ts          # Centralized logging
│   ├── mqttClient.ts      # MQTT client and routing
│   └── types.ts           # TypeScript type definitions
├── package.json
├── tsconfig.json
└── README.md
```

### Building

```bash
npm run build
```

Compiled JavaScript will be in `dist/`.

### Cleaning

```bash
npm run clean
```

## Troubleshooting

### MQTT Connection Issues
- Verify MQTT broker is running: `mosquitto -v`
- Check `MQTT_URL` environment variable
- Test with `mosquitto_sub -h localhost -t '#' -v`

### InfluxDB Connection Issues
- Verify InfluxDB is running: `curl http://localhost:8086/health`
- Check `INFLUX_URL` and `INFLUX_TOKEN`
- Verify bucket exists in InfluxDB UI

### No Data in Grafana
1. Check metrics service logs for errors
2. Verify MQTT messages are being received (check logs)
3. Query InfluxDB directly to confirm data is written:
   ```flux
   from(bucket: "omf-metrics")
     |> range(start: -1h)
     |> limit(n: 10)
   ```

## License

MIT
