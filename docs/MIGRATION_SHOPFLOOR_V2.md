# Shopfloor Layout Migration Guide: v1.1 → v2.0

## Overview

Version 2.0 of the Shopfloor Layout configuration introduces breaking changes to improve asset key consistency and maintainability. This guide helps you migrate from v1.1 to v2.0.

## Breaking Changes

### 1. Configuration Structure

**Old Structure (v1.1):**
```json
{
  "_meta": {
    "_version": "1.1"
  },
  "grid": {
    "cell_size": "100x100"
  },
  "empty_positions": [
    {
      "id": "COMPANY",
      "position": [0, 0],
      "rectangle": "ORBIS",
      "square1": "shelves",
      "square2": "conveyer_belt"
    }
  ]
}
```

**New Structure (v2.0):**
```json
{
  "_meta": {
    "_version": "2.0"
  },
  "grid": {
    "cell_size": "200x200"
  },
  "fixed_positions": [
    {
      "id": "COMPANY",
      "type": "company",
      "position": [0, 0],
      "assets": {
        "rectangle": "ORBIS",
        "square1": "shelves",
        "square2": "conveyer_belt"
      }
    }
  ]
}
```

**Changes:**
- `empty_positions` → `fixed_positions`
- Added `type` field to each position
- Asset keys moved to `assets` object
- Cell size increased from 100x100 to 200x200

### 2. Asset Manager Keys

**Old Keys (v1.1 - DEPRECATED):**
- `EMPTY1_rectangle`, `EMPTY1_square1`, `EMPTY1_square2`
- `EMPTY2_rectangle`, `EMPTY2_square1`, `EMPTY2_square2`
- Lowercase variants: `company_rectangle`, `software_rectangle`

**New Keys (v2.0 - CANONICAL):**
- `COMPANY_rectangle`, `COMPANY_square1`, `COMPANY_square2`
- `SOFTWARE_rectangle`, `SOFTWARE_square1`, `SOFTWARE_square2`

**Legacy Support:**
- Legacy EMPTY1/EMPTY2 keys are **NO LONGER SUPPORTED** in productive code
- Applications must migrate to canonical COMPANY/SOFTWARE keys

## Migration Steps

### Step 1: Update Configuration Files

Update `omf2/config/ccu/shopfloor_layout.json`:

1. Change `_version` from `"1.1"` to `"2.0"`
2. Rename `empty_positions` to `fixed_positions`
3. Add `type` field to each position:
   - COMPANY → `"type": "company"`
   - SOFTWARE → `"type": "software"`
4. Move asset keys to `assets` object
5. Update `cell_size` from `"100x100"` to `"200x200"`

### Step 2: Update Python Code

**Old Code:**
```python
# Get empty position assets
asset_path = asset_manager.get_empty_position_asset("EMPTY1", "rectangle")

# Access empty_positions
empty_positions = layout_config.get("empty_positions", [])
```

**New Code:**
```python
# Get fixed position assets using canonical keys
asset_path = asset_manager.get_shopfloor_asset_path("COMPANY", "rectangle")

# Or use the new deterministic get_asset_file
asset_path = asset_manager.get_asset_file("COMPANY_rectangle")

# Access fixed_positions
fixed_positions = layout_config.get("fixed_positions", [])
```

### Step 3: Update Tests

**Old Tests:**
```python
def test_empty_positions():
    empty_positions = layout_config.get("empty_positions", [])
    assert len(empty_positions) == 2
```

**New Tests:**
```python
def test_fixed_positions():
    fixed_positions = layout_config.get("fixed_positions", [])
    assert len(fixed_positions) == 2
    
def test_canonical_keys():
    # Test COMPANY assets
    path = asset_manager.get_asset_file("COMPANY_rectangle")
    assert "ORBIS_logo_RGB.svg" in path
    
    # Test SOFTWARE assets
    path = asset_manager.get_asset_file("SOFTWARE_square1")
    assert "warehouse.svg" in path
```

### Step 4: Update UI Components

**Old UI Code:**
```python
# Display empty position info
st.info(f"📦 **Empty Position:** {position_id}")
```

**New UI Code:**
```python
# Display position type info
position_type = fixed_position.get('type', 'Unknown').upper()
st.info(f"📦 **Position Type:** {position_type}")
```

## API Changes

### Asset Manager

#### Removed Methods
- `get_module_icon_path("EMPTY1")` - No longer supported
- `get_module_icon_path("EMPTY2")` - No longer supported

#### New Methods
```python
def get_asset_file(key: str) -> str:
    """Get deterministic asset file path for a given key
    
    Args:
        key: Asset key (e.g., "COMPANY_rectangle", "SOFTWARE_square1")
        
    Returns:
        Deterministic path to SVG file or empty.svg as fallback
    """
```

#### Updated Methods
```python
def get_shopfloor_asset_path(asset_type: str, position: str) -> Optional[str]:
    """Get path to shopfloor asset
    
    Args:
        asset_type: "COMPANY" or "SOFTWARE" (canonical format)
        position: "rectangle", "square1", or "square2"
        
    Returns:
        Path to SVG icon or None
    """
```

### Configuration Loader

**Old:**
```python
layout_config = loader.load_shopfloor_layout()
empty_positions = layout_config.get("empty_positions", [])
```

**New:**
```python
layout_config = loader.load_shopfloor_layout()
fixed_positions = layout_config.get("fixed_positions", [])

# Backward compatibility fallback
if not fixed_positions:
    fixed_positions = layout_config.get("empty_positions", [])
```

## Backward Compatibility

### Automatic Fallback

The code includes backward compatibility support:

```python
# In ccu_factory_configuration_subtab.py and shopfloor_layout.py
fixed_positions = layout_config.get("fixed_positions", [])
# Fallback for old structure
if not fixed_positions:
    fixed_positions = layout_config.get("empty_positions", [])
```

### Deprecated Methods

Some methods remain available but are deprecated:

```python
# DEPRECATED - Will log warnings
asset_manager.get_empty_position_asset("COMPANY", "rectangle")
asset_manager.get_empty_position_asset_by_name("ORBIS")

# RECOMMENDED - Use canonical methods
asset_manager.get_shopfloor_asset_path("COMPANY", "rectangle")
asset_manager.get_asset_file("COMPANY_rectangle")
```

## CSS Changes

### Grid Styling

**Old CSS:**
```css
.cell {
    width: 100px;
    height: 100px;
    border-bottom: 2px solid #ddd;
}
```

**New CSS:**
```css
.shopfloor-container {
    overflow: visible;
}
.shopfloor-container::after {
    content: '';
    position: absolute;
    bottom: -2px;
    height: 2px;
    background: #ddd;
}
.cell {
    width: 200px;
    height: 200px;
}
.cell-label {
    position: absolute;
    bottom: 8px;
}
```

**Improvements:**
- Bottom border now visible (fixed overflow issue)
- Cell size increased from 100x100 to 200x200
- Labels separated from icon area using absolute positioning
- Overlay uses z-index for proper stacking

## Testing

### Unit Tests

Run the updated test suite:

```bash
# Run all asset manager tests
python -m pytest tests/test_omf2/test_asset_manager.py -v

# Run shopfloor layout tests
python -m pytest tests/test_omf2/test_shopfloor_layout_events.py -v
```

### Expected Test Results

All tests should pass with the new canonical keys:
- ✅ `test_canonical_company_rectangle` - COMPANY_rectangle → ORBIS_logo_RGB.svg
- ✅ `test_canonical_software_square1` - SOFTWARE_square1 → warehouse.svg
- ✅ `test_icon_visible_at_position_0_0` - Icon visible at [0,0]
- ✅ `test_icon_visible_at_position_0_3` - Icon visible at [0,3]
- ✅ `test_legacy_empty1_deprecated` - EMPTY1 no longer supported
- ✅ `test_legacy_empty2_deprecated` - EMPTY2 no longer supported

## Troubleshooting

### Issue: SVGs Not Visible at [0,0] or [0,3]

**Cause:** Using legacy EMPTY1/EMPTY2 keys instead of canonical COMPANY/SOFTWARE keys

**Solution:**
```python
# Wrong
asset_manager.get_module_icon_path("EMPTY1")

# Correct
asset_manager.get_shopfloor_asset_path("COMPANY", "rectangle")
# or
asset_manager.get_asset_file("COMPANY_rectangle")
```

### Issue: Bottom Border Cut Off

**Cause:** Old CSS with overflow issues

**Solution:** Update to new CSS with `overflow: visible` and `::after` pseudo-element

### Issue: Tests Failing with "EMPTY1/EMPTY2 not found"

**Cause:** Tests using legacy keys

**Solution:** Update tests to use canonical COMPANY/SOFTWARE keys

## Rollback Plan

If you need to rollback to v1.1:

1. Restore `shopfloor_layout.json` from git:
   ```bash
   git checkout HEAD~6 -- omf2/config/ccu/shopfloor_layout.json
   ```

2. Restore asset manager:
   ```bash
   git checkout HEAD~6 -- omf2/assets/asset_manager.py
   ```

3. Restore UI components:
   ```bash
   git checkout HEAD~6 -- omf2/ui/ccu/
   ```

## Support

For questions or issues with migration:
- Review commit history: `git log --oneline --grep="shopfloor"`
- Check PR description for detailed changes
- Contact: ORBIS Team

## References

- [Shopfloor Layout Configuration](../omf2/config/ccu/shopfloor_layout.json)
- [Asset Manager](../omf2/assets/asset_manager.py)
- [Factory Configuration UI](../omf2/ui/ccu/ccu_configuration/ccu_factory_configuration_subtab.py)
- [Shopfloor Layout Component](../omf2/ui/ccu/common/shopfloor_layout.py)
