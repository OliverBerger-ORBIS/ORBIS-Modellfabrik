# Orbis Source Code

This directory contains the Orbis-specific source code for the Agile Production Simulation system.

## 📁 Purpose

This folder contains custom source code developed by Orbis, distinct from the original Fischertechnik content. It follows the naming convention of using the "orbis" suffix to clearly identify Orbis customizations.

## 🚀 Development

- **Python Code**: Custom simulation and analysis scripts
- **Configuration**: Orbis-specific configuration files
- **Utilities**: Helper functions and tools
- **Integration**: Code to integrate with the Fischertechnik system

## 🔧 MQTT Mock System

### **Quick Start**
```bash
# Setup and run demo
python setup_mqtt_mock.py --demo

# Or setup manually
python setup_mqtt_mock.py
python mqtt_mock.py          # Terminal 1
python mqtt_test_client.py   # Terminal 2
```

### **Files**
- `mqtt_mock.py` - Main mock system for Fischertechnik modules
- `mqtt_test_client.py` - Test client for sending MQTT messages
- `setup_mqtt_mock.py` - Setup script for dependencies and broker

## 📋 Structure

```
src-orbis/
├── README.md           # This file
├── simulation/         # Simulation engine code
├── analysis/          # Data analysis tools
├── integration/       # Integration with Fischertechnik
└── utils/            # Utility functions
```

## 🔗 Related Folders

- `docs-orbis/` - Orbis documentation
- `tests-orbis/` - Orbis tests
- `Node-RED/` - Original Fischertechnik Node-RED flows
- `PLC-programs/` - Original Fischertechnik PLC programs

---

*Orbis Development Team* 