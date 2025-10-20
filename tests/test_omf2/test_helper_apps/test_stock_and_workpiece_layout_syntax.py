#!/usr/bin/env python3
"""
Test-Suite für stock_and_workpiece_layout_test.py
Verhindert Syntax- und Indentationsfehler in der Helper-App
"""

import ast
import sys
from pathlib import Path

import pytest

# Absolute Imports verwenden
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestHelperAppSyntax:
    """Test-Klasse für Syntax-Validierung der Helper-App"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.helper_app_path = Path(__file__).parent / "stock_and_workpiece_layout_test.py"

    def test_helper_app_syntax_valid(self):
        """Test: Helper-App hat gültige Python-Syntax"""
        assert self.helper_app_path.exists(), f"Helper-App nicht gefunden: {self.helper_app_path}"

        try:
            with open(self.helper_app_path, encoding="utf-8") as f:
                source_code = f.read()

            # Parse Python-Syntax
            ast.parse(source_code, filename=str(self.helper_app_path))

        except SyntaxError as e:
            pytest.fail(f"Syntax-Fehler in Helper-App: {e}\n" f"Zeile {e.lineno}: {e.text}")
        except IndentationError as e:
            pytest.fail(f"Indentations-Fehler in Helper-App: {e}\n" f"Zeile {e.lineno}: {e.text}")
        except Exception as e:
            pytest.fail(f"Unerwarteter Fehler beim Parsen der Helper-App: {e}")

    def test_helper_app_imports_valid(self):
        """Test: Alle Imports in der Helper-App sind gültig"""
        assert self.helper_app_path.exists(), f"Helper-App nicht gefunden: {self.helper_app_path}"

        try:
            with open(self.helper_app_path, encoding="utf-8") as f:
                source_code = f.read()

            # Parse und extrahiere Imports
            tree = ast.parse(source_code, filename=str(self.helper_app_path))

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            # Teste kritische Imports
            critical_imports = ["streamlit", "pathlib"]

            for critical_import in critical_imports:
                if not any(critical_import in imp for imp in imports):
                    pytest.fail(f"Kritischer Import fehlt: {critical_import}")

        except Exception as e:
            pytest.fail(f"Fehler beim Testen der Imports: {e}")

    def test_helper_app_functions_defined(self):
        """Test: Wichtige Funktionen sind definiert"""
        assert self.helper_app_path.exists(), f"Helper-App nicht gefunden: {self.helper_app_path}"

        try:
            with open(self.helper_app_path, encoding="utf-8") as f:
                source_code = f.read()

            # Parse und extrahiere Funktionsdefinitionen
            tree = ast.parse(source_code, filename=str(self.helper_app_path))

            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)

            # Teste kritische Funktionen
            critical_functions = ["_display_svg_content", "_show_dummy_asset_overview", "main"]

            for critical_function in critical_functions:
                if critical_function not in functions:
                    pytest.fail(f"Kritische Funktion fehlt: {critical_function}")

        except Exception as e:
            pytest.fail(f"Fehler beim Testen der Funktionen: {e}")

    def test_helper_app_no_hardcoded_paths(self):
        """Test: Keine hardcodierten Pfade in der Helper-App"""
        assert self.helper_app_path.exists(), f"Helper-App nicht gefunden: {self.helper_app_path}"

        try:
            with open(self.helper_app_path, encoding="utf-8") as f:
                source_code = f.read()

            # Suche nach hardcodierten Pfaden
            hardcoded_patterns = ["/Users/", "C:\\", "D:\\", "E:\\", "F:\\", "G:\\", "H:\\"]

            lines = source_code.split("\n")
            for i, line in enumerate(lines, 1):
                for pattern in hardcoded_patterns:
                    if pattern in line and not line.strip().startswith("#"):
                        pytest.fail(f"Hardcodierter Pfad gefunden in Zeile {i}: {line.strip()}")

        except Exception as e:
            pytest.fail(f"Fehler beim Testen der Pfade: {e}")

    def test_helper_app_uses_absolute_imports(self):
        """Test: Helper-App verwendet absolute Imports"""
        assert self.helper_app_path.exists(), f"Helper-App nicht gefunden: {self.helper_app_path}"

        try:
            with open(self.helper_app_path, encoding="utf-8") as f:
                source_code = f.read()

            # Suche nach relativen Imports
            lines = source_code.split("\n")
            for i, line in enumerate(lines, 1):
                stripped_line = line.strip()
                if stripped_line.startswith("from .") and not stripped_line.startswith("from ."):
                    pytest.fail(f"Relativer Import gefunden in Zeile {i}: {stripped_line}")
                if stripped_line.startswith("import ."):
                    pytest.fail(f"Relativer Import gefunden in Zeile {i}: {stripped_line}")

        except Exception as e:
            pytest.fail(f"Fehler beim Testen der Imports: {e}")


if __name__ == "__main__":
    # Führe Tests aus
    pytest.main([__file__, "-v"])
