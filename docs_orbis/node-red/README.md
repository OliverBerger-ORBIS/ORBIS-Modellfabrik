# Node-RED Documentation

This section contains comprehensive documentation for the Node-RED flows that power the Orbis Agile Production Simulation system.

## 📋 Documentation Index

### [Flows Overview](./flows-overview.md)
- Tab structure and organization
- Module-specific flows (MILL, DRILL, OVEN, AIQS, HBW, DPS)
- Flow grouping and organization

### [State Machine](./state-machine.md)
- VDA 5050 compliant state transitions
- Action states: PENDING → RUNNING → FINISHED/FAILED
- Connection states: ONLINE/OFFLINE/CONNECTIONBROKEN
- Error handling and recovery

## 🔧 Quick Reference

### System Components
- **25 Production Modules** across 5 types
- **Central Control Unit** (Raspberry Pi)
- **MQTT Broker** (192.168.2.189:1883)
- **OPC-UA Network** (192.168.0.x:4840)

### Key Files
- `flows.json` - Main Node-RED configuration
- `settings.js` - Node-RED settings
- Environment variables for configuration

### Access Points
- **Node-RED UI**: `http://192.168.0.100:1880/`
- **SSH Access**: `ff22` / `ff22+`
- **MQTT Topics**: `module/v1/ff/{serialNumber}/{action}`

## 🚀 Getting Started

1. **Review Architecture** - Understand the overall system design
2. **Study Flows** - Learn how modules are organized
3. **Understand States** - Master the state machine logic
4. **Practice Development** - Follow development guidelines

---

## 📁 Folder Organization

This documentation is part of the Orbis customizations (`docs-orbis/`) and should be distinguished from the original Fischertechnik Node-RED flows in the `Node-RED/` folder.

---

*For technical support, contact the Orbis Development Team* 