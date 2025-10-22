#!/usr/bin/env python3
"""
Unit Tests für OMF2 Asset Manager
=================================

Testet die wesentlichen Asset-Manager-Funktionalitäten:
- SVG-Laden mit CSS-Scoping
- Module-Icon-Verwaltung
- Error-Handling
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).parent.parent.parent))

from omf2.assets.asset_manager import OMF2AssetManager, get_asset_manager, scope_svg_styles


class TestScopeSvgStyles(unittest.TestCase):
    """Tests für die CSS-Scoping-Funktion"""

    def test_scope_svg_with_style_section(self):
        """Test: SVG mit Style-Sektion wird korrekt gescoped"""
        svg_content = """
        <svg viewBox="0 0 100 100">
            <style>
                .cls-1 { fill: red; }
                .cls-2 { stroke: blue; }
            </style>
            <circle class="cls-1" />
            <rect class="cls-2" />
        </svg>
        """

        result = scope_svg_styles(svg_content)

        # Prüfe dass ein eindeutige ID generiert wurde
        self.assertIn("svg-", result)

        # Prüfe dass CSS-Selektoren gescoped wurden
        self.assertIn("#svg-", result)
        self.assertIn(".cls-1", result)  # Original-Selektor sollte noch da sein

        # Prüfe dass SVG in Gruppe eingebettet wurde
        self.assertIn('<g id="svg-', result)
        self.assertIn("</g>", result)

    def test_scope_svg_without_style_section(self):
        """Test: SVG ohne Style-Sektion bleibt unverändert"""
        svg_content = """
        <svg viewBox="0 0 100 100">
            <circle fill="red" />
            <rect stroke="blue" />
        </svg>
        """

        result = scope_svg_styles(svg_content)

        # Sollte unverändert zurückgegeben werden
        self.assertEqual(svg_content.strip(), result.strip())

    def test_scope_svg_unique_ids(self):
        """Test: Jeder Aufruf generiert eindeutige IDs"""
        svg_content = """
        <svg viewBox="0 0 100 100">
            <style>.cls-1 { fill: red; }</style>
            <circle class="cls-1" />
        </svg>
        """

        result1 = scope_svg_styles(svg_content)
        result2 = scope_svg_styles(svg_content)

        # Extrahiere IDs
        id1 = re.search(r'id="(svg-[^"]*)"', result1).group(1)
        id2 = re.search(r'id="(svg-[^"]*)"', result2).group(1)

        # IDs sollten unterschiedlich sein
        self.assertNotEqual(id1, id2)

    def test_scope_svg_multiple_selectors(self):
        """Test: Mehrere CSS-Selektoren werden korrekt gescoped"""
        svg_content = """
        <svg viewBox="0 0 100 100">
            <style>
                .cls-1, .cls-2 { fill: red; }
                #id1, .cls-3 { stroke: blue; }
            </style>
        </svg>
        """

        result = scope_svg_styles(svg_content)

        # Prüfe dass alle Selektoren gescoped wurden
        self.assertIn("#svg-", result)
        self.assertIn(".cls-1", result)
        self.assertIn(".cls-2", result)


class TestAssetManagerInitialization(unittest.TestCase):
    """Tests für Asset-Manager Initialisierung"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.assets_dir.mkdir()

        # Mock assets_dir
        with patch.object(OMF2AssetManager, "__init__", lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir
            self.asset_manager.svgs_dir = self.assets_dir / "svgs"

    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test: Asset-Manager wird korrekt initialisiert"""
        with patch.object(OMF2AssetManager, "__init__", lambda x: None):
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
        with patch.object(OMF2AssetManager, "__init__", lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir

    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def _create_test_svg(self, filename: str, content: str = None):
        """Hilfsmethode: Erstellt Test-SVG-Datei"""
        if content is None:
            content = """
            <svg viewBox="0 0 100 100">
                <style>.cls-1 { fill: red; }</style>
                <circle class="cls-1" />
            </svg>
            """

        svg_path = self.workpiece_dir / filename
        svg_path.write_text(content, encoding="utf-8")
        return svg_path

    def test_get_workpiece_svg_valid_combination(self):
        """Test: Gültige Farbe-Pattern-Kombination"""
        self._create_test_svg("blue_product.svg")

        result = self.asset_manager.get_workpiece_svg("BLUE", "product")

        self.assertIsNotNone(result)
        self.assertIn("<svg", result)
        self.assertIn("svg-", result)  # CSS-Scoping sollte angewendet worden sein

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
        self.assertIn("<svg", result)
        self.assertIn("svg-", result)  # CSS-Scoping sollte angewendet worden sein

    def test_get_workpiece_palett_not_found(self):
        """Test: Palett-SVG nicht gefunden"""
        result = self.asset_manager.get_workpiece_palett()
        self.assertIsNone(result)

    def test_get_workpiece_svg_content_method(self):
        """Test: get_workpiece_svg_content Methode"""
        self._create_test_svg("blue_unprocessed.svg")

        result = self.asset_manager.get_workpiece_svg_content("BLUE", "unprocessed")

        self.assertIsNotNone(result)
        self.assertIn("<svg", result)


class TestModuleIconMethods(unittest.TestCase):
    """Tests für Module-Icon-Methoden"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.svgs_dir = self.assets_dir / "svgs"
        self.svgs_dir.mkdir(parents=True)

        # Mock assets_dir
        with patch.object(OMF2AssetManager, "__init__", lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir
            self.asset_manager.svgs_dir = self.svgs_dir
            self.asset_manager.module_icons = {
                "HBW": "ic_ft_hbw.svg",
                "DRILL": "ic_ft_drill.svg",
                "MILL": "ic_ft_mill.svg",
            }

    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def _create_test_icon(self, filename: str):
        """Hilfsmethode: Erstellt Test-Icon-Datei"""
        icon_path = self.svgs_dir / filename
        icon_path.write_text('<svg viewBox="0 0 24 24"><circle /></svg>', encoding="utf-8")
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


class TestCanonicalShopfloorAssets(unittest.TestCase):
    """Tests für Canonical Shopfloor Assets (COMPANY_*, SOFTWARE_*)"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.svgs_dir = self.assets_dir / "svgs"
        self.svgs_dir.mkdir(parents=True)

        # Create test SVG files
        self._create_test_svg("ORBIS_logo_RGB.svg")
        self._create_test_svg("shelves.svg")
        self._create_test_svg("conveyor_belt.svg")
        self._create_test_svg("factory.svg")
        self._create_test_svg("warehouse.svg")
        self._create_test_svg("delivery_truck_speed.svg")
        self._create_test_svg("empty.svg")

        # Mock assets_dir
        with patch.object(OMF2AssetManager, "__init__", lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir
            self.asset_manager.svgs_dir = self.svgs_dir
            # Setup canonical shopfloor assets mapping
            self.asset_manager.module_icons = {
                "COMPANY_rectangle": str(self.svgs_dir / "ORBIS_logo_RGB.svg"),
                "COMPANY_square1": str(self.svgs_dir / "shelves.svg"),
                "COMPANY_square2": str(self.svgs_dir / "conveyor_belt.svg"),
                "SOFTWARE_rectangle": str(self.svgs_dir / "factory.svg"),
                "SOFTWARE_square1": str(self.svgs_dir / "warehouse.svg"),
                "SOFTWARE_square2": str(self.svgs_dir / "delivery_truck_speed.svg"),
                "ORBIS": str(self.svgs_dir / "ORBIS_logo_RGB.svg"),
                "DSP": str(self.svgs_dir / "factory.svg"),
            }

    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def _create_test_svg(self, filename: str):
        """Hilfsmethode: Erstellt Test-SVG-Datei"""
        svg_path = self.svgs_dir / filename
        svg_path.write_text('<svg viewBox="0 0 24 24"><circle /></svg>', encoding="utf-8")
        return svg_path

    def test_canonical_company_rectangle(self):
        """Test: COMPANY_rectangle liefert ORBIS_logo_RGB.svg"""
        result = self.asset_manager.get_module_icon_path("COMPANY_rectangle")
        self.assertIsNotNone(result)
        self.assertIn("ORBIS_logo_RGB.svg", str(result))

    def test_canonical_company_square1(self):
        """Test: COMPANY_square1 liefert shelves.svg"""
        result = self.asset_manager.get_module_icon_path("COMPANY_square1")
        self.assertIsNotNone(result)
        self.assertIn("shelves.svg", str(result))

    def test_canonical_company_square2(self):
        """Test: COMPANY_square2 liefert conveyor_belt.svg"""
        result = self.asset_manager.get_module_icon_path("COMPANY_square2")
        self.assertIsNotNone(result)
        self.assertIn("conveyor_belt.svg", str(result))

    def test_canonical_software_rectangle(self):
        """Test: SOFTWARE_rectangle liefert factory.svg"""
        result = self.asset_manager.get_module_icon_path("SOFTWARE_rectangle")
        self.assertIsNotNone(result)
        self.assertIn("factory.svg", str(result))

    def test_canonical_software_square1(self):
        """Test: SOFTWARE_square1 liefert warehouse.svg"""
        result = self.asset_manager.get_module_icon_path("SOFTWARE_square1")
        self.assertIsNotNone(result)
        self.assertIn("warehouse.svg", str(result))

    def test_canonical_software_square2(self):
        """Test: SOFTWARE_square2 liefert delivery_truck_speed.svg"""
        result = self.asset_manager.get_module_icon_path("SOFTWARE_square2")
        self.assertIsNotNone(result)
        self.assertIn("delivery_truck_speed.svg", str(result))

    def test_get_asset_file_company_rectangle(self):
        """Test: get_asset_file für COMPANY_rectangle"""
        result = self.asset_manager.get_asset_file("COMPANY_rectangle")
        self.assertIsNotNone(result)
        self.assertIn("ORBIS_logo_RGB.svg", result)

    def test_get_asset_file_software_square1(self):
        """Test: get_asset_file für SOFTWARE_square1"""
        result = self.asset_manager.get_asset_file("SOFTWARE_square1")
        self.assertIsNotNone(result)
        self.assertIn("warehouse.svg", result)

    def test_get_asset_file_fallback_to_empty(self):
        """Test: get_asset_file fallback zu empty.svg bei unbekanntem Key"""
        result = self.asset_manager.get_asset_file("UNKNOWN_KEY")
        self.assertIsNotNone(result)
        self.assertIn("empty.svg", result)

    def test_get_shopfloor_asset_path_company(self):
        """Test: get_shopfloor_asset_path für COMPANY assets"""
        result = self.asset_manager.get_shopfloor_asset_path("COMPANY", "rectangle")
        self.assertIsNotNone(result)
        self.assertIn("ORBIS_logo_RGB.svg", str(result))

    def test_get_shopfloor_asset_path_software(self):
        """Test: get_shopfloor_asset_path für SOFTWARE assets"""
        result = self.asset_manager.get_shopfloor_asset_path("SOFTWARE", "square1")
        self.assertIsNotNone(result)
        self.assertIn("warehouse.svg", str(result))

    def test_legacy_empty1_deprecated(self):
        """Test: EMPTY1 keys are no longer supported in productive code"""
        # Legacy EMPTY1 should not work anymore
        result = self.asset_manager.get_module_icon_path("EMPTY1")
        self.assertIsNone(result)

    def test_legacy_empty2_deprecated(self):
        """Test: EMPTY2 keys are no longer supported in productive code"""
        # Legacy EMPTY2 should not work anymore
        result = self.asset_manager.get_module_icon_path("EMPTY2")
        self.assertIsNone(result)


class TestIconVisibilityAtPositions(unittest.TestCase):
    """Tests für Icon-Visibility an Positionen [0,0] und [0,3]"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.svgs_dir = self.assets_dir / "svgs"
        self.svgs_dir.mkdir(parents=True)

        # Create test SVG files for positions [0,0] and [0,3]
        self._create_test_svg("ORBIS_logo_RGB.svg")
        self._create_test_svg("factory.svg")
        self._create_test_svg("empty.svg")

        # Mock assets_dir
        with patch.object(OMF2AssetManager, "__init__", lambda x: None):
            self.asset_manager = OMF2AssetManager()
            self.asset_manager.assets_dir = self.assets_dir
            self.asset_manager.svgs_dir = self.svgs_dir
            # Setup mapping for position [0,0] (COMPANY) and [0,3] (SOFTWARE)
            self.asset_manager.module_icons = {
                "COMPANY_rectangle": str(self.svgs_dir / "ORBIS_logo_RGB.svg"),
                "SOFTWARE_rectangle": str(self.svgs_dir / "factory.svg"),
            }

    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def _create_test_svg(self, filename: str):
        """Hilfsmethode: Erstellt Test-SVG-Datei"""
        svg_path = self.svgs_dir / filename
        svg_path.write_text('<svg viewBox="0 0 24 24"><circle /></svg>', encoding="utf-8")
        return svg_path

    def test_icon_visible_at_position_0_0(self):
        """Test: Icon ist sichtbar an Position [0,0] (COMPANY)"""
        # Position [0,0] sollte COMPANY_rectangle icon haben
        result = self.asset_manager.get_asset_file("COMPANY_rectangle")
        self.assertIsNotNone(result)
        self.assertTrue(Path(result).exists())
        self.assertIn("ORBIS_logo_RGB.svg", result)

    def test_icon_visible_at_position_0_3(self):
        """Test: Icon ist sichtbar an Position [0,3] (SOFTWARE)"""
        # Position [0,3] sollte SOFTWARE_rectangle icon haben
        result = self.asset_manager.get_asset_file("SOFTWARE_rectangle")
        self.assertIsNotNone(result)
        self.assertTrue(Path(result).exists())
        self.assertIn("factory.svg", result)

    def test_get_asset_file_deterministic(self):
        """Test: get_asset_file liefert deterministische Pfade"""
        # Mehrfache Aufrufe sollten denselben Pfad liefern
        result1 = self.asset_manager.get_asset_file("COMPANY_rectangle")
        result2 = self.asset_manager.get_asset_file("COMPANY_rectangle")
        self.assertEqual(result1, result2)


class TestErrorHandling(unittest.TestCase):
    """Tests für Error-Handling"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.assets_dir = Path(self.temp_dir) / "assets"
        self.workpiece_dir = self.assets_dir / "workpiece"
        self.workpiece_dir.mkdir(parents=True)

        with patch.object(OMF2AssetManager, "__init__", lambda x: None):
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
        svg_path.write_bytes(b"\xff\xfe\x00\x00")  # Ungültiges UTF-8

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


if __name__ == "__main__":
    # Test-Suite ausführen
    unittest.main(verbosity=2)
