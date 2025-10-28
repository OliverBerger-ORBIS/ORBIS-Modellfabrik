"""
CCU Config Loader

Loads domain-specific configuration objects for CCU operations.
Parallel to Registry Manager for domain-specific JSON configurations.

Author: OMF Development Team
Version: 1.0
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Import cache with defensive fallback
try:
    from omf2.common.cache import get_cache

    _cache_available = True
except ImportError:
    logger.warning("Cache module not available, using direct loading for CCU configs")
    _cache_available = False


class CCUConfigLoader:
    """
    Domain-specific configuration loader for CCU operations.

    Loads JSON configuration files from omf2/config/ccu/ directory.
    Provides direct access to configuration objects without Gateway overhead.

    Architecture:
    - Parallel to Registry Manager (system-technical info)
    - Domain-specific (CCU application configurations)
    - Direct access for UI components and Business Managers
    - Uses TTL cache (OMF2_CACHE_TTL) for performance optimization
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

        logger.info(f"CCU Config Loader initialized with path: {self.config_path}")

    def _load_json_config(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file with TTL caching.

        Args:
            filename: Name of JSON file to load

        Returns:
            Dictionary with configuration data

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        # Use TTL cache if available
        if _cache_available:
            cache = get_cache()
            cache_key = f"ccu_config:{filename}:{self.config_path}"

            def loader():
                return self._load_json_from_disk(filename)

            return cache.get_or_set(cache_key, loader)
        else:
            # Fallback to direct loading
            return self._load_json_from_disk(filename)

    def _load_json_from_disk(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON configuration file from disk.

        Args:
            filename: Name of JSON file to load

        Returns:
            Dictionary with configuration data

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If JSON is malformed
        """
        config_file = self.config_path / filename

        if not config_file.exists():
            raise FileNotFoundError(f"CCU config file not found: {config_file}")

        try:
            with open(config_file, encoding="utf-8") as f:
                config_data = json.load(f)

            logger.debug(f"Loaded CCU config from disk: {filename}")

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
        """
        Clear configuration cache.

        Note: This clears the TTL cache. To fully clear, use the global cache's clear method.
        """
        if _cache_available:
            cache = get_cache()
            cache.clear()
            logger.debug("CCU config TTL cache cleared")
        else:
            logger.debug("No cache to clear (cache not available)")

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
