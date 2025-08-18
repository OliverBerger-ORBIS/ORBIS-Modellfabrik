#!/usr/bin/env python3
"""
MQTT Message Library - Fischertechnik APS
Library of working MQTT messages for remote control
"""

import json
import uuid
from typing import Dict, List, Any

class MQTTMessageLibrary:
    """Library of working MQTT messages for APS modules"""
    
    # APS Module Configuration
    APS_MODULES = {
        "MILL": {
            "serial": "SVR3QA2098",
            "ip": "192.168.0.40",
            "working_commands": ["PICK", "DROP"]  # MILL command not supported directly
        },
        "DRILL": {
            "serial": "SVR4H76449", 
            "ip": "192.168.0.50",
            "working_commands": ["PICK", "DROP"]  # DRILL command not supported directly
        },
        "AIQS": {
            "serial": "SVR4H76530",
            "ip": "192.168.0.70",
            "working_commands": ["PICK", "DROP", "CHECK_QUALITY"]
        },
        "HBW": {
            "serial": "SVR3QA0022",
            "ip": "192.168.0.80",
            "working_commands": ["PICK", "DROP", "STORE"]
        },
        "DPS": {
            "serial": "SVR4H73275",
            "ip": "192.168.0.90",
            "working_commands": ["PICK", "DROP"]
        }
    }
    
    @staticmethod
    def create_order_message(module_name: str, command: str, metadata: dict = None) -> Dict[str, Any]:
        """Create a working order message for a module"""
        if module_name not in MQTTMessageLibrary.APS_MODULES:
            raise ValueError(f"Unknown module: {module_name}")
        
        config = MQTTMessageLibrary.APS_MODULES[module_name]
        
        if command not in config["working_commands"]:
            raise ValueError(f"Command '{command}' not supported for module '{module_name}'")
        
        if metadata is None:
            metadata = {
                "priority": "NORMAL",
                "timeout": 300
            }
        
        # Add type parameter for PICK/DROP commands
        if command in ["PICK", "DROP"] and "type" not in metadata:
            metadata["type"] = "WHITE"
        
        order_data = {
            "serialNumber": config["serial"],
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": 1,
            "action": {
                "id": str(uuid.uuid4()),
                "command": command,
                "metadata": metadata
            }
        }
        
        return order_data
    
    @staticmethod
    def create_instant_action_message(module_name: str, action_type: str, metadata: dict = None) -> Dict[str, Any]:
        """Create an instant action message for a module"""
        if module_name not in MQTTMessageLibrary.APS_MODULES:
            raise ValueError(f"Unknown module: {module_name}")
        
        config = MQTTMessageLibrary.APS_MODULES[module_name]
        
        if metadata is None:
            metadata = {}
        
        action_data = {
            "serialNumber": config["serial"],
            "orderId": str(uuid.uuid4()),
            "orderUpdateId": 1,
            "actions": [
                {
                    "actionId": str(uuid.uuid4()),
                    "actionType": action_type,
                    "metadata": metadata
                }
            ]
        }
        
        return action_data
    
    @staticmethod
    def get_working_commands(module_name: str) -> List[str]:
        """Get list of working commands for a module"""
        if module_name not in MQTTMessageLibrary.APS_MODULES:
            return []
        
        return MQTTMessageLibrary.APS_MODULES[module_name]["working_commands"]
    
    @staticmethod
    def get_module_info(module_name: str) -> Dict[str, Any]:
        """Get module information"""
        if module_name not in MQTTMessageLibrary.APS_MODULES:
            return {}
        
        return MQTTMessageLibrary.APS_MODULES[module_name]
    
    @staticmethod
    def list_all_modules() -> List[str]:
        """List all available modules"""
        return list(MQTTMessageLibrary.APS_MODULES.keys())
    
    @staticmethod
    def get_topic(module_name: str, message_type: str = "order") -> str:
        """Get MQTT topic for a module and message type"""
        if module_name not in MQTTMessageLibrary.APS_MODULES:
            raise ValueError(f"Unknown module: {module_name}")
        
        config = MQTTMessageLibrary.APS_MODULES[module_name]
        serial_number = config["serial"]
        
        if message_type == "order":
            return f"module/v1/ff/{serial_number}/order"
        elif message_type == "instantAction":
            return f"module/v1/ff/{serial_number}/instantAction"
        elif message_type == "state":
            return f"module/v1/ff/{serial_number}/state"
        else:
            raise ValueError(f"Unknown message type: {message_type}")

# Pre-defined working message templates
WORKING_MESSAGE_TEMPLATES = {
    "DRILL_PICK_WHITE": {
        "description": "DRILL module PICK command for WHITE workpiece",
        "module": "DRILL",
        "command": "PICK",
        "metadata": {
            "priority": "NORMAL",
            "timeout": 300,
            "type": "WHITE"
        },
        "expected_response": "RUNNING",
        "notes": "Successfully tested - module accepts PICK command"
    },
    "DRILL_DROP_WHITE": {
        "description": "DRILL module DROP command for WHITE workpiece",
        "module": "DRILL",
        "command": "DROP",
        "metadata": {
            "priority": "NORMAL",
            "timeout": 300,
            "type": "WHITE"
        },
        "expected_response": "RUNNING",
        "notes": "Should work but may need valid orderId"
    },
    "MILL_PICK_WHITE": {
        "description": "MILL module PICK command for WHITE workpiece",
        "module": "MILL",
        "command": "PICK",
        "metadata": {
            "priority": "NORMAL",
            "timeout": 300,
            "type": "WHITE"
        },
        "expected_response": "RUNNING",
        "notes": "Expected to work based on module capabilities"
    },
    "HBW_STORE_WHITE": {
        "description": "HBW module STORE command for WHITE workpiece",
        "module": "HBW",
        "command": "STORE",
        "metadata": {
            "priority": "NORMAL",
            "timeout": 300,
            "type": "WHITE"
        },
        "expected_response": "RUNNING",
        "notes": "Expected to work based on module capabilities"
    },
    "AIQS_CHECK_QUALITY_WHITE": {
        "description": "AIQS module CHECK_QUALITY command for WHITE workpiece",
        "module": "AIQS",
        "command": "CHECK_QUALITY",
        "metadata": {
            "priority": "NORMAL",
            "timeout": 300,
            "type": "WHITE"
        },
        "expected_response": "RUNNING",
        "notes": "Expected to work based on module capabilities"
    }
}

def create_message_from_template(template_name: str) -> Dict[str, Any]:
    """Create a message from a pre-defined template"""
    if template_name not in WORKING_MESSAGE_TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}")
    
    template = WORKING_MESSAGE_TEMPLATES[template_name]
    return MQTTMessageLibrary.create_order_message(
        template["module"],
        template["command"],
        template["metadata"]
    )

def list_available_templates() -> List[str]:
    """List all available message templates"""
    return list(WORKING_MESSAGE_TEMPLATES.keys())

def get_template_info(template_name: str) -> Dict[str, Any]:
    """Get information about a message template"""
    if template_name not in WORKING_MESSAGE_TEMPLATES:
        return {}
    
    return WORKING_MESSAGE_TEMPLATES[template_name]

# Example usage functions
def example_usage():
    """Example usage of the MQTT Message Library"""
    print("🔧 MQTT Message Library - Example Usage")
    print("=" * 50)
    
    # List all modules
    modules = MQTTMessageLibrary.list_all_modules()
    print(f"Available modules: {', '.join(modules)}")
    
    # Create a working message
    try:
        message = MQTTMessageLibrary.create_order_message("DRILL", "PICK")
        print(f"\n✅ Working DRILL PICK message:")
        print(json.dumps(message, indent=2))
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # Use a template
    try:
        template_message = create_message_from_template("DRILL_PICK_WHITE")
        print(f"\n✅ Template message:")
        print(json.dumps(template_message, indent=2))
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # Get topic
    try:
        topic = MQTTMessageLibrary.get_topic("DRILL", "order")
        print(f"\n📡 MQTT Topic: {topic}")
    except ValueError as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    example_usage()
