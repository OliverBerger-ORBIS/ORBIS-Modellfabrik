#!/usr/bin/env python3
"""
i18n Compliance Validator für OMF2

Validiert automatisch die Einhaltung der i18n Development Rules:
- I18n-Manager aus Session State verwenden (nicht lokal erstellen)
- Hardcodierte deutsche Texte durch i18n.t() ersetzen
- Icons bleiben universal (UISymbols), werden nicht übersetzt
- Flache YAML-Keys verwenden (domain.section.key)
- String-Interpolation mit {variable} für dynamische Werte
"""

import os
import sys
from pathlib import Path
from typing import List

# Projekt-Root ermitteln
PROJECT_ROOT = Path(__file__).parent.parent.parent


class I18nComplianceValidator:
    """Validiert die Einhaltung der i18n Development Rules"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.project_root = PROJECT_ROOT

    def validate_file(self, file_path: Path) -> List[str]:
        """Validiert eine einzelne Datei gegen die i18n Development Rules"""
        file_errors = []

        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Nur Python-Dateien in OMF2 UI validieren
            if file_path.suffix != '.py' or not str(file_path).startswith(str(self.project_root / 'omf2/ui/')):
                return file_errors

            # i18n-Compliance prüfen
            file_errors.extend(self._check_i18n_manager_usage(content, file_path))
            file_errors.extend(self._check_hardcoded_german_text(content, file_path))
            file_errors.extend(self._check_icon_translation(content, file_path))
            file_errors.extend(self._check_yaml_structure(content, file_path))

        except Exception as e:
            file_errors.append(f"Fehler beim Lesen der Datei: {e}")

        return file_errors

    def _check_i18n_manager_usage(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf korrekte I18n-Manager Verwendung"""
        errors = []

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
                errors.append("❌ Streamlit UI-Komponente ohne i18n-Manager aus Session State")

        # I18n-Manager lokal erstellen (statt aus Session State)
        if 'I18nManager(' in content and 'st.session_state.get("i18n_manager")' not in content:
            errors.append("❌ Lokale I18nManager-Instanz gefunden - verwende st.session_state.get('i18n_manager')")

        return errors

    def _check_hardcoded_german_text(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf hardcodierte deutsche Texte"""
        errors = []

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
            'st.warning("Warnung:")',
            'st.caption("Hinweis:")',
        ]
        
        for pattern in german_patterns:
            if pattern in content:
                errors.append(f"❌ Hardcodierter deutscher Text: '{pattern}'")

        return errors

    def _check_icon_translation(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf Icon-Übersetzung (Icons sind universal)"""
        errors = []

        # Icons übersetzen (Icons sind universal)
        if 'i18n.t("icons.' in content or 'i18n.t(\'icons.' in content:
            errors.append("❌ Icons werden übersetzt - Icons bleiben universal (UISymbols)")

        return errors

    def _check_yaml_structure(self, content: str, file_path: Path) -> List[str]:
        """Prüft auf korrekte YAML-Struktur (flache Keys)"""
        errors = []

        # Tiefe Verschachtelung in i18n.t() Aufrufen finden
        if 'i18n.t("' in content:
            lines = content.split('\n')
            for line in lines:
                if 'i18n.t("' in line:
                    # Suche nach tiefen Verschachtelungen (mehr als 2 Punkte)
                    import re
                    matches = re.findall(r'i18n\.t\("([^"]+)"\)', line)
                    for match in matches:
                        if match.count('.') > 2:  # Mehr als 2 Ebenen
                            errors.append(f"❌ Tiefe YAML-Verschachtelung: '{match}' - verwende flache Keys")

        return errors

    def validate_project(self) -> bool:
        """Validiert das gesamte OMF2 UI-Projekt"""
        print("🔍 Validiere i18n Compliance...")

        # Python-Dateien in OMF2 UI finden
        ui_files = []
        for root, dirs, files in os.walk(self.project_root / 'omf2/ui/'):
            # Verzeichnisse ausschließen
            dirs[:] = [
                d
                for d in dirs
                if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv', 'env']
            ]

            for file in files:
                if file.endswith('.py'):
                    ui_files.append(Path(root) / file)

        # Dateien validieren
        total_errors = 0
        for file_path in ui_files:
            file_errors = self.validate_file(file_path)
            if file_errors:
                print(f"\n📁 {file_path.relative_to(self.project_root)}:")
                for error in file_errors:
                    print(f"  {error}")
                total_errors += len(file_errors)

        if total_errors == 0:
            print("✅ Alle i18n Development Rules eingehalten!")
            return True
        else:
            print(f"\n❌ {total_errors} i18n-Regel-Verletzungen gefunden!")
            return False


def main():
    """Hauptfunktion"""
    validator = I18nComplianceValidator()
    success = validator.validate_project()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
