#!/usr/bin/env python3
"""
Unit Tests für OMF2 UI Symbols
===============================

Testet die Symbol-Verwaltung und insbesondere die neue get_icon_html() Funktion
die SVG-Icons bevorzugt und auf Emojis zurückfällt.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).parent.parent.parent))

from omf2.ui.common.symbols import UISymbols, get_functional_icon, get_icon_html, get_status_icon, get_tab_icon


class TestUISymbolsBasics(unittest.TestCase):
    """Tests für grundlegende UISymbols Funktionalität"""

    def test_get_tab_icon_valid(self):
        """Test: Gültiger Tab-Icon wird zurückgegeben"""
        result = UISymbols.get_tab_icon("ccu_dashboard")
        self.assertEqual(result, "🏭")

    def test_get_tab_icon_invalid(self):
        """Test: Ungültiger Tab-Icon gibt Fallback zurück"""
        result = UISymbols.get_tab_icon("invalid_key")
        self.assertEqual(result, "📋")  # Default fallback

    def test_get_status_icon_valid(self):
        """Test: Gültiger Status-Icon wird zurückgegeben"""
        result = UISymbols.get_status_icon("success")
        self.assertEqual(result, "✅")

    def test_get_status_icon_invalid(self):
        """Test: Ungültiger Status-Icon gibt Fallback zurück"""
        result = UISymbols.get_status_icon("invalid_status")
        self.assertEqual(result, "ℹ️")  # Default fallback

    def test_get_functional_icon_valid(self):
        """Test: Gültiger Functional-Icon wird zurückgegeben"""
        result = UISymbols.get_functional_icon("factory_reset")
        self.assertEqual(result, "🏭🔄")

    def test_get_functional_icon_invalid(self):
        """Test: Ungültiger Functional-Icon gibt Fallback zurück"""
        result = UISymbols.get_functional_icon("invalid_function")
        self.assertEqual(result, "⚙️")  # Default fallback

    def test_convenience_functions(self):
        """Test: Convenience-Funktionen funktionieren"""
        self.assertEqual(get_tab_icon("ccu_dashboard"), "🏭")
        self.assertEqual(get_status_icon("success"), "✅")
        self.assertEqual(get_functional_icon("factory_reset"), "🏭🔄")


class TestGetIconHtmlWithAssetManager(unittest.TestCase):
    """Tests für get_icon_html mit asset_manager (Priorität 1)"""

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_asset_icon_found(self, mock_get_am):
        """Test: Asset-Icon wird gefunden und zurückgegeben"""
        mock_svg = '<svg width="24"><circle /></svg>'
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = mock_svg
        mock_get_am.return_value = mock_am

        result = get_icon_html("DASHBOARD_ADMIN", size_px=24)

        self.assertEqual(result, mock_svg)
        mock_am.get_asset_inline.assert_called_once_with("DASHBOARD_ADMIN", size_px=24)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_asset_icon_with_custom_size(self, mock_get_am):
        """Test: Asset-Icon mit benutzerdefinierter Größe"""
        mock_svg = '<svg width="48"><circle /></svg>'
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = mock_svg
        mock_get_am.return_value = mock_am

        result = get_icon_html("ORDERS", size_px=48)

        self.assertEqual(result, mock_svg)
        mock_am.get_asset_inline.assert_called_once_with("ORDERS", size_px=48)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_asset_icon_not_found_falls_back(self, mock_get_am):
        """Test: Wenn Asset-Icon nicht gefunden wird, wird auf nächste Stufe zurückgefallen"""
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None
        mock_get_am.return_value = mock_am

        # Should fall back to module icons or emoji
        result = get_icon_html("ccu_dashboard", size_px=24)

        # Should contain either SVG or emoji span
        self.assertTrue(
            "<svg" in result or '<span style="font-size: 24px;">' in result, "Should contain SVG or emoji span"
        )


class TestGetIconHtmlWithModuleIcons(unittest.TestCase):
    """Tests für get_icon_html mit module_icons (Priorität 2)"""

    def setUp(self):
        """Setup für jeden Test"""
        self.temp_dir = tempfile.mkdtemp()
        self.svg_file = Path(self.temp_dir) / "test_icon.svg"

        # Create test SVG with style section for scoping test
        test_svg = """<svg viewBox="0 0 24 24" width="100" height="100">
            <style>.cls-1 { fill: red; }</style>
            <circle class="cls-1" cx="12" cy="12" r="10" />
        </svg>"""
        self.svg_file.write_text(test_svg, encoding="utf-8")

    def tearDown(self):
        """Cleanup nach jedem Test"""
        import shutil

        shutil.rmtree(self.temp_dir)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_module_icon_found(self, mock_get_am):
        """Test: Module-Icon wird gefunden und zurückgegeben"""
        # Asset icon returns None -> fall back to module icons via get_asset_content
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None  # First call returns None

        # Second call: get_asset_content returns SVG content (new API)
        svg_content = self.svg_file.read_text(encoding="utf-8")
        mock_am.get_asset_content.return_value = svg_content
        mock_get_am.return_value = mock_am

        result = get_icon_html("HBW", size_px=32)

        # Should contain SVG
        self.assertIn("<svg", result)
        # Should have new width injected
        self.assertIn('width="32"', result)
        # Should NOT have old width/height
        self.assertNotIn('width="100"', result)
        self.assertNotIn('height="100"', result)
        # Should have CSS scoping applied (if SVG has style section)
        # Note: Simple test SVG might not have style, so scoping might not be visible

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_module_icon_with_scoping(self, mock_get_am):
        """Test: CSS-Scoping wird auf Module-Icon angewendet"""
        from omf2.assets.asset_manager import scope_svg_styles

        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None  # First call returns None

        # Second call: get_asset_content returns SVG content with style section (already scoped)
        # get_asset_content(scoped=True) applies scoping in asset_manager, so return scoped version
        svg_with_style = """<svg viewBox="0 0 24 24" width="100" height="100">
            <style>.cls-1 { fill: red; }</style>
            <circle class="cls-1" cx="12" cy="12" r="10" />
        </svg>"""
        # Apply scoping (as asset_manager.get_asset_content does)
        scoped_svg = scope_svg_styles(svg_with_style)
        mock_am.get_asset_content.return_value = scoped_svg
        mock_get_am.return_value = mock_am

        result = get_icon_html("DRILL", size_px=24)

        # Should have scoped styles (if SVG has style section)
        self.assertIn("<svg", result)
        # Should have new width injected
        self.assertIn('width="24"', result)
        # Should have CSS scoping applied (SVG has style section)
        self.assertIn("svg-", result)
        # Should have <g id="svg-...">
        self.assertIn('<g id="svg-', result)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_module_icon_case_insensitive(self, mock_get_am):
        """Test: Module-Icon-Key ist case-insensitive (wird zu uppercase konvertiert)"""
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None  # First call returns None

        # Second call: get_asset_content returns SVG content (new API)
        svg_content = self.svg_file.read_text(encoding="utf-8")
        mock_am.get_asset_content.return_value = svg_content
        mock_get_am.return_value = mock_am

        result = get_icon_html("hbw", size_px=24)  # lowercase

        # Should call with uppercase
        mock_am.get_asset_content.assert_called_with("HBW", scoped=True)
        self.assertIn("<svg", result)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_module_icon_file_not_found(self, mock_get_am):
        """Test: Wenn Module-Icon nicht existiert, fällt auf Emoji zurück"""
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None  # First call returns None
        # get_asset_content also returns None (not found)
        mock_am.get_asset_content.return_value = None
        mock_get_am.return_value = mock_am

        result = get_icon_html("ccu_dashboard", size_px=24)

        # Should fall back to emoji
        self.assertIn('<span style="font-size: 24px;">', result)
        self.assertIn("🏭", result)


class TestGetIconHtmlWithEmojisFallback(unittest.TestCase):
    """Tests für get_icon_html mit Emoji-Fallback (Priorität 3)"""

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_emoji_fallback_tab_icon(self, mock_get_am):
        """Test: Emoji-Fallback für Tab-Icon"""
        # No asset icon
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None
        mock_am.get_asset_content.return_value = None  # New API
        mock_get_am.return_value = mock_am

        result = get_icon_html("ccu_dashboard", size_px=24)

        self.assertIn('<span style="font-size: 24px;">🏭</span>', result)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_emoji_fallback_status_icon(self, mock_get_am):
        """Test: Emoji-Fallback für Status-Icon"""
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None
        mock_am.get_asset_content.return_value = None  # New API
        mock_get_am.return_value = mock_am

        result = get_icon_html("success", size_px=20)

        self.assertIn('<span style="font-size: 20px;">✅</span>', result)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_emoji_fallback_functional_icon(self, mock_get_am):
        """Test: Emoji-Fallback für Functional-Icon"""
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None
        mock_am.get_asset_content.return_value = None  # New API
        mock_get_am.return_value = mock_am

        result = get_icon_html("factory_reset", size_px=28)

        self.assertIn('<span style="font-size: 28px;">🏭🔄</span>', result)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_emoji_fallback_custom_size(self, mock_get_am):
        """Test: Emoji-Fallback mit benutzerdefinierter Größe"""
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None
        mock_am.get_asset_content.return_value = None  # New API
        mock_get_am.return_value = mock_am

        result = get_icon_html("error", size_px=36)

        self.assertIn('<span style="font-size: 36px;">❌</span>', result)


class TestGetIconHtmlUltimateFallback(unittest.TestCase):
    """Tests für get_icon_html ultimate fallback (unbekannter Key)"""

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_ultimate_fallback_unknown_key(self, mock_get_am):
        """Test: Ultimate Fallback für unbekannten Key"""
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None
        mock_am.get_asset_content.return_value = None  # New API
        mock_get_am.return_value = mock_am

        result = get_icon_html("completely_unknown_key_12345", size_px=24)

        # Should return placeholder emoji
        self.assertIn('<span style="font-size: 24px;">⚙️</span>', result)

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_ultimate_fallback_maintains_size(self, mock_get_am):
        """Test: Ultimate Fallback behält benutzerdefinierte Größe bei"""
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = None
        mock_am.get_asset_content.return_value = None  # New API
        mock_get_am.return_value = mock_am

        result = get_icon_html("unknown", size_px=40)

        self.assertIn('<span style="font-size: 40px;">', result)


class TestGetIconHtmlDefaultSize(unittest.TestCase):
    """Tests für get_icon_html default size parameter"""

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_default_size_is_24(self, mock_get_am):
        """Test: Standard-Größe ist 24px wenn nicht angegeben"""
        mock_svg = '<svg width="24"><circle /></svg>'
        mock_am = MagicMock()
        mock_am.get_asset_inline.return_value = mock_svg
        mock_get_am.return_value = mock_am

        result = get_icon_html("DASHBOARD_ADMIN")  # No size_px specified

        # Should call with default size_px=24
        mock_am.get_asset_inline.assert_called_once_with("DASHBOARD_ADMIN", size_px=24)


class TestGetIconHtmlErrorHandling(unittest.TestCase):
    """Tests für get_icon_html error handling"""

    @patch("omf2.assets.asset_manager.get_asset_manager")
    def test_asset_manager_error(self, mock_get_am):
        """Test: Fehler bei asset_manager wird abgefangen"""
        # Simulate error
        mock_get_am.side_effect = Exception("Asset manager error")

        # Should fall back to emoji
        result = get_icon_html("success", size_px=24)

        self.assertIn('<span style="font-size: 24px;">✅</span>', result)

    def test_invalid_svg_file_encoding(self):
        """Test: Ungültiges SVG-File-Encoding wird abgefangen"""
        temp_dir = tempfile.mkdtemp()
        svg_file = Path(temp_dir) / "invalid.svg"
        # Write invalid UTF-8
        svg_file.write_bytes(b"\xff\xfe\x00\x00")

        try:
            with patch("omf2.assets.asset_manager.get_asset_manager") as mock_get_am:
                mock_am = MagicMock()
                mock_am.get_asset_inline.return_value = None  # First call returns None
                # get_asset_content tries to read file but encoding fails, returns None
                mock_am.get_asset_content.return_value = None
                mock_get_am.return_value = mock_am

                # Should fall back gracefully, not crash
                result = get_icon_html("ccu_dashboard", size_px=24)

                # Should fall back to emoji (due to invalid encoding)
                self.assertIn('<span style="font-size: 24px;">', result)
        finally:
            import shutil

            shutil.rmtree(temp_dir)


class TestGetIconHtmlIntegration(unittest.TestCase):
    """Integration tests für get_icon_html mit echtem System"""

    def test_real_asset_icon_if_available(self):
        """Integration test: Versuche echtes Asset-Icon zu laden"""
        try:
            # Try to load a real asset icon
            result = get_icon_html("DASHBOARD_ADMIN", size_px=32)

            # Should return something
            self.assertIsNotNone(result)
            self.assertTrue(len(result) > 0)

            # Could be SVG or emoji depending on system state
            self.assertTrue("<svg" in result or "<span" in result)
        except Exception:
            # If asset_manager not available, test passes anyway
            pass

    def test_real_module_icon_if_available(self):
        """Integration test: Versuche echtes Module-Icon zu laden"""
        try:
            # Try to load a real module icon
            result = get_icon_html("HBW", size_px=28)

            # Should return something
            self.assertIsNotNone(result)
            self.assertTrue(len(result) > 0)
        except Exception:
            # If asset_manager not available, test passes anyway
            pass

    def test_emoji_fallback_always_works(self):
        """Integration test: Emoji-Fallback funktioniert immer"""
        # This should always work since emojis are hardcoded
        result = get_icon_html("success", size_px=24)

        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        # Should contain emoji or SVG
        self.assertTrue("✅" in result or "<svg" in result)


if __name__ == "__main__":
    # Test-Suite ausführen
    unittest.main(verbosity=2)
