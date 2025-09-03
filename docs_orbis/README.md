# Orbis Modellfabrik - Documentation

This directory contains comprehensive documentation for the Orbis Modellfabrik system, based on the Fischertechnik Agile Production Simulation 24V.

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

### [Project Analysis Summary](./project-analysis-summary.md)
- **System Overview** - Complete project analysis and architecture
- **Core Technology** - MQTT-based communication system
- **Orbis Components** - Central configuration managers and dashboard
- **Current Status** - Modern YAML-based architecture

### [Project Status](./project-status.md)
- **Completed Features** - Central configuration managers, dashboard modernization
- **Cleaned Components** - Removed obsolete components and documentation
- **Next Steps** - Live APS integration roadmap
- **Current Architecture** - YAML-based configuration system

### [Node-RED Documentation](./node-red/)
- **System Architecture** - Overall system design and components
- **Flows Overview** - Tab structure and module organization
- **Subflows** - Reusable components and their functions
- **State Machine** - VDA 5050 compliant state transitions
- **Communication** - MQTT and OPC-UA protocols
- **Troubleshooting** - Common issues and solutions
- **Development** - Guidelines for customization

### [MQTT Documentation](./mqtt/)
- **Dashboard MQTT Integration** - Template-based control system
- **MQTT Control Summary** - Module control and commands
- **State Machine Notes** - FTS and module state management
- **Setup Guides** - Remote control and traffic logging

### [Configuration Guides]
- **[NFC Code Configuration](./nfc-code-configuration-guide.md)** - Central NFC code management
- **[Module Configuration](./module-configuration-guide.md)** - APS module configuration
- **[Topic Configuration](./topic-configuration-guide.md)** - MQTT topic mappings

### [Prerequisites](./prerequisites.md)
- **System Requirements** - All necessary prerequisites
- **Installation Guide** - Step-by-step installation
- **Troubleshooting** - Common issues and solutions
- **Quick Start** - Get up and running fast

### [Credentials & Access](./credentials.md)
- **Default Login Credentials** - Access information for all components
- **Network Configuration** - IP addresses and connectivity
- **Security Guidelines** - Best practices for production use
- **Troubleshooting Access** - Solutions for authentication issues

### [Analysis Documentation](./analysis/)
- **Session Analysis** - MQTT session analysis results
- **Workflow Analysis** - Comprehensive workflow documentation
- **PDF Analysis** - Documentation analysis results

## 🚀 Quick Start

1. **System Overview**: Start with [Project Analysis Summary](./project-analysis-summary.md)
2. **Current Status**: Review [Project Status](./project-status.md)
3. **Configuration**: Set up [NFC Codes](./nfc-code-configuration-guide.md) and [Modules](./module-configuration-guide.md)
4. **Dashboard**: Launch the modern Streamlit dashboard

## 🔧 System Components

### Modern Architecture (Januar 2025)
- **Central Configuration Managers** - YAML-based configuration for all components
- **MQTT Client System** - OMFMqttClient mit Singleton-Pattern
- **Modern Dashboard** - Streamlit-based interface mit funktionierenden Commands
- **Session Analysis Tools** - Template analyzers für CCU, TXT, Module, Node-RED

### Production Modules
- **25 Production Modules** (MILL, DRILL, OVEN, AIQS, HBW, FTS, CHRG)
- **Central Control Unit** (Raspberry Pi with Node-RED)
- **PLC Network** (Siemens S7-1200)
- **TXT4.0 Controllers** (Fischertechnik)
- **OPC-UA Communication** (Industrial IoT)

## 🎯 Key Features

### Central Configuration
- **NFC Code Manager** - Central YAML configuration for all NFC codes
- **Module Manager** - APS module configuration (ID, Name, Type, IP-Range)
- **Topic Manager** - MQTT topic mappings and friendly names
- **MQTT Client Manager** - OMFMqttClient mit Singleton-Pattern für zuverlässige Verbindungen

### Dashboard Integration
- **Factory Control** - All modules controlled via hardcoded working commands
- **Factory Reset Integration** - Direct factory reset functionality
- **Order Management** - ROT, WEISS, BLAU order processing
- **Central Configuration** - All settings manageable via dashboard tabs
- **Node-RED Integration** - Dedicated tab for Node-RED analysis

### Session Analysis
- **Template Analyzers** - Separate analysis tools for developers
- **15 Sessions Analyzed** - Wareneingang (9), Auftrag (3), AI-not-ok (3)
- **12,420 MQTT Messages** - Systematically analyzed and documented
- **3 Workflow Types** - Fully understood and implemented as templates

The system is now functional for basic factory control and ready for MessageGenerator integration in the next phase. 