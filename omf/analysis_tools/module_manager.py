#!/usr/bin/env python3
"""
Module Manager
Central manager for module operations using YAML configuration
Replaces module_mapping_utils.py with enhanced functionality
"""

import os
from typing import Any, Dict, List, Optional

import yaml

class ModuleManager:
    """Central Module Manager using YAML configuration"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize Module Manager with YAML configuration"""
        self.config_path = config_path or self._get_default_config_path()
        self.config = self.load_yaml_config()

        if not self.config:
            raise ValueError(f"Could not load module configuration from {self.config_path}")

    def _get_default_config_path(self) -> str:
        """Get default path to module configuration YAML file"""
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to config directory
        config_dir = os.path.join(current_dir, "../config")
        return os.path.join(config_dir, "module_config.yml")

    def load_yaml_config(self) -> Optional[Dict[str, Any]]:
        """Load module configuration from YAML file"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Module configuration file not found: {self.config_path}")
            return None
        except Exception as e:
            print(f"❌ Error loading module configuration: {e}")
            return None

    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get complete module information"""
        if not self.config:
            return None

        # Check in modules first
        if "modules" in self.config and module_id in self.config["modules"]:
            return self.config["modules"][module_id]

        # Check in transports
        if "transports" in self.config and module_id in self.config["transports"]:
            return self.config["transports"][module_id]

        return None

    def get_module_name(self, module_id: str) -> str:
        """Get module name for module ID (e.g., 'SVR3QA0022' -> 'HBW')"""
        module_info = self.get_module_info(module_id)
        return module_info.get("name", module_id) if module_info else module_id

    def get_module_name_long_en(self, module_id: str) -> str:
        """Get English long name for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("name_lang_en", module_id) if module_info else module_id

    def get_module_name_long_de(self, module_id: str) -> str:
        """Get German long name for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("name_lang_de", module_id) if module_info else module_id

    def get_module_type(self, module_id: str) -> str:
        """Get module type for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("type", "Unknown") if module_info else "Unknown"

    def get_module_ip_range(self, module_id: str) -> str:
        """Get IP range for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("ip_range", "Unknown") if module_info else "Unknown"

    def get_module_ip_addresses(self, module_id: str) -> List[str]:
        """Get all IP addresses for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("ip_addresses", []) if module_info else []

    def get_all_ip_addresses(self) -> Dict[str, List[str]]:
        """Get all IP addresses for all modules"""
        all_modules = self.get_all_modules()
        ip_addresses = {}
        for module_id, info in all_modules.items():
            ip_addresses[module_id] = info.get("ip_addresses", [])
        return ip_addresses

    def get_module_description(self, module_id: str) -> str:
        """Get description for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("description", "") if module_info else ""

    def get_module_commands(self, module_id: str) -> List[str]:
        """Get available commands for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("commands", []) if module_info else []

    def get_module_sub_type(self, module_id: str) -> str:
        """Get sub type for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("sub_type", "Unknown") if module_info else "Unknown"

    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get all modules"""
        if not self.config:
            return {}

        modules = {}
        if "modules" in self.config:
            modules.update(self.config["modules"])
        if "transports" in self.config:
            modules.update(self.config["transports"])

        return modules

    def get_modules_by_type(self, module_type: str) -> Dict[str, Dict[str, Any]]:
        """Get all modules of a specific type"""
        all_modules = self.get_all_modules()
        return {module_id: info for module_id, info in all_modules.items() if info.get("type") == module_type}

    def get_all_module_ids(self) -> List[str]:
        """Get all module IDs"""
        return list(self.get_all_modules().keys())

    def get_all_module_names(self) -> List[str]:
        """Get all module names"""
        all_modules = self.get_all_modules()
        return [info.get("name", module_id) for module_id, info in all_modules.items()]

    def is_module_id(self, value: str) -> bool:
        """Check if value is a known module ID"""
        return value in self.get_all_modules()

    def is_module_name(self, value: str) -> bool:
        """Check if value is a known module name"""
        all_modules = self.get_all_modules()
        module_names = [info.get("name") for info in all_modules.values()]
        return value in module_names

    def validate_module_id(self, module_id: str) -> bool:
        """Validate if module ID exists in configuration"""
        return self.is_module_id(module_id)

    def get_module_id_by_name(self, module_name: str) -> Optional[str]:
        """Get module ID for module name"""
        all_modules = self.get_all_modules()
        for module_id, info in all_modules.items():
            if info.get("name") == module_name:
                return module_id
        return None

    def format_module_display_name(self, module_id: str, include_id: bool = True) -> str:
        """Format module name for display (e.g., 'HBW (SVR3QA0022)')"""
        module_name = self.get_module_name(module_id)
        if include_id and module_name != module_id:
            return f"{module_name} ({module_id})"
        return module_name

    def get_module_types(self) -> List[str]:
        """Get all available module types"""
        if not self.config or "module_types" not in self.config:
            return []
        return self.config["module_types"]

    def get_commands(self) -> List[str]:
        """Get all available commands"""
        if not self.config or "commands" not in self.config:
            return []
        return self.config["commands"]

    def get_availability_status(self) -> List[str]:
        """Get all available availability status"""
        if not self.config or "availability_status" not in self.config:
            return []
        return self.config["availability_status"]

    def get_enum_values(self, enum_name: str) -> Dict[str, str]:
        """Get ENUM values for template analysis (backward compatibility)"""
        if not self.config or "enums" not in self.config:
            return {}

        # Map old enum names to new structure
        enum_mapping = {
            "workpieceTypes": "workpiece_types",
            "workpieceStates": "workpiece_states",
            "orderTypes": "order_types",
            "actionTypes": "action_types",
            "actionStates": "action_states",
            "locations": "locations",
            "commands": "commands",
            "moduleSubTypes": "module_sub_types",
        }

        new_enum_name = enum_mapping.get(enum_name, enum_name)
        return self.config["enums"].get(new_enum_name, {})

    def get_workpiece_types(self) -> Dict[str, str]:
        """Get workpiece types"""
        return self.get_enum_values("workpieceTypes")

    def get_workpiece_states(self) -> Dict[str, str]:
        """Get workpiece states"""
        return self.get_enum_values("workpieceStates")

    def get_order_types(self) -> Dict[str, str]:
        """Get order types"""
        return self.get_enum_values("orderTypes")

    def get_action_types(self) -> Dict[str, str]:
        """Get action types"""
        return self.get_enum_values("actionTypes")

    def get_action_states(self) -> Dict[str, str]:
        """Get action states"""
        return self.get_enum_values("actionStates")

    def get_locations(self) -> Dict[str, str]:
        """Get locations"""
        return self.get_enum_values("locations")

    def get_template_placeholders(self) -> Dict[str, str]:
        """Get template placeholders for modules"""
        if not self.config or "template_placeholders" not in self.config:
            return {
                "module_id": "<moduleId>",
                "module_name": "<moduleName>",
                "module_type": "<moduleType>",
                "ip_range": "<ipRange>",
            }
        return self.config["template_placeholders"]

    def get_mqtt_paths(self) -> List[List[str]]:
        """Get MQTT paths for module detection"""
        if not self.config or "mqtt_paths" not in self.config:
            return [["moduleId"], ["id"], ["source"], ["target"]]
        return self.config["mqtt_paths"]

    def get_statistics(self) -> Dict[str, Any]:
        """Get module statistics"""
        if not self.config:
            return {}

        all_modules = self.get_all_modules()
        total_modules = len(all_modules)
        type_counts = {}
        command_counts = {}

        for info in all_modules.values():
            module_type = info.get("type", "Unknown")
            commands = info.get("commands", [])

            type_counts[module_type] = type_counts.get(module_type, 0) + 1

            for command in commands:
                command_counts[command] = command_counts.get(command, 0) + 1

        return {
            "total_modules": total_modules,
            "type_counts": type_counts,
            "command_counts": command_counts,
            "module_types": list(type_counts.keys()),
            "commands": list(command_counts.keys()),
        }

    def reload_config(self) -> bool:
        """Reload configuration from YAML file"""
        new_config = self.load_yaml_config()
        if new_config:
            self.config = new_config
            return True
        return False

# Backward compatibility functions (for existing code)
def get_module_info(module_id: str) -> Optional[Dict[str, Any]]:
    """Backward compatibility function"""
    manager = ModuleManager()
    return manager.get_module_info(module_id)

def get_module_name(module_id: str) -> str:
    """Backward compatibility function"""
    manager = ModuleManager()
    return manager.get_module_name(module_id)

def get_module_type(module_id: str) -> str:
    """Backward compatibility function"""
    manager = ModuleManager()
    return manager.get_module_type(module_id)

def validate_module_id(module_id: str) -> bool:
    """Backward compatibility function"""
    manager = ModuleManager()
    return manager.validate_module_id(module_id)

# Create global instance for easy access
_module_manager = None

def get_module_manager() -> ModuleManager:
    """Get global module manager instance"""
    global _module_manager
    if _module_manager is None:
        _module_manager = ModuleManager()
    return _module_manager

if __name__ == "__main__":
    """Test the Module Manager"""
    manager = ModuleManager()

    print("🔧 Module Manager Test")
    print("=" * 50)

    # Test basic functionality
    print(f"📋 Total Modules: {len(manager.get_all_modules())}")
    print(f"🏭 Processing Modules: {len(manager.get_modules_by_type('Processing'))}")
    print(f"📦 Storage Modules: {len(manager.get_modules_by_type('Storage'))}")
    print(f"🔍 Quality-Control Modules: {len(manager.get_modules_by_type('Quality-Control'))}")

    # Test module info
    test_module_id = "SVR3QA0022"
    module_info = manager.get_module_info(test_module_id)
    print(f"📋 Module {test_module_id}: {module_info}")

    # Test name conversion
    module_name = manager.get_module_name(test_module_id)
    print(f"📋 Module Name: {test_module_id} -> {module_name}")

    # Test reverse conversion
    module_id = manager.get_module_id_by_name(module_name)
    print(f"📋 Module ID: {module_name} -> {module_id}")

    # Test statistics
    stats = manager.get_statistics()
    print(f"📊 Statistics: {stats}")

    print("✅ Module Manager test completed")
