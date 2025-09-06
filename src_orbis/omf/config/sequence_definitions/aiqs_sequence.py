"""
Beispiel Python-Sequenz-Definition für AIQS
Demonstriert komplexe Logik und dynamische Payloads
"""

try:
    from ...tools.sequence_executor import SequenceDefinition, SequenceStep
except ImportError:
    # Fallback für direkte Ausführung
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
    from sequence_executor import SequenceDefinition, SequenceStep


def get_sequence_definition():
    """Gibt die AIQS-Sequenz-Definition zurück"""

    # Dynamische Kontext-Variablen
    context = {"module_serial": "SVR4H76530", "module_type": "AIQS", "quality_check_enabled": True}  # AIQS Seriennummer

    # Schritte mit komplexer Logik
    steps = [
        SequenceStep(
            step_id=1,
            name="PICK",
            topic="module/v1/ff/{{module_serial}}/order",
            payload={
                "serialNumber": "{{module_serial}}",
                "orderId": "{{orderId}}",
                "orderUpdateId": "{{orderUpdateId}}",
                "action": {
                    "id": "{{action_id}}",
                    "command": "PICK",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
            wait_condition={
                "topic": "module/v1/ff/{{module_serial}}/state",
                "payload_contains": {"actionState": "IDLE"},
            },
        ),
        SequenceStep(
            step_id=2,
            name="AIQS_QUALITY_CHECK",
            topic="module/v1/ff/{{module_serial}}/order",
            payload={
                "serialNumber": "{{module_serial}}",
                "orderId": "{{orderId}}",
                "orderUpdateId": "{{orderUpdateId}}",
                "action": {
                    "id": "{{action_id}}",
                    "command": "CHECK_QUALITY",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
            wait_condition={
                "topic": "module/v1/ff/{{module_serial}}/state",
                "payload_contains": {"actionState": "IDLE", "qualityResult": True},
            },
        ),
        SequenceStep(
            step_id=3,
            name="DROP",
            topic="module/v1/ff/{{module_serial}}/order",
            payload={
                "serialNumber": "{{module_serial}}",
                "orderId": "{{orderId}}",
                "orderUpdateId": "{{orderUpdateId}}",
                "action": {
                    "id": "{{action_id}}",
                    "command": "DROP",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
        ),
    ]

    return SequenceDefinition(
        name="aiqs_complete_sequence",
        description="Komplette AIQS-Sequenz mit Quality-Check",
        steps=steps,
        context=context,
    )
