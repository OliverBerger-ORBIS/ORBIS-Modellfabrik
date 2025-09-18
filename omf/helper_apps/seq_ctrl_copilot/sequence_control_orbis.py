import threading
from typing import Any, Dict, List, Optional

class WorkflowOrderManager:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if WorkflowOrderManager._instance is not None:
            raise Exception("Singleton!")
        self.sequences = {}
        WorkflowOrderManager._instance = self

    @staticmethod
    def get_instance():
        with WorkflowOrderManager._lock:
            if WorkflowOrderManager._instance is None:
                WorkflowOrderManager()
            return WorkflowOrderManager._instance

    def start_sequence(self, order_id: str, sequence: List[Dict[str, Any]]):
        self.sequences[order_id] = {
            "steps": sequence,
            "current_step": 0,
            "aborted": False,
            "orderUpdateId": 0,
            "status": "running",
        }

    def next_step(self, order_id: str):
        seq = self.sequences[order_id]
        if seq["aborted"]:
            return None
        seq["current_step"] += 1
        seq["orderUpdateId"] += 1
        if seq["current_step"] >= len(seq["steps"]):
            seq["status"] = "finished"

    def abort_sequence(self, order_id: str):
        seq = self.sequences[order_id]
        seq["aborted"] = True
        seq["status"] = "aborted"

    def get_status(self, order_id: str) -> str:
        return self.sequences[order_id]["status"]

    def get_current_step(self, order_id: str) -> Optional[Dict[str, Any]]:
        seq = self.sequences.get(order_id)
        if not seq or seq["current_step"] >= len(seq["steps"]):
            return None
        return seq["steps"][seq["current_step"]]
