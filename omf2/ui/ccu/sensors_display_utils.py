#!/usr/bin/env python3
"""
Sensor Display Utilities
Utility functions for normalizing and processing sensor data for OMF-style visualization
"""

from pathlib import Path
from typing import Dict, Tuple

import yaml

from omf2.common.logger import get_logger

logger = get_logger(__name__)


def load_sensor_display_config() -> Dict:
    """
    Load sensor display configuration from YAML file
    
    Returns:
        Dict: Configuration dictionary
    """
    config_path = Path(__file__).parent.parent.parent / "registry" / "sensors_display.yml"
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.debug(f"Loaded sensor display config from {config_path}")
            return config
    except Exception as e:
        logger.error(f"Failed to load sensor display config: {e}")
        return _get_default_config()


def _get_default_config() -> Dict:
    """
    Get default sensor display configuration as fallback
    
    Returns:
        Dict: Default configuration
    """
    return {
        "temperature": {"min": -30.0, "max": 60.0, "unit": "°C"},
        "humidity": {"min": 0.0, "max": 100.0, "unit": "%"},
        "brightness": {"max_lux": 1000.0, "unit": "lux"},
        "pressure": {"min": 900.0, "max": 1100.0, "unit": "hPa"},
        "iaq": {
            "thresholds": {"good": 50, "moderate": 100, "unhealthy": 150},
            "colors": {
                "good": "#28a745",
                "moderate": "#ffc107",
                "unhealthy": "#fd7e14",
                "hazard": "#dc3545",
            },
            "labels": {
                "good": "Good",
                "moderate": "Moderate",
                "unhealthy": "Unhealthy",
                "hazard": "Hazardous",
            },
        },
    }


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between min and max bounds
    
    Args:
        value: Value to clamp
        min_val: Minimum bound
        max_val: Maximum bound
        
    Returns:
        float: Clamped value
    """
    return max(min_val, min(max_val, value))


def percent_from_range(value: float, min_val: float, max_val: float) -> float:
    """
    Convert a value to percentage based on min/max range
    
    Args:
        value: Value to convert
        min_val: Minimum value of range
        max_val: Maximum value of range
        
    Returns:
        float: Percentage (0-100)
    """
    if max_val <= min_val:
        logger.warning(f"Invalid range: max ({max_val}) <= min ({min_val})")
        return 0.0
    
    # Clamp value to range
    clamped = clamp(value, min_val, max_val)
    
    # Convert to percentage
    percent = ((clamped - min_val) / (max_val - min_val)) * 100.0
    
    # Ensure result is within 0-100
    return clamp(percent, 0.0, 100.0)


def lux_to_percent(lux: float, max_lux: float = 1000.0) -> float:
    """
    Convert lux value to percentage (0-100%)
    
    Args:
        lux: Light intensity in lux
        max_lux: Maximum lux value for 100% (default: 1000)
        
    Returns:
        float: Percentage (0-100), never exceeds 100%
    """
    if max_lux <= 0:
        logger.warning(f"Invalid max_lux: {max_lux}, using default 1000")
        max_lux = 1000.0
    
    # Convert to percentage and clamp to 0-100
    percent = (lux / max_lux) * 100.0
    return clamp(percent, 0.0, 100.0)


def iaq_level(iaq_value: float, config: Dict = None) -> str:
    """
    Determine IAQ level based on thresholds
    
    Args:
        iaq_value: IAQ sensor value
        config: Optional configuration dict (uses default if None)
        
    Returns:
        str: Level name ('good', 'moderate', 'unhealthy', 'hazard')
    """
    if config is None:
        config = _get_default_config()
    
    thresholds = config.get("iaq", {}).get("thresholds", {})
    good_threshold = thresholds.get("good", 50)
    moderate_threshold = thresholds.get("moderate", 100)
    unhealthy_threshold = thresholds.get("unhealthy", 150)
    
    if iaq_value <= good_threshold:
        return "good"
    elif iaq_value <= moderate_threshold:
        return "moderate"
    elif iaq_value <= unhealthy_threshold:
        return "unhealthy"
    else:
        return "hazard"


def iaq_color(iaq_value: float, config: Dict = None) -> str:
    """
    Get color for IAQ value (traffic light style)
    
    Args:
        iaq_value: IAQ sensor value
        config: Optional configuration dict (uses default if None)
        
    Returns:
        str: Hex color code
    """
    if config is None:
        config = _get_default_config()
    
    level = iaq_level(iaq_value, config)
    colors = config.get("iaq", {}).get("colors", {})
    
    return colors.get(level, "#808080")  # Default to gray if level not found


def iaq_label(iaq_value: float, config: Dict = None) -> str:
    """
    Get human-readable label for IAQ value
    
    Args:
        iaq_value: IAQ sensor value
        config: Optional configuration dict (uses default if None)
        
    Returns:
        str: Human-readable label
    """
    if config is None:
        config = _get_default_config()
    
    level = iaq_level(iaq_value, config)
    labels = config.get("iaq", {}).get("labels", {})
    
    return labels.get(level, "Unknown")


def normalize_temperature(temp: float, config: Dict = None) -> float:
    """
    Normalize temperature to percentage based on configured range
    
    Args:
        temp: Temperature value in °C
        config: Optional configuration dict (uses default if None)
        
    Returns:
        float: Percentage (0-100)
    """
    if config is None:
        config = _get_default_config()
    
    temp_config = config.get("temperature", {})
    min_temp = temp_config.get("min", -30.0)
    max_temp = temp_config.get("max", 60.0)
    
    return percent_from_range(temp, min_temp, max_temp)


def normalize_humidity(humidity: float) -> float:
    """
    Normalize humidity to percentage (already 0-100%)
    
    Args:
        humidity: Humidity value in %
        
    Returns:
        float: Percentage (0-100), clamped
    """
    return clamp(humidity, 0.0, 100.0)


def normalize_brightness(lux: float, config: Dict = None) -> float:
    """
    Normalize brightness (lux) to percentage
    
    Args:
        lux: Light intensity in lux
        config: Optional configuration dict (uses default if None)
        
    Returns:
        float: Percentage (0-100)
    """
    if config is None:
        config = _get_default_config()
    
    max_lux = config.get("brightness", {}).get("max_lux", 1000.0)
    return lux_to_percent(lux, max_lux)


def normalize_pressure(pressure: float, config: Dict = None) -> float:
    """
    Normalize air pressure to percentage based on configured range
    
    Args:
        pressure: Pressure value in hPa
        config: Optional configuration dict (uses default if None)
        
    Returns:
        float: Percentage (0-100)
    """
    if config is None:
        config = _get_default_config()
    
    pressure_config = config.get("pressure", {})
    min_pressure = pressure_config.get("min", 900.0)
    max_pressure = pressure_config.get("max", 1100.0)
    
    return percent_from_range(pressure, min_pressure, max_pressure)


def get_iaq_info(iaq_value: float, config: Dict = None) -> Tuple[str, str, str]:
    """
    Get complete IAQ information (level, color, label)
    
    Args:
        iaq_value: IAQ sensor value
        config: Optional configuration dict (uses default if None)
        
    Returns:
        Tuple[str, str, str]: (level, color, label)
    """
    if config is None:
        config = _get_default_config()
    
    level = iaq_level(iaq_value, config)
    color = iaq_color(iaq_value, config)
    label = iaq_label(iaq_value, config)
    
    return level, color, label
