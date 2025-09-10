"""
Beispiel Python-Sequenz-Definition für AIQS
Demonstriert komplexe Logik und dynamische Payloads
"""

from src_orbis.omf.tools.sequence_executor import SequenceDefinition, SequenceStep


def get_sequence_definition():
    """Gibt die AIQS-Sequenz-Definition zurück"""

    # Dynamische Kontext-Variablen
    context = {'module_serial': 'SVR4H76530', 'module_type': 'AIQS', 'quality_check_enabled': True}  # AIQS Seriennummer

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
                'qualityCheck': '{{quality_check_enabled}}',
            },
            wait_condition={
                'topic': 'module/v1/ff/{{module_serial}}/state',
                'payload_contains': {'actionState': 'IDLE'},
            },
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
                'parameters': {'tolerance': 0.1, 'checkType': 'FULL'},
            },
            wait_condition={
                'topic': 'module/v1/ff/{{module_serial}}/state',
                'payload_contains': {'actionState': 'IDLE', 'qualityResult': True},
            },
        ),
        SequenceStep(
            step_id=3,
            name='DROP',
            topic='module/v1/ff/{{module_serial}}/order',
            payload={'orderId': '{{orderId}}', 'orderUpdateId': '{{orderUpdateId}}', 'action': 'DROP'},
        ),
    ]

    return SequenceDefinition(
        name='aiqs_complete_sequence',
        description='Komplette AIQS-Sequenz mit Quality-Check',
        steps=steps,
        context=context,
    )
