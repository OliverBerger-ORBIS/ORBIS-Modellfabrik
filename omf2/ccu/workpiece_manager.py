#!/usr/bin/env python3
"""
Workpiece Manager for CCU Domain
Manages workpiece configurations and validation
"""

import logging
import yaml
import json
import jsonschema
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WorkpieceManager:
    """
    Workpiece Manager - Handles workpiece configuration and validation for CCU domain
    """
    
    def __init__(self, registry_dir: Path = None):
        self.registry_dir = registry_dir or Path(__file__).parent.parent / "registry"
        self.workpieces_file = self.registry_dir / "model" / "v2" / "workpieces.yml"
        self.schema_file = self.registry_dir / "schemas" / "workpieces.schema.json"
        
        self.workpieces_config = {}
        self.schema = {}
        
        # Load configuration and schema
        self.reload_config()
        
        logger.info(f"🔧 Workpiece Manager initialized with registry: {self.registry_dir}")
    
    def reload_config(self) -> bool:
        """Reload workpieces configuration and schema"""
        try:
            # Load workpieces configuration
            if self.workpieces_file.exists():
                with open(self.workpieces_file, 'r', encoding='utf-8') as f:
                    self.workpieces_config = yaml.safe_load(f) or {}
            else:
                logger.warning(f"Workpieces file not found: {self.workpieces_file}")
                self.workpieces_config = self._get_default_config()
                self._save_config()
            
            # Load schema
            if self.schema_file.exists():
                with open(self.schema_file, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
            else:
                logger.warning(f"Schema file not found: {self.schema_file}")
                self.schema = {}
            
            # Validate configuration against schema
            if self.schema:
                self._validate_config()
            
            logger.info("✅ Workpiece configuration reloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to reload workpiece configuration: {e}")
            return False
    
    def _validate_config(self) -> bool:
        """Validate workpieces configuration against schema"""
        try:
            jsonschema.validate(self.workpieces_config, self.schema)
            logger.info("✅ Workpieces configuration is valid")
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"❌ Workpieces configuration validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Schema validation error: {e}")
            return False
    
    def get_workpiece_by_id(self, workpiece_id: str) -> Optional[Dict[str, Any]]:
        """Get workpiece configuration by ID"""
        workpieces = self.workpieces_config.get("workpieces", {})
        return workpieces.get(workpiece_id)
    
    def get_workpiece_by_nfc_code(self, nfc_code: str) -> Optional[Dict[str, Any]]:
        """Get workpiece by NFC code"""
        workpieces = self.workpieces_config.get("workpieces", {})
        
        for workpiece_id, workpiece_data in workpieces.items():
            nfc_codes = workpiece_data.get("nfc_codes", [])
            if nfc_code in nfc_codes:
                return workpiece_data
        
        return None
    
    def get_all_workpieces(self) -> Dict[str, Any]:
        """Get all workpieces"""
        return self.workpieces_config.get("workpieces", {})
    
    def get_workpiece_colors(self) -> List[Dict[str, str]]:
        """Get available workpiece colors"""
        return self.workpieces_config.get("colors", [])
    
    def get_workpiece_types(self) -> Dict[str, Any]:
        """Get available workpiece types"""
        return self.workpieces_config.get("types", {})
    
    def get_quality_checks(self) -> Dict[str, Any]:
        """Get available quality checks"""
        return self.workpieces_config.get("quality_checks", {})
    
    def get_processing_steps(self) -> Dict[str, Any]:
        """Get available processing steps"""
        return self.workpieces_config.get("processing_steps", {})
    
    def get_workpieces_by_color(self, color: str) -> List[Dict[str, Any]]:
        """Get workpieces by color"""
        workpieces = self.workpieces_config.get("workpieces", {})
        return [wp for wp in workpieces.values() if wp.get("color") == color]
    
    def get_workpieces_by_type(self, workpiece_type: str) -> List[Dict[str, Any]]:
        """Get workpieces by type"""
        workpieces = self.workpieces_config.get("workpieces", {})
        return [wp for wp in workpieces.values() if wp.get("type") == workpiece_type]
    
    def validate_nfc_code(self, nfc_code: str) -> bool:
        """Validate NFC code format and existence"""
        # Check format (hex string with minimum 12 characters)
        if not isinstance(nfc_code, str) or len(nfc_code) < 12:
            return False
        
        try:
            int(nfc_code, 16)  # Check if valid hex
        except ValueError:
            return False
        
        # Check if code exists in any workpiece
        return self.get_workpiece_by_nfc_code(nfc_code) is not None
    
    def get_workpiece_display_name(self, workpiece_id: str, include_id: bool = True) -> str:
        """Get formatted display name for workpiece"""
        workpiece = self.get_workpiece_by_id(workpiece_id)
        if not workpiece:
            return workpiece_id
        
        name = workpiece.get("name", workpiece_id)
        if include_id:
            return f"{name} ({workpiece_id})"
        return name
    
    def get_workpiece_by_nfc_display_name(self, nfc_code: str, include_code: bool = True) -> str:
        """Get formatted display name for workpiece by NFC code"""
        workpiece = self.get_workpiece_by_nfc_code(nfc_code)
        if not workpiece:
            return nfc_code
        
        name = workpiece.get("name", workpiece.get("id", "Unknown"))
        if include_code:
            return f"{name} ({nfc_code[:8]}...)"
        return name
    
    def add_workpiece(self, workpiece_id: str, workpiece_data: Dict[str, Any]) -> bool:
        """Add new workpiece to configuration"""
        try:
            # Validate workpiece data
            test_config = self.workpieces_config.copy()
            test_config.setdefault("workpieces", {})[workpiece_id] = workpiece_data
            
            if self.schema:
                jsonschema.validate(test_config, self.schema)
            
            # Add to configuration
            self.workpieces_config.setdefault("workpieces", {})[workpiece_id] = workpiece_data
            
            # Save configuration
            self._save_config()
            
            logger.info(f"✅ Workpiece added: {workpiece_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add workpiece {workpiece_id}: {e}")
            return False
    
    def update_workpiece(self, workpiece_id: str, workpiece_data: Dict[str, Any]) -> bool:
        """Update existing workpiece"""
        try:
            if workpiece_id not in self.workpieces_config.get("workpieces", {}):
                logger.error(f"Workpiece not found: {workpiece_id}")
                return False
            
            # Validate updated data
            test_config = self.workpieces_config.copy()
            test_config["workpieces"][workpiece_id] = workpiece_data
            
            if self.schema:
                jsonschema.validate(test_config, self.schema)
            
            # Update configuration
            self.workpieces_config["workpieces"][workpiece_id] = workpiece_data
            
            # Save configuration
            self._save_config()
            
            logger.info(f"✅ Workpiece updated: {workpiece_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update workpiece {workpiece_id}: {e}")
            return False
    
    def remove_workpiece(self, workpiece_id: str) -> bool:
        """Remove workpiece from configuration"""
        try:
            workpieces = self.workpieces_config.get("workpieces", {})
            if workpiece_id not in workpieces:
                logger.error(f"Workpiece not found: {workpiece_id}")
                return False
            
            del workpieces[workpiece_id]
            
            # Save configuration
            self._save_config()
            
            logger.info(f"✅ Workpiece removed: {workpiece_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove workpiece {workpiece_id}: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get workpiece statistics"""
        workpieces = self.workpieces_config.get("workpieces", {})
        
        stats = {
            "total_workpieces": len(workpieces),
            "colors": {},
            "types": {},
            "total_nfc_codes": 0
        }
        
        for workpiece in workpieces.values():
            # Color stats
            color = workpiece.get("color", "unknown")
            stats["colors"][color] = stats["colors"].get(color, 0) + 1
            
            # Type stats
            workpiece_type = workpiece.get("type", "unknown")
            stats["types"][workpiece_type] = stats["types"].get(workpiece_type, 0) + 1
            
            # NFC codes count
            nfc_codes = workpiece.get("nfc_codes", [])
            stats["total_nfc_codes"] += len(nfc_codes)
        
        return stats
    
    def _save_config(self) -> bool:
        """Save workpieces configuration to file"""
        try:
            self.workpieces_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.workpieces_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.workpieces_config, f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save workpieces configuration: {e}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default workpieces configuration"""
        return {
            "metadata": {
                "version": "2.0.0",
                "description": "OMF2 Workpieces Registry",
                "schema_version": "workpieces.schema.json"
            },
            "workpieces": {},
            "types": {
                "cylinder": {
                    "name": "Cylindrical",
                    "description": "Round cylindrical workpiece",
                    "default_dimensions": ["diameter", "height"]
                }
            },
            "colors": [
                {"id": "red", "name": "Red", "hex": "#FF0000"},
                {"id": "blue", "name": "Blue", "hex": "#0000FF"},
                {"id": "green", "name": "Green", "hex": "#00FF00"}
            ],
            "quality_checks": {},
            "processing_steps": {}
        }


# Global workpiece manager instance for CCU domain
_workpiece_manager = None


def get_workpiece_manager(**kwargs) -> WorkpieceManager:
    """Get global workpiece manager instance"""
    global _workpiece_manager
    if _workpiece_manager is None:
        _workpiece_manager = WorkpieceManager(**kwargs)
        logger.info("🔧 Workpiece Manager singleton created")
    return _workpiece_manager