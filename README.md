# Agile-Production-Simulation-24V
>If you have any questions, please contact fischertechnik-technik@fischer.de

## Links
- [Product Page](https://www.fischertechnik.de/en/products/industry-and-universities/training-models/569289-agile-production-simulation-24v)
- [Overview Page](https://www.fischertechnik.de/en/industry-and-universities/technical-documents/simulate/agile-production-simulation#overview)
- [Quick Start Guide](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/quick-start-guide-agile-production-simulation_en.pdf)
- [Documentation](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/documentation_aps_en-0424.pdf)
- [Assigment Plans](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/assignmentplans_aps_en.pdf)
- [Calibration](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/en/calibration-en.zip)
- [Digital Learning Platform](https://www.fischertechnik-digital-learning-platform.de/)
- [Update Blog](https://www.fischertechnik.de/en/industry-and-universities/technical-documents/simulate/agile-production-simulation/update-blog)
- [Troubleshooting (DE)](https://www.fischertechnik.de/-/media/fischertechnik/rebrush/industrie-und-hochschulen/technische-dokumente/agile-production-simulation/de/fehlersuche_aps_de.pdf)

## Content

The PLC project archives of the individual modules are in the `PLC-programs` folder.

The solution to the exercise can be found in the folder `PLC-programs\S7_1200_TIAv18\Exercises`.

The `TXT4.0 programs` folder contains the project files of the 4 different TXTs of the APS.

The `Node-RED` folder contains the flows of Node-RED as a Json file

### Documentation

For detailed documentation of the Node-RED flows, system architecture, and development guidelines, see the [Orbis Documentation Directory](./docs-orbis/).

- **[Project Status](./docs-orbis/project-status.md)** - Aktueller Projektstand und Features
- **[Node-RED Documentation](./docs-orbis/node-red/)** - Complete flow analysis, state machine, and development guides
- **[System Architecture](./docs-orbis/node-red/architecture.md)** - Overall system design and components
- **[Flows Overview](./docs-orbis/node-red/flows-overview.md)** - Detailed tab and module structure
- **[State Machine](./docs-orbis/node-red/state-machine.md)** - VDA 5050 compliant state transitions
- **[Topic Configuration Guide](./docs-orbis/topic-configuration-guide.md)** - Zentrale MQTT Topic-Konfiguration
- **[Module Configuration Guide](./docs-orbis/module-configuration-guide.md)** - Zentrale Modul-Konfiguration
- **[MQTT Template Analysis](./docs-orbis/mqtt-template-analysis.md)** - Template-Analyse und -Management

### 🚀 Dashboard

Das **ORBIS Modellfabrik Dashboard** bietet umfassende MQTT-Template-Analyse und -Verwaltung:

- **📊 Template Library**: 67 analysierte MQTT-Topics (CCU, TXT, MODULE, Node-RED)
- **🔍 4-stufige Filterung**: Kategorie → Sub-Kategorie → Modul → Template
- **🏭 Modul-Namen-Filterung**: Benutzerfreundliche Namen (DRILL, AIQS, HBW, MILL, DPS, CHRG)
- **📋 Template-Strukturen**: Vollständige Analyse mit Beispielen und Validierungsregeln
- **⚙️ Zentrale Konfiguration**: YAML-basierte Verwaltung aller Templates

**Dashboard starten:**
```bash
source .venv/bin/activate
streamlit run src_orbis/mqtt/dashboard/aps_dashboard.py --server.port 8501
```

## 📁 Project Structure

### Original Fischertechnik Content
- `data/` - Original data files
- `PLC-programs/` - Original PLC programs  
- `TXT4.0-programs/` - Original TXT4.0 programs
- `Node-RED/` - Original Node-RED flows
- `doc/` - Original documentation

### Orbis Customizations
- `docs-orbis/` - Orbis documentation and analysis
- `src-orbis/` - Orbis source code
- `tests-orbis/` - Orbis tests

### Raspberry PI Image / Central Control Unit (CCU)

The Raspberry PI image can be found under the following link: https://short.omm.cloud/rpi-v130

see [Installation Instructions](RPI_Image.md)

For experienced users, SSH is enabled on the image with username `ff22` and password `ff22+`

### TXT 4.0 Controller

[ROBO Pro Coding](https://www.fischertechnik.de/de-de/industrie-und-hochschulen/apps) is required to access the code of the [TXT 4.0 Controllers](https://www.fischertechnik.de/txt40controller). This can be found in the Microsoft Store via the search.

Once the program has started, the project files can be imported and changed.

### Node-RED

A [Node-RED](https://nodered.org/) container is running on the Raspberry PI of the APS. To view the Node-RED flows of the APS, you can connect to the Node-RED via `http://192.168.0.100:1880/`. This requires a LAN or WLAN connection to the APS.

### PLC

TIAv18 is required to access the PLC programs.

As soon as TIAv18 is installed, the project files can be loaded and edited.
