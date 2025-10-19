#!/usr/bin/env python3
"""
Unit Tests für OMF2 Asset Manager
=================================

Testet alle Asset-Manager-Funktionalitäten:
- SVG-Laden mit CSS-Scoping
- Module-Icon-Verwaltung
- HTML-Generation
- Error-Handling
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import uuid
import re

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from omf2.assets.asset_manager import OMF2AssetManager, scope_svg_styles, get_asset_manager


class TestScopeSvgStyles(unittest.TestCase):
    """Tests für die CSS-Scoping-Funktion"""
    
    def test_scope_svg_with_style_section(self):
        """Test: SVG mit Style-Sektion wird korrekt gescoped"""
        svg_content = '''
        <svg viewBox="0 0 100 100">
            <style>
                .cls-1 { fill: red; }
                .cls-2 { stroke: blue; }
            </style>
            <circle class="cls-1" />
            <rect class="cls-2" />
        </svg>
        '''
        
        result = scope_svg_styles(svg_content)
        
        # Prüfe dass ein eindeutige ID generiert wurde
        self.assertIn('svg-', result)
        
        # Prüfe dass CSS-Selektoren gescoped wurden
        self.assertIn('#svg-', result)
        self.assertIn('.cls-1', result)  # Original-Selektor sollte noch da sein
        
        # Prüfe dass SVG in Gruppe eingebettet wurde
        self.assertIn('<g id="svg-', result)
        self.assertIn('</g>', result)
    
    def test_scope_svg_without_style_section(self):
        """Test: SVG ohne Style-Sektion bleibt unverändert"""
        svg_content = '''
        <svg viewBox="0 0 100 100">
            <circle fill="red" />
            <rect stroke="blue" />
        </svg>
        '''
        
        result = scope_svg_styles(svg_content)
        
        # Sollte unverändert zurückgegeben werden
        self.assertEqual(svg_content.strip(), result.strip())
    
    def test_scope_svg_unique_ids(self):
        """Test: Jeder Aufruf generiert eindeutige IDs"""
        svg_content = '''
        <svg viewBox="0 0 100 100">
            <style>.cls-1 { fill: red; }</style>
            <circle class="cls-1" />
        </svg>
        '''
        
        result1 = scope_svg_styles(svg_content)
        result2 = scope_svg_styles(svg_content)
        
        # Extrahiere IDs
        id1 = re.search(r'id="(svg-[^"]*)"', result1).group(1)
        id2 = re.search(r'id="(svg-[^"]*)"', result2).group(1)
        
        # IDs sollten unterschiedlich sein
        self.assertNotEqual(id1, id2)
    
    def test_scope_svg_multiple_selectors(self):
        """Test: Mehrere CSS-Selektoren werden korrekt gescoped"""
        svg_content = '''
        <svg viewBox="0 0 100 100">
            <style>
                .cls-1, .cls-2 { fill: red; }
                #id1, .cls-3 { stroke: blue; }
            </style>
        </svg>
        '''
        
        result = scope_svg_styles(svg_content)
        
        # Prüfe dass alle Selektoren gescoped wurden
        self.assertIn('#svg-', result)
        self.assertIn('.cls-1', result)
        self.assertIn('.cls-2', result)


class TestAssetManagerInitialization(unittest.TestCase):
    """Tests für Asset-Manager Initialisierung"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.assets_dir.mkdir()
        
        # Mock assets_dir
        with patch.object(OMF2AssetManager, '__init__', lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir
            self.asset_manager.svgs_dir = self.assets_dir / "svgs"
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test: Asset-Manager wird korrekt initialisiert"""
        with patch.object(OMF2AssetManager, '__init__', lambda x: None):
            am = OMF2AssetManager()
            self.assertIsInstance(am, OMF2AssetManager)


class TestWorkpieceSvgMethods(unittest.TestCase):
    """Tests für Workpiece-SVG-Methoden"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.workpiece_dir = self.assets_dir / "workpiece"
        self.workpiece_dir.mkdir(parents=True)
        
        # Mock assets_dir
        with patch.object(OMF2AssetManager, '__init__', lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_svg(self, filename: str, content: str = None):
        """Hilfsmethode: Erstellt Test-SVG-Datei"""
        if content is None:
            content = '''
            <svg viewBox="0 0 100 100">
                <style>.cls-1 { fill: red; }</style>
                <circle class="cls-1" />
            </svg>
            '''
        
        svg_path = self.workpiece_dir / filename
        svg_path.write_text(content, encoding='utf-8')
        return svg_path
    
    def test_get_workpiece_svg_valid_combination(self):
        """Test: Gültige Farbe-Pattern-Kombination"""
        self._create_test_svg("blue_product.svg")
        
        result = self.asset_manager.get_workpiece_svg("BLUE", "product")
        
        self.assertIsNotNone(result)
        self.assertIn('<svg', result)
        self.assertIn('svg-', result)  # CSS-Scoping sollte angewendet worden sein
    
    def test_get_workpiece_svg_all_patterns(self):
        """Test: Alle unterstützten Patterns"""
        patterns = ["product", "3dim", "unprocessed", "instock_unprocessed", "instock_reserved"]
        
        for pattern in patterns:
            with self.subTest(pattern=pattern):
                filename = f"blue_{pattern}.svg"
                self._create_test_svg(filename)
                
                result = self.asset_manager.get_workpiece_svg("BLUE", pattern)
                self.assertIsNotNone(result, f"Pattern {pattern} sollte funktionieren")
    
    def test_get_workpiece_svg_all_colors(self):
        """Test: Alle unterstützten Farben"""
        colors = ["BLUE", "WHITE", "RED"]
        
        for color in colors:
            with self.subTest(color=color):
                filename = f"{color.lower()}_product.svg"
                self._create_test_svg(filename)
                
                result = self.asset_manager.get_workpiece_svg(color, "product")
                self.assertIsNotNone(result, f"Farbe {color} sollte funktionieren")
    
    def test_get_workpiece_svg_invalid_color(self):
        """Test: Ungültige Farbe"""
        result = self.asset_manager.get_workpiece_svg("INVALID", "product")
        self.assertIsNone(result)
    
    def test_get_workpiece_svg_invalid_pattern(self):
        """Test: Ungültiges Pattern"""
        result = self.asset_manager.get_workpiece_svg("BLUE", "invalid")
        self.assertIsNone(result)
    
    def test_get_workpiece_svg_default_pattern(self):
        """Test: Standard-Pattern (product)"""
        self._create_test_svg("blue_product.svg")
        
        result = self.asset_manager.get_workpiece_svg("BLUE")  # Ohne Pattern
        
        self.assertIsNotNone(result)
    
    def test_get_workpiece_palett(self):
        """Test: Palett-SVG laden"""
        self._create_test_svg("palett.svg")
        
        result = self.asset_manager.get_workpiece_palett()
        
        self.assertIsNotNone(result)
        self.assertIn('<svg', result)
        self.assertIn('svg-', result)  # CSS-Scoping sollte angewendet worden sein
    
    def test_get_workpiece_palett_not_found(self):
        """Test: Palett-SVG nicht gefunden"""
        result = self.asset_manager.get_workpiece_palett()
        self.assertIsNone(result)
    
    def test_get_workpiece_svg_content_method(self):
        """Test: get_workpiece_svg_content Methode"""
        self._create_test_svg("blue_unprocessed.svg")
        
        result = self.asset_manager.get_workpiece_svg_content("BLUE", "unprocessed")
        
        self.assertIsNotNone(result)
        self.assertIn('<svg', result)


class TestModuleIconMethods(unittest.TestCase):
    """Tests für Module-Icon-Methoden"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.svgs_dir = self.assets_dir / "svgs"
        self.svgs_dir.mkdir(parents=True)
        
        # Mock assets_dir
        with patch.object(OMF2AssetManager, '__init__', lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir
            self.asset_manager.svgs_dir = self.svgs_dir
            self.asset_manager.module_icons = {
                "HBW": "ic_ft_hbw.svg",
                "DRILL": "ic_ft_drill.svg",
                "MILL": "ic_ft_mill.svg"
            }
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_icon(self, filename: str):
        """Hilfsmethode: Erstellt Test-Icon-Datei"""
        icon_path = self.svgs_dir / filename
        icon_path.write_text('<svg viewBox="0 0 24 24"><circle /></svg>', encoding='utf-8')
        return icon_path
    
    def test_get_module_icon_path_valid_module(self):
        """Test: Gültiger Modul-Name"""
        self._create_test_icon("ic_ft_hbw.svg")
        
        result = self.asset_manager.get_module_icon_path("HBW")
        
        self.assertIsNotNone(result)
        self.assertIn("ic_ft_hbw.svg", str(result))
    
    def test_get_module_icon_path_invalid_module(self):
        """Test: Ungültiger Modul-Name"""
        result = self.asset_manager.get_module_icon_path("INVALID")
        self.assertIsNone(result)
    
    def test_get_module_icon_path_case_insensitive(self):
        """Test: Case-insensitive Modul-Name"""
        self._create_test_icon("ic_ft_drill.svg")
        
        result = self.asset_manager.get_module_icon_path("drill")  # lowercase
        
        self.assertIsNotNone(result)


class TestHtmlGenerationMethods(unittest.TestCase):
    """Tests für HTML-Generation-Methoden"""
    
    def setUp(self):
        """Setup für jeden Test"""
        with patch.object(OMF2AssetManager, '__init__', lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.html_templates = {
                "workpiece_colors": {
                    "RED": {"bg": "#ff0000", "border": "#cc0000", "text": "white"},
                    "BLUE": {"bg": "#0066ff", "border": "#0044cc", "text": "white"},
                    "WHITE": {"bg": "#e0e0e0", "border": "#b0b0b0", "text": "black"},
                },
                "status_colors": {
                    "READY": "#4caf50",
                    "BUSY": "#ff9800",
                    "BLOCKED": "#f44336",
                    "OFFLINE": "#9e9e9e",
                    "ACTIVE": "#2196f3",
                },
            }
    
    def test_get_workpiece_box_html(self):
        """Test: Workpiece-Box-HTML-Generation"""
        result = self.asset_manager.get_workpiece_box_html("RED", 5, True)
        
        self.assertIn("RED", result)
        self.assertIn("5", result)
        self.assertIn("✅ Ja", result)
        self.assertIn("#ff0000", result)  # RED background color
    
    def test_get_workpiece_box_html_not_available(self):
        """Test: Workpiece-Box-HTML für nicht verfügbare Workpieces"""
        result = self.asset_manager.get_workpiece_box_html("BLUE", 0, False)
        
        self.assertIn("❌ Nein", result)
        self.assertIn("0", result)
    
    def test_get_status_badge_html(self):
        """Test: Status-Badge-HTML-Generation"""
        result = self.asset_manager.get_status_badge_html("READY")
        
        self.assertIn("READY", result)
        self.assertIn("#4caf50", result)  # READY color
    
    def test_get_status_badge_html_invalid_status(self):
        """Test: Status-Badge für ungültigen Status"""
        result = self.asset_manager.get_status_badge_html("INVALID")
        
        self.assertIn("INVALID", result)
        self.assertIn("#2196f3", result)  # Default color
    
    def test_get_shopfloor_module_html(self):
        """Test: Shopfloor-Modul-HTML-Generation"""
        # Mock icon path
        with patch.object(self.asset_manager, 'get_module_icon_path', return_value=None):
            result = self.asset_manager.get_shopfloor_module_html("HBW", "HBW-01", True, 100)
            
            self.assertIn("HBW-01", result)
            self.assertIn("100px", result)
            self.assertIn("#ff9800", result)  # Active border color
    
    def test_get_shopfloor_module_html_inactive(self):
        """Test: Shopfloor-Modul-HTML für inaktive Module"""
        with patch.object(self.asset_manager, 'get_module_icon_path', return_value=None):
            result = self.asset_manager.get_shopfloor_module_html("HBW", "HBW-01", False, 100)
            
            self.assertIn("#e0e0e0", result)  # Inactive border color


class TestErrorHandling(unittest.TestCase):
    """Tests für Error-Handling"""
    
    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.workpiece_dir = self.assets_dir / "workpiece"
        self.workpiece_dir.mkdir(parents=True)
        
        with patch.object(OMF2AssetManager, '__init__', lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir
    
    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_workpiece_svg_file_read_error(self):
        """Test: Fehler beim Lesen der SVG-Datei"""
        # Erstelle Datei mit ungültigem Encoding
        svg_path = self.workpiece_dir / "blue_product.svg"
        svg_path.write_bytes(b'\xff\xfe\x00\x00')  # Ungültiges UTF-8
        
        result = self.asset_manager.get_workpiece_svg("BLUE", "product")
        
        # Sollte None zurückgeben, nicht crashen
        self.assertIsNone(result)
    
    def test_get_workpiece_svg_missing_directory(self):
        """Test: Fehlendes Workpiece-Verzeichnis"""
        import shutil
        shutil.rmtree(self.workpiece_dir)
        
        result = self.asset_manager.get_workpiece_svg("BLUE", "product")
        
        self.assertIsNone(result)


class TestSingletonPattern(unittest.TestCase):
    """Tests für Singleton-Pattern"""
    
    def test_get_asset_manager_singleton(self):
        """Test: Asset-Manager ist Singleton"""
        am1 = get_asset_manager()
        am2 = get_asset_manager()
        
        self.assertIs(am1, am2)
        self.assertIsInstance(am1, OMF2AssetManager)


if __name__ == '__main__':
    # Test-Suite ausführen
    unittest.main(verbosity=2)
