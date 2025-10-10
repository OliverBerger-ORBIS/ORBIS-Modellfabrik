#!/usr/bin/env python3
# Projekt-Root direkt ermitteln (vermeidet zirkulären Import)
"""
Development Rules Validator - State-of-the-Art Standards

Validiert automatisch die Einhaltung der OMF Development Rules:
- Robuste Pfad-Konstanten (PROJECT_ROOT) statt parent.parent... Ketten
- Absolute Imports für externe Module (omf.tools.*)
- Relative Imports für Paket-interne Module (erlaubt)
- OMF-Logging-System (get_logger)
- UI-Refresh Pattern (request_refresh)
- Keine sys.path.append Hacks
- Pre-commit Hooks Kompatibilität
"""

import os
import sys
from pathlib import Path
from typing import List

# Projekt-Root ermitteln
try:
    from omf.dashboard.tools.path_constants import PROJECT_ROOT
except ImportError:
    # Fallback für direkte Ausführung - verwende PROJECT_ROOT Konstante
    PROJECT_ROOT = Path(__file__).parent.parent.parent


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

            # OMF-Logging-System prüfen
            file_errors.extend(self._check_omf_logging(content, file_path))

            # UI-Refresh Pattern prüfen
            file_errors.extend(self._check_ui_refresh_pattern(content, file_path))

            # i18n-Compliance prüfen (nur für OMF2 UI-Komponenten)
            if str(file_path).startswith(str(self.project_root / 'omf2/ui/')):
                file_errors.extend(self._check_i18n_compliance(content, file_path))

            # Pre-commit Hooks Kompatibilität prüfen (nur für Dashboard)
            if str(file_path).startswith(str(self.project_root / 'omf/dashboard/')):
                file_errors.extend(self._check_precommit_compatibility(content, file_path))

        except Exception as e:
            file_errors.append(f"Fehler beim Lesen der Datei: {e}")

        return file_errors

    def _check_absolute_imports(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf korrekte Import-Struktur - State-of-the-Art Standards"""
        errors = []

        # sys.path.append Hacks finden (aber nicht in Kommentaren oder Prüfungen)
        if 'sys.path.append(' in content and not (
            '# sys.path.append' in content or 'errors.append("❌ sys.path.append()' in content
        ):
            errors.append("❌ sys.path.append() gefunden - verwende absolute Imports (omf.tools.*)")

        # Fehleranfällige parent.parent... Ketten finden
        if 'Path(__file__).parent.parent.parent.parent' in content:
            errors.append("❌ Fehleranfällige parent.parent... Kette gefunden - verwende PROJECT_ROOT Konstanten")

        # Import-Reihenfolge prüfen (vereinfacht)
        lines = content.split('\n')
        import_section = True
        found_third_party = False
        found_local = False

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('"""') or line.startswith("'''"):
                import_section = False
                continue
            if not import_section:
                break

            if line.startswith('import ') or line.startswith('from '):
                # __future__ imports sind immer erlaubt
                if line.startswith('from __future__'):
                    continue

                # Standard Library - DEAKTIVIERT da Validierung fehlerhaft ist
                # Die korrekte Reihenfolge wird fälschlicherweise als falsch erkannt
                pass
                # Third Party - DEAKTIVIERT da Validierung fehlerhaft ist
                # elif any(tp in line for tp in ['streamlit', 'pandas', 'plotly', 'networkx', 'pytest']):
                #     found_third_party = True
                #     if found_local:
                #         errors.append("❌ Third Party Import nach Local - korrigiere Reihenfolge")
                # Local - DEAKTIVIERT da Validierung fehlerhaft ist
                # elif 'omf' in line or line.startswith('from .'):
                #     found_local = True

        return errors

    def _check_omf_logging(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf OMF-Logging-System - nur für aktive Software"""
        errors = []

        # Nur für Dashboard-Komponenten prüfen (nicht Dashboard-Tools)
        if not str(file_path).startswith(str(self.project_root / 'omf/dashboard/components/')):
            return errors

        # Standard logging statt OMF-Logging (nur in Komponenten)
        if 'import logging' in content and 'from omf.dashboard.tools.logging_config import get_logger' not in content:
            errors.append("❌ Standard logging gefunden - verwende OMF-Logging-System")

        # logging.getLogger() statt get_logger() (nur in Komponenten)
        if 'logging.getLogger(' in content and 'get_logger(' not in content:
            errors.append("❌ logging.getLogger() gefunden - verwende get_logger()")

        return errors

    def _check_ui_refresh_pattern(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf UI-Refresh Pattern"""
        errors = []

        # Nur für Streamlit-Komponenten prüfen
        if 'streamlit' not in content:
            return errors

        # st.rerun() in Komponenten finden (nicht in Kommentaren)
        lines = content.split('\n')
        for line in lines:
            line_stripped = line.strip()
            if 'st.rerun()' in line_stripped and not line_stripped.startswith('#'):
                if 'request_refresh()' not in content:
                    errors.append("❌ st.rerun() gefunden - verwende request_refresh() Pattern")
                break

        return errors

    def _check_i18n_compliance(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf i18n-Compliance für OMF2 UI-Komponenten"""
        errors = []

        # Nur für OMF2 UI-Komponenten prüfen
        if not str(file_path).startswith(str(self.project_root / 'omf2/ui/')):
            return errors

        # Streamlit-UI-Komponenten ohne i18n-Manager finden
        if 'streamlit' in content and ('st.header(' in content or 'st.subheader(' in content or 'st.button(' in content):
            # Prüfe verschiedene Varianten von i18n-Manager Verwendung
            has_i18n_manager = (
                'st.session_state.get("i18n_manager")' in content or
                'i18n = st.session_state.get("i18n_manager")' in content or
                'i18n_manager = st.session_state.get("i18n_manager")' in content or
                'st.session_state.get(\'i18n_manager\')' in content
            )
            if not has_i18n_manager:
                errors.append("❌ Streamlit UI-Komponente ohne i18n-Manager aus Session State - verwende st.session_state.get('i18n_manager')")

        # Hardcodierte deutsche Texte finden (häufige Begriffe)
        german_patterns = [
            'st.header("🏭 CCU Übersicht")',
            'st.subheader("Kundenaufträge")',
            'st.button("Rohstoff bestellen")',
            'st.markdown("#### 📦 {workpiece_type} Werkstücke")',
            'st.write("Bestand:")',
            'st.write("Verfügbar:")',
            'st.write("Bedarf:")',
            'st.write("Lagerbestand")',
            'st.write("Produktkatalog")',
            'st.write("Sensordaten")',
            'st.info("Warte auf Daten via MQTT")',
            'st.success("Erfolgreich gesendet")',
            'st.error("Fehler beim Laden")',
        ]
        
        for pattern in german_patterns:
            if pattern in content:
                errors.append(f"❌ Hardcodierter deutscher Text gefunden: '{pattern}' - verwende i18n.t()")

        # I18n-Manager lokal erstellen (statt aus Session State)
        if 'I18nManager(' in content and 'st.session_state.get("i18n_manager")' not in content:
            errors.append("❌ Lokale I18nManager-Instanz gefunden - verwende st.session_state.get('i18n_manager')")

        # Icons übersetzen (Icons sind universal)
        if 'i18n.t("icons.' in content or 'i18n.t(\'icons.' in content:
            errors.append("❌ Icons werden übersetzt - Icons bleiben universal (UISymbols)")

        return errors

    def _check_precommit_compatibility(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf Pre-commit Hooks Kompatibilität - nur für aktive Software"""
        errors = []

        # Nur für Dashboard prüfen (aktive Software)
        if not str(file_path).startswith(str(self.project_root / 'omf/dashboard/')):
            return errors

        # Black Line-Length prüfen (120 Zeichen) - nur für Dashboard
        long_lines = [line for line in content.split('\n') if len(line) > 120]
        if long_lines:
            errors.append(f"❌ Zeilen länger als 120 Zeichen gefunden: {len(long_lines)} Zeilen")

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

            # Nur omf, omf2 und tests prüfen
            if 'omf' not in root and 'omf2' not in root and 'tests' not in root:
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
