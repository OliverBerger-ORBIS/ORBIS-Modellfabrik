#!/usr/bin/env python3
"""
Shopfloor Display Module
========================

Provides registry and helper functions for shopfloor display configuration.
Builds registry from shopfloor_layout.json and exposes helpers for:
- Dropdown key selection (get_dropdown_keys)
- Display region resolution (get_display_region_for_key)
- Position-to-key lookup (find_keys_for_position)
- Asset path resolution (resolve_asset_path)

This module decouples display logic from configuration and enables
name-based module selection with compound region highlighting.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from omf2.common.logger import get_logger

logger = get_logger(__name__)

# Singleton registry
_registry: Optional[Dict] = None


def _build_registry() -> Dict:
    """Build shopfloor display registry from shopfloor_layout.json
    
    Returns:
        Registry dict with entries for each module, fixed position, and intersection
        Each entry contains: id, type, position, display_region, click_keys, etc.
    """
    import json
    
    registry = {}
    
    # Load shopfloor_layout.json
    config_path = Path(__file__).parent / "shopfloor_layout.json"
    if not config_path.exists():
        logger.error(f"shopfloor_layout.json not found at {config_path}")
        return registry
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load shopfloor_layout.json: {e}")
        return registry
    
    # Process modules
    modules = config.get("modules", [])
    for module in modules:
        module_id = module.get("id")
        module_type = module.get("type")
        position = tuple(module.get("position", []))
        attached_assets = module.get("attached_assets", [])
        display_variants = module.get("display_variants", {})
        
        # Default display region is the module position itself
        default_region = display_variants.get("default", [position])
        cell_only_region = display_variants.get("cell_only", [position])
        
        registry[module_id] = {
            "id": module_id,
            "type": module_type,
            "position": position,
            "attached_assets": attached_assets,
            "display_variants": display_variants,
            "default_region": [tuple(pos) for pos in default_region],
            "cell_only_region": [tuple(pos) for pos in cell_only_region],
            "is_module": True,
            "is_fixed": False,
        }
    
    # Process fixed positions (COMPANY, SOFTWARE)
    fixed_positions = config.get("fixed_positions", [])
    for fixed in fixed_positions:
        fixed_id = fixed.get("id")
        fixed_type = fixed.get("type")
        position = tuple(fixed.get("position", []))
        assets = fixed.get("assets", {})
        display_variants = fixed.get("display_variants", {})
        
        # Default display region for fixed positions
        default_region = display_variants.get("default", [position])
        rectangle_only_region = display_variants.get("rectangle_only", [position])
        
        # Create base entry for fixed position (semantic key)
        registry[fixed_id] = {
            "id": fixed_id,
            "type": fixed_type,
            "position": position,
            "assets": assets,
            "display_variants": display_variants,
            "default_region": [tuple(pos) for pos in default_region],
            "rectangle_only_region": [tuple(pos) for pos in rectangle_only_region],
            "is_module": False,
            "is_fixed": True,
        }
        
        # Create explicit *_RECT key for click behavior (rectangle-only selection)
        rect_key = f"{fixed_id}_RECT"
        registry[rect_key] = {
            "id": rect_key,
            "type": f"{fixed_type}_rect",
            "position": position,
            "assets": assets,
            "display_variants": {"default": [position]},
            "default_region": [position],
            "rectangle_only_region": [position],
            "is_module": False,
            "is_fixed": True,
            "is_rect_only": True,
        }
    
    # Process intersections
    intersections = config.get("intersections", [])
    for intersection in intersections:
        intersection_id = intersection.get("id")
        position = tuple(intersection.get("position", []))
        
        # Intersection display name
        display_id = f"INTERSECTION-{intersection_id}"
        
        registry[display_id] = {
            "id": display_id,
            "type": "intersection",
            "position": position,
            "display_variants": {"default": [position]},
            "default_region": [position],
            "is_module": False,
            "is_fixed": False,
            "is_intersection": True,
        }
    
    logger.info(f"Built shopfloor display registry with {len(registry)} entries")
    return registry


def get_shopfloor_display() -> 'ShopfloorDisplay':
    """Get singleton ShopfloorDisplay instance"""
    return ShopfloorDisplay()


class ShopfloorDisplay:
    """Shopfloor display helper class"""
    
    def __init__(self):
        """Initialize ShopfloorDisplay"""
        global _registry
        if _registry is None:
            _registry = _build_registry()
        self.registry = _registry
    
    def get_dropdown_keys(self) -> List[Tuple[str, str]]:
        """Get list of (key, label) tuples for dropdown selection
        
        Excludes *_RECT entries (those are for click behavior only).
        
        Returns:
            List of (key, label) tuples sorted by semantic order
        """
        keys = []
        
        # Order: modules first, then fixed positions (COMPANY, SOFTWARE), then intersections
        for key, entry in self.registry.items():
            # Skip *_RECT entries
            if key.endswith("_RECT"):
                continue
            
            # Get display label
            entry_id = entry.get("id")
            entry_type = entry.get("type", "unknown")
            
            if entry.get("is_module"):
                label = f"{entry_id} ({entry_type})"
            elif entry.get("is_intersection"):
                label = entry_id
            elif entry.get("is_fixed"):
                label = f"{entry_id} (Fixed Position)"
            else:
                label = entry_id
            
            keys.append((key, label))
        
        # Sort: modules first, then fixed, then intersections
        def sort_key(item):
            key, label = item
            entry = self.registry.get(key, {})
            if entry.get("is_module"):
                return (0, key)
            elif entry.get("is_fixed"):
                return (1, key)
            else:
                return (2, key)
        
        keys.sort(key=sort_key)
        return keys
    
    def get_display_region_for_key(self, key: str, variant: Optional[str] = None) -> List[Tuple[int, int]]:
        """Get display region (list of grid positions) for a given key
        
        Args:
            key: Module/position key (e.g., "HBW", "COMPANY", "INTERSECTION-1")
            variant: Display variant (e.g., "default", "cell_only", "rectangle_only")
                    If None, uses "default"
        
        Returns:
            List of (row, col) tuples representing the display region
            Returns empty list if key not found
        """
        entry = self.registry.get(key)
        if not entry:
            logger.warning(f"Key not found in registry: {key}")
            return []
        
        # Determine which region to use
        if variant is None:
            variant = "default"
        
        # Get region from display_variants
        display_variants = entry.get("display_variants", {})
        region = display_variants.get(variant)
        
        if region is not None:
            # Convert to list of tuples if needed
            return [tuple(pos) if isinstance(pos, list) else pos for pos in region]
        
        # Fallback to default_region or single position
        if variant == "default" and "default_region" in entry:
            return entry["default_region"]
        
        # Ultimate fallback: single position
        position = entry.get("position")
        if position:
            return [position]
        
        return []
    
    def find_keys_for_position(self, pos: Tuple[int, int], mode: str = 'click') -> List[str]:
        """Find all keys that contain the given position
        
        Args:
            pos: Grid position as (row, col) tuple
            mode: 'click' or 'config'
                  - 'click': prefers *_RECT keys for fixed positions (click on rectangle only)
                  - 'config': prefers semantic keys (compound HBW/DPS selection)
        
        Returns:
            List of keys that contain this position, ordered by preference
        """
        matching_keys = []
        
        for key, entry in self.registry.items():
            # Check if position is in default_region
            default_region = entry.get("default_region", [])
            if pos in default_region:
                matching_keys.append(key)
        
        # Filter and sort based on mode
        if mode == 'click':
            # Click mode: prefer *_RECT keys for fixed positions
            rect_keys = [k for k in matching_keys if k.endswith("_RECT")]
            other_keys = [k for k in matching_keys if not k.endswith("_RECT")]
            return rect_keys + other_keys
        else:
            # Config mode: prefer semantic keys (HBW, DPS, COMPANY, SOFTWARE)
            # Exclude *_RECT keys
            semantic_keys = [k for k in matching_keys if not k.endswith("_RECT")]
            # Sort: modules first, then fixed positions
            def sort_key(k):
                entry = self.registry.get(k, {})
                if entry.get("is_module"):
                    return (0, k)
                elif entry.get("is_fixed"):
                    return (1, k)
                else:
                    return (2, k)
            semantic_keys.sort(key=sort_key)
            return semantic_keys
    
    def resolve_asset_path(self, logical_attached_key: str) -> Optional[str]:
        """Resolve logical attached asset key to SVG file path
        
        Args:
            logical_attached_key: Logical key (e.g., "HBW_SQUARE1", "DPS_SQUARE2")
        
        Returns:
            Path to SVG file or None if not found
        """
        try:
            from omf2.assets import get_asset_manager
            asset_manager = get_asset_manager()
            return asset_manager.get_asset_file(logical_attached_key)
        except Exception as e:
            logger.error(f"Failed to resolve asset path for {logical_attached_key}: {e}")
            return None


# Convenience functions for backward compatibility
def get_dropdown_keys() -> List[Tuple[str, str]]:
    """Get list of (key, label) tuples for dropdown selection"""
    return get_shopfloor_display().get_dropdown_keys()


def get_display_region_for_key(key: str, variant: Optional[str] = None) -> List[Tuple[int, int]]:
    """Get display region for a given key"""
    return get_shopfloor_display().get_display_region_for_key(key, variant)


def find_keys_for_position(pos: Tuple[int, int], mode: str = 'click') -> List[str]:
    """Find keys for a given position"""
    return get_shopfloor_display().find_keys_for_position(pos, mode)


def resolve_asset_path(logical_attached_key: str) -> Optional[str]:
    """Resolve logical attached asset key to SVG file path"""
    return get_shopfloor_display().resolve_asset_path(logical_attached_key)
