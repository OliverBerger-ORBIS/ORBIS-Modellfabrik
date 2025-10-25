"""
Business Functions Loader

Loads and validates business_functions.yml configuration using Pydantic models.
Provides functions for loading, validating, and saving business function configurations.

Author: OMF Development Team
Version: 1.0.0
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from omf2.common.logger import get_logger
from omf2.config.schemas.business_functions_schema import (
    BusinessFunctionsConfig,
    is_pydantic_available,
)

logger = get_logger(__name__)


class BusinessFunctionsLoader:
    """
    Loader for business functions configuration.
    
    Handles loading, validation, and saving of business_functions.yml
    using Pydantic models for type safety and validation.
    """
    
    DEFAULT_CONFIG_FILENAME = "business_functions.yml"
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the loader.
        
        Args:
            config_dir: Path to config directory. Defaults to omf2/registry/
        """
        if config_dir is None:
            # Default to omf2/registry directory
            self.config_dir = Path(__file__).parent.parent / "registry"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_file = self.config_dir / self.DEFAULT_CONFIG_FILENAME
        logger.info(f"Business Functions Loader initialized with path: {self.config_file}")
    
    def load_raw(self) -> Dict[str, Any]:
        """
        Load raw YAML configuration without validation.
        
        Returns:
            Dictionary with configuration data
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Business functions config not found: {self.config_file}"
            )
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            logger.debug(f"Loaded raw business functions config from {self.config_file}")
            return data
        
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in business functions config: {e}")
            raise
    
    def load_validated(self) -> BusinessFunctionsConfig:
        """
        Load and validate configuration using Pydantic models.
        
        Returns:
            Validated BusinessFunctionsConfig object
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is malformed
            ValidationError: If validation fails (when pydantic is available)
        """
        data = self.load_raw()
        
        if not is_pydantic_available():
            logger.warning(
                "Pydantic not available - skipping validation. "
                "Install pydantic for schema validation."
            )
            # Return dict as-is when pydantic is not available
            return data
        
        try:
            config = BusinessFunctionsConfig(**data)
            logger.info(
                f"Successfully validated business functions config with "
                f"{len(config.business_functions)} functions"
            )
            return config
        
        except Exception as e:
            logger.error(f"Validation error in business functions config: {e}")
            raise
    
    def save(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to YAML file.
        
        Args:
            config: Configuration dictionary or Pydantic model to save
            
        Raises:
            IOError: If file cannot be written
        """
        # Convert Pydantic model to dict if needed
        if hasattr(config, 'model_dump'):
            config_dict = config.model_dump()
        elif hasattr(config, 'dict'):
            config_dict = config.dict()
        else:
            config_dict = config
        
        try:
            # Ensure directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    config_dict,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True
                )
            
            logger.info(f"Saved business functions config to {self.config_file}")
        
        except Exception as e:
            logger.error(f"Error saving business functions config: {e}")
            raise
    
    def get_enabled_functions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get only enabled business functions.
        
        Returns:
            Dictionary of enabled function names to their configurations
        """
        config = self.load_raw()
        business_functions = config.get('business_functions', {})
        
        enabled = {
            name: func
            for name, func in business_functions.items()
            if func.get('enabled', False)
        }
        
        logger.debug(f"Found {len(enabled)} enabled business functions")
        return enabled
    
    def validate_importability(self) -> Dict[str, bool]:
        """
        Optionally validate that module_path and class_name are importable.
        
        This is an optional check that can be enabled with ENABLE_IMPORT_CHECK env var.
        It attempts to import each business function class to verify they exist.
        
        Returns:
            Dictionary mapping function names to import success status
        """
        if not os.environ.get('ENABLE_IMPORT_CHECK'):
            logger.debug(
                "Import check disabled. Set ENABLE_IMPORT_CHECK=1 to enable."
            )
            return {}
        
        config = self.load_raw()
        business_functions = config.get('business_functions', {})
        results = {}
        
        for name, func in business_functions.items():
            module_path = func.get('module_path')
            class_name = func.get('class_name')
            
            if not module_path or not class_name:
                results[name] = False
                continue
            
            try:
                # Attempt to import the module and get the class
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                results[name] = True
                logger.debug(f"✓ Successfully imported {module_path}.{class_name}")
            
            except (ImportError, AttributeError) as e:
                results[name] = False
                logger.warning(
                    f"✗ Failed to import {module_path}.{class_name}: {e}"
                )
        
        return results


# Module-level functions for convenience

def load_business_functions(config_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load business functions configuration.
    
    Args:
        config_dir: Optional path to config directory
        
    Returns:
        Dictionary with business functions configuration
    """
    loader = BusinessFunctionsLoader(config_dir)
    return loader.load_raw()


def save_business_functions(
    config: Dict[str, Any],
    config_dir: Optional[Path] = None
) -> None:
    """
    Save business functions configuration.
    
    Args:
        config: Configuration dictionary to save
        config_dir: Optional path to config directory
    """
    loader = BusinessFunctionsLoader(config_dir)
    loader.save(config)


def get_loader(config_dir: Optional[Path] = None) -> BusinessFunctionsLoader:
    """
    Get a BusinessFunctionsLoader instance.
    
    Args:
        config_dir: Optional path to config directory
        
    Returns:
        BusinessFunctionsLoader instance
    """
    return BusinessFunctionsLoader(config_dir)
