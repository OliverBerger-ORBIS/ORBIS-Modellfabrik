from typing import Callable, Dict, Any, List

class PythonSequence:
    """Definiert eine Sequenz und ihre Schritte per Python-Objekt."""
    def __init__(self, name: str, module: str):
        self.name = name
        self.module = module
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, name: str, step_type: str, func: Callable, context: Dict[str, Any] = None):
        self.steps.append({
            "name": name,
            "type": step_type,
            "func": func,
            "context": context or {},
        })

    def run_step(self, idx: int, global_context: Dict[str, Any]) -> Any:
        step = self.steps[idx]
        return step["func"](step["context"], global_context)

# Beispiel für eine individuelle Sequenz mit Logik

def pick_step(step_ctx, global_ctx):
    # Individuelle Logik, z.B. dynamische Payload
    return {"topic": f"module/v1/ff/{global_ctx['module']}/order", "payload": {"action": "PICK", "orderId": global_ctx["orderId"]}}

def wait_pick_step(step_ctx, global_ctx):
    # Warten auf Event, z.B. mit Pattern-Matching
    return {"wait_for": "PICK_DONE", "orderId": global_ctx["orderId"]}

def mill_step(step_ctx, global_ctx):
    return {"topic": f"module/v1/ff/{global_ctx['module']}/order", "payload": {"action": "MILL", "orderId": global_ctx["orderId"]}}

def drop_step(step_ctx, global_ctx):
    return {"topic": f"module/v1/ff/{global_ctx['module']}/order", "payload": {"action": "DROP", "orderId": global_ctx["orderId"]}}

python_sequence = PythonSequence("MILL_SEQUENCE_PY", "MILL-01")
python_sequence.add_step("PICK", "command", pick_step)
python_sequence.add_step("WAIT_PICK", "wait", wait_pick_step)
python_sequence.add_step("MILL", "command", mill_step)
python_sequence.add_step("DROP", "command", drop_step)

# Zugriff: python_sequence.steps, python_sequence.run_step(idx, context)
