"""
OMF NFC Manager
Central manager for NFC code operations using YAML configuration
Version: 3.0.0
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class OmfNfcManager:
    """OMF NFC Manager using YAML configuration"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize OMF NFC Manager with YAML configuration"""
        self.config_path = config_path or self._get_default_config_path()
        self.config = self.load_yaml_config()

        if not self.config:
            raise ValueError(f"Could not load NFC configuration from {self.config_path}")

    def _get_default_config_path(self) -> str:
        """Get default path to NFC configuration YAML file"""
        # Get the directory of this file
        current_dir = Path(__file__).parent
        # Navigate to config directory
        config_dir = current_dir.parent / "config"
        return str(config_dir / "nfc_config.yml")

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

    def get_nfc_info(self, workpieceId: str) -> Optional[Dict[str, Any]]:
        """Get complete NFC code information"""
        if not self.config:
            return None

        if "workpieceIds" in self.config and workpieceId in self.config["workpieceIds"]:
            return self.config["workpieceIds"][workpieceId]

        return None

    def get_friendly_id(self, workpieceId: str) -> str:
        """Get friendly ID for NFC code"""
        nfc_info = self.get_nfc_info(workpieceId)
        return nfc_info.get("friendly_id", workpieceId) if nfc_info else workpieceId

    def get_workpieceId_by_friendly_id(self, friendly_id: str) -> Optional[str]:
        """Get NFC code by friendly ID"""
        if not self.config:
            return None

        for workpieceId, info in self.config["workpieceIds"].items():
            if info.get("friendly_id") == friendly_id:
                return workpieceId

        return None

    def get_color(self, workpieceId: str) -> str:
        """Get color for NFC code"""
        nfc_info = self.get_nfc_info(workpieceId)
        return nfc_info.get("color", "Unknown") if nfc_info else "Unknown"

    def get_quality_check(self, workpieceId: str) -> str:
        """Get quality check status for NFC code"""
        nfc_info = self.get_nfc_info(workpieceId)
        return nfc_info.get("quality_check", "Unknown") if nfc_info else "Unknown"

    def get_description(self, workpieceId: str) -> str:
        """Get description for NFC code"""
        nfc_info = self.get_nfc_info(workpieceId)
        return nfc_info.get("description", "No description") if nfc_info else "No description"

    def is_enabled(self, workpieceId: str) -> bool:
        """Check if NFC code is enabled"""
        nfc_info = self.get_nfc_info(workpieceId)
        return nfc_info.get("enabled", True) if nfc_info else False

    def get_all_workpieceIds(self) -> Dict[str, Dict[str, Any]]:
        """Get all NFC codes"""
        return self.config.get("workpieceIds", {}) if self.config else {}

    def get_enabled_workpieceIds(self) -> Dict[str, Dict[str, Any]]:
        """Get only enabled NFC codes"""
        all_codes = self.get_all_workpieceIds()
        return {k: v for k, v in all_codes.items() if v.get("enabled", True)}

    def get_workpieceIds_by_color(self, color: str) -> Dict[str, Dict[str, Any]]:
        """Get NFC codes by color"""
        all_codes = self.get_all_workpieceIds()
        return {k: v for k, v in all_codes.items() if v.get("color") == color}

    def get_workpieceIds_by_quality(self, quality: str) -> Dict[str, Dict[str, Any]]:
        """Get NFC codes by quality check status"""
        all_codes = self.get_all_workpieceIds()
        return {k: v for k, v in all_codes.items() if v.get("quality_check") == quality}

    def validate_workpieceId(self, workpieceId: str) -> bool:
        """Validate if NFC code exists"""
        return workpieceId in self.get_all_workpieceIds()

    def get_nfc_statistics(self) -> Dict[str, Any]:
        """Get NFC code statistics"""
        all_codes = self.get_enabled_workpieceIds()
        total_codes = len(all_codes)

        color_counts = {}
        quality_counts = {}

        for info in all_codes.values():
            color = info.get("color", "Unknown")
            quality = info.get("quality_check", "Unknown")

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

    def save_config(self) -> bool:
        """Save current configuration to YAML file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"❌ Error saving NFC configuration: {e}")
            return False

    def update_workpieceId(self, workpieceId: str, updates: Dict[str, Any]) -> bool:
        """Update NFC code configuration"""
        nfc_info = self.get_nfc_info(workpieceId)
        if not nfc_info:
            return False

        # Update NFC info
        nfc_info.update(updates)

        # Save to config
        if "workpieceIds" in self.config and workpieceId in self.config["workpieceIds"]:
            self.config["workpieceIds"][workpieceId] = nfc_info

        return self.save_config()


# Global instance for easy access
_omf_nfc_manager = None


def get_omf_nfc_manager() -> OmfNfcManager:
    """Get global OMF NFC manager instance"""
    global _omf_nfc_manager
    if _omf_nfc_manager is None:
        _omf_nfc_manager = OmfNfcManager()
    return _omf_nfc_manager


# Backward compatibility functions
def get_nfc_info(workpieceId: str) -> Optional[Dict[str, Any]]:
    """Backward compatibility function"""
    manager = get_omf_nfc_manager()
    return manager.get_nfc_info(workpieceId)


def get_friendly_id(workpieceId: str) -> str:
    """Backward compatibility function"""
    manager = get_omf_nfc_manager()
    return manager.get_friendly_id(workpieceId)


def validate_workpieceId(workpieceId: str) -> bool:
    """Backward compatibility function"""
    manager = get_omf_nfc_manager()
    return manager.validate_workpieceId(workpieceId)


if __name__ == "__main__":
    """Test the OMF NFC Manager"""
    manager = OmfNfcManager()

    print("📱 OMF NFC Manager Test")
    print("=" * 50)

    # Test basic functionality
    print(f"📋 Total NFC Codes: {len(manager.get_all_workpieceIds())}")
    print(f"✅ Enabled NFC Codes: {len(manager.get_enabled_workpieceIds())}")
    print(f"🔴 Red NFC Codes: {len(manager.get_workpieceIds_by_color('RED'))}")
    print(f"⚪ White NFC Codes: {len(manager.get_workpieceIds_by_color('WHITE'))}")
    print(f"🔵 Blue NFC Codes: {len(manager.get_workpieceIds_by_color('BLUE'))}")

    # Test NFC code info
    test_workpieceId = "040a8dca341291"
    nfc_info = manager.get_nfc_info(test_workpieceId)
    print(f"📋 NFC Code {test_workpieceId}: {nfc_info}")

    # Test friendly ID conversion
    friendly_id = manager.get_friendly_id(test_workpieceId)
    print(f"📋 Friendly ID: {test_workpieceId} -> {friendly_id}")

    # Test reverse conversion
    workpieceId = manager.get_workpieceId_by_friendly_id(friendly_id)
    print(f"📋 NFC Code: {friendly_id} -> {workpieceId}")

    # Test statistics
    stats = manager.get_nfc_statistics()
    print(f"📊 Statistics: {stats}")

    print("✅ OMF NFC Manager test completed")
