#!/usr/bin/env python3
"""
NFC Code Manager
Central manager for NFC code operations using YAML configuration
Replaces workpieceId_mapping.py with enhanced functionality
"""

import os
from typing import Any, Dict, List, Optional

import yaml


class WorkpieceManager:
    """Central NFC Code Manager using YAML configuration"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize NFC Code Manager with YAML configuration"""
        self.config_path = config_path or self._get_default_config_path()
        self.config = self.load_yaml_config()

        if not self.config:
            raise ValueError(f"Could not load NFC configuration from {self.config_path}")

    def _get_default_config_path(self) -> str:
        """Get default path to NFC configuration YAML file"""
        # Always use the omf/config directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        omf_config_path = os.path.join(base_dir, "..", "config", "nfc_config.yml")
        return os.path.abspath(omf_config_path)

    def load_yaml_config(self) -> Optional[Dict[str, Any]]:
        """Load NFC configuration from YAML file"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ NFC configuration file not found: {self.config_path}")
            return None
        except Exception as e:
            print(f"❌ Error loading NFC configuration: {e}")
            return None

    def get_friendly_name(self, workpieceId: str) -> str:
        """Get friendly name for workpieceId (e.g., '040a8dca341291' -> 'R1')"""
        if not self.config or "nfc_codes" not in self.config:
            return workpieceId

        nfc_info = self.config["nfc_codes"].get(workpieceId)
        return nfc_info.get("friendly_id", workpieceId) if nfc_info else workpieceId

    def get_workpieceId(self, friendly_name: str) -> str:
        """Get NFC code for friendly name (e.g., 'R1' -> '040a8dca341291')"""
        if not self.config or "nfc_codes" not in self.config:
            return friendly_name

        for workpieceId, info in self.config["workpieceIds"].items():
            if info.get("friendly_id") == friendly_name:
                return workpieceId

        return friendly_name

    def get_nfc_info(self, workpieceId: str) -> Optional[Dict[str, Any]]:
        """Get complete NFC code information"""
        if not self.config or "nfc_codes" not in self.config:
            return None

        return self.config["nfc_codes"].get(workpieceId)

    def get_workpieceIds_by_color(self, color: str) -> List[str]:
        """Get all NFC codes for a specific color"""
        if not self.config or "nfc_codes" not in self.config:
            return []

        color = color.upper()
        return [code for code, info in self.config["workpieceIds"].items() if info.get("color") == color]

    def get_workpieceIds_by_quality(self, quality: str) -> List[str]:
        """Get all NFC codes with specific quality check status"""
        if not self.config or "nfc_codes" not in self.config:
            return []

        quality = quality.upper()
        return [code for code, info in self.config["workpieceIds"].items() if info.get("quality_check") == quality]

    def get_all_workpieceIds(self) -> List[str]:
        """Get all NFC codes"""
        if not self.config or "nfc_codes" not in self.config:
            return []

        return list(self.config["nfc_codes"].keys())

    def get_all_friendly_names(self) -> List[str]:
        """Get all friendly names"""
        if not self.config or "nfc_codes" not in self.config:
            return []

        return [info.get("friendly_id") for info in self.config["nfc_codes"].values()]

    def get_all_workpieceIds(self) -> List[str]:
        """Get all workpieceIds"""
        if not self.config or "nfc_codes" not in self.config:
            return []
        return list(self.config["nfc_codes"].keys())

    def get_workpieceId(self, friendly_name: str) -> Optional[str]:
        """Get workpieceId for friendly name"""
        if not self.config or "nfc_codes" not in self.config:
            return None
        
        for workpieceId, info in self.config["nfc_codes"].items():
            if info.get("friendly_id") == friendly_name:
                return workpieceId
        return None

    def get_workpieceIds_by_color(self, color: str) -> List[str]:
        """Get workpieceIds by color (case-insensitive)"""
        if not self.config or "nfc_codes" not in self.config:
            return []
        
        result = []
        color_upper = color.upper()
        for workpieceId, info in self.config["nfc_codes"].items():
            if info.get("color", "").upper() == color_upper:
                result.append(workpieceId)
        return result

    def get_workpieceIds_by_quality(self, quality: str) -> List[str]:
        """Get workpieceIds by quality check status"""
        if not self.config or "nfc_codes" not in self.config:
            return []
        
        result = []
        for workpieceId, info in self.config["nfc_codes"].items():
            if info.get("quality_check") == quality:
                result.append(workpieceId)
        return result

    def is_workpieceId(self, value: str) -> bool:
        """Check if value is a known NFC code"""
        if not self.config or "nfc_codes" not in self.config:
            return False

        return value in self.config["nfc_codes"]

    def is_friendly_name(self, value: str) -> bool:
        """Check if value is a known friendly name"""
        if not self.config or "nfc_codes" not in self.config:
            return False

        friendly_names = [info.get("friendly_id") for info in self.config["nfc_codes"].values()]
        return value in friendly_names

    def validate_workpieceId(self, workpieceId: str) -> bool:
        """Validate if NFC code exists in configuration"""
        return self.is_workpieceId(workpieceId)

    # Backward compatibility method aliases
    def get_all_nfc_codes(self) -> List[str]:
        """Backward compatibility: Get all workpieceIds"""
        return self.get_all_workpieceIds()

    def get_nfc_code(self, friendly_name: str) -> Optional[str]:
        """Backward compatibility: Get workpieceId for friendly name"""
        return self.get_workpieceId(friendly_name)

    def get_nfc_codes_by_color(self, color: str) -> List[str]:
        """Backward compatibility: Get workpieceIds by color"""
        return self.get_workpieceIds_by_color(color)

    def get_nfc_codes_by_quality(self, quality: str) -> List[str]:
        """Backward compatibility: Get workpieceIds by quality"""
        return self.get_workpieceIds_by_quality(quality)

    def get_color_for_nfc_code(self, workpieceId: str) -> Optional[str]:
        """Backward compatibility: Get color for workpieceId"""
        return self.get_color_for_workpieceId(workpieceId)

    def get_quality_for_nfc_code(self, workpieceId: str) -> Optional[str]:
        """Backward compatibility: Get quality for workpieceId"""
        return self.get_quality_for_workpieceId(workpieceId)

    def get_description_for_nfc_code(self, workpieceId: str) -> Optional[str]:
        """Backward compatibility: Get description for workpieceId"""
        return self.get_description_for_workpieceId(workpieceId)

    def is_nfc_code(self, value: str) -> bool:
        """Backward compatibility: Check if value is a known workpieceId"""
        return self.is_workpieceId(value)

    def validate_nfc_code(self, workpieceId: str) -> bool:
        """Backward compatibility: Validate workpieceId"""
        return self.validate_workpieceId(workpieceId)

    def get_color_for_workpieceId(self, workpieceId: str) -> Optional[str]:
        """Get color for workpieceId"""
        nfc_info = self.get_nfc_info(workpieceId)
        return nfc_info.get("color") if nfc_info else None

    def get_quality_for_workpieceId(self, workpieceId: str) -> Optional[str]:
        """Get quality check status for workpieceId"""
        nfc_info = self.get_nfc_info(workpieceId)
        return nfc_info.get("quality_check") if nfc_info else None

    def get_description_for_workpieceId(self, workpieceId: str) -> Optional[str]:
        """Get description for workpieceId"""
        nfc_info = self.get_nfc_info(workpieceId)
        return nfc_info.get("description") if nfc_info else None

    def format_nfc_display_name(self, workpieceId: str, include_code: bool = True) -> str:
        """Format NFC code for display (e.g., 'R1 (040a8dca341291)')"""
        friendly_name = self.get_friendly_name(workpieceId)
        if include_code and friendly_name != workpieceId:
            return f"{friendly_name} ({workpieceId})"
        return friendly_name

    def get_mqtt_paths(self) -> List[List[str]]:
        """Get MQTT paths for NFC code detection"""
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

    def get_template_placeholders(self) -> Dict[str, str]:
        """Get template placeholders for NFC codes"""
        if not self.config or "template_placeholders" not in self.config:
            return {
                "workpieceId": "<workpieceId>",
                "workpiece_id": "<workpieceId>",
                "color": "<color>",
                "quality": "<quality>",
            }

        return self.config["template_placeholders"]

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

    def get_statistics(self) -> Dict[str, Any]:
        """Get NFC code statistics"""
        if not self.config or "nfc_codes" not in self.config:
            return {}

        total_codes = len(self.config["nfc_codes"])
        color_counts = {}
        quality_counts = {}

        for info in self.config["nfc_codes"].values():
            color = info.get("color", "UNKNOWN")
            quality = info.get("quality_check", "UNKNOWN")

            color_counts[color] = color_counts.get(color, 0) + 1
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        return {
            "total_codes": total_codes,
            "color_counts": color_counts,
            "quality_counts": quality_counts,
            "colors": list(color_counts.keys()),
            "quality_options": list(quality_counts.keys()),
        }

    def reload_config(self) -> bool:
        """Reload configuration from YAML file"""
        new_config = self.load_yaml_config()
        if new_config:
            self.config = new_config
            return True
        return False


# Backward compatibility functions (for existing code)
def get_friendly_name(workpieceId: str) -> str:
    """Backward compatibility function"""
    manager = WorkpieceManager()
    return manager.get_friendly_name(workpieceId)


def get_workpieceId(friendly_name: str) -> str:
    """Backward compatibility function"""
    manager = WorkpieceManager()
    return manager.get_workpieceId(friendly_name)


def is_workpieceId(value: str) -> bool:
    """Backward compatibility function"""
    manager = WorkpieceManager()
    return manager.is_workpieceId(value)


def get_workpieceIds_by_color(color: str) -> List[str]:
    """Backward compatibility function"""
    manager = WorkpieceManager()
    return manager.get_workpieceIds_by_color(color)


# Legacy constants for backward compatibility
def get_all_workpieceIds() -> List[str]:
    """Backward compatibility function"""
    manager = WorkpieceManager()
    return manager.get_all_workpieceIds()


# Create global instance for easy access
_nfc_manager = None


def get_nfc_manager() -> WorkpieceManager:
    """Get global NFC manager instance"""
    global _nfc_manager
    if _nfc_manager is None:
        _nfc_manager = WorkpieceManager()
    return _nfc_manager


if __name__ == "__main__":
    """Test the NFC Code Manager"""
    manager = WorkpieceManager()

    print("🔧 NFC Code Manager Test")
    print("=" * 50)

    # Test basic functionality
    print(f"📋 Total NFC Codes: {len(manager.get_all_workpieceIds())}")
    print(f"🔴 RED Codes: {manager.get_workpieceIds_by_color('RED')}")
    print(f"⚪ WHITE Codes: {manager.get_workpieceIds_by_color('WHITE')}")
    print(f"🔵 BLUE Codes: {manager.get_workpieceIds_by_color('BLUE')}")

    # Test friendly name conversion
    test_code = "040a8dca341291"
    friendly_name = manager.get_friendly_name(test_code)
    print(f"📋 NFC Code {test_code} -> {friendly_name}")

    # Test reverse conversion
    workpieceId = manager.get_workpieceId(friendly_name)
    print(f"📋 Friendly Name {friendly_name} -> {workpieceId}")

    # Test statistics
    stats = manager.get_statistics()
    print(f"📊 Statistics: {stats}")

    print("✅ NFC Code Manager test completed")


# Backward compatibility aliases
def get_all_nfc_codes() -> List[str]:
    """Backward compatibility: Get all NFC codes"""
    manager = WorkpieceManager()
    return manager.get_all_workpieceIds()


def get_friendly_name(workpieceId: str) -> str:
    """Backward compatibility: Get friendly name for workpieceId"""
    manager = WorkpieceManager()
    return manager.get_friendly_name(workpieceId)


def get_nfc_code(friendly_name: str) -> Optional[str]:
    """Backward compatibility: Get workpieceId for friendly name"""
    manager = WorkpieceManager()
    return manager.get_workpieceId(friendly_name)


def get_nfc_codes_by_color(color: str) -> List[str]:
    """Backward compatibility: Get workpieceIds by color"""
    manager = WorkpieceManager()
    return manager.get_workpieceIds_by_color(color)


def is_nfc_code(value: str) -> bool:
    """Backward compatibility: Check if value is a known workpieceId"""
    manager = WorkpieceManager()
    return manager.is_workpieceId(value)


def get_nfc_manager() -> WorkpieceManager:
    """Backward compatibility: Get WorkpieceManager instance"""
    return WorkpieceManager()
