#!/usr/bin/env python3
"""
Dashboard-Regeln-Validator

Prüft automatisch, ob Dashboard-Komponenten die Regeln befolgen:
- MQTT-Singleton-Pattern
- Per-Topic Subscription
- Kein st.rerun() in MQTT-Kontext
- Absolute Imports
"""

import ast
from pathlib import Path


class DashboardRulesValidator:
    """Validiert Dashboard-Komponenten gegen die Regeln"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        # Nur OMF-Dashboard prüfen, nicht Session Manager
        self.dashboard_path = project_root / "src_orbis" / "omf" / "dashboard"
        self.violations = []

    def validate_all(self) -> bool:
        """Validiert alle Dashboard-Komponenten"""
        print("🔍 Validiere Dashboard-Regeln...")

        # Finde alle Python-Dateien im Dashboard
        python_files = list(self.dashboard_path.rglob("*.py"))

        for file_path in python_files:
            if file_path.name.startswith("__"):
                continue

            print(f"  📄 {file_path.relative_to(self.project_root)}")
            self._validate_file(file_path)

        # Zeige Ergebnisse
        self._show_results()
        return len(self.violations) == 0

    def _validate_file(self, file_path: Path):
        """Validiert eine einzelne Datei"""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Validiere verschiedene Regeln
            self._check_mqtt_singleton_pattern(tree, file_path)
            self._check_per_topic_subscription(tree, file_path)
            self._check_no_rerun_in_mqtt_context(tree, file_path)
            self._check_absolute_imports(tree, file_path)
            self._check_private_function_naming(tree, file_path)

        except Exception as e:
            self.violations.append(
                {
                    'file': str(file_path.relative_to(self.project_root)),
                    'rule': 'FILE_PARSE_ERROR',
                    'line': 0,
                    'message': f"Datei konnte nicht geparst werden: {e}",
                }
            )

    def _check_mqtt_singleton_pattern(self, tree: ast.AST, file_path: Path):
        """Prüft MQTT-Singleton-Pattern"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Prüfe auf OmfMqttClient() Aufrufe
                if isinstance(node.func, ast.Name) and node.func.id == "OmfMqttClient":
                    self.violations.append(
                        {
                            'file': str(file_path.relative_to(self.project_root)),
                            'rule': 'MQTT_SINGLETON_VIOLATION',
                            'line': node.lineno,
                            'message': "❌ FALSCH: Neuen MQTT-Client erstellen - "
                            "verwende st.session_state.get('mqtt_client')",
                        }
                    )

    def _check_per_topic_subscription(self, tree: ast.AST, file_path: Path):
        """Prüft Per-Topic Subscription Pattern"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Prüfe auf get_messages() Aufrufe
                if isinstance(node.func, ast.Attribute) and node.func.attr == "get_messages":
                    self.violations.append(
                        {
                            'file': str(file_path.relative_to(self.project_root)),
                            'rule': 'PER_TOPIC_SUBSCRIPTION_VIOLATION',
                            'line': node.lineno,
                            'message': "❌ FALSCH: get_messages() verwenden - "
                            "verwende get_buffer() mit subscribe_many()",
                        }
                    )

    def _check_no_rerun_in_mqtt_context(self, tree: ast.AST, file_path: Path):
        """Prüft auf st.rerun() in MQTT-Kontext (nur OMF-Dashboard)"""
        # Prüfe ob es eine OMF-Dashboard-Datei ist
        if "session_manager" in str(file_path):
            return  # Session Manager: st.rerun() ist erlaubt

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Prüfe auf st.rerun() Aufrufe
                if (
                    isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "st"
                    and node.func.attr == "rerun"
                ):
                    self.violations.append(
                        {
                            'file': str(file_path.relative_to(self.project_root)),
                            'rule': 'RERUN_VIOLATION',
                            'line': node.lineno,
                            'message': "❌ FALSCH: st.rerun() zerstört MQTT-Subscriptions - entferne st.rerun()",
                        }
                    )

    def _check_absolute_imports(self, tree: ast.AST, file_path: Path):
        """Prüft absolute Imports"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                # Prüfe auf relative Imports
                if node.level > 0:
                    self.violations.append(
                        {
                            'file': str(file_path.relative_to(self.project_root)),
                            'rule': 'RELATIVE_IMPORT_VIOLATION',
                            'line': node.lineno,
                            'message': "❌ FALSCH: Relativer Import - "
                            "verwende absolute Imports: from src_orbis.omf.tools.module import Class",
                        }
                    )

    def _check_private_function_naming(self, tree: ast.AST, file_path: Path):
        """Prüft private Funktionen-Naming"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Prüfe auf private Funktionen ohne _ Prefix
                if (
                    node.name.startswith('_')
                    and not node.name.startswith('__')
                    and not node.name.startswith('_show_')
                    and not node.name.startswith('_send_')
                    and not node.name.startswith('_get_')
                    and not node.name.startswith('_check_')
                ):
                    self.violations.append(
                        {
                            'file': str(file_path.relative_to(self.project_root)),
                            'rule': 'PRIVATE_FUNCTION_NAMING_VIOLATION',
                            'line': node.lineno,
                            'message': f"❌ FALSCH: Private Funktion '{node.name}' sollte "
                            f"_show_<function>_section() oder _send_<action>_command() heißen",
                        }
                    )

    def _show_results(self):
        """Zeigt Validierungsergebnisse"""
        if not self.violations:
            print("✅ Alle Dashboard-Regeln eingehalten!")
            return

        print(f"\n❌ {len(self.violations)} Regelverstöße gefunden:")
        print("=" * 60)

        # Gruppiere nach Regel
        by_rule = {}
        for violation in self.violations:
            rule = violation['rule']
            if rule not in by_rule:
                by_rule[rule] = []
            by_rule[rule].append(violation)

        for rule, violations in by_rule.items():
            print(f"\n🔴 {rule} ({len(violations)} Verstöße):")
            for violation in violations:
                print(f"  📄 {violation['file']}:{violation['line']}")
                print(f"     {violation['message']}")

        print("\n" + "=" * 60)
        print("💡 Tipp: Siehe docs_orbis/development/dashboard-component-rules.md")


def main():
    """Hauptfunktion"""
    project_root = Path(__file__).parent.parent.parent
    validator = DashboardRulesValidator(project_root)

    success = validator.validate_all()

    if not success:
        print("\n🚨 Dashboard-Regeln verletzt!")
        exit(1)
    else:
        print("\n🎉 Alle Dashboard-Regeln eingehalten!")


if __name__ == "__main__":
    main()
