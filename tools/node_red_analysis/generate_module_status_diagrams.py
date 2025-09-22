#!/usr/bin/env python3
"""
Generate module status transition diagrams for Fischertechnik APS
"""


def generate_mill_status_diagram():
    """Generate MILL module status transition diagram"""

    mermaid = []
    mermaid.append("stateDiagram-v2")
    mermaid.append("    [*] --> IDLE")
    mermaid.append("")
    mermaid.append("    %% MILL Module Status Transitions")
    mermaid.append("    IDLE -->|PICK Command| PICKBUSY")
    mermaid.append("    PICKBUSY -->|PICK Complete| WAITING_AFTER_PICK")
    mermaid.append("    WAITING_AFTER_PICK -->|MILL Command| MILLBUSY")
    mermaid.append("    MILLBUSY -->|MILL Complete| WAITING_AFTER_MILL")
    mermaid.append("    WAITING_AFTER_MILL -->|DROP Command| DROPBUSY")
    mermaid.append("    DROPBUSY -->|DROP Complete| IDLE")
    mermaid.append("")
    mermaid.append("    %% Error States")
    mermaid.append("    PICKBUSY -->|Error| FAILED")
    mermaid.append("    MILLBUSY -->|Error| FAILED")
    mermaid.append("    DROPBUSY -->|Error| FAILED")
    mermaid.append("    FAILED -->|Reset| IDLE")
    mermaid.append("")
    mermaid.append("    %% Calibration")
    mermaid.append("    IDLE -->|Calibration| CALIBRATION")
    mermaid.append("    CALIBRATION -->|Complete| IDLE")

    return '\n'.join(mermaid)


def generate_drill_status_diagram():
    """Generate DRILL module status transition diagram"""

    mermaid = []
    mermaid.append("stateDiagram-v2")
    mermaid.append("    [*] --> IDLE")
    mermaid.append("")
    mermaid.append("    %% DRILL Module Status Transitions")
    mermaid.append("    IDLE -->|PICK Command| PICKBUSY")
    mermaid.append("    PICKBUSY -->|PICK Complete| WAITING_AFTER_PICK")
    mermaid.append("    WAITING_AFTER_PICK -->|DRILL Command| DRILLBUSY")
    mermaid.append("    DRILLBUSY -->|DRILL Complete| WAITING_AFTER_DRILL")
    mermaid.append("    WAITING_AFTER_DRILL -->|DROP Command| DROPBUSY")
    mermaid.append("    DROPBUSY -->|DROP Complete| IDLE")
    mermaid.append("")
    mermaid.append("    %% Error States")
    mermaid.append("    PICKBUSY -->|Error| FAILED")
    mermaid.append("    DRILLBUSY -->|Error| FAILED")
    mermaid.append("    DROPBUSY -->|Error| FAILED")
    mermaid.append("    FAILED -->|Reset| IDLE")
    mermaid.append("")
    mermaid.append("    %% Calibration")
    mermaid.append("    IDLE -->|Calibration| CALIBRATION")
    mermaid.append("    CALIBRATION -->|Complete| IDLE")

    return '\n'.join(mermaid)


def generate_aiqs_status_diagram():
    """Generate AIQS module status transition diagram"""

    mermaid = []
    mermaid.append("stateDiagram-v2")
    mermaid.append("    [*] --> IDLE")
    mermaid.append("")
    mermaid.append("    %% AIQS Module Status Transitions")
    mermaid.append("    IDLE -->|PICK Command| PICKBUSY")
    mermaid.append("    PICKBUSY -->|PICK Complete| WAITING_AFTER_PICK")
    mermaid.append("    WAITING_AFTER_PICK -->|FIRE Command| FIREBUSY")
    mermaid.append("    FIREBUSY -->|FIRE Complete| WAITING_AFTER_FIRE")
    mermaid.append("    WAITING_AFTER_FIRE -->|DROP Command| DROPBUSY")
    mermaid.append("    DROPBUSY -->|DROP Complete| IDLE")
    mermaid.append("")
    mermaid.append("    %% Error States")
    mermaid.append("    PICKBUSY -->|Error| FAILED")
    mermaid.append("    FIREBUSY -->|Error| FAILED")
    mermaid.append("    DROPBUSY -->|Error| FAILED")
    mermaid.append("    FAILED -->|Reset| IDLE")
    mermaid.append("")
    mermaid.append("    %% Calibration")
    mermaid.append("    IDLE -->|Calibration| CALIBRATION")
    mermaid.append("    CALIBRATION -->|Complete| IDLE")

    return '\n'.join(mermaid)


def generate_dps_status_diagram():
    """Generate DPS module status transition diagram"""

    mermaid = []
    mermaid.append("stateDiagram-v2")
    mermaid.append("    [*] --> IDLE")
    mermaid.append("")
    mermaid.append("    %% DPS Module Status Transitions")
    mermaid.append("    IDLE -->|PICK Command| PICKBUSY")
    mermaid.append("    PICKBUSY -->|PICK Complete| WAITING")
    mermaid.append("    WAITING -->|DROP Command| DROPBUSY")
    mermaid.append("    DROPBUSY -->|DROP Complete| IDLE")
    mermaid.append("")
    mermaid.append("    %% Error States")
    mermaid.append("    PICKBUSY -->|Error| FAILED")
    mermaid.append("    DROPBUSY -->|Error| FAILED")
    mermaid.append("    FAILED -->|Reset| IDLE")
    mermaid.append("")
    mermaid.append("    %% Calibration")
    mermaid.append("    IDLE -->|Calibration| CALIBRATION")
    mermaid.append("    CALIBRATION -->|Complete| IDLE")

    return '\n'.join(mermaid)


def generate_hbw_status_diagram():
    """Generate HBW module status transition diagram"""

    mermaid = []
    mermaid.append("stateDiagram-v2")
    mermaid.append("    [*] --> IDLE")
    mermaid.append("")
    mermaid.append("    %% HBW Module Status Transitions")
    mermaid.append("    IDLE -->|PICK Command| PICKBUSY")
    mermaid.append("    PICKBUSY -->|PICK Complete| WAITING")
    mermaid.append("    WAITING -->|DROP Command| DROPBUSY")
    mermaid.append("    DROPBUSY -->|DROP Complete| IDLE")
    mermaid.append("")
    mermaid.append("    %% Error States")
    mermaid.append("    PICKBUSY -->|Error| FAILED")
    mermaid.append("    DROPBUSY -->|Error| FAILED")
    mermaid.append("    FAILED -->|Reset| IDLE")
    mermaid.append("")
    mermaid.append("    %% Calibration")
    mermaid.append("    IDLE -->|Calibration| CALIBRATION")
    mermaid.append("    CALIBRATION -->|Complete| IDLE")

    return '\n'.join(mermaid)


def generate_oven_status_diagram():
    """Generate OVEN module status transition diagram"""

    mermaid = []
    mermaid.append("stateDiagram-v2")
    mermaid.append("    [*] --> IDLE")
    mermaid.append("")
    mermaid.append("    %% OVEN Module Status Transitions")
    mermaid.append("    IDLE -->|PICK Command| PICKBUSY")
    mermaid.append("    PICKBUSY -->|PICK Complete| WAITING_AFTER_PICK")
    mermaid.append("    WAITING_AFTER_PICK -->|FIRE Command| FIREBUSY")
    mermaid.append("    FIREBUSY -->|FIRE Complete| WAITING_AFTER_FIRE")
    mermaid.append("    WAITING_AFTER_FIRE -->|DROP Command| DROPBUSY")
    mermaid.append("    DROPBUSY -->|DROP Complete| IDLE")
    mermaid.append("")
    mermaid.append("    %% Error States")
    mermaid.append("    PICKBUSY -->|Error| FAILED")
    mermaid.append("    FIREBUSY -->|Error| FAILED")
    mermaid.append("    DROPBUSY -->|Error| FAILED")
    mermaid.append("    FAILED -->|Reset| IDLE")
    mermaid.append("")
    mermaid.append("    %% Calibration")
    mermaid.append("    IDLE -->|Calibration| CALIBRATION")
    mermaid.append("    CALIBRATION -->|Complete| IDLE")

    return '\n'.join(mermaid)


def generate_production_flow_diagram():
    """Generate overall production flow diagram"""

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


def generate_system_architecture_diagram():
    """Generate system architecture diagram"""

    mermaid = []
    mermaid.append("graph TB")
    mermaid.append("    subgraph \"Fischertechnik APS System\"")
    mermaid.append("        subgraph \"Production Layer\"")
    mermaid.append("            MILL[MILL Module<br/>192.168.0.40:4840]")
    mermaid.append("            DRILL[DRILL Module<br/>192.168.0.50:4840]")
    mermaid.append("            AIQS[AIQS Module<br/>192.168.0.70:4840]")
    mermaid.append("            DPS[DPS Module<br/>192.168.0.90:4840]")
    mermaid.append("            HBW[HBW Module<br/>192.168.0.80:4840]")
    mermaid.append("            OVEN[OVEN Module<br/>192.168.0.60:4840]")
    mermaid.append("        end")
    mermaid.append("")
    mermaid.append("        subgraph \"Control Layer\"")
    mermaid.append("            CCU[Central Control Unit<br/>Node-RED<br/>192.168.0.100:1880]")
    mermaid.append("            MQTT[MQTT Broker<br/>192.168.2.189:1883]")
    mermaid.append("        end")
    mermaid.append("")
    mermaid.append("        subgraph \"Network Layer\"")
    mermaid.append("            SWITCH[Network Switch<br/>192.168.0.1]")
    mermaid.append("            ROUTER[Router<br/>192.168.2.1]")
    mermaid.append("        end")
    mermaid.append("    end")
    mermaid.append("")
    mermaid.append("    %% Production to Control")
    mermaid.append("    MILL -->|OPC-UA| CCU")
    mermaid.append("    DRILL -->|OPC-UA| CCU")
    mermaid.append("    AIQS -->|OPC-UA| CCU")
    mermaid.append("    DPS -->|OPC-UA| CCU")
    mermaid.append("    HBW -->|OPC-UA| CCU")
    mermaid.append("    OVEN -->|OPC-UA| CCU")
    mermaid.append("")
    mermaid.append("    %% Control to MQTT")
    mermaid.append("    CCU -->|Publish/Subscribe| MQTT")
    mermaid.append("")
    mermaid.append("    %% Network connections")
    mermaid.append("    CCU --> SWITCH")
    mermaid.append("    MILL --> SWITCH")
    mermaid.append("    DRILL --> SWITCH")
    mermaid.append("    AIQS --> SWITCH")
    mermaid.append("    DPS --> SWITCH")
    mermaid.append("    HBW --> SWITCH")
    mermaid.append("    OVEN --> SWITCH")
    mermaid.append("")
    mermaid.append("    SWITCH --> ROUTER")
    mermaid.append("    ROUTER --> MQTT")

    return '\n'.join(mermaid)


def generate_opcua_communication_diagram():
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


def generate_mqtt_topic_hierarchy_diagram():
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


def main():
    """Generate all diagrams and save them"""

    diagrams = {
        'mill_status_diagram.mermaid': generate_mill_status_diagram(),
        'drill_status_diagram.mermaid': generate_drill_status_diagram(),
        'aiqs_status_diagram.mermaid': generate_aiqs_status_diagram(),
        'dps_status_diagram.mermaid': generate_dps_status_diagram(),
        'hbw_status_diagram.mermaid': generate_hbw_status_diagram(),
        'oven_status_diagram.mermaid': generate_oven_status_diagram(),
        'production_flow_diagram.mermaid': generate_production_flow_diagram(),
        'system_architecture_diagram.mermaid': generate_system_architecture_diagram(),
        'opcua_communication_diagram.mermaid': generate_opcua_communication_diagram(),
        'mqtt_topic_hierarchy_diagram.mermaid': generate_mqtt_topic_hierarchy_diagram(),
    }

    output_dir = Path('docs/analysis/node-red/aps_docs')
    output_dir.mkdir(exist_ok=True)

    for filename, content in diagrams.items():
        file_path = output_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Generated: {file_path}")

    print(f"\nAll module status diagrams generated in: {output_dir}")


if __name__ == "__main__":
    from pathlib import Path

    main()
