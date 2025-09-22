"""
OMF Module Manager
Central manager for module operations using YAML configuration
Version: 3.0.0
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class OmfModuleManager:
    def get_all_module_ids(self) -> list:
        """Get all module IDs (keys) from all modules."""
        return list(self.get_all_modules().keys())

    """OMF Module Manager using YAML configuration"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize OMF Module Manager with YAML configuration"""
        self.config_path = config_path or self._get_default_config_path()
        self.config = self.load_yaml_config()

        # If no config found, try to use registry v1 as fallback
        if not self.config:
            try:
                from .registry_manager import get_registry

                registry = get_registry()
                modules_data = registry.modules()
                if modules_data:
                    self.config = modules_data
                    print("✅ Using registry v1 modules as fallback")
                    return
            except Exception as e:
                print(f"⚠️ Registry v1 fallback failed: {e}")

            raise ValueError(f"Could not load module configuration from {self.config_path}")

    def _get_default_config_path(self) -> str:
        """Get default path to module configuration YAML file"""
        # Projekt-Root-relative Pfade verwenden
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent

        # Registry v1 (primary)
        registry_path = project_root / "registry" / "model" / "v1" / "modules.yml"
        if registry_path.exists():
            print(f"✅ Using registry v1: {registry_path}")
            return str(registry_path)

        # Fallback to legacy config (deprecated)
        legacy_path = project_root / "omf" / "config" / "module_config.yml"
        print("⚠️ Using deprecated module_config.yml - consider migrating to registry/model/v0/modules.yml")
        return str(legacy_path.resolve())

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

        # Registry v1 format (modules as array)
        if "modules" in self.config and isinstance(self.config["modules"], list):
            for module in self.config["modules"]:
                if module.get("serial") == module_id or module.get("id") == module_id:
                    return module

        # Registry v1 format (transports as array)
        if "transports" in self.config and isinstance(self.config["transports"], list):
            for transport in self.config["transports"]:
                if transport.get("serial") == module_id or transport.get("id") == module_id:
                    return transport

        # Legacy format (modules as dict)
        if (
            "modules" in self.config
            and isinstance(self.config["modules"], dict)
            and module_id in self.config["modules"]
        ):
            return self.config["modules"][module_id]

        # Legacy format (transports as dict)
        if (
            "transports" in self.config
            and isinstance(self.config["transports"], dict)
            and module_id in self.config["transports"]
        ):
            return self.config["transports"][module_id]

        return None

    def get_module_name(self, module_id: str, language: str = "de") -> str:
        """Get module short name for module ID (immer 'name' aus YAML)"""
        module_info = self.get_module_info(module_id)
        if not module_info:
            return module_id
        return module_info.get("name", module_id)

    def get_module_type(self, module_id: str) -> str:
        """Get module type for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("type", "Unknown") if module_info else "Unknown"

    def get_module_icon(self, module_id: str) -> str:
        """Get module icon for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("icon", "❓") if module_info else "❓"

    def get_module_ip_range(self, module_id: str) -> str:
        """Get IP range for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("ip_range", "Unknown") if module_info else "Unknown"

    def get_module_ip_addresses(self, module_id: str) -> List[str]:
        """Get all IP addresses for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("ip_addresses", []) if module_info else []

    def get_module_commands(self, module_id: str) -> List[str]:
        """Get available commands for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("commands", []) if module_info else []

    def get_module_description(self, module_id: str, language: str = "de") -> str:
        """Get description for module ID"""
        module_info = self.get_module_info(module_id)
        return module_info.get("description", "No description") if module_info else "No description"

    def is_module_enabled(self, module_id: str) -> bool:
        """Check if module is enabled"""
        module_info = self.get_module_info(module_id)
        return module_info.get("enabled", True) if module_info else False

    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get all modules"""
        modules = {}

        # Registry v1 format (modules as array)
        if "modules" in self.config and isinstance(self.config["modules"], list):
            for module in self.config["modules"]:
                key = module.get("serial") or module.get("id")
                if key:
                    modules[key] = module

        # Registry v1 format (transports as array)
        if "transports" in self.config and isinstance(self.config["transports"], list):
            for transport in self.config["transports"]:
                key = transport.get("serial") or transport.get("id")
                if key:
                    modules[key] = transport

        # Legacy format (modules as dict)
        if "modules" in self.config and isinstance(self.config["modules"], dict):
            modules.update(self.config["modules"])

        # Legacy format (transports as dict)
        if "transports" in self.config and isinstance(self.config["transports"], dict):
            modules.update(self.config["transports"])

        return modules

    def get_enabled_modules(self) -> Dict[str, Dict[str, Any]]:
        """Get only enabled modules"""
        all_modules = self.get_all_modules()
        return {k: v for k, v in all_modules.items() if v.get("enabled", True)}

    def get_modules_by_type(self, module_type: str) -> Dict[str, Dict[str, Any]]:
        """Get modules by type"""
        all_modules = self.get_all_modules()
        return {k: v for k, v in all_modules.items() if v.get("type") == module_type}

    def get_module_id_by_name(self, module_name: str) -> Optional[str]:
        """Get module ID by name"""
        all_modules = self.get_all_modules()
        for module_id, info in all_modules.items():
            if info.get("name") == module_name:
                return module_id
        return None

    def validate_module_id(self, module_id: str) -> bool:
        """Validate if module ID exists"""
        return module_id in self.get_all_modules()

    def get_module_statistics(self) -> Dict[str, Any]:
        """Get module statistics"""
        all_modules = self.get_enabled_modules()
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

    def save_config(self) -> bool:
        """Save current configuration to YAML file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"❌ Error saving module configuration: {e}")
            return False

    def update_module(self, module_id: str, updates: Dict[str, Any]) -> bool:
        """Update module configuration"""
        module_info = self.get_module_info(module_id)
        if not module_info:
            return False

        # Update module info
        module_info.update(updates)

        # Save to config
        if "modules" in self.config and module_id in self.config["modules"]:
            self.config["modules"][module_id] = module_info
        elif "transports" in self.config and module_id in self.config["transports"]:
            self.config["transports"][module_id] = module_info

        return self.save_config()


# Global instance for easy access
_omf_module_manager = None


def get_omf_module_manager() -> OmfModuleManager:
    """Get global OMF module manager instance"""
    global _omf_module_manager
    if _omf_module_manager is None:
        _omf_module_manager = OmfModuleManager()
    return _omf_module_manager


# Backward compatibility functions
def get_module_info(module_id: str) -> Optional[Dict[str, Any]]:
    """Backward compatibility function"""
    manager = get_omf_module_manager()
    return manager.get_module_info(module_id)


def get_module_name(module_id: str, language: str = "de") -> str:
    """Backward compatibility function"""
    manager = get_omf_module_manager()
    return manager.get_module_name(module_id, language)


def get_module_type(module_id: str) -> str:
    """Backward compatibility function"""
    manager = get_omf_module_manager()
    return manager.get_module_type(module_id)


def validate_module_id(module_id: str) -> bool:
    """Backward compatibility function"""
    manager = get_omf_module_manager()
    return manager.validate_module_id(module_id)


if __name__ == "__main__":
    """Test the OMF Module Manager"""
    manager = OmfModuleManager()

    print("🔧 OMF Module Manager Test")
    print("=" * 50)

    # Test basic functionality
    print(f"📋 Total Modules: {len(manager.get_all_modules())}")
    print(f"✅ Enabled Modules: {len(manager.get_enabled_modules())}")
    print(f"🏭 Processing Modules: {len(manager.get_modules_by_type('Processing'))}")
    print(f"📦 Storage Modules: {len(manager.get_modules_by_type('Storage'))}")

    # Test module info
    test_module_id = "SVR3QA0022"
    module_info = manager.get_module_info(test_module_id)
    print(f"📋 Module {test_module_id}: {module_info}")

    # Test name conversion
    module_name = manager.get_module_name(test_module_id)
    print(f"📋 Module Name: {test_module_id} -> {module_name}")

    # Test statistics
    stats = manager.get_module_statistics()
    print(f"📊 Statistics: {stats}")

    print("✅ OMF Module Manager test completed")
