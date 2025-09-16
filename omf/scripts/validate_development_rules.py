#!/usr/bin/env python3
"""
Development Rules Validator

Validiert automatisch die Einhaltung der OMF Development Rules:
- Absolute Imports
- Absolute Pfade
- OMF-Logging-System
- UI-Refresh Pattern
- Pre-commit Hooks Kompatibilität
"""

import os
import re
import sys
from pathlib import Path
from typing import List

# Projekt-Root ermitteln
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DevelopmentRulesValidator:
    """Validiert die Einhaltung der Development Rules"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = PROJECT_ROOT

    def validate_file(self, file_path: Path) -> List[str]:
        """Validiert eine einzelne Datei gegen die Development Rules"""
        file_errors = []

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Nur Python-Dateien validieren
            if file_path.suffix != '.py':
                return file_errors

            # Absolute Imports prüfen
            file_errors.extend(self._check_absolute_imports(content, file_path))

            # Absolute Pfade prüfen
            file_errors.extend(self._check_absolute_paths(content, file_path))

            # OMF-Logging-System prüfen
            file_errors.extend(self._check_omf_logging(content, file_path))

            # UI-Refresh Pattern prüfen
            file_errors.extend(self._check_ui_refresh_pattern(content, file_path))

            # Pre-commit Hooks Kompatibilität prüfen
            file_errors.extend(self._check_precommit_compatibility(content, file_path))

        except Exception as e:
            file_errors.append(f"Fehler beim Lesen der Datei: {e}")

        return file_errors

    def _check_absolute_imports(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf absolute Imports"""
        errors = []

        # Relative Imports finden
        relative_imports = re.findall(r'from\s+\.+', content)
        if relative_imports:
            errors.append(f"❌ Relative Imports gefunden: {relative_imports}")

        # sys.path.append Hacks finden
        if 'sys.path.append' in content:
            errors.append("❌ sys.path.append() gefunden - verwende absolute Imports")

        # Lokale Imports finden (ohne omf)
        local_imports = re.findall(r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import', content)
        for imp in local_imports:
            if not imp.startswith('omf') and imp not in [
                'os',
                'sys',
                'json',
                'datetime',
                'typing',
                'pathlib',
                're',
                'ast',
            ]:
                errors.append(f"❌ Lokaler Import gefunden: {imp} - verwende absolute Imports")

        return errors

    def _check_absolute_paths(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf absolute Pfade"""
        errors = []

        # Relative Pfade finden
        relative_paths = re.findall(r'["\']\.\.?/', content)
        if relative_paths:
            errors.append(f"❌ Relative Pfade gefunden: {relative_paths}")

        # Path(__file__).parent Hacks finden
        if 'Path(__file__).parent' in content:
            errors.append("❌ Path(__file__).parent gefunden - verwende absolute Pfade")

        # os.path.join Hacks finden
        if 'os.path.join(os.path.dirname(__file__)' in content:
            errors.append("❌ os.path.join(os.path.dirname(__file__)) gefunden - verwende absolute Pfade")

        return errors

    def _check_omf_logging(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf OMF-Logging-System"""
        errors = []

        # Nur für OMF-Komponenten prüfen
        if 'omf/' not in str(file_path) and 'omf/helper_apps/' not in str(file_path):
            return errors

        # Standard logging statt OMF-Logging
        if 'import logging' in content and 'from omf.tools.logging_config import get_logger' not in content:
            errors.append("❌ Standard logging gefunden - verwende OMF-Logging-System")

        # logging.getLogger() statt get_logger()
        if 'logging.getLogger(' in content and 'get_logger(' not in content:
            errors.append("❌ logging.getLogger() gefunden - verwende get_logger()")

        return errors

    def _check_ui_refresh_pattern(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf UI-Refresh Pattern"""
        errors = []

        # Nur für Streamlit-Komponenten prüfen
        if 'streamlit' not in content:
            return errors

        # st.rerun() in Komponenten finden
        if 'st.rerun()' in content and 'request_refresh()' not in content:
            errors.append("❌ st.rerun() gefunden - verwende request_refresh() Pattern")

        return errors

    def _check_precommit_compatibility(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf Pre-commit Hooks Kompatibilität"""
        errors = []

        # Black Line-Length prüfen (120 Zeichen)
        long_lines = [line for line in content.split('\n') if len(line) > 120]
        if long_lines:
            errors.append(f"❌ Zeilen länger als 120 Zeichen gefunden: {len(long_lines)} Zeilen")

        # Ruff-kritische Patterns
        if 'print(' in content and 'logger.' not in content:
            errors.append("❌ print() gefunden - verwende logger.debug()")

        return errors

    def validate_project(self) -> bool:
        """Validiert das gesamte Projekt"""
        print("🔍 Validiere Development Rules...")

        # Python-Dateien finden (nur Projekt-Dateien)
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Verzeichnisse ausschließen
            dirs[:] = [
                d
                for d in dirs
                if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', 'env']
            ]

            # Nur omf und tests prüfen
            if 'omf' not in root and 'tests' not in root:
                continue

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        # Dateien validieren
        total_errors = 0
        for file_path in python_files:
            file_errors = self.validate_file(file_path)
            if file_errors:
                print(f"\n📁 {file_path.relative_to(self.project_root)}:")
                for error in file_errors:
                    print(f"  {error}")
                total_errors += len(file_errors)

        if total_errors == 0:
            print("✅ Alle Development Rules eingehalten!")
            return True
        else:
            print(f"\n❌ {total_errors} Regel-Verletzungen gefunden!")
            return False


def main():
    """Hauptfunktion"""
    validator = DevelopmentRulesValidator()
    success = validator.validate_project()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
