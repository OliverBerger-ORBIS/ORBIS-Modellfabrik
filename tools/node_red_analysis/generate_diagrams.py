#!/usr/bin/env python3
"""
Generate additional Mermaid diagrams for Node-RED documentation
"""

from pathlib import Path


def generate_module_flow_diagram():
    """Generate module flow diagram"""

    mermaid = []
    mermaid.append("graph TD")
    mermaid.append("    subgraph \"Production Module Flow\"")
    mermaid.append("        START([Order Received])")
    mermaid.append("        IDLE[IDLE State]")
    mermaid.append("        PICK[PICK Operation]")
    mermaid.append("        PROCESS[PROCESS Operation]")
    mermaid.append("        DROP[DROP Operation]")
    mermaid.append("        END([Order Complete])")
    mermaid.append("")
    mermaid.append("        START --> IDLE")
    mermaid.append("        IDLE -->|PICK Command| PICK")
    mermaid.append("        PICK -->|PICK Complete| PROCESS")
    mermaid.append("        PROCESS -->|PROCESS Complete| DROP")
    mermaid.append("        DROP -->|DROP Complete| IDLE")
    mermaid.append("        IDLE -->|No More Orders| END")
    mermaid.append("    end")
    mermaid.append("")
    mermaid.append("    subgraph \"State Details\"")
    mermaid.append("        PICKBUSY[PICKBUSY]")
    mermaid.append("        MILLBUSY[MILLBUSY]")
    mermaid.append("        DRILLBUSY[DRILLBUSY]")
    mermaid.append("        DROPBUSY[DROPBUSY]")
    mermaid.append("    end")
    mermaid.append("")
    mermaid.append("    PICK -.-> PICKBUSY")
    mermaid.append("    PROCESS -.-> MILLBUSY")
    mermaid.append("    PROCESS -.-> DRILLBUSY")
    mermaid.append("    DROP -.-> DROPBUSY")

    return '\n'.join(mermaid)


def generate_mqtt_topic_hierarchy():
    """Generate MQTT topic hierarchy diagram"""

    mermaid = []
    mermaid.append("graph TD")
    mermaid.append("    ROOT[ROOT]")
    mermaid.append("")
    mermaid.append("    subgraph \"Module Topics\"")
    mermaid.append("        MODULE[module/v1/ff/]")
    mermaid.append("        SERIAL[{serialNumber}]")
    mermaid.append("        STATE[/state]")
    mermaid.append("        ORDER[/order]")
    mermaid.append("        CONNECTION[/connection]")
    mermaid.append("        INSTANTACTION[/instantAction]")
    mermaid.append("    end")
    mermaid.append("")
    mermaid.append("    subgraph \"CCU Topics\"")
    mermaid.append("        CCU[ccu/]")
    mermaid.append("        GLOBAL[global]")
    mermaid.append("        ORDERREQ[order/request]")
    mermaid.append("        ORDERACT[order/active]")
    mermaid.append("    end")
    mermaid.append("")
    mermaid.append("    subgraph \"System Topics\"")
    mermaid.append("        SYSTEM[system/]")
    mermaid.append("        RACK[rack.positions]")
    mermaid.append("        SERIALREAD[readSerial]")
    mermaid.append("    end")
    mermaid.append("")
    mermaid.append("    ROOT --> MODULE")
    mermaid.append("    ROOT --> CCU")
    mermaid.append("    ROOT --> SYSTEM")
    mermaid.append("")
    mermaid.append("    MODULE --> SERIAL")
    mermaid.append("    SERIAL --> STATE")
    mermaid.append("    SERIAL --> ORDER")
    mermaid.append("    SERIAL --> CONNECTION")
    mermaid.append("    SERIAL --> INSTANTACTION")
    mermaid.append("")
    mermaid.append("    CCU --> GLOBAL")
    mermaid.append("    CCU --> ORDERREQ")
    mermaid.append("    CCU --> ORDERACT")
    mermaid.append("")
    mermaid.append("    SYSTEM --> RACK")
    mermaid.append("    SYSTEM --> SERIALREAD")

    return '\n'.join(mermaid)


def generate_opcua_communication_flow():
    """Generate OPC-UA communication flow diagram"""

    mermaid = []
    mermaid.append("sequenceDiagram")
    mermaid.append("    participant NR as Node-RED")
    mermaid.append("    participant OPC as OPC-UA Server")
    mermaid.append("    participant HW as Hardware Module")
    mermaid.append("")
    mermaid.append("    Note over NR,HW: Command Execution Flow")
    mermaid.append("")
    mermaid.append("    NR->>OPC: Write Command (ns=4;i=5)")
    mermaid.append("    OPC->>HW: Execute PICK Operation")
    mermaid.append("    HW->>OPC: Operation Status")
    mermaid.append("    OPC->>NR: Status Update (ns=4;i=8)")
    mermaid.append("")
    mermaid.append("    Note over NR,HW: Status Monitoring")
    mermaid.append("")
    mermaid.append("    NR->>OPC: Read Status (ns=4;i=7)")
    mermaid.append("    OPC->>HW: Get Current State")
    mermaid.append("    HW->>OPC: State Information")
    mermaid.append("    OPC->>NR: State Response")
    mermaid.append("")
    mermaid.append("    Note over NR,HW: Error Handling")
    mermaid.append("")
    mermaid.append("    HW->>OPC: Error Occurred")
    mermaid.append("    OPC->>NR: Error Status (ns=4;i=15)")
    mermaid.append("    NR->>NR: Handle Error State")

    return '\n'.join(mermaid)


def generate_system_overview():
    """Generate system overview diagram"""

    mermaid = []
    mermaid.append("graph TB")
    mermaid.append("    subgraph \"ORBIS Modellfabrik\"")
    mermaid.append("        subgraph \"Production Layer\"")
    mermaid.append("            MILL[MILL Module<br/>192.168.0.40:4840]")
    mermaid.append("            DRILL[DRILL Module<br/>192.168.0.50:4840]")
    mermaid.append("            AIQS[AIQS Module<br/>192.168.0.70:4840]")
    mermaid.append("            DPS[DPS Module<br/>192.168.0.90:4840]")
    mermaid.append("            HBW[HBW Module<br/>192.168.0.80:4840]")
    mermaid.append("        end")
    mermaid.append("")
    mermaid.append("        subgraph \"Control Layer\"")
    mermaid.append("            NODERED[Node-RED CCU<br/>192.168.0.100:1880]")
    mermaid.append("            MQTT[MQTT Broker<br/>192.168.2.189:1883]")
    mermaid.append("        end")
    mermaid.append("")
    mermaid.append("        subgraph \"Dashboard Layer\"")
    mermaid.append("            OMF[OMF Dashboard<br/>192.168.0.103]")
    mermaid.append("            WEB[Web Dashboard<br/>172.18.0.5]")
    mermaid.append("        end")
    mermaid.append("    end")
    mermaid.append("")
    mermaid.append("    %% Production to Control")
    mermaid.append("    MILL -->|OPC-UA| NODERED")
    mermaid.append("    DRILL -->|OPC-UA| NODERED")
    mermaid.append("    AIQS -->|OPC-UA| NODERED")
    mermaid.append("    DPS -->|OPC-UA| NODERED")
    mermaid.append("    HBW -->|OPC-UA| NODERED")
    mermaid.append("")
    mermaid.append("    %% Control to MQTT")
    mermaid.append("    NODERED -->|Publish| MQTT")
    mermaid.append("    NODERED -->|Subscribe| MQTT")
    mermaid.append("")
    mermaid.append("    %% Dashboard to MQTT")
    mermaid.append("    OMF -->|Commands| MQTT")
    mermaid.append("    OMF -->|Status| MQTT")
    mermaid.append("    WEB -->|Monitor| MQTT")
    mermaid.append("")
    mermaid.append("    %% MQTT to Control")
    mermaid.append("    MQTT -->|Orders| NODERED")
    mermaid.append("    MQTT -->|Status| NODERED")

    return '\n'.join(mermaid)


def generate_all_diagrams():
    """Generate all diagrams and save them"""

    diagrams = {
        'module_flow_diagram.mermaid': generate_module_flow_diagram(),
        'mqtt_topic_hierarchy.mermaid': generate_mqtt_topic_hierarchy(),
        'opcua_communication_flow.mermaid': generate_opcua_communication_flow(),
        'system_overview.mermaid': generate_system_overview(),
    }

    output_dir = Path('docs/analysis/node-red')
    output_dir.mkdir(exist_ok=True)

    for filename, content in diagrams.items():
        file_path = output_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Generated: {file_path}")

    # Create a combined diagrams file
    combined_file = output_dir / 'all_diagrams.md'
    with open(combined_file, 'w') as f:
        f.write("# Node-RED Diagrams - ORBIS Modellfabrik\n\n")

        f.write("## Module Flow Diagram\n\n")
        f.write("```mermaid\n")
        f.write(generate_module_flow_diagram())
        f.write("\n```\n\n")

        f.write("## MQTT Topic Hierarchy\n\n")
        f.write("```mermaid\n")
        f.write(generate_mqtt_topic_hierarchy())
        f.write("\n```\n\n")

        f.write("## OPC-UA Communication Flow\n\n")
        f.write("```mermaid\n")
        f.write(generate_opcua_communication_flow())
        f.write("\n```\n\n")

        f.write("## System Overview\n\n")
        f.write("```mermaid\n")
        f.write(generate_system_overview())
        f.write("\n```\n")

    print(f"Generated: {combined_file}")


def main():
    print("=== Generate Node-RED Diagrams ===")
    generate_all_diagrams()
    print("\nAll diagrams generated successfully!")


if __name__ == "__main__":
    main()
