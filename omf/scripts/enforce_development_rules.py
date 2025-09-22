#!/usr/bin/env python3
"""
Automatische Regel-Erzwingung für OMF Development Rules

State-of-the-Art Standards werden automatisch durchgesetzt:
- Robuste Pfad-Konstanten statt parent.parent... Ketten
- Absolute Imports statt sys.path.append Hacks
- Konsistente Import-Struktur
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Projekt-Root ermitteln
PROJECT_ROOT = PROJECT_ROOT


class DevelopmentRulesEnforcer:
    """Erzwingt State-of-the-Art Development Rules automatisch"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.fixes_applied = []
        self.errors_found = []

    def enforce_file(self, file_path: Path) -> bool:
        """Erzwingt Regeln in einer einzelnen Datei"""
        if file_path.suffix != '.py':
            return True

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            original_content = content
            content = self._fix_sys_path_hacks(content, file_path)
            content = self._fix_parent_chains(content, file_path)
            content = self._add_path_constants_import(content, file_path)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.fixes_applied.append(str(file_path))
                return True

        except Exception as e:
            self.errors_found.append(f"Fehler in {file_path}: {e}")
            return False

        return True

    def _fix_sys_path_hacks(self, content: str, file_path: Path) -> str:
        """Ersetzt sys.path.append Hacks durch absolute Imports"""
        lines = content.split('\n')
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # sys.path.append Hacks erkennen und entfernen
            if 'tools_path' in line and 'Path(__file__).parent' in line:
                # Nächste Zeilen prüfen
                if i + 1 < len(lines) and 'if tools_path not in sys.path:' in lines[i + 1]:
                    if i + 2 < len(lines) and 'pass' in lines[i + 2]:
                        # sys.path.append Hack entfernen
                        i += 3  # Überspringe die 3 Zeilen
                        continue

                # sys.path.append direkt entfernen
                # Zeile überspringen
                i += 1
                continue

            new_lines.append(line)
            i += 1

        return '\n'.join(new_lines)

    def _fix_parent_chains(self, content: str, file_path: Path) -> str:
        """Ersetzt fehleranfällige parent.parent... Ketten durch Konstanten"""
        # Pattern für parent.parent... Ketten
        patterns = [
            (r'Path\(__file__\)\.parent\.parent\.parent\.parent\.parent', 'PROJECT_ROOT'),
            (r'Path\(__file__\)\.parent\.parent\.parent\.parent', 'PROJECT_ROOT'),
            (r'Path\(__file__\)\.parent\.parent\.parent', 'PROJECT_ROOT'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        return content

    def _add_path_constants_import(self, content: str, file_path: Path) -> str:
        """Fügt path_constants Import hinzu wenn nötig"""
        if 'PROJECT_ROOT' in content and 'from omf.dashboard.tools.path_constants import' not in content:
            # Import nach den Standard-Imports hinzufügen
            lines = content.split('\n')
            import_section_end = 0

            for i, line in enumerate(lines):
                if (
                    line.strip()
                    and not line.startswith('#')
                    and not line.startswith('import')
                    and not line.startswith('from')
                ):
                    import_section_end = i
                    break

            # path_constants Import hinzufügen
            import_line = "from omf.dashboard.tools.path_constants import PROJECT_ROOT, SESSIONS_DIR, CONFIG_DIR"
            lines.insert(import_section_end, import_line)
            content = '\n'.join(lines)

        return content

    def enforce_project(self) -> bool:
        """Erzwingt Regeln im gesamten Projekt"""
        print("🔧 Erzwinge State-of-the-Art Development Rules...")

        # Python-Dateien finden
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Verzeichnisse ausschließen
            dirs[:] = [
                d
                for d in dirs
                if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', 'env']
            ]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)

        # Dateien bearbeiten
        success_count = 0
        for file_path in python_files:
            if self.enforce_file(file_path):
                success_count += 1

        # Ergebnisse anzeigen
        print(f"✅ {success_count}/{len(python_files)} Dateien erfolgreich bearbeitet")

        if self.fixes_applied:
            print(f"🔧 {len(self.fixes_applied)} Dateien automatisch korrigiert:")
            for fix in self.fixes_applied:
                print(f"  - {fix}")

        if self.errors_found:
            print(f"❌ {len(self.errors_found)} Fehler gefunden:")
            for error in self.errors_found:
                print(f"  - {error}")

        return len(self.errors_found) == 0


def main():
    """Hauptfunktion"""
    enforcer = DevelopmentRulesEnforcer()
    success = enforcer.enforce_project()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
