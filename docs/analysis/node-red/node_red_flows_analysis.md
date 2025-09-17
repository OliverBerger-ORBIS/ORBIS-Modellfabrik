# Node-RED Flows Analysis

## Overview
Analysis of Node-RED flows from the Fischertechnik factory system running on Raspberry Pi (192.168.0.100).

## System Architecture

### Total Components
- **25 Tabs (Flows)**: Each representing a different module or system component
- **1,403 Nodes**: Total nodes across all flows
- **24 OPC-UA Connectors**: Connecting to various hardware modules
- **13 MQTT Nodes**: For message communication

### Module Categories

#### Processing Modules
- **MILL**: 5 instances (MILL #1-5)
  - IPs: 192.168.0.40-44
  - OPC-UA endpoints on port 4840
- **DRILL**: 5 instances (DRILL #1-5)
  - IPs: 192.168.0.50-54
  - OPC-UA endpoints on port 4840
- **OVEN**: 5 instances (OVEN #1-5)
  - IPs: 192.168.0.60-64
  - OPC-UA endpoints on port 4840
- **AIQS**: 5 instances (AIQS #1-5)
  - IPs: 192.168.0.70-74
  - OPC-UA endpoints on port 4840

#### Storage & Transport
- **HBW**: 3 instances (HBW #1-3)
  - IPs: 192.168.0.80-82
  - OPC-UA endpoints on port 4840
- **DPS**: 1 instance
  - IP: 192.168.0.90
  - OPC-UA endpoint on port 4840

## Node Types Distribution

| Node Type | Count | Purpose |
|-----------|-------|---------|
| function | 402 | Business logic implementation |
| debug | 226 | Debugging and logging |
| change | 91 | Data transformation |
| link out | 84 | Flow connections |
| OPCUA-IIoT-Inject | 72 | OPC-UA data injection |
| switch | 66 | Conditional routing |
| OPCUA-IIoT-Write | 55 | Writing to OPC-UA servers |
| OPCUA-IIoT-Read | 48 | Reading from OPC-UA servers |
| catch | 31 | Error handling |
| subflow | 53 | Reusable flow components |
| group | 26 | Node grouping |
| OPCUA-IIoT-Connector | 24 | OPC-UA connections |
| delay | 24 | Timing control |
| OPCUA-IIoT-Listener | 24 | OPC-UA event listening |

## MQTT Communication

### Topics Identified
- `/j1/txt/1/o/ptu` - TXT controller communication
- `ccu/global` - Central control unit global commands
- `rack.positions` - Rack position management
- `readSerial` - Serial number reading

### MQTT Nodes
- **Lokal_MQTT**: Main MQTT broker connection
- **dynamic Connection**: Dynamic MQTT topic handling
- **mqtt retained**: Publishing with retention
- **mqtt not retained**: Publishing without retention
- **global-reset**: Global reset functionality

## OPC-UA Connections

### Hardware Module Mapping
| Module | IP Address | Purpose |
|--------|------------|---------|
| MILL_OPCUA | 192.168.0.40 | Milling machine #1 |
| MILL2_OPCUA | 192.168.0.41 | Milling machine #2 |
| MILL3_OPCUA | 192.168.0.42 | Milling machine #3 |
| MILL4_OPCUA | 192.168.0.43 | Milling machine #4 |
| MILL5_OPCUA | 192.168.0.44 | Milling machine #5 |
| DRILL1_OPCUA | 192.168.0.50 | Drill machine #1 |
| DRILL2_OPCUA | 192.168.0.51 | Drill machine #2 |
| DRILL3_OPCUA | 192.168.0.52 | Drill machine #3 |
| DRILL4_OPCUA | 192.168.0.53 | Drill machine #4 |
| DRILL5_OPCUA | 192.168.0.54 | Drill machine #5 |
| OVEN1_OPCUA | 192.168.0.60 | Oven #1 |
| OVEN2_OPCUA | 192.168.0.61 | Oven #2 |
| OVEN3_OPCUA | 192.168.0.62 | Oven #3 |
| OVEN4_OPCUA | 192.168.0.63 | Oven #4 |
| OVEN5_OPCUA | 192.168.0.64 | Oven #5 |
| AIQS1_OPCUA | 192.168.0.70 | AI Quality System #1 |
| AIQS2_OPCUA | 192.168.0.71 | AI Quality System #2 |
| AIQS3_OPCUA | 192.168.0.72 | AI Quality System #3 |
| AIQS4_OPCUA | 192.168.0.73 | AI Quality System #4 |
| AIQS5_OPCUA | 192.168.0.74 | AI Quality System #5 |
| HBW1_OPCUA | 192.168.0.80 | High Bay Warehouse #1 |
| HBW2_OPCUA | 192.168.0.81 | High Bay Warehouse #2 |
| HBW3_OPCUA | 192.168.0.82 | High Bay Warehouse #3 |
| DPS_OPCUA | 192.168.0.90 | Distribution and Picking Station |

## Key Function Nodes

### Connection Management
- **connection state**: Manages module connection states
- **sub order**: Subscribes to order topics
- **sub instantAction**: Subscribes to instant action topics
- **leere state**: Handles empty state conditions

### Data Processing
- **factsheet Update**: Updates module factsheets
- **global-reset**: Handles global reset operations

## Flow Structure

### Tab Organization
Each module type has its own tab with:
- OPC-UA connector for hardware communication
- MQTT nodes for message handling
- Function nodes for business logic
- Debug nodes for monitoring
- Switch nodes for conditional processing

### Subflows
- **ea935d7649fccac4**: 27 instances (likely common functionality)
- **fb6b02d4d9963179**: 26 instances (likely common functionality)

## Business Logic Patterns

### Module Communication
1. **OPC-UA Connection**: Each module connects to its hardware via OPC-UA
2. **MQTT Publishing**: Module status and data published to MQTT topics
3. **Dynamic Topics**: Topics are dynamically constructed based on module configuration
4. **State Management**: Connection states and module states are tracked

### Order Processing
- **Order Handling**: Each module has an "Order Handling" function that processes incoming orders
- **Order ID Management**: Orders are tracked by `orderId` and `orderUpdateId`
- **Module State Machine**: Each module follows a state machine pattern:
  - `IDLE` → `PICKBUSY` → `PROCESSING` → `DROPBUSY` → `IDLE`
- **VDA Status Updates**: Modules publish status updates using VDA (Verband der Automobilindustrie) standards

### Module-Specific Processing

#### Processing Modules (MILL, DRILL, OVEN)
- **Common Pattern**: PICK → PROCESS → DROP
- **State Transitions**:
  - `IDLE` → `PICKBUSY` (when order received)
  - `PICKBUSY` → `PROCESSING` (when pick completed)
  - `PROCESSING` → `DROPBUSY` (when processing completed)
  - `DROPBUSY` → `IDLE` (when drop completed)

#### AIQS (AI Quality System)
- **Extended Pattern**: PICK → CHECK_QUALITY → DROP
- **State Transitions**:
  - `IDLE` → `RPICK` (Running Pick)
  - `RPICK` → `WCQ` (Waiting Check Quality)
  - `WCQ` → `RCQ` (Running Check Quality)
  - `RCQ` → `WDROP` (Waiting Drop)
  - `WDROP` → `RDROP` (Running Drop)
  - `RDROP` → `IDLE`

#### HBW (High Bay Warehouse)
- **Storage Operations**: PICK, DROP, Calibration
- **Calibration Functions**: `startCalibration`, `stopCalibration`, `setCalibrationValues`
- **Factsheet Management**: `factsheetRequest` for module information

#### DPS (Distribution and Picking Station)
- **Complex Operations**: Multiple calibration and error handling functions
- **Error Management**: Comprehensive error tracking and reporting

### State Management
- **Flow Variables**: Each module maintains state in Node-RED flow variables
- **Key Variables**:
  - `moduleState`: Current operational state
  - `orderId`: Current order being processed
  - `orderUpdateId`: Order update counter
  - `loads`: Array of workpieces/loads
  - `headerId`: Message header identifier
  - `actionState`: Current action state

### Error Handling
- Catch nodes for error handling
- Debug nodes for monitoring
- State validation and recovery
- Error logging and reporting

## Integration Points

### MQTT Broker
- Local MQTT broker for internal communication
- Topics for module communication and control
- Global reset and control commands

### OPC-UA Servers
- Each hardware module runs an OPC-UA server
- Standard port 4840 for all connections
- Read/Write operations for control and monitoring

### External Systems
- TXT controllers for order initiation
- Central Control Unit (CCU) for coordination
- Frontend for monitoring and control

## Visual Documentation

### State Machine Diagrams
- **Module State Machine**: `module_state_machine.mermaid` - Shows the basic state machine pattern for processing modules
- **AIQS State Machine**: `aiqs_state_machine.mermaid` - Shows the extended state machine for AI Quality System modules

### Architecture Diagrams
- **Node-RED Architecture**: `nodered_architecture.mermaid` - Shows the overall system architecture with all modules and connections
- **Order Processing Flow**: `order_processing_flow.mermaid` - Shows the sequence of operations for order processing

## Key Insights

### Module Patterns
1. **Standardized Structure**: All modules follow a consistent pattern with 9 function nodes
2. **State Machine Implementation**: Each module implements a state machine for operational control
3. **OPC-UA Integration**: Direct hardware control through OPC-UA servers
4. **MQTT Communication**: Status updates and control commands via MQTT

### Order Processing
1. **Order ID Management**: Orders are tracked with `orderId` and `orderUpdateId`
2. **State Transitions**: Clear state transitions for each operational phase
3. **VDA Compliance**: Status updates follow VDA standards for automotive industry
4. **Error Handling**: Comprehensive error tracking and recovery mechanisms

### Integration Points
1. **TXT Controllers**: Order initiation and status monitoring
2. **Central Control Unit**: Order coordination and distribution
3. **OPC-UA Servers**: Hardware control and monitoring
4. **MQTT Broker**: Message routing and communication

## Recommendations

### For OMF Integration
1. **MQTT Topics**: Map existing topics to OMF message templates
2. **OPC-UA Integration**: Consider OPC-UA connectivity for hardware control
3. **State Management**: Implement similar state tracking mechanisms
4. **Error Handling**: Adopt similar error handling patterns
5. **VDA Compliance**: Maintain VDA standards for status reporting

### For Documentation
1. **Flow Diagrams**: Visual representations created in Mermaid format
2. **Topic Mapping**: Document MQTT topic usage patterns
3. **Module Interfaces**: Document OPC-UA interface specifications
4. **Business Logic**: Document key function node implementations
5. **State Machines**: Document module state machine patterns
