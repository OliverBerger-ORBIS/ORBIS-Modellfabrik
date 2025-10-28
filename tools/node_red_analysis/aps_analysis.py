#!/usr/bin/env python3
"""
Fischertechnik APS (Agile Production Simulation) Analyse
"""

import json
import re
from collections import defaultdict
from pathlib import Path


def extract_aps_states(flows_file):
    """Extract states for Fischertechnik APS system"""

    with open(flows_file) as f:
        flows = json.load(f)

    # Tab-Mapping erstellen
    tab_mapping = {}
    for item in flows:
        if item.get("type") == "tab":
            tab_mapping[item["id"]] = item.get("label", "Unknown")

    function_nodes = [item for item in flows if item.get("type") == "function"]

    results = {
        "module_states": set(),
        "action_states": set(),
        "commands": set(),
        "opcua_nodeids": set(),
        "mqtt_topics": set(),
        "module_analysis": defaultdict(lambda: {"states": set(), "commands": set(), "functions": []}),
        "all_functions": [],
        "system_stats": {
            "total_flows": len(flows),
            "total_functions": len(function_nodes),
            "total_tabs": len(tab_mapping),
        },
    }

    for node in function_nodes:
        if "func" not in node:
            continue

        func_code = node["func"]
        node_name = node.get("name", "Unnamed")
        tab_id = node.get("tab", "Unknown")
        tab_name = tab_mapping.get(tab_id, "Unknown")

        # Modul-Typ bestimmen
        module_type = None
        if "MILL" in tab_name:
            module_type = "MILL"
        elif "DRILL" in tab_name:
            module_type = "DRILL"
        elif "AIQS" in tab_name:
            module_type = "AIQS"
        elif "DPS" in tab_name:
            module_type = "DPS"
        elif "HBW" in tab_name:
            module_type = "HBW"
        elif "OVEN" in tab_name:
            module_type = "OVEN"

        # States extrahieren
        state_keywords = [
            "PICKBUSY",
            "MILLBUSY",
            "DRILLBUSY",
            "DROPBUSY",
            "FIREBUSY",
            "IDLE",
            "CALIBRATION",
            "WAITING",
            "WAITING_AFTER_PICK",
            "WAITING_AFTER_MILL",
            "WAITING_AFTER_DRILL",
            "WAITING_AFTER_DROP",
            "WAITING_AFTER_FIRE",
        ]

        found_states = []
        for keyword in state_keywords:
            if keyword in func_code:
                results["module_states"].add(keyword)
                found_states.append(keyword)
                if module_type:
                    results["module_analysis"][module_type]["states"].add(keyword)

        # Action States extrahieren
        action_keywords = ["PENDING", "RUNNING", "FINISHED", "FAILED"]
        found_action_states = []
        for keyword in action_keywords:
            if keyword in func_code:
                results["action_states"].add(keyword)
                found_action_states.append(keyword)

        # Commands extrahieren
        command_keywords = ["PICK", "DROP", "MILL", "DRILL", "FIRE", "CALIBRATION"]
        found_commands = []
        for keyword in command_keywords:
            if keyword in func_code:
                results["commands"].add(keyword)
                found_commands.append(keyword)
                if module_type:
                    results["module_analysis"][module_type]["commands"].add(keyword)

        # OPC-UA NodeIds extrahieren
        nodeid_matches = re.findall(r"ns=4;i=(\d+)", func_code)
        for match in nodeid_matches:
            results["opcua_nodeids"].add(f"ns=4;i={match}")

        # MQTT Topics extrahieren
        topic_matches = re.findall(r'topic["\']?\s*:\s*["\']([^"\']+)["\']', func_code)
        for match in topic_matches:
            if match and not match.startswith("$"):
                results["mqtt_topics"].add(match)

        # Function-Info speichern
        func_info = {
            "name": node_name,
            "tab_id": tab_id,
            "tab_name": tab_name,
            "module_type": module_type,
            "has_states": len(found_states) > 0,
            "has_commands": len(found_commands) > 0,
            "has_opcua": "ns=4;i=" in func_code,
            "has_mqtt": "topic" in func_code.lower(),
            "states": found_states,
            "commands": found_commands,
            "opcua_count": len(nodeid_matches),
        }

        results["all_functions"].append(func_info)

        if module_type:
            results["module_analysis"][module_type]["functions"].append(func_info)

    # Sets zu Listen konvertieren
    results["module_states"] = sorted(list(results["module_states"]))
    results["action_states"] = sorted(list(results["action_states"]))
    results["commands"] = sorted(list(results["commands"]))
    results["opcua_nodeids"] = sorted(list(results["opcua_nodeids"]))
    results["mqtt_topics"] = sorted(list(results["mqtt_topics"]))

    for module_type in results["module_analysis"]:
        results["module_analysis"][module_type]["states"] = sorted(
            list(results["module_analysis"][module_type]["states"])
        )
        results["module_analysis"][module_type]["commands"] = sorted(
            list(results["module_analysis"][module_type]["commands"])
        )

    return results


def generate_aps_flows_md(analysis_results):
    """Generate flows.md content"""

    content = []
    content.append("# Node-RED Flows - Fischertechnik APS")
    content.append("")
    content.append("## Overview")
    content.append("")
    content.append("Die Node-RED Flows der Fischertechnik Agile Production Simulation (APS) sind in Tabs organisiert.")
    content.append("Jeder Tab repräsentiert ein Produktionsmodul oder eine Systemkomponente.")
    content.append("")

    content.append("## Tab Structure")
    content.append("")
    content.append("### Production Modules")
    content.append("")

    # Module analysis
    for module_type, data in analysis_results["module_analysis"].items():
        content.append(f"#### {module_type} Module")
        content.append(f"- **Functions**: {len(data['functions'])}")
        content.append(f"- **States**: {', '.join(data['states']) if data['states'] else 'Keine'}")
        content.append(f"- **Commands**: {', '.join(data['commands']) if data['commands'] else 'Keine'}")
        content.append("")

    content.append("### System Components")
    content.append("")
    content.append("- **NodeRed Init** - System initialization")
    content.append("- **Global Functions** - Shared functionality")
    content.append("- **MQTT Configuration** - Message broker setup")
    content.append("")

    content.append("## Flow Organization")
    content.append("")
    content.append("### Module-Specific Flows")
    content.append("")
    content.append("Jedes Produktionsmodul hat eigene Flows für:")
    content.append("- State management")
    content.append("- Command processing")
    content.append("- OPC-UA communication")
    content.append("- MQTT messaging")
    content.append("")

    content.append("### Shared Flows")
    content.append("")
    content.append("- Order processing")
    content.append("- Status monitoring")
    content.append("- Error handling")
    content.append("- System configuration")
    content.append("")

    return "\n".join(content)


def generate_aps_flows_detailed_md(analysis_results):
    """Generate flows-detailed.md content"""

    content = []
    content.append("# Node-RED Flows Detailed - Fischertechnik APS")
    content.append("")
    content.append("## Detailed Flow Analysis")
    content.append("")
    content.append("### System Statistics")
    content.append("")
    content.append(f"- **Total Flows**: {analysis_results['system_stats']['total_flows']}")
    content.append(f"- **Function Nodes**: {analysis_results['system_stats']['total_functions']}")
    content.append(f"- **Tabs**: {analysis_results['system_stats']['total_tabs']}")
    content.append("")

    content.append("### Module Analysis")
    content.append("")

    for module_type, data in analysis_results["module_analysis"].items():
        content.append(f"#### {module_type} Module")
        content.append("")
        content.append(f"**Functions**: {len(data['functions'])}")
        content.append("")

        # Function details
        state_functions = [f for f in data["functions"] if f["has_states"]]
        command_functions = [f for f in data["functions"] if f["has_commands"]]
        opcua_functions = [f for f in data["functions"] if f["has_opcua"]]
        mqtt_functions = [f for f in data["functions"] if f["has_mqtt"]]

        content.append(f"- State Functions: {len(state_functions)}")
        content.append(f"- Command Functions: {len(command_functions)}")
        content.append(f"- OPC-UA Functions: {len(opcua_functions)}")
        content.append(f"- MQTT Functions: {len(mqtt_functions)}")
        content.append("")

        # Show key functions
        content.append("**Key Functions:**")
        for func in data["functions"][:5]:
            content.append(f"- {func['name']} (Tab: {func['tab_name']})")
            if func["states"]:
                content.append(f"  - States: {', '.join(func['states'])}")
            if func["commands"]:
                content.append(f"  - Commands: {', '.join(func['commands'])}")
        content.append("")

    content.append("### Flow Patterns")
    content.append("")
    content.append("#### State Management Pattern")
    content.append("")
    content.append("```javascript")
    content.append("// State transition example")
    content.append("if (flow.get('moduleState') == 'IDLE') {")
    content.append("    flow.set('moduleState', 'PICKBUSY');")
    content.append("    // Execute PICK operation")
    content.append("}")
    content.append("```")
    content.append("")

    content.append("#### OPC-UA Communication Pattern")
    content.append("")
    content.append("```javascript")
    content.append("// OPC-UA write example")
    content.append("msg.payload = {")
    content.append("    nodeId: 'ns=4;i=5',")
    content.append("    value: 'PICK'")
    content.append("};")
    content.append("return msg;")
    content.append("```")
    content.append("")

    content.append("#### MQTT Messaging Pattern")
    content.append("")
    content.append("```javascript")
    content.append("// MQTT topic construction")
    content.append("msg.topic = flow.get('$parent.MQTT_topic') + '/state';")
    content.append("msg.payload = flow.get('moduleState');")
    content.append("return msg;")
    content.append("```")
    content.append("")

    return "\n".join(content)


def generate_aps_opcua_nodes_md(analysis_results):
    """Generate opc-ua-nodes.md content"""

    content = []
    content.append("# OPC-UA Nodes - Fischertechnik APS")
    content.append("")
    content.append("## Overview")
    content.append("")
    content.append("Die Fischertechnik APS verwendet OPC-UA für die Kommunikation mit den Hardware-Modulen.")
    content.append("Jedes Modul hat einen OPC-UA Server, der über standardisierte NodeIds angesprochen wird.")
    content.append("")

    content.append("## NodeId Structure")
    content.append("")
    content.append("Alle NodeIds folgen dem Schema: `ns=4;i={number}`")
    content.append("")
    content.append("### Hardware Control NodeIds")
    content.append("")

    # Group NodeIds by function
    control_nodeids = []
    status_nodeids = []

    for nodeid in analysis_results["opcua_nodeids"]:
        if "i=5" in nodeid or "i=6" in nodeid or "i=52" in nodeid or "i=56" in nodeid:
            control_nodeids.append(nodeid)
        else:
            status_nodeids.append(nodeid)

    for nodeid in control_nodeids:
        content.append(f"- **{nodeid}** - Hardware Control")

    content.append("")
    content.append("### Status Monitoring NodeIds")
    content.append("")

    for nodeid in status_nodeids:
        content.append(f"- **{nodeid}** - Status Monitoring")

    content.append("")
    content.append("## Communication Flow")
    content.append("")
    content.append("```mermaid")
    content.append("sequenceDiagram")
    content.append("    participant NR as Node-RED")
    content.append("    participant OPC as OPC-UA Server")
    content.append("    participant HW as Hardware Module")
    content.append("")
    content.append("    Note over NR,HW: Command Execution")
    content.append("")
    content.append("    NR->>OPC: Write Command (ns=4;i=5)")
    content.append("    OPC->>HW: Execute Operation")
    content.append("    HW->>OPC: Operation Status")
    content.append("    OPC->>NR: Status Update (ns=4;i=8)")
    content.append("")
    content.append("    Note over NR,HW: Status Monitoring")
    content.append("")
    content.append("    NR->>OPC: Read Status (ns=4;i=7)")
    content.append("    OPC->>HW: Get State")
    content.append("    HW->>OPC: State Information")
    content.append("    OPC->>NR: State Response")
    content.append("```")
    content.append("")

    content.append("## Module-Specific Implementations")
    content.append("")

    for module_type, data in analysis_results["module_analysis"].items():
        content.append(f"### {module_type} Module")
        content.append("")
        opcua_functions = [f for f in data["functions"] if f["has_opcua"]]
        content.append(f"- **OPC-UA Functions**: {len(opcua_functions)}")
        content.append(f"- **NodeIds Used**: {data.get('opcua_count', 0)}")
        content.append("")

    content.append("## Error Handling")
    content.append("")
    content.append("### Connection States")
    content.append("")
    content.append("- **ONLINE** - Module connected and operational")
    content.append("- **OFFLINE** - Module disconnected")
    content.append("- **CONNECTIONBROKEN** - Connection lost during operation")
    content.append("")

    content.append("### Error Recovery")
    content.append("")
    content.append("1. **Connection Monitoring** - Continuous status checks")
    content.append("2. **Automatic Reconnection** - Retry failed connections")
    content.append("3. **State Recovery** - Restore module state after reconnection")
    content.append("4. **Error Logging** - Log all connection issues")
    content.append("")

    return "\n".join(content)


def generate_aps_state_machine_md(analysis_results):
    """Generate state-machine.md content"""

    content = []
    content.append("# State Machine - Fischertechnik APS")
    content.append("")
    content.append("## Overview")
    content.append("")
    content.append("Die Fischertechnik APS implementiert eine VDA 5050-konforme State Machine.")
    content.append("Jedes Produktionsmodul durchläuft definierte Zustände und Übergänge.")
    content.append("")

    content.append("## State Diagram")
    content.append("")
    content.append("```mermaid")
    content.append("stateDiagram-v2")
    content.append("    [*] --> IDLE")
    content.append("")
    content.append("    %% Module States")
    for state in analysis_results["module_states"]:
        if state != "IDLE":
            content.append(f"    IDLE --> {state}")

    content.append("")
    content.append("    %% State Transitions")

    # Common transitions
    transitions = [
        ("PICKBUSY", "WAITING_AFTER_PICK"),
        ("MILLBUSY", "WAITING_AFTER_MILL"),
        ("DRILLBUSY", "WAITING_AFTER_DRILL"),
        ("DROPBUSY", "IDLE"),
        ("FIREBUSY", "WAITING_AFTER_FIRE"),
        ("WAITING_AFTER_PICK", "MILLBUSY"),
        ("WAITING_AFTER_PICK", "DRILLBUSY"),
        ("WAITING_AFTER_PICK", "FIREBUSY"),
        ("WAITING_AFTER_MILL", "DROPBUSY"),
        ("WAITING_AFTER_DRILL", "DROPBUSY"),
        ("WAITING_AFTER_FIRE", "DROPBUSY"),
        ("CALIBRATION", "IDLE"),
    ]

    for from_state, to_state in transitions:
        if from_state in analysis_results["module_states"] and to_state in analysis_results["module_states"]:
            content.append(f"    {from_state} --> {to_state}")

    content.append("```")
    content.append("")

    content.append("## Module States")
    content.append("")
    content.append("### Primary States")
    content.append("")
    for state in analysis_results["module_states"]:
        content.append(f"- **{state}** - {get_state_description(state)}")
    content.append("")

    content.append("## Action States")
    content.append("")
    content.append("### VDA 5050 Compliant")
    content.append("")
    for state in analysis_results["action_states"]:
        content.append(f"- **{state}** - {get_action_description(state)}")
    content.append("")

    content.append("## Commands")
    content.append("")
    content.append("### Available Commands")
    content.append("")
    for cmd in analysis_results["commands"]:
        content.append(f"- **{cmd}** - {get_command_description(cmd)}")
    content.append("")

    content.append("## State Transitions")
    content.append("")
    content.append("### Typical Production Flow")
    content.append("")
    content.append("1. **IDLE** → **PICKBUSY** (Start PICK operation)")
    content.append("2. **PICKBUSY** → **WAITING_AFTER_PICK** (PICK completed)")
    content.append("3. **WAITING_AFTER_PICK** → **MILLBUSY** (Start MILL operation)")
    content.append("4. **MILLBUSY** → **WAITING_AFTER_MILL** (MILL completed)")
    content.append("5. **WAITING_AFTER_MILL** → **DROPBUSY** (Start DROP operation)")
    content.append("6. **DROPBUSY** → **IDLE** (DROP completed)")
    content.append("")

    content.append("## Error Handling")
    content.append("")
    content.append("### Error States")
    content.append("")
    content.append("- **FAILED** - Operation failed")
    content.append("- **CONNECTIONBROKEN** - OPC-UA connection lost")
    content.append("- **TIMEOUT** - Operation timeout")
    content.append("")

    content.append("### Recovery Procedures")
    content.append("")
    content.append("1. **State Reset** - Return to IDLE state")
    content.append("2. **Connection Retry** - Reconnect to OPC-UA server")
    content.append("3. **Operation Retry** - Retry failed operation")
    content.append("4. **Error Logging** - Log error details")
    content.append("")

    return "\n".join(content)


def get_state_description(state):
    """Get description for module state"""
    descriptions = {
        "IDLE": "Module is idle and ready for commands",
        "PICKBUSY": "Module is executing PICK operation",
        "MILLBUSY": "Module is executing MILL operation",
        "DRILLBUSY": "Module is executing DRILL operation",
        "DROPBUSY": "Module is executing DROP operation",
        "FIREBUSY": "Module is executing FIRE operation",
        "CALIBRATION": "Module is in calibration mode",
        "WAITING": "Module is waiting for next operation",
        "WAITING_AFTER_PICK": "Module waiting after PICK completion",
        "WAITING_AFTER_MILL": "Module waiting after MILL completion",
        "WAITING_AFTER_DRILL": "Module waiting after DRILL completion",
        "WAITING_AFTER_DROP": "Module waiting after DROP completion",
        "WAITING_AFTER_FIRE": "Module waiting after FIRE completion",
    }
    return descriptions.get(state, "Unknown state")


def get_action_description(state):
    """Get description for action state"""
    descriptions = {
        "PENDING": "Action is queued and waiting to start",
        "RUNNING": "Action is currently executing",
        "FINISHED": "Action completed successfully",
        "FAILED": "Action failed with error",
    }
    return descriptions.get(state, "Unknown action state")


def get_command_description(cmd):
    """Get description for command"""
    descriptions = {
        "PICK": "Pick up workpiece from input position",
        "DROP": "Drop workpiece to output position",
        "MILL": "Execute milling operation on workpiece",
        "DRILL": "Execute drilling operation on workpiece",
        "FIRE": "Execute firing operation (AIQS module)",
        "CALIBRATION": "Calibrate module to reference position",
    }
    return descriptions.get(cmd, "Unknown command")


def generate_aps_integration_guide_md():
    """Generate integration-guide.md content"""

    content = []
    content.append("# Integration Guide - Fischertechnik APS")
    content.append("")
    content.append("## Overview")
    content.append("")
    content.append("Dieser Guide beschreibt die Integration und Verwaltung der Fischertechnik APS Node-RED Flows.")
    content.append("")

    content.append("## Backup and Restore")
    content.append("")
    content.append("### Creating Backups")
    content.append("")
    content.append("1. **SSH Access**")
    content.append("   ```bash")
    content.append("   ssh ff22@192.168.0.100")
    content.append("   # Password: ff22+")
    content.append("   ```")
    content.append("")
    content.append("2. **Backup flows.json**")
    content.append("   ```bash")
    content.append("   cp ~/.node-red/flows.json ~/.node-red/backups/flows_$(date +%Y%m%d_%H%M%S).json")
    content.append("   ```")
    content.append("")
    content.append("3. **Backup settings.js**")
    content.append("   ```bash")
    content.append("   cp ~/.node-red/settings.js ~/.node-red/backups/settings_$(date +%Y%m%d_%H%M%S).js")
    content.append("   ```")
    content.append("")

    content.append("### Restoring Backups")
    content.append("")
    content.append("1. **Stop Node-RED**")
    content.append("   ```bash")
    content.append("   sudo systemctl stop nodered")
    content.append("   ```")
    content.append("")
    content.append("2. **Restore files**")
    content.append("   ```bash")
    content.append("   cp ~/.node-red/backups/flows_YYYYMMDD_HHMMSS.json ~/.node-red/flows.json")
    content.append("   cp ~/.node-red/backups/settings_YYYYMMDD_HHMMSS.js ~/.node-red/settings.js")
    content.append("   ```")
    content.append("")
    content.append("3. **Start Node-RED**")
    content.append("   ```bash")
    content.append("   sudo systemctl start nodered")
    content.append("   ```")
    content.append("")

    content.append("## SSH and Admin API")
    content.append("")
    content.append("### SSH Access")
    content.append("")
    content.append("- **Host**: 192.168.0.100")
    content.append("- **User**: ff22")
    content.append("- **Password**: ff22+")
    content.append("")

    content.append("### Admin API")
    content.append("")
    content.append("- **URL**: http://192.168.0.100:1880/admin")
    content.append("- **Authentication**: Basic Auth (ff22/ff22+)")
    content.append("")

    content.append("## Troubleshooting")
    content.append("")
    content.append("### Common Issues")
    content.append("")
    content.append("1. **Node-RED not starting**")
    content.append("   - Check logs: `journalctl -u nodered -f`")
    content.append("   - Verify flows.json syntax")
    content.append("   - Check file permissions")
    content.append("")
    content.append("2. **OPC-UA connection issues**")
    content.append("   - Verify module IP addresses")
    content.append("   - Check OPC-UA server status")
    content.append("   - Test with OPC-UA client")
    content.append("")
    content.append("3. **MQTT communication problems**")
    content.append("   - Check MQTT broker status")
    content.append("   - Verify topic subscriptions")
    content.append("   - Monitor MQTT traffic")
    content.append("")

    content.append("### Maintenance")
    content.append("")
    content.append("1. **Regular Backups**")
    content.append("   - Daily automated backups")
    content.append("   - Weekly manual verification")
    content.append("   - Monthly archive cleanup")
    content.append("")
    content.append("2. **System Updates**")
    content.append("   - Update Node-RED packages")
    content.append("   - Update system packages")
    content.append("   - Test after updates")
    content.append("")
    content.append("3. **Performance Monitoring**")
    content.append("   - Monitor CPU usage")
    content.append("   - Check memory consumption")
    content.append("   - Monitor network traffic")
    content.append("")

    return "\n".join(content)


def generate_aps_readme_md(analysis_results):
    """Generate README.md content for APS"""

    content = []
    content.append("# 🔴 Node-RED Integration Documentation")
    content.append("")
    content.append(
        "Diese Sektion enthält die umfassende Dokumentation der Node-RED Flows der Fischertechnik Agile Production Simulation (APS)."
    )
    content.append("")

    content.append("## 🔗 Integration Management")
    content.append("")
    content.append(
        "- **[Node-RED Integration](../../integrations/node_red/README.md)** - Backup, Restore und Management"
    )
    content.append("- **[Integration Guide](./integration-guide.md)** - Detaillierte Setup-Anleitung")
    content.append("")
    content.append("> **🔗 Verwandte Systeme:**")
    content.append("> - **[APS Overview](../aps/README.md)** - Fischertechnik Agile Production Simulation")
    content.append("> - **[FTS VDA 5050](../fts/README.md)** - Fahrerloses Transportsystem")
    content.append("> - **[System Context](../../02-architecture/system-context.md)** - Gesamtarchitektur")
    content.append("")

    content.append("## 📋 Documentation Index")
    content.append("")
    content.append("### [Flows](./flows.md)")
    content.append("- Tab structure and organization")
    content.append("- Module-specific flows (MILL, DRILL, OVEN, AIQS, HBW, DPS)")
    content.append("- Flow grouping and organization")
    content.append("")
    content.append("### [Flows Detailed](./flows-detailed.md)")
    content.append("- Detailed flow analysis and implementation")
    content.append("- Node-RED flow patterns and best practices")
    content.append("- State diagrams and pseudocode")
    content.append("")
    content.append("### [OPC UA Nodes](./opc-ua-nodes.md)")
    content.append("- OPC UA NodeIds and state transitions")
    content.append("- Connection states and error handling")
    content.append("- Module-specific OPC UA implementations")
    content.append("")
    content.append("### [State Machine](./state-machine.md)")
    content.append("- VDA 5050 compliant state transitions")
    content.append("- Action states: PENDING → RUNNING → FINISHED/FAILED")
    content.append("- Connection states: ONLINE/OFFLINE/CONNECTIONBROKEN")
    content.append("- Error handling and recovery")
    content.append("")
    content.append("### [Integration Guide](./integration-guide.md)")
    content.append("- Backup and restore procedures")
    content.append("- SSH and Admin API management")
    content.append("- Troubleshooting and maintenance")
    content.append("")

    content.append("## 🔧 Quick Reference")
    content.append("")
    content.append("### System Components")
    content.append("- **25 Production Modules** across 5 types")
    content.append("- **Central Control Unit** (Raspberry Pi)")
    content.append("- **MQTT Broker** (192.168.2.189:1883)")
    content.append("- **OPC-UA Network** (192.168.0.x:4840)")
    content.append("")

    content.append("### Key Files")
    content.append("- `flows.json` - Main Node-RED configuration")
    content.append("- `settings.js` - Node-RED settings")
    content.append("- Environment variables for configuration")
    content.append("")

    content.append("### Access Points")
    content.append("- **Node-RED UI**: `http://192.168.0.100:1880/`")
    content.append("- **SSH Access**: `ff22` / `ff22+`")
    content.append("- **MQTT Topics**: `module/v1/ff/{serialNumber}/{action}`")
    content.append("")

    content.append("## 🚀 Getting Started")
    content.append("")
    content.append("1. **Review Architecture** - Understand the overall system design")
    content.append("2. **Study Flows** - Learn how modules are organized")
    content.append("3. **Understand States** - Master the state machine logic")
    content.append("4. **Practice Development** - Follow development guidelines")
    content.append("")

    content.append("---")
    content.append("")
    content.append("## 📁 Folder Organization")
    content.append("")
    content.append(
        "Diese Dokumentation ist Teil der ORBIS-Anpassungen (`docs/06-integrations/`) und sollte von den ursprünglichen Fischertechnik Node-RED Flows im `Node-RED/` Ordner unterschieden werden."
    )
    content.append("")
    content.append("### Integration Structure")
    content.append("```")
    content.append("integrations/node_red/          # Backup/Restore Management")
    content.append("docs/06-integrations/     # Dokumentation")
    content.append("├── node-red/                   # Node-RED spezifische Docs")
    content.append("│   ├── README.md              # Diese Datei")
    content.append("│   ├── flows.md               # Flow-Übersicht")
    content.append("│   ├── flows-detailed.md      # Detaillierte Flow-Analyse")
    content.append("│   ├── opc-ua-nodes.md        # OPC UA NodeIds und States")
    content.append("│   ├── state-machine.md       # State Machine Dokumentation")
    content.append("│   └── integration-guide.md   # Integration Guide")
    content.append("```")
    content.append("")
    content.append("---")
    content.append("")
    content.append("*For technical support, contact the ORBIS Development Team*")

    return "\n".join(content)


def main():
    flows_file = Path("integrations/node_red/backups/20250915T102133Z/flows.json")

    if not flows_file.exists():
        print(f"Error: {flows_file} not found")
        return

    print("=== Fischertechnik APS Analyse ===")

    # Extract states
    analysis_results = extract_aps_states(flows_file)

    # Generate all MD files
    output_dir = Path("docs/analysis/node-red/aps_docs")
    output_dir.mkdir(exist_ok=True)

    # Generate flows.md
    flows_content = generate_aps_flows_md(analysis_results)
    flows_file = output_dir / "flows.md"
    with open(flows_file, "w") as f:
        f.write(flows_content)
    print(f"Generated: {flows_file}")

    # Generate flows-detailed.md
    flows_detailed_content = generate_aps_flows_detailed_md(analysis_results)
    flows_detailed_file = output_dir / "flows-detailed.md"
    with open(flows_detailed_file, "w") as f:
        f.write(flows_detailed_content)
    print(f"Generated: {flows_detailed_file}")

    # Generate opc-ua-nodes.md
    opcua_content = generate_aps_opcua_nodes_md(analysis_results)
    opcua_file = output_dir / "opc-ua-nodes.md"
    with open(opcua_file, "w") as f:
        f.write(opcua_content)
    print(f"Generated: {opcua_file}")

    # Generate state-machine.md
    state_machine_content = generate_aps_state_machine_md(analysis_results)
    state_machine_file = output_dir / "state-machine.md"
    with open(state_machine_file, "w") as f:
        f.write(state_machine_content)
    print(f"Generated: {state_machine_file}")

    # Generate integration-guide.md
    integration_content = generate_aps_integration_guide_md()
    integration_file = output_dir / "integration-guide.md"
    with open(integration_file, "w") as f:
        f.write(integration_content)
    print(f"Generated: {integration_file}")

    # Generate README.md
    readme_content = generate_aps_readme_md(analysis_results)
    readme_file = output_dir / "README.md"
    with open(readme_file, "w") as f:
        f.write(readme_content)
    print(f"Generated: {readme_file}")

    # Save analysis data
    data_file = output_dir / "aps_analysis_data.json"
    with open(data_file, "w") as f:
        json.dump(analysis_results, f, indent=2)
    print(f"Generated: {data_file}")

    print(f"\nAlle APS-Dokumentationen erstellt in: {output_dir}")


if __name__ == "__main__":
    main()
