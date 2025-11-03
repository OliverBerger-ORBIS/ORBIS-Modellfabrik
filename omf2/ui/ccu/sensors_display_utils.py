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
        with open(config_path, encoding="utf-8") as f:
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
        "brightness": {"max_lux": 65000.0, "unit": "lux"},
        "pressure": {"min": 900.0, "max": 1100.0, "unit": "hPa"},
        "aq": {"min": 0.0, "max": 5.0, "unit": "AQ"},
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


def lux_to_percent(lux: float, max_lux: float = 65000.0) -> float:
    """
    Convert lux value to percentage (0-100%) using logarithmic scale
    for better human perception of brightness levels.

    Args:
        lux: Light intensity in lux
        max_lux: Maximum lux value for 100% (default: 65000, configurable via sensors_display.yml)

    Returns:
        float: Percentage (0-100), never exceeds 100%
    """
    if max_lux <= 0:
        logger.warning(f"Invalid max_lux: {max_lux}, using default 65000")
        max_lux = 65000.0

    # Logarithmic conversion for better human perception
    # Formula: log(1 + lux) / log(1 + max_lux) * 100
    import math

    if lux <= 0:
        return 0.0

    # Logarithmic scale: more realistic brightness perception
    percent = (math.log(1 + lux) / math.log(1 + max_lux)) * 100.0
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

    max_lux = config.get("brightness", {}).get("max_lux", 65000.0)
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


def normalize_aq(aq_value: float, config: Dict = None) -> float:
    """
    Normalize AQ (Air Quality Score) to percentage based on configured range
    AQ scale: 0 = sehr gut, 5 = schlecht

    Args:
        aq_value: AQ score (0-5)
        config: Optional configuration dict (uses default if None)

    Returns:
        float: Percentage (0-100)
    """
    if config is None:
        config = _get_default_config()

    aq_config = config.get("aq", {})
    min_aq = aq_config.get("min", 0.0)
    max_aq = aq_config.get("max", 5.0)

    return percent_from_range(aq_value, min_aq, max_aq)


def aq_level(aq_value: float, config: Dict = None) -> str:
    """
    Determine AQ level based on score (0-5 scale)

    Args:
        aq_value: AQ score (0-5)
        config: Optional configuration dict (uses default if None)

    Returns:
        str: Level name ('sehr_gut', 'gut', 'maessig', 'schlecht', 'sehr_schlecht')
    """
    if config is None:
        config = _get_default_config()

    if aq_value <= 1.0:
        return "sehr_gut"
    elif aq_value <= 2.0:
        return "gut"
    elif aq_value <= 3.0:
        return "maessig"
    elif aq_value <= 4.0:
        return "schlecht"
    else:
        return "sehr_schlecht"


def aq_color(aq_value: float, config: Dict = None) -> str:
    """
    Get color for AQ value based on bar chart color ranges

    Args:
        aq_value: AQ score (0-5)
        config: Optional configuration dict (uses default if None)

    Returns:
        str: Hex color code
    """
    if config is None:
        config = _get_default_config()

    bar_config = config.get("aq", {}).get("bar_chart", {})
    color_ranges = bar_config.get(
        "color_ranges",
        [
            [0, 1, "#28a745"],  # Excellent
            [1, 2, "#90EE90"],  # Good
            [2, 3, "#ffc107"],  # Moderate
            [3, 4, "#fd7e14"],  # Poor
            [4, 5, "#dc3545"],  # Very Poor
        ],
    )

    # Support both old format [min, max, color] and new format [min, max, color, i18n_key]
    for range_item in color_ranges:
        if len(range_item) >= 3:
            min_val = range_item[0]
            max_val = range_item[1]
            color = range_item[2]
            if min_val <= aq_value < max_val:
                return color

    return "#808080"  # Default gray


def aq_label(aq_value: float, config: Dict = None) -> str:
    """
    Get i18n key for AQ value label (translation should be done in UI code)

    Args:
        aq_value: AQ score (0-5)
        config: Optional configuration dict (uses default if None)

    Returns:
        str: i18n key for the label (or fallback label if no key found)
    """
    if config is None:
        config = _get_default_config()

    bar_config = config.get("aq", {}).get("bar_chart", {})
    color_ranges = bar_config.get(
        "color_ranges",
        [
            [0, 1, "#28a745", "ccu_overview.sensor_data.aq.label_excellent"],
            [1, 2, "#90EE90", "ccu_overview.sensor_data.aq.label_good"],
            [2, 3, "#ffc107", "ccu_overview.sensor_data.aq.label_moderate"],
            [3, 4, "#fd7e14", "ccu_overview.sensor_data.aq.label_poor"],
            [4, 5, "#dc3545", "ccu_overview.sensor_data.aq.label_very_poor"],
        ],
    )

    # Support both old format [min, max, color] and new format [min, max, color, i18n_key]
    for range_item in color_ranges:
        if len(range_item) >= 3:
            min_val = range_item[0]
            max_val = range_item[1]
            if min_val <= aq_value < max_val:
                # Return i18n key if present (4th element), otherwise fallback to level name
                if len(range_item) >= 4:
                    return range_item[3]  # i18n key
                else:
                    # Fallback to level-based label
                    level = aq_level(aq_value, config)
                    level_map = {
                        "sehr_gut": "Excellent",
                        "gut": "Good",
                        "maessig": "Moderate",
                        "schlecht": "Poor",
                        "sehr_schlecht": "Very Poor",
                    }
                    return level_map.get(level, "Unknown")

    return "Unknown"


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


def get_aq_info(aq_value: float, config: Dict = None) -> Tuple[str, str, str]:
    """
    Get complete AQ information (level, color, label)

    Args:
        aq_value: AQ score (0-5)
        config: Optional configuration dict (uses default if None)

    Returns:
        Tuple[str, str, str]: (level, color, label)
    """
    if config is None:
        config = _get_default_config()

    level = aq_level(aq_value, config)
    color = aq_color(aq_value, config)
    label = aq_label(aq_value, config)

    return level, color, label
