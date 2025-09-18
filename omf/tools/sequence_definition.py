"""
SequenceDefinition - YML und Python Sequenz-Definitionen
Lädt und verwaltet Sequenz-Definitionen aus verschiedenen Quellen
"""

from pathlib import Path
import os
from typing import Any, Dict, Optional

import yaml

try:
    from .sequence_executor import SequenceDefinition, SequenceStep
except ImportError:
    from sequence_executor import SequenceDefinition, SequenceStep

class SequenceDefinitionLoader:
    """Lädt Sequenz-Definitionen aus YML und Python"""

    def __init__(self, base_path: str = None):
        self.base_path = base_path or str(Path(__file__).parent / ".." / "config" / "sequence_definitions")
        self.sequences: Dict[str, SequenceDefinition] = {}
        self._load_all_sequences()

    def _load_all_sequences(self):
        """Lädt alle verfügbaren Sequenz-Definitionen"""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)
            return

        # YML-Dateien laden
        for filename in os.listdir(self.base_path):
            if filename.endswith(".yml") or filename.endswith(".yaml"):
                self._load_yml_sequence(filename)
            elif filename.endswith(".py") and not filename.startswith("__"):
                self._load_python_sequence(filename)

    def _load_yml_sequence(self, filename: str):
        """Lädt YML-Sequenz-Definition"""
        try:
            filepath = os.path.join(self.base_path, filename)
            with open(filepath, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            sequence = self._parse_yml_sequence(data, filename)
            if sequence:
                self.sequences[sequence.name] = sequence

        except Exception as e:
            print(f"Fehler beim Laden der YML-Sequenz {filename}: {e}")

    def _load_python_sequence(self, filename: str):
        """Lädt Python-Sequenz-Definition"""
        try:
            # Python-Modul dynamisch importieren
            module_name = filename[:-3]  # .py entfernen
            import importlib.util

            filepath = os.path.join(self.base_path, filename)
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Sequenz-Definition aus Modul extrahieren
            if hasattr(module, "get_sequence_definition"):
                sequence = module.get_sequence_definition()
                if sequence:
                    self.sequences[sequence.name] = sequence

        except Exception as e:
            print(f"Fehler beim Laden der Python-Sequenz {filename}: {e}")

    def _parse_yml_sequence(self, data: Dict[str, Any], filename: str) -> Optional[SequenceDefinition]:
        """Parst YML-Daten zu SequenceDefinition"""
        try:
            name = data.get("name", filename[:-4])  # .yml entfernen
            description = data.get("description", "")
            context = data.get("context", {})

            steps = []
            for i, step_data in enumerate(data.get("steps", [])):
                step = SequenceStep(
                    step_id=i + 1,
                    name=step_data.get("name", f"Step {i + 1}"),
                    topic=step_data.get("topic", ""),
                    payload=step_data.get("payload", {}),
                    wait_condition=step_data.get("wait_condition"),
                    context_vars=step_data.get("context_vars", {}),
                )
                steps.append(step)

            return SequenceDefinition(name=name, description=description, steps=steps, context=context)

        except Exception as e:
            print(f"Fehler beim Parsen der YML-Sequenz {filename}: {e}")
            return None

    def get_sequence(self, name: str) -> Optional[SequenceDefinition]:
        """Holt eine Sequenz-Definition"""
        return self.sequences.get(name)

    def get_all_sequences(self) -> Dict[str, SequenceDefinition]:
        """Gibt alle Sequenz-Definitionen zurück"""
        return self.sequences.copy()

    def reload_sequences(self):
        """Lädt alle Sequenzen neu"""
        self.sequences.clear()
        self._load_all_sequences()

# Beispiel YML-Sequenz-Definitionen erstellen
def create_example_sequences():
    """Erstellt Beispiel-Sequenz-Definitionen"""
    base_path = str(Path(__file__).parent / ".." / "config" / "sequence_definitions")
    os.makedirs(base_path, exist_ok=True)

    # MILL-Sequenz Beispiel
    mill_sequence = {
        "name": "mill_complete_sequence",
        "description": "Komplette MILL-Sequenz: PICK → MILL → DROP",
        "context": {"module_serial": "SVR3QA2098", "module_type": "MILL"},  # MILL Seriennummer
        "steps": [
            {
                "name": "PICK",
                "topic": "module/v1/ff/{{module_serial}}/order",
                "payload": {"orderId": "{{orderId}}", "orderUpdateId": "{{orderUpdateId}}", "action": "PICK"},
                "wait_condition": {
                    "topic": "module/v1/ff/{{module_serial}}/state",
                    "payload_contains": {"actionState": "IDLE"},
                },
            },
            {
                "name": "MILL",
                "topic": "module/v1/ff/{{module_serial}}/order",
                "payload": {"orderId": "{{orderId}}", "orderUpdateId": "{{orderUpdateId}}", "action": "MILL"},
                "wait_condition": {
                    "topic": "module/v1/ff/{{module_serial}}/state",
                    "payload_contains": {"actionState": "IDLE"},
                },
            },
            {
                "name": "DROP",
                "topic": "module/v1/ff/{{module_serial}}/order",
                "payload": {"orderId": "{{orderId}}", "orderUpdateId": "{{orderUpdateId}}", "action": "DROP"},
            },
        ],
    }

    # YML-Datei schreiben
    yml_path = os.path.join(base_path, "mill_sequence.yml")
    with open(yml_path, "w", encoding="utf-8") as f:
        yaml.dump(mill_sequence, f, default_flow_style=False, allow_unicode=True)

    # DRILL-Sequenz Beispiel
    drill_sequence = {
        "name": "drill_complete_sequence",
        "description": "Komplette DRILL-Sequenz: PICK → DRILL → DROP",
        "context": {"module_serial": "SVR4H76449", "module_type": "DRILL"},  # DRILL Seriennummer
        "steps": [
            {
                "name": "PICK",
                "topic": "module/v1/ff/{{module_serial}}/order",
                "payload": {"orderId": "{{orderId}}", "orderUpdateId": "{{orderUpdateId}}", "action": "PICK"},
                "wait_condition": {
                    "topic": "module/v1/ff/{{module_serial}}/state",
                    "payload_contains": {"actionState": "IDLE"},
                },
            },
            {
                "name": "DRILL",
                "topic": "module/v1/ff/{{module_serial}}/order",
                "payload": {"orderId": "{{orderId}}", "orderUpdateId": "{{orderUpdateId}}", "action": "DRILL"},
                "wait_condition": {
                    "topic": "module/v1/ff/{{module_serial}}/state",
                    "payload_contains": {"actionState": "IDLE"},
                },
            },
            {
                "name": "DROP",
                "topic": "module/v1/ff/{{module_serial}}/order",
                "payload": {"orderId": "{{orderId}}", "orderUpdateId": "{{orderUpdateId}}", "action": "DROP"},
            },
        ],
    }

    # YML-Datei schreiben
    yml_path = os.path.join(base_path, "drill_sequence.yml")
    with open(yml_path, "w", encoding="utf-8") as f:
        yaml.dump(drill_sequence, f, default_flow_style=False, allow_unicode=True)

# Beispiel Python-Sequenz-Definition
def create_example_python_sequence():
    """Erstellt eine Beispiel Python-Sequenz-Definition"""
    base_path = str(Path(__file__).parent / ".." / "config" / "sequence_definitions")
    os.makedirs(base_path, exist_ok=True)

    python_code = '''"""
Beispiel Python-Sequenz-Definition für AIQS
Demonstriert komplexe Logik und dynamische Payloads
"""

from omf.tools.sequence_executor import SequenceDefinition, SequenceStep

def get_sequence_definition():
    """Gibt die AIQS-Sequenz-Definition zurück"""

    # Dynamische Kontext-Variablen
    context = {
        'module_serial': 'SVR4H76530',  # AIQS Seriennummer
        'module_type': 'AIQS',
        'quality_check_enabled': True
    }

    # Schritte mit komplexer Logik
    steps = [
        SequenceStep(
            step_id=1,
            name='PICK',
            topic='module/v1/ff/{{module_serial}}/order',
            payload={
                'orderId': '{{orderId}}',
                'orderUpdateId': '{{orderUpdateId}}',
                'action': 'PICK',
                'qualityCheck': '{{quality_check_enabled}}'
            },
            wait_condition={
                'topic': 'module/v1/ff/{{module_serial}}/state',
                'payload_contains': {
                    'actionState': 'IDLE'
                }
            }
        ),
        SequenceStep(
            step_id=2,
            name='AIQS_QUALITY_CHECK',
            topic='module/v1/ff/{{module_serial}}/order',
            payload={
                'orderId': '{{orderId}}',
                'orderUpdateId': '{{orderUpdateId}}',
                'action': 'AIQS',
                'qualityCheck': True,
                'parameters': {
                    'tolerance': 0.1,
                    'checkType': 'FULL'
                }
            },
            wait_condition={
                'topic': 'module/v1/ff/{{module_serial}}/state',
                'payload_contains': {
                    'actionState': 'IDLE',
                    'qualityResult': True
                }
            }
        ),
        SequenceStep(
            step_id=3,
            name='DROP',
            topic='module/v1/ff/{{module_serial}}/order',
            payload={
                'orderId': '{{orderId}}',
                'orderUpdateId': '{{orderUpdateId}}',
                'action': 'DROP'
            }
        )
    ]

    return SequenceDefinition(
        name='aiqs_complete_sequence',
        description='Komplette AIQS-Sequenz mit Quality-Check',
        steps=steps,
        context=context
    )
'''

    # Python-Datei schreiben
    python_path = os.path.join(base_path, "aiqs_sequence.py")
    with open(python_path, "w", encoding="utf-8") as f:
        f.write(python_code)

if __name__ == "__main__":
    # Beispiel-Sequenzen erstellen
    create_example_sequences()
    create_example_python_sequence()
    print("Beispiel-Sequenz-Definitionen erstellt!")
