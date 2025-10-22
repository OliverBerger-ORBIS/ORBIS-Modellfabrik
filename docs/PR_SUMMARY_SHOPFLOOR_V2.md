# Shopfloor Assets Structure Refactoring - PR Summary

## Overview

This PR implements a comprehensive refactoring of the shopfloor layout configuration and asset management system, migrating from legacy EMPTY1/EMPTY2 naming to canonical COMPANY/SOFTWARE keys. The changes improve code clarity, maintainability, and fix several UI rendering issues.

## Target Branch

`omf2-refactoring`

## Changes Summary

### 1. Configuration Migration (v1.1 → v2.0)

**File:** `omf2/config/ccu/shopfloor_layout.json`

- ✅ Migrated `empty_positions` → `fixed_positions` with explicit type field
- ✅ Updated version from 1.1 to 2.0
- ✅ Increased cell_size from 100x100 to 200x200
- ✅ Added migration notes in _meta
- ✅ Added type field to each position (company/software)
- ✅ Moved asset keys into `assets` object for better structure

**Migration Example:**
```json
// Before (v1.1)
"empty_positions": [
  {
    "id": "COMPANY",
    "position": [0, 0],
    "rectangle": "ORBIS",
    "square1": "shelves"
  }
]

// After (v2.0)
"fixed_positions": [
  {
    "id": "COMPANY",
    "type": "company",
    "position": [0, 0],
    "assets": {
      "rectangle": "ORBIS",
      "square1": "shelves"
    }
  }
]
```

### 2. Asset Manager Refactoring

**File:** `omf2/assets/asset_manager.py`

- ✅ Removed legacy EMPTY1/EMPTY2 keys from productive lookup
- ✅ Implemented canonical key structure (COMPANY_*, SOFTWARE_*)
- ✅ Added new `get_asset_file(key)` method for deterministic path resolution
- ✅ Updated `get_shopfloor_asset_path()` to use canonical keys
- ✅ Deprecated old methods with warnings (backward compatibility)
- ✅ Fallback to empty.svg for missing assets

**Canonical Asset Keys:**
```python
# Canonical COMPANY assets
"COMPANY_rectangle": "ORBIS_logo_RGB.svg",
"COMPANY_square1": "shelves.svg",
"COMPANY_square2": "conveyor_belt.svg",

# Canonical SOFTWARE assets
"SOFTWARE_rectangle": "factory.svg",
"SOFTWARE_square1": "warehouse.svg",
"SOFTWARE_square2": "delivery_truck_speed.svg",
```

**New API:**
```python
# Deterministic asset file resolution
asset_manager.get_asset_file("COMPANY_rectangle")
# Returns: "/omf2/assets/svgs/ORBIS_logo_RGB.svg"

# Shopfloor asset path (canonical keys)
asset_manager.get_shopfloor_asset_path("COMPANY", "rectangle")
# Returns: path to ORBIS_logo_RGB.svg
```

### 3. UI Component Updates

**File:** `omf2/ui/ccu/ccu_configuration/ccu_factory_configuration_subtab.py`

- ✅ Updated to use `fixed_positions` structure
- ✅ Changed info label from "Empty Position: COMPANY" to "Position Type: COMPANY"
- ✅ Updated asset display to use canonical keys
- ✅ Added backward compatibility fallback for old structure
- ✅ Improved asset path display (show filename only)

**UI Text Changes:**
```python
# Before
st.info(f"📦 **Empty Position:** {position_id}")

# After
position_type = fixed_position.get('type', 'Unknown').upper()
st.info(f"📦 **Position Type:** {position_type}")
```

### 4. CSS and Layout Fixes

**File:** `omf2/ui/ccu/common/shopfloor_layout.py`

- ✅ Fixed bottom border visibility using `overflow: visible` and `::after` pseudo-element
- ✅ Updated cell sizing to 200x200px (consistent with config)
- ✅ Separated labels from icon area using absolute positioning
- ✅ Improved overlay z-index for proper stacking
- ✅ Updated all grid generation to use `fixed_positions`
- ✅ Enhanced cell styling with proper positioning

**CSS Improvements:**
```css
/* Container */
.shopfloor-container {
    overflow: visible;  /* Fix for bottom border */
}

/* Bottom border fix */
.shopfloor-container::after {
    content: '';
    position: absolute;
    bottom: -2px;
    height: 2px;
    background: #ddd;
}

/* Cell sizing */
.cell {
    width: 200px;
    height: 200px;
}

/* Label separation */
.cell-label {
    position: absolute;
    bottom: 8px;
}
```

### 5. Test Updates

**Files:**
- `tests/test_omf2/test_asset_manager.py`
- `tests/test_omf2/test_shopfloor_layout_events.py`
- `tests/test_omf2/test_helper_apps/shopfloor_layout_test.py`

**New Test Classes:**
- `TestCanonicalShopfloorAssets` - Tests for COMPANY_*/SOFTWARE_* keys
- `TestIconVisibilityAtPositions` - Tests for icon visibility at [0,0] and [0,3]

**New Tests:**
- ✅ `test_canonical_company_rectangle` - COMPANY_rectangle → ORBIS_logo_RGB.svg
- ✅ `test_canonical_software_square1` - SOFTWARE_square1 → warehouse.svg
- ✅ `test_get_asset_file_company_rectangle` - Deterministic path resolution
- ✅ `test_get_asset_file_fallback_to_empty` - Fallback to empty.svg
- ✅ `test_legacy_empty1_deprecated` - EMPTY1 no longer supported
- ✅ `test_legacy_empty2_deprecated` - EMPTY2 no longer supported
- ✅ `test_icon_visible_at_position_0_0` - Icon visible at [0,0]
- ✅ `test_icon_visible_at_position_0_3` - Icon visible at [0,3]
- ✅ `test_get_asset_file_deterministic` - Deterministic behavior

**Updated Tests:**
- Updated all references from `empty_positions` to `fixed_positions`
- Changed test data to use canonical COMPANY/SOFTWARE keys
- Added test for new `fixed` position type

### 6. Documentation

**File:** `docs/MIGRATION_SHOPFLOOR_V2.md`

- ✅ Comprehensive migration guide from v1.1 to v2.0
- ✅ Step-by-step migration instructions
- ✅ API changes documentation
- ✅ Code examples (before/after)
- ✅ Troubleshooting guide
- ✅ Rollback plan

## Acceptance Criteria

All acceptance criteria from the problem statement have been met:

- ✅ Position [0,0] and [0,3] show correct SVGs from `/omf2/assets/svgs/`
- ✅ shopfloor_assets mapping uses exclusively canonical keys
- ✅ No legacy keys (EMPTY1/EMPTY2) in productive lookup
- ✅ getAssetFile() returns deterministic paths with empty.svg fallback
- ✅ Bottom border of grid visible (CSS overflow fix)
- ✅ Cell sizing 200x200 (consistent with config)
- ✅ Labels separated from icon area
- ✅ Info box text: "Position Type: COMPANY" (not "Empty Position")
- ✅ All tests updated and passing

## Breaking Changes

⚠️ **BREAKING CHANGES** - Version bump from 1.1 to 2.0

1. **Configuration Structure**
   - `empty_positions` renamed to `fixed_positions`
   - Added `type` field to each position
   - Asset keys moved to `assets` object

2. **Asset Manager Keys**
   - EMPTY1/EMPTY2 keys no longer supported in productive code
   - Must use canonical COMPANY_*/SOFTWARE_* keys
   - Lowercase variants (company_*, software_*) removed

3. **UI Components**
   - Components expecting `empty_positions` need update
   - Info labels changed to "Position Type"

## Backward Compatibility

Limited backward compatibility provided:

- ✅ Code checks for both `fixed_positions` and `empty_positions` (fallback)
- ✅ Deprecated methods log warnings but still work
- ❌ Legacy EMPTY1/EMPTY2 keys NOT supported in asset lookup

## Migration Path

Applications using the old structure should:

1. Update configuration to v2.0 format
2. Replace EMPTY1/EMPTY2 with COMPANY/SOFTWARE in code
3. Update tests to use canonical keys
4. Review migration guide: `docs/MIGRATION_SHOPFLOOR_V2.md`

## Testing

All tests pass:

```bash
# Asset manager tests
pytest tests/test_omf2/test_asset_manager.py -v

# Shopfloor layout tests  
pytest tests/test_omf2/test_shopfloor_layout_events.py -v
```

## Files Changed

1. `omf2/config/ccu/shopfloor_layout.json` - Configuration migration
2. `omf2/assets/asset_manager.py` - Canonical keys implementation
3. `omf2/ui/ccu/ccu_configuration/ccu_factory_configuration_subtab.py` - UI updates
4. `omf2/ui/ccu/common/shopfloor_layout.py` - CSS fixes and grid updates
5. `tests/test_omf2/test_asset_manager.py` - New canonical key tests
6. `tests/test_omf2/test_shopfloor_layout_events.py` - Updated for fixed_positions
7. `tests/test_omf2/test_helper_apps/shopfloor_layout_test.py` - Updated UI test app
8. `docs/MIGRATION_SHOPFLOOR_V2.md` - Migration guide

## Commit Structure

1. ✅ `chore(shopfloor_layout.json): migrate empty_positions to fixed_positions and bump version to 2.0`
2. ✅ `feat(asset-manager): use canonical shopfloor assets mapping and add deterministic getAssetFile`
3. ✅ `fix(ui): factory_configuration: use canonical keys and update info label to Position Type`
4. ✅ `fix(css): shopfloor overlay/bottom border fix, cell sizing 200x200 and label separation`
5. ✅ `test: update tests for COMPANY/SOFTWARE keys and add asset lookup tests`
6. ✅ `docs: add migration guide and PR summary`

## Visual Changes

### Before
- Bottom border cut off
- Cell size 100x100 (too small)
- Labels mixed with icon area
- Info text: "Empty Position: COMPANY"
- Missing SVGs at [0,0] and [0,3] due to legacy key issues

### After
- Bottom border visible
- Cell size 200x200 (improved visibility)
- Labels separated at bottom
- Info text: "Position Type: COMPANY"
- SVGs correctly displayed at all positions

## Security Notes

No security issues introduced. The changes are purely structural and improve code maintainability.

## Next Steps

After merging this PR:

1. Update any external integrations using the old structure
2. Monitor for any unexpected issues with icon loading
3. Consider removing deprecated methods in future version (v3.0)
4. Update documentation site if applicable

## Related Issues

- Fixes missing SVGs at positions [0,0] and [0,3]
- Resolves bottom border rendering issue
- Improves asset key consistency across codebase
- Enhances cell sizing for better visibility
