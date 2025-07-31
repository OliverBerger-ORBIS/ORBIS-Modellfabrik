# Orbis Agile Production Simulation - Documentation

This directory contains comprehensive documentation for the Orbis Agile Production Simulation system, based on the Fischertechnik Agile Production Simulation 24V.

## 📁 Folder Structure

### Original Fischertechnik Content
- `data/` - Original data files
- `PLC-programs/` - Original PLC programs
- `TXT4.0-programs/` - Original TXT4.0 programs
- `Node-RED/` - Original Node-RED flows
- `doc/` - Original documentation

### Orbis Customizations
- `docs-orbis/` - Orbis documentation (this folder)
- `src-orbis/` - Orbis source code
- `tests-orbis/` - Orbis tests

## 📚 Documentation Structure

### [Node-RED Documentation](./node-red/)
- **System Architecture** - Overall system design and components
- **Flows Overview** - Tab structure and module organization
- **Subflows** - Reusable components and their functions
- **State Machine** - VDA 5050 compliant state transitions
- **Communication** - MQTT and OPC-UA protocols
- **Troubleshooting** - Common issues and solutions
- **Development** - Guidelines for customization

### [PLC Documentation](./plc/)
- Siemens S7-1200 TIA v18 programs
- Module-specific PLC configurations
- Exercise solutions

### [TXT4.0 Documentation](./txt4.0/)
- Fischertechnik controller programs
- Configuration and programming guidelines

### [API Documentation](./api/)
- VDA 5050 specification implementation
- Communication protocols and standards

## 🚀 Quick Start

1. **System Overview**: Start with [Node-RED Architecture](./node-red/architecture.md)
2. **Module Structure**: Review [Flows Overview](./node-red/flows-overview.md)
3. **State Management**: Understand [State Machine](./node-red/state-machine.md)
4. **Development**: Follow [Development Guidelines](./node-red/development.md)

## 🔧 System Components

- **25 Production Modules** (MILL, DRILL, OVEN, AIQS, HBW)
- **Central Control Unit** (Raspberry Pi with Node-RED)
- **PLC Network** (Siemens S7-1200)
- **TXT4.0 Controllers** (Fischertechnik)
- **OPC-UA Communication** (Industrial IoT)
- **MQTT Messaging** (Inter-module communication)

## 📖 Original Documentation

For the original Fischertechnik documentation, see the [main README](../README.md) and the original `doc/` folder.

---

*Documentation maintained by Orbis Development Team* 