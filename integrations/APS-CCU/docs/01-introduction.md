# 1. Introduction

## 1.1 Purpose of this Documentation

This documentation provides comprehensive information about the MQTT protocol interface of the fischertechnik Agile Production Simulation (APS) 24V system. Its primary goals are:

- **Enable Customer Independence**: Empower end customers to independently control and interact with the factory at the MQTT level
- **Facilitate Integration**: Provide all necessary information for integrating external systems with the factory
- **Support Development**: Serve as a technical reference for developers working with the factory's communication layer
- **Document Protocol Details**: Clearly explain the modified VDA5050 protocol implementation used in the system

### Target Audience

This documentation is intended for:
- Software developers integrating with the APS
- System integrators connecting external systems
- Technical personnel implementing custom control logic
- Engineers extending the factory's capabilities

## 1.2 Basic Concepts

### Communication Architecture (MQTT & OPC UA)

The system is built on a layered communication architecture:

1.  **MQTT (Public Interface)**: The primary interface for external control and integration. This documentation focuses on this layer.
2.  **OPC UA (Internal Control)**: Used internally between the factory's PLCs (Simatic S7) and the gateway software. This low-level industrial communication is abstracted away, allowing integrators to work purely with the lightweight MQTT protocol.

### MQTT Basics

**MQTT** (Message Queuing Telemetry Transport) is a publish-subscribe messaging transport. We utilize specific features to ensure robust factory automation:

- **Publish-Subscribe Pattern**: Decouples devices. Modules **publish** their status, while the Central Control Unit (CCU) **subscribes** to them to monitor the factory. Conversely, the CCU publishes orders that modules subscribe to.
- **Quality of Service (QoS)**: High QoS levels (1 and 2) are used to guarantee command delivery, ensuring no production orders are lost.
- **Retained Messages**: Used for device states, ensuring that any system checking the factory immediately receives the last known status without waiting for an update.

#### Topics

Topics are hierarchical strings separated by forward slashes (`/`), for example:
- `module/v1/ff/MILL001/state` - State updates from the milling module
- `fts/v1/ff/AGV001/order` - Navigation orders for a specific AGV
- `ccu/order/request` - Topic for requesting new production orders

This follows a strict command-response pattern where `order` topics drive changes reflected in `state` topics.

### The VDA5050 Standard

This factory implementation is based on **VDA5050**, a standardized interface originally designed for automated guided vehicles (AGVs) by the German Association of the Automotive Industry.

While VDA5050 is traditionally used only for transport robots, the APS extends these principles to the entire factory floor. We use the standard's robust state management, JSON message structures, and action-based control logic for all static production modules (milling, drilling, etc.) as well. This provides a unified communication interface where a milling machine is controlled using the same structural logic as a transport vehicle.

Specific extensions (custom actions like `DRILL` or `CHECK_QUALITY`, and additional topics for stock management) have been added to cover non-logistical manufacturing tasks, while preserving compatibility with standard VDA5050 tools where possible.

### Communication Flow Overview

1. **Order Creation**: An external system or frontend sends an order request to the CCU
2. **Order Planning**: The CCU generates a production plan with individual steps
3. **Command Distribution**: The CCU sends commands to modules and AGV
4. **State Monitoring**: Devices continuously publish their state
5. **Action Execution**: Modules execute actions and report progress
6. **Order Completion**: The CCU tracks completion and updates order status

## Next Steps

- Continue to [System Architecture](02-architecture.md) for an overview of the factory's communication structure
- Jump to [Message Structure](05-message-structure.md) for technical details on message formats
- See [Module-Specific Documentation](06-modules.md) for detailed command examples
