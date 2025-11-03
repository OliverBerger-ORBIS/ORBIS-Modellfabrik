# Sensors Display Configuration

## Overview

The `sensors_display.yml` configuration file defines the normalization parameters and visualization settings for sensor data in the OMF (ORBIS Modellfabrik) system. This configuration enables consistent, normalized displays of various sensor readings including temperature, humidity, brightness, air pressure, and Indoor Air Quality (IAQ).

## Location

`omf2/registry/sensors_display.yml`

## Purpose

The configuration provides:
- **Normalization ranges** for converting raw sensor values to percentages (0-100%)
- **Display thresholds** for color-coding and alerts
- **Traffic light mappings** for IAQ indicators
- **i18n support** for all labels and subtitles (EN/DE/FR)
- **Configurable parameters** without code changes

## Configuration Structure

### Temperature

```yaml
temperature:
  min: -30.0      # Minimum temperature for 0% fill
  max: 60.0       # Maximum temperature for 100% fill
  unit: "°C"
  show_subtitle: true
  subtitle: "ccu_overview.sensor_data.temperature.subtitle"  # i18n key (supports {min}, {max})
  gauge:
    bar_color: "darkred"
    steps:
      - { from: -30.0, to: 6.0, color: "lightblue" }
      - { from: 6.0, to: 18.0, color: "lightgreen" }
      - { from: 18.0, to: 60.0, color: "lightyellow" }
```

**Normalization**: Temperature values are mapped linearly from the min/max range to 0-100%
- `-30°C` → 0%
- `15°C` (midpoint) → 50%
- `60°C` → 100%

**Use Case**: Displays temperature as a gauge with fill level based on the configured range.

### Humidity

```yaml
humidity:
  min: 0.0
  max: 100.0
  unit: "%"
  gauge:
    color_ranges:
      - [0, 30, "orange"]    # Too dry
      - [30, 60, "green"]    # Comfortable
      - [60, 100, "blue"]    # Too humid
```

**Normalization**: Humidity is already a percentage, so it's clamped to 0-100% range.

**Use Case**: Displays relative humidity with comfort zone indicators.

### Brightness

```yaml
brightness:
  max_lux: 1000.0  # Maximum lux for 100% normalization
  unit: "lux"
  gauge:
    color_ranges:
      - [0, 20, "darkblue"]   # Dark
      - [20, 50, "blue"]      # Dim
      - [50, 80, "yellow"]    # Bright
      - [80, 100, "orange"]   # Very bright
```

**Normalization**: Lux values are converted to percentage, **never exceeding 100%**
- `0 lux` → 0%
- `500 lux` → 50%
- `1000 lux` → 100%
- `2000 lux` → 100% (clamped)

**Use Case**: Prevents brightness from showing over 100%, provides consistent scale across different light sensors.

### Air Pressure

```yaml
pressure:
  min: 900.0   # Minimum pressure in hPa
  max: 1100.0  # Maximum pressure in hPa
  unit: "hPa"
  gauge:
    color_ranges:
      - [0, 40, "blue"]      # Low pressure
      - [40, 60, "green"]    # Normal
      - [60, 100, "orange"]  # High pressure
```

**Normalization**: Pressure values are mapped from the typical atmospheric range to 0-100%
- `900 hPa` → 0%
- `1000 hPa` → 50%
- `1100 hPa` → 100%

**Use Case**: Displays barometric pressure with weather indication zones.

### Indoor Air Quality (IAQ)

```yaml
iaq:
  unit: "IAQ"
  show_subtitle: true
  subtitle: "ccu_overview.sensor_data.iaq.subtitle"  # i18n key (supports {value}, {label})
  show_value_below: true  # Display value below traffic light
  thresholds:
    good: 50         # 0-50: Good air quality
    moderate: 100    # 51-100: Moderate air quality
    unhealthy: 150   # 101-150: Unhealthy for sensitive groups
    # 151+: Unhealthy/Hazardous
  colors:
    top: "#e03b3b"    # Red top (unhealthy)
    mid: "#f3c22a"    # Yellow middle (moderate)
    bot: "#16b64a"    # Green bottom (good)
  labels:
    good: "ccu_overview.sensor_data.iaq.label_good"       # i18n key
    moderate: "ccu_overview.sensor_data.iaq.label_moderate"
    unhealthy: "ccu_overview.sensor_data.iaq.label_unhealthy"
    hazard: "ccu_overview.sensor_data.iaq.label_hazard"
```

**Traffic Light System**: Only the active light (based on IAQ value) is displayed, others are gray
| IAQ Value | Level | Color | Meaning |
|-----------|-------|-------|---------|
| 0-50 | Good | Green (bottom) | Excellent air quality |
| 51-100 | Moderate | Yellow (middle) | Acceptable air quality |
| 101-150 | Unhealthy | Yellow (middle) | Unhealthy for sensitive groups |
| 151+ | Hazardous | Red (top) | Unhealthy for all |

**Use Case**: Displays IAQ as a traffic light with only the active light visible.

## Usage

### In Python Code

```python
from omf2.ui.ccu.sensors_display_utils import (
    load_sensor_display_config,
    normalize_temperature,
    normalize_humidity,
    normalize_brightness,
    normalize_pressure,
    get_iaq_info
)

# Load configuration
config = load_sensor_display_config()

# Normalize sensor values
temp_percent = normalize_temperature(25.0, config)  # Returns ~61.1%
humidity_percent = normalize_humidity(65.0)          # Returns 65.0%
brightness_percent = normalize_brightness(1500.0, config)  # Returns 100.0% (clamped)
pressure_percent = normalize_pressure(1013.0, config)      # Returns 56.5%

# Get IAQ information (label is now an i18n key)
level, color, label_key = get_iaq_info(75.0, config)
# Returns: ("moderate", "#ffc107", "ccu_overview.sensor_data.iaq.label_moderate")
# Translate in UI: label = i18n.t(label_key)

# Get AQ information (label is now an i18n key)
level, color, label_key = get_aq_info(2.5, config)
# Returns: ("maessig", "#ffc107", "ccu_overview.sensor_data.aq.label_moderate")
# Translate in UI: label = i18n.t(label_key)
```

### In UI Components

The sensor data subtab (`omf2/ui/ccu/ccu_overview/sensor_data_subtab.py`) automatically uses this configuration to:
- Display Plotly gauges with normalized values
- Show IAQ as a traffic light badge (only active light visible)
- Apply color-coded zones to all sensor displays
- Translate all labels and subtitles based on selected language

## Internationalization (i18n)

All labels and subtitles support i18n through translation keys. The configuration uses i18n keys that are translated by the UI code based on the selected language (EN/DE/FR).

### Subtitle i18n Keys

All sensor types support `subtitle` with i18n keys:
- Format parameters (e.g., `{min}`, `{max}`, `{value}`, `{label}`) are supported
- Example: `"ccu_overview.sensor_data.temperature.subtitle"` → "Range: -30°C to 60°C" (EN)

### Label i18n Keys

IAQ and AQ labels use i18n keys:
- `iaq.labels.*` → `ccu_overview.sensor_data.iaq.label_*`
- `aq.bar_chart.color_ranges` → Each range can include an i18n key as 4th element

### Step Label i18n Keys

Brightness and Pressure gauge steps support i18n:
- Each step can have a `label` field with an i18n key
- Example: `"ccu_overview.sensor_data.brightness.step_dark"`

### Translation Files

i18n keys are defined in:
- `omf2/config/translations/en/ccu_overview.yml` (English - default)
- `omf2/config/translations/de/ccu_overview.yml` (German)
- `omf2/config/translations/fr/ccu_overview.yml` (French)

## Customization

To customize the sensor display behavior:

1. **Adjust temperature range**: Modify `temperature.min` and `temperature.max` for your climate zone
2. **Change brightness sensitivity**: Adjust `brightness.max_lux` for your lighting environment
3. **Customize IAQ thresholds**: Modify `iaq.thresholds` based on your air quality standards
4. **Update colors**: Change color hex codes to match your UI theme

### Example: Different Climate Zone

```yaml
temperature:
  min: 0.0    # No sub-zero temperatures expected
  max: 40.0   # Tropical climate max
```

### Example: Brighter Environment

```yaml
brightness:
  max_lux: 2000.0  # Higher threshold for very bright spaces
```

## Testing

Unit tests for the sensor display utilities are in `tests/test_sensors_display_utils.py`:

```bash
# Run all sensor display tests
pytest tests/test_sensors_display_utils.py -v

# Run specific test class
pytest tests/test_sensors_display_utils.py::TestNormalizeBrightness -v
```

**Test Coverage**:
- ✅ Clamp function
- ✅ Percent from range conversion
- ✅ Lux to percent (never exceeds 100%)
- ✅ IAQ level determination
- ✅ IAQ color mapping
- ✅ All normalization functions
- ✅ Integration tests with realistic values

## QA Steps

### Prerequisites
- OMF system running with sensor data feed
- Streamlit dashboard accessible
- BME680 sensor providing temperature, humidity, pressure, IAQ
- LDR sensor providing brightness/light data

### Testing Procedure

1. **Navigate to Sensor Data Subtab**
   - Open the CCU Overview tab in the dashboard
   - Select the "Sensor Data" subtab

2. **Verify Temperature Display**
   - Check that temperature gauge shows value in °C
   - Verify fill level is calculated correctly (e.g., 20°C should show ~56%)
   - Confirm temperature values outside range are clamped to 0-100%

3. **Verify Humidity Display**
   - Check that humidity gauge shows 0-100%
   - Verify values never exceed 100%
   - Confirm gauge color zones are correct

4. **Verify Brightness Display**
   - **Critical**: Verify brightness never shows >100% regardless of lux input
   - Test with values: 500 lux (50%), 1000 lux (100%), 2000 lux (100%)
   - Check that actual lux value is shown alongside percentage

5. **Verify Pressure Display**
   - Check that pressure gauge shows hPa values
   - Verify fill level calculation (1000 hPa should show ~50%)
   - Confirm gauge ranges from configured min to max

6. **Verify IAQ Badge**
   - **Critical**: Verify IAQ shows as colored badge (not gauge)
   - Test traffic light colors:
     - IAQ 25 → Green badge "Good"
     - IAQ 75 → Yellow badge "Moderate"
     - IAQ 125 → Orange badge "Unhealthy"
     - IAQ 200 → Red badge "Hazardous"
   - Verify threshold information is displayed

7. **Verify Configuration Loading**
   - Check logs for successful config loading
   - Verify no errors in browser console
   - Confirm all gauges render properly

8. **Test Edge Cases**
   - Verify behavior with null/missing sensor values
   - Test with extreme values (negative, very large)
   - Confirm error handling shows warning messages

### Expected Results

✅ All sensor values display correctly  
✅ Brightness never exceeds 100%  
✅ Humidity is exactly 0-100%  
✅ Temperature fill level based on min/max  
✅ IAQ shows as colored badge with correct traffic light colors  
✅ All gauges use Plotly visualization  
✅ Configuration is loaded from YAML  
✅ No errors in console or logs  

### Note on State Store Integration

The `get_latest_sensor_values()` function in the subtab currently integrates with the existing `get_ccu_sensor_manager()` to retrieve sensor data from the BME680 and LDR topics. This implementation:
- Uses the existing sensor manager pattern from the codebase
- Retrieves data from `/j1/txt/1/i/bme680` (temperature, humidity, pressure, IAQ)
- Retrieves data from `/j1/txt/1/i/ldr` (light/brightness)

If you need to integrate with a different state store (Redis, database, etc.), you can modify the `get_latest_sensor_values()` function to query your preferred data source while maintaining the same return structure.

## Troubleshooting

### Configuration Not Loading
- Check file path: `omf2/registry/sensors_display.yml`
- Verify YAML syntax is valid
- Check application logs for load errors

### Brightness Shows >100%
- Verify you're using `normalize_brightness()` function
- Check `max_lux` configuration value
- Ensure clamping is applied in UI code

### IAQ Colors Wrong
- Verify threshold values in configuration
- Check that `get_iaq_info()` is being used
- Confirm color hex codes are valid

### Gauges Not Displaying
- Ensure Plotly is installed: `pip install plotly`
- Check browser console for JavaScript errors
- Verify Streamlit version compatibility

## Related Files

- **Configuration**: `omf2/registry/sensors_display.yml`
- **Utilities**: `omf2/ui/ccu/sensors_display_utils.py`
- **UI Component**: `omf2/ui/ccu/ccu_overview/sensor_data_subtab.py`
- **Tests**: `tests/test_sensors_display_utils.py`
- **Documentation**: `docs/registry/sensors_display.md` (this file)

## Version History

- **v1.1** (2025-11-01): i18n Support and Enhanced Features
  - Full i18n support for all labels and subtitles (EN/DE/FR)
  - IAQ traffic light now shows only active light (inactive lights are gray)
  - Brightness and Pressure steps moved to YAML with i18n support
  - Subtitle configuration with i18n keys and format parameters
  - `show_subtitle` and `show_value_below` flags for all sensors
  - All sensor labels use i18n keys instead of hardcoded strings

- **v1.0** (2025-10-26): Initial implementation
  - Temperature, humidity, brightness, pressure, IAQ normalization
  - Traffic light IAQ indicator
  - Configurable thresholds and ranges
  - Unit tests with 100% pass rate
