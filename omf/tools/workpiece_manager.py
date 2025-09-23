#!/usr/bin/env python3
"""
OMF Workpiece Manager - Registry-basierte Workpiece-Verwaltung
Version: 3.0.0
Ersetzt nfc_manager.py und nfc_code_manager.py mit Registry-basierter Implementierung
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from omf.dashboard.tools.logging_config import get_logger


class OmfWorkpieceManager:
    """OMF Workpiece Manager using Registry v1 configuration"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize OMF Workpiece Manager with Registry v1 configuration"""
        self.logger = get_logger("omf.tools.workpiece_manager")
        self.logger.info("WorkpieceManager initialisiert")

        self.config_path = config_path or self._get_default_config_path()
        self.config = self.load_yaml_config()

        # If no config found, try to use legacy fallback
        if not self.config:
            try:
                legacy_config = self._get_legacy_config_path()
                if legacy_config.exists():
                    self.config_path = str(legacy_config)
                    self.config = self.load_yaml_config()
                    self.logger.warning("⚠️ Using legacy nfc_config.yml - consider migrating to registry")
                    return
            except Exception as e:
                self.logger.error(f"Legacy fallback failed: {e}")

            raise ValueError(f"Could not load workpiece configuration from {self.config_path}")

    def _get_default_config_path(self) -> str:
        """Get default path to Registry v1 workpieces configuration"""
        from omf.dashboard.tools.path_constants import REGISTRY_DIR
        
        # Registry v1 (primary)
        registry_path = REGISTRY_DIR / "model" / "v1" / "workpieces.yml"
        if registry_path.exists():
            self.logger.info(f"✅ Using registry v1: {registry_path}")
            return str(registry_path)

        # Fallback to legacy config (deprecated)
        from omf.dashboard.tools.path_constants import PROJECT_ROOT
        legacy_path = PROJECT_ROOT / "omf" / "config" / "nfc_config.yml"
        if legacy_path.exists():
            self.logger.warning(f"⚠️ Using legacy config: {legacy_path}")
            return str(legacy_path)

        return str(registry_path)  # Default to registry path

    def _get_legacy_config_path(self) -> Path:
        """Get legacy config path for fallback"""
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        return project_root / "omf" / "config" / "nfc_config.yml"

    def load_yaml_config(self) -> Optional[Dict[str, Any]]:
        """Load workpiece configuration from YAML file"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.logger.info(f"✅ Loaded workpiece config: {len(config.get('nfc_codes', {}))} workpieces")
                return config
        except FileNotFoundError:
            self.logger.error(f"❌ Workpiece configuration file not found: {self.config_path}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Error loading workpiece configuration: {e}")
            return None

    # Core Workpiece Operations
    def get_workpiece_info(self, nfc_code: str) -> Optional[Dict[str, Any]]:
        """Get complete workpiece information by NFC code"""
        if not self.config or "nfc_codes" not in self.config:
            return None

        return self.config["nfc_codes"].get(nfc_code)

    def get_friendly_id(self, nfc_code: str) -> str:
        """Get friendly ID for NFC code (e.g., '040a8dca341291' -> 'R1')"""
        workpiece_info = self.get_workpiece_info(nfc_code)
        return workpiece_info.get("friendly_id", nfc_code) if workpiece_info else nfc_code

    def get_nfc_code_by_friendly_id(self, friendly_id: str) -> Optional[str]:
        """Get NFC code by friendly ID (e.g., 'R1' -> '040a8dca341291')"""
        if not self.config or "nfc_codes" not in self.config:
            return None

        for nfc_code, info in self.config["nfc_codes"].items():
            if info.get("friendly_id") == friendly_id:
                return nfc_code

        return None

    def get_color(self, nfc_code: str) -> str:
        """Get color for NFC code"""
        workpiece_info = self.get_workpiece_info(nfc_code)
        return workpiece_info.get("color", "Unknown") if workpiece_info else "Unknown"

    def get_quality_check(self, nfc_code: str) -> str:
        """Get quality check status for NFC code"""
        workpiece_info = self.get_workpiece_info(nfc_code)
        return workpiece_info.get("quality_check", "Unknown") if workpiece_info else "Unknown"

    def get_description(self, nfc_code: str) -> str:
        """Get description for NFC code"""
        workpiece_info = self.get_workpiece_info(nfc_code)
        return workpiece_info.get("description", "No description") if workpiece_info else "No description"

    def is_enabled(self, nfc_code: str) -> bool:
        """Check if workpiece is enabled"""
        workpiece_info = self.get_workpiece_info(nfc_code)
        return workpiece_info.get("enabled", True) if workpiece_info else False

    # Bulk Operations
    def get_all_workpieces(self) -> Dict[str, Dict[str, Any]]:
        """Get all workpieces"""
        return self.config.get("nfc_codes", {}) if self.config else {}

    def get_enabled_workpieces(self) -> Dict[str, Dict[str, Any]]:
        """Get only enabled workpieces"""
        all_workpieces = self.get_all_workpieces()
        return {k: v for k, v in all_workpieces.items() if v.get("enabled", True)}

    def get_workpieces_by_color(self, color: str) -> Dict[str, Dict[str, Any]]:
        """Get workpieces by color"""
        all_workpieces = self.get_all_workpieces()
        return {k: v for k, v in all_workpieces.items() if v.get("color") == color}

    def get_workpieces_by_quality(self, quality: str) -> Dict[str, Dict[str, Any]]:
        """Get workpieces by quality check status"""
        all_workpieces = self.get_all_workpieces()
        return {k: v for k, v in all_workpieces.items() if v.get("quality_check") == quality}

    # Validation
    def validate_workpiece(self, nfc_code: str) -> bool:
        """Validate if workpiece exists"""
        return nfc_code in self.get_all_workpieces()

    def is_nfc_code(self, value: str) -> bool:
        """Check if value is a known NFC code"""
        return self.validate_workpiece(value)

    def is_friendly_id(self, value: str) -> bool:
        """Check if value is a known friendly ID"""
        if not self.config or "nfc_codes" not in self.config:
            return False

        friendly_ids = [info.get("friendly_id") for info in self.config["nfc_codes"].values()]
        return value in friendly_ids

    # Statistics and Analysis
    def get_workpiece_statistics(self) -> Dict[str, Any]:
        """Get workpiece statistics"""
        enabled_workpieces = self.get_enabled_workpieces()
        total_workpieces = len(enabled_workpieces)

        color_counts = {}
        quality_counts = {}

        for info in enabled_workpieces.values():
            color = info.get("color", "Unknown")
            quality = info.get("quality_check", "Unknown")

            color_counts[color] = color_counts.get(color, 0) + 1
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        return {
            "total_workpieces": total_workpieces,
            "color_counts": color_counts,
            "quality_counts": quality_counts,
            "colors": list(color_counts.keys()),
            "quality_options": list(quality_counts.keys()),
        }

    # Configuration Management
    def get_quality_check_options(self) -> List[str]:
        """Get available quality check options"""
        if not self.config or "quality_check_options" not in self.config:
            return ["OK", "NOT-OK", "PENDING", "FAILED"]

        return self.config["quality_check_options"]

    def get_colors(self) -> List[str]:
        """Get available colors"""
        if not self.config or "colors" not in self.config:
            return ["RED", "WHITE", "BLUE"]

        return self.config["colors"]

    def get_template_placeholders(self) -> Dict[str, str]:
        """Get template placeholders for workpieces"""
        if not self.config or "template_placeholders" not in self.config:
            return {
                "nfc_code": "<nfcCode>",
                "workpiece_id": "<workpieceId>",
                "color": "<color>",
                "quality": "<quality>",
            }

        return self.config["template_placeholders"]

    def get_mqtt_paths(self) -> List[List[str]]:
        """Get MQTT paths for workpiece detection"""
        if not self.config or "mqtt_paths" not in self.config:
            return [
                ["workpieceId"],
                ["metadata", "workpiece", "workpieceId"],
                ["action", "metadata", "workpiece", "workpieceId"],
                ["workpiece", "workpieceId"],
                ["loadId"],
                ["id"],
            ]

        return self.config["mqtt_paths"]

    # Display and Formatting
    def format_workpiece_display_name(self, nfc_code: str, include_code: bool = True) -> str:
        """Format workpiece for display (e.g., 'R1 (040a8dca341291)')"""
        friendly_id = self.get_friendly_id(nfc_code)
        if include_code and friendly_id != nfc_code:
            return f"{friendly_id} ({nfc_code})"
        return friendly_id

    # Configuration Reload
    def reload_config(self) -> bool:
        """Reload configuration from YAML file"""
        new_config = self.load_yaml_config()
        if new_config:
            self.config = new_config
            self.logger.info("✅ Workpiece configuration reloaded")
            return True
        return False

    # Registry Integration
    def is_using_registry(self) -> bool:
        """Check if manager is using Registry v1 or legacy config"""
        return "registry" in self.config_path and "v1" in self.config_path


# Global instance for easy access
_omf_workpiece_manager = None


def get_omf_workpiece_manager() -> OmfWorkpieceManager:
    """Get global OMF Workpiece manager instance"""
    global _omf_workpiece_manager
    if _omf_workpiece_manager is None:
        _omf_workpiece_manager = OmfWorkpieceManager()
    return _omf_workpiece_manager


# Backward compatibility functions (for existing code)
def get_nfc_info(nfc_code: str) -> Optional[Dict[str, Any]]:
    """Backward compatibility function"""
    manager = get_omf_workpiece_manager()
    return manager.get_workpiece_info(nfc_code)


def get_friendly_id(nfc_code: str) -> str:
    """Backward compatibility function"""
    manager = get_omf_workpiece_manager()
    return manager.get_friendly_id(nfc_code)


def get_friendly_name(nfc_code: str) -> str:
    """Backward compatibility function (alias for get_friendly_id)"""
    return get_friendly_id(nfc_code)


def validate_nfc_code(nfc_code: str) -> bool:
    """Backward compatibility function"""
    manager = get_omf_workpiece_manager()
    return manager.validate_workpiece(nfc_code)


def get_nfc_codes_by_color(color: str) -> List[str]:
    """Backward compatibility function"""
    manager = get_omf_workpiece_manager()
    workpieces = manager.get_workpieces_by_color(color)
    return list(workpieces.keys())


def get_all_nfc_codes() -> List[str]:
    """Backward compatibility function"""
    manager = get_omf_workpiece_manager()
    workpieces = manager.get_all_workpieces()
    return list(workpieces.keys())


def is_nfc_code(value: str) -> bool:
    """Backward compatibility function"""
    manager = get_omf_workpiece_manager()
    return manager.is_nfc_code(value)


if __name__ == "__main__":
    """Test the OMF Workpiece Manager"""
    manager = OmfWorkpieceManager()

    print("🔧 OMF Workpiece Manager Test")
    print("=" * 50)

    # Test basic functionality
    print(f"📋 Total Workpieces: {len(manager.get_all_workpieces())}")
    print(f"✅ Enabled Workpieces: {len(manager.get_enabled_workpieces())}")
    print(f"🔴 Red Workpieces: {len(manager.get_workpieces_by_color('RED'))}")
    print(f"⚪ White Workpieces: {len(manager.get_workpieces_by_color('WHITE'))}")
    print(f"🔵 Blue Workpieces: {len(manager.get_workpieces_by_color('BLUE'))}")

    # Test workpiece info
    test_nfc_code = "040a8dca341291"
    workpiece_info = manager.get_workpiece_info(test_nfc_code)
    print(f"📋 Workpiece {test_nfc_code}: {workpiece_info}")

    # Test friendly ID conversion
    friendly_id = manager.get_friendly_id(test_nfc_code)
    print(f"📋 Friendly ID: {test_nfc_code} -> {friendly_id}")

    # Test reverse conversion
    nfc_code = manager.get_nfc_code_by_friendly_id(friendly_id)
    print(f"📋 NFC Code: {friendly_id} -> {nfc_code}")

    # Test statistics
    stats = manager.get_workpiece_statistics()
    print(f"📊 Statistics: {stats}")

    # Test registry usage
    print(f"🏛️ Using Registry: {manager.is_using_registry()}")

    print("✅ OMF Workpiece Manager test completed")
