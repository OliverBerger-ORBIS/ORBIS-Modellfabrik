#!/usr/bin/env python3
"""
Projekt-Struktur Validator

Überprüft, dass die Projekt-Struktur eingehalten wird:
- Original Fischertechnik Dateien bleiben im Root
- Orbis-spezifische Dateien sind in den richtigen Ordnern
- Keine unerwünschten Dateien im Root
"""

import sys
from pathlib import Path
from typing import List, Tuple


class ProjectStructureValidator:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()

        # Original Fischertechnik Dateien (bleiben im Root)
        self.allowed_root_files = {
            "README.md",
            "RPI_Image.md",
            "OPC-UA.md",
            "pyproject.toml",
            "pytest.ini",
            "requirements.txt",
            "run_tests_by_branch.py",
            "session_manager_settings.json",
            ".cursorrules",
            ".cursorcontext",
            ".gitignore",
            ".pre-commit-config.yaml",
            ".editorconfig",
            ".envrc",
            "__init__.py",
            "Makefile",
            ".DS_Store",  # macOS system file
        }

        # Original Fischertechnik Ordner (bleiben im Root)
        self.allowed_root_dirs = {
            "PLC-programs",
            "TXT4.0-programs",
            "Node-RED",
            "doc",
            "src_orbis",
            "tests_orbis",
            "docs_orbis",
            "data",
            ".git",
            ".venv",
            ".pytest_cache",
            ".ruff_cache",
            ".streamlit",
            ".vscode",
            ".github",  # GitHub Actions workflows
        }

        # Verbotene Dateien im Root (sollten in Unterordnern sein)
        self.forbidden_root_patterns = [
            "*.py",  # Python-Dateien außer __init__.py
            "*.md",  # Markdown-Dateien außer erlaubten
            "*.log",  # Log-Dateien
            "*.db",  # Datenbank-Dateien
            "*.json",  # JSON-Dateien außer erlaubten
            "*.yml",  # YAML-Dateien
            "*.yaml",  # YAML-Dateien
        ]

        # Erlaubte Ausnahmen für verbotene Patterns
        self.allowed_exceptions = {
            "*.py": ["__init__.py", "run_tests_by_branch.py"],
            "*.md": ["README.md", "RPI_Image.md", "OPC-UA.md"],
            "*.json": ["session_manager_settings.json"],
        }

    def validate_structure(self) -> Tuple[bool, List[str]]:
        """Validiert die Projekt-Struktur und gibt Fehler zurück."""
        errors = []

        # Prüfe Root-Dateien
        root_files = [f.name for f in self.project_root.iterdir() if f.is_file()]
        for file in root_files:
            if file not in self.allowed_root_files:
                # Prüfe ob es eine erlaubte Ausnahme ist
                is_exception = False
                for pattern, exceptions in self.allowed_exceptions.items():
                    if any(file.endswith(ext.replace("*", "")) for ext in pattern.split(",")):
                        if file in exceptions:
                            is_exception = True
                            break

                if not is_exception:
                    errors.append(f"Unerlaubte Datei im Root: {file}")

        # Prüfe Root-Ordner
        root_dirs = [d.name for d in self.project_root.iterdir() if d.is_dir()]
        for dir_name in root_dirs:
            if dir_name not in self.allowed_root_dirs:
                errors.append(f"Unerlaubter Ordner im Root: {dir_name}")

        # Prüfe auf verbotene Patterns
        for pattern in self.forbidden_root_patterns:
            matches = list(self.project_root.glob(pattern))
            for match in matches:
                if match.is_file() and match.name not in self.allowed_root_files:
                    # Prüfe Ausnahmen
                    is_exception = False
                    if pattern in self.allowed_exceptions:
                        if match.name in self.allowed_exceptions[pattern]:
                            is_exception = True

                    if not is_exception:
                        errors.append(f"Verbotene Datei im Root (Pattern {pattern}): {match.name}")

        # Prüfe spezifische Struktur-Regeln
        errors.extend(self._validate_specific_rules())

        return len(errors) == 0, errors

    def _validate_specific_rules(self) -> List[str]:
        """Validiert spezifische Struktur-Regeln."""
        errors = []

        # Prüfe dass wichtige Ordner existieren
        required_dirs = ["src_orbis", "tests_orbis", "docs_orbis", "data"]
        for dir_name in required_dirs:
            if not (self.project_root / dir_name).exists():
                errors.append(f"Erforderlicher Ordner fehlt: {dir_name}")

        # Prüfe dass data/ die richtigen Unterordner hat
        data_dir = self.project_root / "data"
        if data_dir.exists():
            expected_subdirs = ["mqtt-data", "omf-data"]
            for subdir in expected_subdirs:
                if not (data_dir / subdir).exists():
                    errors.append(f"Erwarteter Unterordner fehlt: data/{subdir}")

        # Prüfe dass keine Orbis-Dateien im Root sind
        orbis_files = list(self.project_root.glob("*orbis*"))
        for file in orbis_files:
            if file.name not in ["src_orbis", "tests_orbis", "docs_orbis"]:
                errors.append(f"Orbis-Datei im Root gefunden: {file.name}")

        return errors

    def print_validation_report(self) -> bool:
        """Druckt einen Validierungsbericht und gibt Erfolg zurück."""
        print("🔍 Validiere Projekt-Struktur...")
        print(f"📁 Projekt-Root: {self.project_root}")
        print()

        success, errors = self.validate_structure()

        if success:
            print("✅ Projekt-Struktur ist korrekt!")
            return True
        else:
            print("❌ Projekt-Struktur-Fehler gefunden:")
            print()
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
            print()
            print(
                "💡 Tipp: Verwende 'python src_orbis/scripts/validate_project_structure.py --fix' für automatische Korrekturen"
            )
            return False

    def fix_structure(self) -> bool:
        """Versucht, Struktur-Probleme automatisch zu beheben."""
        print("🔧 Versuche automatische Struktur-Korrektur...")

        success, errors = self.validate_structure()
        if success:
            print("✅ Keine Korrekturen nötig!")
            return True

        fixed_count = 0
        for error in errors:
            if "Unerlaubte Datei im Root:" in error:
                filename = error.split(": ")[1]
                file_path = self.project_root / filename

                # Versuche Datei in passenden Ordner zu verschieben
                if filename.endswith('.py') and filename != '__init__.py':
                    target_dir = self.project_root / "src_orbis"
                elif filename.endswith('.md') and filename not in ["README.md", "RPI_Image.md", "OPC-UA.md"]:
                    target_dir = self.project_root / "docs_orbis"
                elif filename.endswith(('.log', '.db')):
                    target_dir = self.project_root / "data"
                else:
                    continue

                try:
                    target_dir.mkdir(exist_ok=True)
                    file_path.rename(target_dir / filename)
                    print(f"  ✅ {filename} → {target_dir.name}/")
                    fixed_count += 1
                except Exception as e:
                    print(f"  ❌ Konnte {filename} nicht verschieben: {e}")

        if fixed_count > 0:
            print(f"✅ {fixed_count} Dateien automatisch korrigiert!")
        else:
            print("⚠️  Keine automatischen Korrekturen möglich")

        return fixed_count > 0


def main():
    """Hauptfunktion für CLI-Nutzung."""
    import argparse

    parser = argparse.ArgumentParser(description="Validiert die Projekt-Struktur")
    parser.add_argument("--fix", action="store_true", help="Versuche automatische Korrekturen")
    parser.add_argument("--project-root", default=".", help="Projekt-Root-Verzeichnis")

    args = parser.parse_args()

    validator = ProjectStructureValidator(args.project_root)

    if args.fix:
        success = validator.fix_structure()
        sys.exit(0 if success else 1)
    else:
        success = validator.print_validation_report()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
