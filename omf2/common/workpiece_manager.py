#!/usr/bin/env python3
"""
WorkpieceManager Singleton - Zentrale Utility für Registry v2 Workpieces
"""

import logging
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class WorkpieceManager:
    """
    Singleton für Workpiece Management
    
    Lädt Registry v2 Workpieces ohne Schema-Validierung.
    Bietet Methoden zum Laden, Filtern und Abrufen von Werkstück-Daten.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, registry_path: str = "omf2/registry/"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, registry_path: str = "omf2/registry/"):
        if WorkpieceManager._initialized:
            return
            
        self.registry_path = Path(registry_path)
        self.workpieces = {}
        self.colors = []
        self.quality_checks = []
        
        # Registry v2 laden
        self._load_registry()
        WorkpieceManager._initialized = True
        
        logger.info("🔧 WorkpieceManager Singleton initialized")
    
    def _load_registry(self):
        """Lädt alle Registry v2 Workpiece-Komponenten"""
        try:
            # Workpieces laden
            workpieces_file = self.registry_path / "workpieces.yml"
            if workpieces_file.exists():
                with open(workpieces_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    # Workpieces sind jetzt als Liste
                    workpieces_list = data.get('workpieces', [])
                    self.workpieces = {}
                    for wp_data in workpieces_list:
                        if isinstance(wp_data, dict) and 'id' in wp_data:
                            workpiece_id = wp_data['id']
                            self.workpieces[workpiece_id] = wp_data
                    self.colors = data.get('colors', [])
                    self.quality_checks = data.get('quality_check_options', [])
            
            logger.info(f"📚 Registry v2 loaded: {len(self.workpieces)} workpieces, {len(self.colors)} colors")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Registry v2: {e}")
            raise
    
    def get_all_workpieces(self) -> Dict[str, Any]:
        """Gibt alle Werkstücke zurück"""
        return self.workpieces
    
    def get_workpieces_by_color(self, color: str) -> List[Dict[str, Any]]:
        """
        Gibt Werkstücke nach Farbe zurück
        
        Args:
            color: Farbe (z.B. "RED", "BLUE", "WHITE")
            
        Returns:
            Liste von Werkstück-Dicts
        """
        result = []
        for workpiece_id, wp_data in self.workpieces.items():
            if wp_data.get('color') == color:
                result.append(wp_data)
        return result
    
    def get_workpieces_by_color_with_nfc(self, color: str) -> Dict[str, Dict[str, Any]]:
        """
        Gibt alle Werkstücke einer bestimmten Farbe mit ID als Key zurück
        
        Args:
            color: Farbe (z.B. "RED", "BLUE", "WHITE")
            
        Returns:
            Dictionary mit ID als Key und Werkstück-Daten als Value
        """
        result = {}
        for workpiece_id, wp_data in self.workpieces.items():
            if wp_data.get('color') == color:
                result[workpiece_id] = wp_data
        return result
    
    def get_workpiece_by_nfc_code(self, nfc_code: str) -> Optional[Dict[str, Any]]:
        """
        Gibt Werkstück nach NFC-Code zurück
        
        Args:
            nfc_code: NFC-Code
            
        Returns:
            Werkstück-Dict oder None
        """
        return self.workpieces.get(nfc_code)
    
    def get_workpiece_by_friendly_id(self, friendly_id: str) -> Optional[Dict[str, Any]]:
        """
        Gibt Werkstück nach friendly_id zurück
        
        Args:
            friendly_id: Friendly ID (z.B. "R1", "B1", "W1")
            
        Returns:
            Werkstück-Dict oder None
        """
        for nfc_code, wp_data in self.workpieces.items():
            if wp_data.get('friendly_id') == friendly_id:
                return wp_data
        return None
    
    def get_workpieces_by_quality(self, quality: str) -> List[Dict[str, Any]]:
        """
        Gibt Werkstücke nach Qualität zurück
        
        Args:
            quality: Qualität (z.B. "OK", "NOT-OK")
            
        Returns:
            Liste von Werkstück-Dicts
        """
        result = []
        for nfc_code, wp_data in self.workpieces.items():
            if wp_data.get('quality_check') == quality:
                result.append(wp_data)
        return result
    
    def get_workpieces_by_enabled(self, enabled: bool = True) -> List[Dict[str, Any]]:
        """
        Gibt Werkstücke nach enabled-Status zurück
        
        Args:
            enabled: Enabled-Status
            
        Returns:
            Liste von Werkstück-Dicts
        """
        result = []
        for nfc_code, wp_data in self.workpieces.items():
            if wp_data.get('enabled', True) == enabled:
                result.append(wp_data)
        return result
    
    def get_available_colors(self) -> List[str]:
        """Gibt verfügbare Farben zurück"""
        return [color.get('id', color) if isinstance(color, dict) else color for color in self.colors]
    
    def get_workpiece_colors(self) -> List[str]:
        """Gibt verfügbare Farben zurück (Kompatibilität)"""
        return self.get_available_colors()
    
    def get_available_quality_checks(self) -> List[str]:
        """Gibt verfügbare Qualitätsprüfungen zurück"""
        return self.quality_checks
    
    def get_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über Werkstücke zurück"""
        stats = {
            'total_workpieces': len(self.workpieces),
            'colors': {},
            'quality_checks': {},
            'enabled': {'enabled': 0, 'disabled': 0}
        }
        
        for nfc_code, wp_data in self.workpieces.items():
            # Farben zählen
            color = wp_data.get('color', 'unknown')
            stats['colors'][color] = stats['colors'].get(color, 0) + 1
            
            # Qualitätsprüfungen zählen
            quality = wp_data.get('quality_check', 'unknown')
            stats['quality_checks'][quality] = stats['quality_checks'].get(quality, 0) + 1
            
            # Enabled-Status zählen
            if wp_data.get('enabled', True):
                stats['enabled']['enabled'] += 1
            else:
                stats['enabled']['disabled'] += 1
        
        return stats
    
    def search_workpieces(self, **filters) -> List[Dict[str, Any]]:
        """
        Sucht Werkstücke nach verschiedenen Filtern
        
        Args:
            **filters: Filter-Parameter (color, quality_check, enabled, etc.)
            
        Returns:
            Liste von Werkstück-Dicts
        """
        result = []
        for nfc_code, wp_data in self.workpieces.items():
            match = True
            for key, value in filters.items():
                if wp_data.get(key) != value:
                    match = False
                    break
            if match:
                result.append(wp_data)
        return result


# Singleton Factory
def get_workpiece_manager(registry_path: str = "omf2/registry/") -> WorkpieceManager:
    """
    Factory-Funktion für WorkpieceManager Singleton
    
    Args:
        registry_path: Pfad zur Registry v2
        
    Returns:
        WorkpieceManager Singleton Instance
    """
    return WorkpieceManager(registry_path)
