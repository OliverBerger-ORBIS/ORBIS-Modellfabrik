# Metrics Service (Node.js + TypeScript) - Backend Variant A

## Übersicht

Der **Metrics Service** ist ein Backend-Dienst, der MQTT-Telemetriedaten von der Fischertechnik Modell-Fabrik (FMF) konsumiert und in eine Time-Series-Datenbank (InfluxDB) schreibt. Dies ermöglicht die Visualisierung von Produktions-KPIs, FTS-Metriken, Modulauslastung und Umweltdaten in Grafana-Dashboards.

### Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│              Fischertechnik Modell-Fabrik (FMF)                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐          │
│  │   CCU   │  │   FTS   │  │ Module  │  │ Sensoren │          │
│  │ Backend │  │  (5iO4) │  │ (DRILL, │  │ (BME680) │          │
│  │         │  │         │  │  MILL)  │  │          │          │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬─────┘          │
│       │            │            │            │                  │
│       └────────────┴────────────┴────────────┘                  │
│                         │                                        │
│                    MQTT Broker                                   │
│                   (Mosquitto)                                    │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │   Metrics Service     │
              │  (Node.js + TypeScript)│
              │                       │
              │  • MQTT Subscriber    │
              │  • Payload Parser     │
              │  • InfluxDB Writer    │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │      InfluxDB 2.x     │
              │   (Time-Series DB)    │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │       Grafana         │
              │    (Dashboards)       │
              └───────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │    Angular Web UI     │
              │ (oder Grafana direkt) │
              └───────────────────────┘
```

## Installation und Setup

### Voraussetzungen

- **Node.js** 18+ und npm
- **MQTT Broker** (Mosquitto) auf localhost:1883 oder konfigurierbare IP
- **Docker** und **Docker Compose** (für InfluxDB + Grafana)

### 1. Backend Service installieren

```bash
cd backend/metrics-service
npm install
```

### 2. InfluxDB + Grafana starten

```bash
cd ../../deploy
docker compose -f docker-compose.metrics.yml up -d
```

Dies startet:
- **InfluxDB** auf http://localhost:8086
  - Benutzername: `admin`
  - Passwort: `adminpassword`
  - Token: `dev-token-please-change`
  - Organisation: `orbis`
  - Bucket: `omf-metrics`
- **Grafana** auf http://localhost:3000
  - Benutzername: `admin`
  - Passwort: `admin`

### 3. Umgebungsvariablen konfigurieren

Erstellen Sie eine `.env`-Datei im `backend/metrics-service`-Verzeichnis:

```bash
# Lokal (Development)
MQTT_URL=mqtt://localhost:1883
INFLUX_URL=http://localhost:8086
INFLUX_TOKEN=dev-token-please-change
INFLUX_ORG=orbis
INFLUX_BUCKET=omf-metrics
```

Für die **Messe-Demo** ändern Sie die IP:

```bash
# Messe / Trade Fair
MQTT_URL=mqtt://192.168.0.100:1883
INFLUX_URL=http://192.168.0.100:8086
# Token, Org, Bucket bleiben gleich
```

### 4. Metrics Service starten

**Development-Modus (mit Auto-Reload):**
```bash
npm run dev
```

**Production-Modus:**
```bash
npm run build
npm start
```

## MQTT Topics und Mapping

Der Service subscribet folgende Topics und mapped sie zu InfluxDB-Measurements:

### 1. Order Management

**Topic**: `ccu/order/completed`

**Beispiel-Payload**: Siehe [`data/omf-data/test_topics/ccu_order_completed_storage_005.json`](../../data/omf-data/test_topics/ccu_order_completed_storage_005.json)

**InfluxDB-Mappings**:
- **Measurement**: `order_durations`
  - **Tags**: `order_id`, `type` (Farbe: RED/BLUE/WHITE), `order_type`, `workpiece_id`
  - **Fields**: `duration_s` (Sekunden), `steps_count` (Anzahl Produktionsschritte)
  - **Time**: `stoppedAt` Timestamp

- **Measurement**: `production_step_durations`
  - **Tags**: `order_id`, `step_id`, `step_type`, `module_type`, `serial_number`, `command`
  - **Fields**: `duration_s`
  - **Time**: Step `stoppedAt` Timestamp

### 2. FTS (Fahrerloses Transportsystem)

#### FTS State
**Topic**: `fts/v1/ff/+/state` (Wildcard für beliebige FTS-IDs)

**Measurement**: `fts_state`
- **Tags**: `fts_id`, `action_state`, `motion_state`, `order_id`
- **Fields**: 
  - `battery_level` (0-100)
  - `is_driving` (Boolean)
  - `is_idle` (Boolean)
  - `has_errors` (Boolean)
  - `load_count` (Anzahl geladener Workpieces)

#### FTS Connection
**Topic**: `fts/v1/ff/+/connection`

**Measurement**: `fts_connection`
- **Tags**: `fts_id`, `connection_state`
- **Fields**: `connected` (0 oder 1)

#### FTS Orders
**Topic**: `fts/v1/ff/+/order`

**Measurement**: `fts_orders`
- **Tags**: `fts_id`, `order_id`, `order_type`, `load_type`
- **Fields**: `order_count` (immer 1), `order_update_id`, `node_count`, `edge_count`

#### FTS Instant Actions
**Topic**: `fts/v1/ff/+/instantAction`

**Measurement**: `fts_instant_actions`
- **Tags**: `fts_id`, `action_id`, `action_type`
- **Fields**: `action_count` (immer 1)

### 3. Produktionsmodule

**Topic**: `module/v1/ff/+/state` und `module/v1/ff/NodeRed/+/state`

**Measurement**: `module_state`
- **Tags**: `module_id`, `state`, `module_type`, `is_node_red`, `order_id`, `serial_number`
- **Fields**: 
  - `active` (1 für MANUFACTURE-State, sonst 0)
  - `has_order` (Boolean)

**Module**: DRILL, MILL, HBW, DPS, AIQS

### 4. Umweltsensoren

**Topic**: `/j1/txt/1/i/bme680`

**Measurement**: `environment`
- **Tags**: `sensor_id`, `sensor_type`
- **Fields**: 
  - `temperature` (°C)
  - `humidity` (%)
  - `iaq` (Indoor Air Quality Index)
  - `pressure` (hPa)
  - `gas_resistance` (Ohm)

### 5. Lagerbestand

**Topic**: `/j1/txt/1/f/i/stock`

**Beispiel-Payload**: Siehe [`data/omf-data/test_topics/_j1_txt_1_f_i_stock__000089.json`](../../data/omf-data/test_topics/_j1_txt_1_f_i_stock__000089.json)

**InfluxDB-Mappings**:
- **Measurement**: `stock_levels` (pro Location)
  - **Tags**: `hbw`, `location`, `workpiece_type`, `workpiece_state`, `workpiece_id`
  - **Fields**: `stock_count`, `has_workpiece`

- **Measurement**: `stock_aggregate` (Gesamt-Statistik)
  - **Tags**: `hbw`
  - **Fields**: `total_items`, `raw_items`, `processed_items`, `empty_locations`

## Grafana Dashboard-Beispiele

Nach dem Start von Grafana (http://localhost:3000) können Sie Dashboards erstellen:

### 1. Data Source hinzufügen

1. Navigieren Sie zu **Configuration** → **Data Sources**
2. Klicken Sie auf **Add data source**
3. Wählen Sie **InfluxDB**
4. Konfiguration:
   - **Query Language**: Flux
   - **URL**: `http://influxdb:8086` (Docker-intern) oder `http://localhost:8086`
   - **Organization**: `orbis`
   - **Token**: `dev-token-please-change`
   - **Default Bucket**: `omf-metrics`

### 2. Dashboard-KPIs

#### Order & Produktions-KPIs

**Panel 1: Order Throughput (Aufträge pro Stunde)**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "order_durations")
  |> aggregateWindow(every: 1h, fn: count)
```

**Panel 2: Durchschnittliche Auftragsdauer**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "order_durations")
  |> filter(fn: (r) => r._field == "duration_s")
  |> mean()
```

**Panel 3: Auftragsverteilung nach Farbe**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "order_durations")
  |> group(columns: ["type"])
  |> count()
```

**Panel 4: Produktionsschritt-Analyse (Welcher Schritt dauert am längsten?)**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "production_step_durations")
  |> filter(fn: (r) => r._field == "duration_s")
  |> group(columns: ["step_type", "module_type"])
  |> mean()
```

#### FTS-Metriken

**Panel 5: FTS Batteriestatus**
```flux
from(bucket: "omf-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "fts_state")
  |> filter(fn: (r) => r._field == "battery_level")
  |> last()
```

**Panel 6: FTS Auslastung (Driving vs. Idle)**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fts_state")
  |> filter(fn: (r) => r._field == "is_driving" or r._field == "is_idle")
  |> aggregateWindow(every: 1h, fn: mean)
```

**Panel 7: FTS Trip Counter (Anzahl abgeschlossener Navigationsaufgaben)**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "fts_orders")
  |> filter(fn: (r) => r._field == "order_count")
  |> aggregateWindow(every: 1h, fn: sum)
```

#### Modul-Performance

**Panel 8: Modul-Auslastung (Zeit in MANUFACTURE-State)**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "module_state")
  |> filter(fn: (r) => r._field == "active")
  |> group(columns: ["module_id"])
  |> aggregateWindow(every: 1h, fn: mean)
```

**Panel 9: Auftragsverteilung nach Modul**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "production_step_durations")
  |> group(columns: ["module_type"])
  |> count()
```

#### Umwelt & Qualität

**Panel 10: Temperatur- und Luftfeuchte-Trends**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "temperature" or r._field == "humidity")
```

**Panel 11: Indoor Air Quality (IAQ)**
```flux
from(bucket: "omf-metrics")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "environment")
  |> filter(fn: (r) => r._field == "iaq")
```

**Panel 12: Lagerbestand (Stock Levels)**
```flux
from(bucket: "omf-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "stock_aggregate")
  |> filter(fn: (r) => r._field == "total_items" or r._field == "raw_items" or r._field == "processed_items")
  |> last()
```

**Panel 13: Workpiece Location Heatmap**
```flux
from(bucket: "omf-metrics")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "stock_levels")
  |> filter(fn: (r) => r._field == "has_workpiece")
  |> last()
  |> group(columns: ["location", "workpiece_type"])
```

## Entwicklung

### Projektstruktur

```
backend/metrics-service/
├── src/
│   ├── handlers/              # Topic-spezifische Handler
│   │   ├── orderCompletedHandler.ts
│   │   ├── ftsStateHandler.ts
│   │   ├── ftsConnectionHandler.ts
│   │   ├── ftsOrderHandler.ts
│   │   ├── ftsInstantActionHandler.ts
│   │   ├── moduleStateHandler.ts
│   │   ├── environmentHandler.ts
│   │   └── stockHandler.ts
│   ├── config.ts              # Konfiguration via Env-Variablen
│   ├── index.ts               # Haupteinstiegspunkt
│   ├── influxWriter.ts        # InfluxDB-Wrapper mit Batching
│   ├── logger.ts              # Zentralisiertes Logging
│   ├── mqttClient.ts          # MQTT-Client und Routing
│   └── types.ts               # TypeScript-Typdefinitionen
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

### TypeScript-Konfiguration

Die `tsconfig.json` ist mit `strict: true` konfiguriert für maximale Type-Safety. Alle Payload-Strukturen sind als Interfaces in `types.ts` definiert.

### Fehlerbehandlung

- **MQTT-Reconnect**: Automatisch alle 5 Sekunden
- **InfluxDB-Fehler**: Werden geloggt, Service crasht nicht
- **Parsing-Fehler**: Robuste Parser mit Try-Catch, unerwartete Felder werden ignoriert

### Logging

Zentralisiertes Logging mit `logger.ts`:
- **DEBUG**: Detaillierte Informationen (z.B. geschriebene Points)
- **INFO**: Wichtige Events (z.B. MQTT-Verbindung, Topics subscribed)
- **WARN**: Warnungen (z.B. fehlende Felder in Payloads)
- **ERROR**: Fehler (z.B. Parsing-Fehler, InfluxDB-Schreibfehler)

## Betrieb

### Lokal (Development)

```bash
# InfluxDB + Grafana starten
docker compose -f deploy/docker-compose.metrics.yml up -d

# Metrics Service starten
cd backend/metrics-service
npm run dev
```

### Messe-Demo

1. **MQTT-Broker** auf Messe-IP (`192.168.0.100`) erreichbar machen
2. **InfluxDB + Grafana** auf Messe-Hardware deployen (oder in Docker)
3. **Environment-Variablen** anpassen:
   ```bash
   export MQTT_URL=mqtt://192.168.0.100:1883
   export INFLUX_URL=http://192.168.0.100:8086
   ```
4. **Metrics Service** starten:
   ```bash
   npm run build
   npm start
   ```

### Production Deployment

Für Production-Deployment können Sie:
1. **Docker-Container** nutzen (siehe auskommentierte Sektion in `docker-compose.metrics.yml`)
2. **Systemd-Service** erstellen
3. **PM2** oder ähnliche Process-Manager verwenden

## Troubleshooting

### Problem: MQTT-Verbindung schlägt fehl

**Lösung**:
1. MQTT-Broker läuft? → `mosquitto -v`
2. IP/Port korrekt? → `MQTT_URL` überprüfen
3. Test mit: `mosquitto_sub -h localhost -t '#' -v`

### Problem: InfluxDB-Verbindung schlägt fehl

**Lösung**:
1. InfluxDB läuft? → `curl http://localhost:8086/health`
2. Token korrekt? → In InfluxDB UI überprüfen
3. Bucket existiert? → In InfluxDB UI nachsehen

### Problem: Keine Daten in Grafana

**Lösung**:
1. Metrics-Service-Logs prüfen → `npm run dev` (zeigt Debug-Logs)
2. MQTT-Nachrichten kommen an? → Logs nach "Processed X point(s)" suchen
3. InfluxDB-Daten direkt abfragen:
   ```flux
   from(bucket: "omf-metrics")
     |> range(start: -1h)
     |> limit(n: 10)
   ```

## Verwandte Dokumentation

- [FTS Integration](./TXT-FTS/README.md) - FTS-Steuerung und VDA 5050
- [MQTT Topic Conventions](./00-REFERENCE/mqtt-topic-conventions.md) - Topic-Naming-Patterns
- [Pub/Sub Analysis](../../archive/analysis/aps-mqtt-logs/pub-sub-pattern-analysis-2025-09-28.md) - MQTT-Kommunikationsmuster

## Lizenz

MIT
