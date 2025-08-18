# MQTT Analysis Scripts - Fischertechnik APS

## 📁 Structure

### `/loggers/` - MQTT Data Collection
- **`aps_persistent_logger.py`** - Main persistent logger with SQLite storage
- **`aps_mqtt_logger.py`** - Simple MQTT logger for live data
- **`aps_persistent_data_analyzer.py`** - Data analyzer for persistent logs
- **`aps_persistent_analyzer.py`** - Legacy analyzer
- **`aps_web_tester.py`** - Web interface tester
- **`comprehensive_mqtt_logger.py`** - Comprehensive logging (legacy)
- **`simple_aps_logger.py`** - Simple logger for testing

### `/analyzers/` - Data Analysis & Visualization
- **`live_aps_analyzer.py`** - Live data analysis from log files
- **`simple_mqtt_visualizer.py`** - Simple visualization tool
- **`mqtt_traffic_analyzer.py`** - Traffic analysis (legacy)

### `/tools/` - Utility Scripts
- **`mqtt_bridge_logger.py`** - MQTT bridge with logging
- **`mqtt_bridge_simple.py`** - Simple MQTT bridge
- **`mqtt_connection_tester.py`** - Connection testing tool
- **`mqtt_mock.py`** - Mock MQTT broker
- **`mqtt_test_client.py`** - Test client
- **`remote_mqtt_client.py`** - Remote client
- **`setup_mqtt_mock.py`** - Mock setup

### `/dashboard/` - Interactive Dashboard
- **`aps_dashboard.py`** - Streamlit dashboard for MQTT analysis

## 🚀 Quick Start

### 1. Start Logger
```bash
cd src-orbis/mqtt/loggers/
python aps_persistent_logger.py
```

### 2. Start Dashboard
```bash
cd src-orbis/mqtt/dashboard/
streamlit run aps_dashboard.py
```

### 3. Analyze Data
```bash
cd src-orbis/mqtt/analyzers/
python live_aps_analyzer.py
```

## 📊 Data Flow

1. **Logger** → Collects MQTT data → `mqtt-data/logs/` + `mqtt-data/databases/`
2. **Dashboard** → Reads from databases → Interactive visualization
3. **Analyzers** → Process data → `mqtt-data/exports/`

## 🔧 Configuration

- **Credentials**: `config/credentials.yml`
- **Log Files**: `mqtt-data/logs/`
- **Databases**: `mqtt-data/databases/`
- **Exports**: `mqtt-data/exports/`
