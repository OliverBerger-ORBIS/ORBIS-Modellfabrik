"""
CCU Config Loader

Loads domain-specific configuration objects for CCU operations.
Parallel to Registry Manager for domain-specific JSON configurations.

Author: OMF Development Team
Version: 1.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from omf2.common.logger import get_logger

logger = get_logger("ccu.config_loader")


class CCUConfigLoader:
    """
    Domain-specific configuration loader for CCU operations.
    
    Loads JSON configuration files from omf2/config/ccu/ directory.
    Provides direct access to configuration objects without Gateway overhead.
    
    Architecture:
    - Parallel to Registry Manager (system-technical info)
    - Domain-specific (CCU application configurations)
    - Direct access for UI components and Business Managers
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize CCU Config Loader.
        
        Args:
            config_path: Path to CCU config directory. Defaults to omf2/config/ccu/
        """
        if config_path is None:
            # Source-relative path for CCU config directory
            self.config_path = Path(__file__).parent.parent / "config" / "ccu"
        else:
            self.config_path = Path(config_path)
            
        self._cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"CCU Config Loader initialized with path: {self.config_path}")
    
    def _load_json_config(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file with caching.
        
        Args:
            filename: Name of JSON file to load
            
        Returns:
            Dictionary with configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        if filename in self._cache:
            return self._cache[filename]
            
        config_file = self.config_path / filename
        
        if not config_file.exists():
            raise FileNotFoundError(f"CCU config file not found: {config_file}")
            
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            self._cache[filename] = config_data
            logger.debug(f"Loaded CCU config: {filename}")
            
            return config_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in CCU config {filename}: {e}")
            raise
    
    def load_production_workflows(self) -> Dict[str, Any]:
        """
        Load production workflows configuration.
        
        Returns:
            Dictionary with production workflows for different workpiece types
        """
        return self._load_json_config("production_workflows.json")
    
    def load_production_settings(self) -> Dict[str, Any]:
        """
        Load production settings configuration.
        
        Returns:
            Dictionary with production durations, settings, and FTS settings
        """
        return self._load_json_config("production_settings.json")
    
    def load_shopfloor_layout(self) -> Dict[str, Any]:
        """
        Load shopfloor layout configuration.
        
        Returns:
            Dictionary with grid, modules, intersections, and roads
        """
        return self._load_json_config("shopfloor_layout.json")
    
    def get_config_meta(self, config_name: str) -> Dict[str, Any]:
        """
        Get metadata from configuration file.
        
        Args:
            config_name: Name of configuration (e.g., 'production_workflows')
            
        Returns:
            Dictionary with _meta information
        """
        filename = f"{config_name}.json"
        config_data = self._load_json_config(filename)
        
        return config_data.get("_meta", {})
    
    def clear_cache(self):
        """Clear configuration cache."""
        self._cache.clear()
        logger.debug("CCU config cache cleared")
    
    def list_available_configs(self) -> list[str]:
        """
        List available configuration files.
        
        Returns:
            List of available JSON configuration filenames
        """
        if not self.config_path.exists():
            return []
            
        json_files = list(self.config_path.glob("*.json"))
        return [f.name for f in json_files if f.name != "__pycache__"]


# Singleton instance for global access
_ccu_config_loader: Optional[CCUConfigLoader] = None


def get_ccu_config_loader() -> CCUConfigLoader:
    """
    Get singleton instance of CCU Config Loader.
    
    Returns:
        CCUConfigLoader instance
    """
    global _ccu_config_loader
    
    if _ccu_config_loader is None:
        _ccu_config_loader = CCUConfigLoader()
        
    return _ccu_config_loader
