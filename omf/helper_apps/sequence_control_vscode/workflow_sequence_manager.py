import threading
from typing import Any, Dict, Optional

from omf.tools.workflow_order_manager import get_workflow_order_manager

from .sequence_loader import SequenceLoader


class WorkflowSequenceManager:
    """Verwaltet die Ausführung von Sequenzen als logische Einheit."""

    def __init__(self, recipes_dir: str):
        self.loader = SequenceLoader(recipes_dir)
        self.active_sequences: Dict[str, Dict] = {}
        self.lock = threading.Lock()

    def start_sequence(self, sequence_name: str, module: str, context: Optional[Dict[str, Any]] = None) -> str:
        sequence = self.loader.load_sequence(sequence_name)
        workflow_manager = get_workflow_order_manager()
        order_id = workflow_manager.start_workflow(module, [step["name"] for step in sequence["steps"]])
        seq_context = {
            "orderId": order_id,
            "orderUpdateId": 0,
            "module": module,
        }
        if context:
            seq_context.update(context)
        self.active_sequences[order_id] = {
            "sequence": sequence,
            "context": seq_context,
            "current_step": 0,
            "status": "active",
        }
        return order_id

    def get_sequence_status(self, order_id: str) -> Optional[Dict]:
        return self.active_sequences.get(order_id)

    def next_step(self, order_id: str) -> Optional[Dict]:
        seq = self.active_sequences.get(order_id)
        if not seq or seq["status"] != "active":
            return None
        steps = seq["sequence"]["steps"]
        idx = seq["current_step"]
        if idx >= len(steps):
            seq["status"] = "completed"
            return None
        step = steps[idx]
        seq["current_step"] += 1
        return step

    def abort_sequence(self, order_id: str):
        if order_id in self.active_sequences:
            self.active_sequences[order_id]["status"] = "aborted"


# Singleton
_sequence_manager = None


def get_workflow_sequence_manager(recipes_dir: str) -> WorkflowSequenceManager:
    global _sequence_manager
    if _sequence_manager is None:
        _sequence_manager = WorkflowSequenceManager(recipes_dir)
    return _sequence_manager
