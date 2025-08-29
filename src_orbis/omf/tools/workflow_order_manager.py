"""
WorkflowOrderManager für ORDER-ID Management
Verwaltet ORDER-IDs und orderUpdateId für sequenzielle Commands
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional


class WorkflowOrderManager:
    """Verwaltet ORDER-IDs und orderUpdateId für sequenzielle Commands"""

    def __init__(self):
        self.active_workflows: Dict[str, Dict] = {}
        self.workflow_history: List[Dict] = []

    def start_workflow(
        self, module: str, commands: List[str], workpiece_type: str = "WHITE"
    ) -> str:
        """Startet einen neuen Workflow und gibt orderId zurück"""
        order_id = str(uuid.uuid4())

        self.active_workflows[order_id] = {
            "orderId": order_id,
            "orderUpdateId": 0,
            "module": module,
            "commands": commands,
            "workpiece_type": workpiece_type,
            "status": "active",
            "start_time": datetime.now(),
            "executed_commands": [],
        }

        return order_id

    def get_next_order_update_id(self, order_id: str) -> int:
        """Gibt die nächste orderUpdateId für einen Workflow zurück"""
        if order_id in self.active_workflows:
            self.active_workflows[order_id]["orderUpdateId"] += 1
            return self.active_workflows[order_id]["orderUpdateId"]
        return 1

    def execute_command(self, order_id: str, command: str) -> Dict:
        """Führt einen Command im Workflow aus"""
        if order_id not in self.active_workflows:
            raise ValueError(f"Workflow {order_id} nicht gefunden")

        workflow = self.active_workflows[order_id]
        order_update_id = self.get_next_order_update_id(order_id)

        # Command ausführen
        workflow["executed_commands"].append(
            {
                "command": command,
                "orderUpdateId": order_update_id,
                "timestamp": datetime.now(),
            }
        )

        return {
            "orderId": order_id,
            "orderUpdateId": order_update_id,
            "command": command,
            "module": workflow["module"],
        }

    def complete_workflow(self, order_id: str) -> Dict:
        """Schließt einen Workflow ab"""
        if order_id not in self.active_workflows:
            raise ValueError(f"Workflow {order_id} nicht gefunden")

        workflow = self.active_workflows[order_id]
        workflow["status"] = "completed"
        workflow["end_time"] = datetime.now()

        # Zur Historie hinzufügen
        self.workflow_history.append(workflow.copy())
        del self.active_workflows[order_id]

        return workflow

    def get_workflow_status(self, order_id: str) -> Optional[Dict]:
        """Gibt den Status eines Workflows zurück"""
        return self.active_workflows.get(order_id)

    def get_active_workflows(self) -> Dict[str, Dict]:
        """Gibt alle aktiven Workflows zurück"""
        return self.active_workflows.copy()

    def get_workflow_history(self) -> List[Dict]:
        """Gibt die Workflow-Historie zurück"""
        return self.workflow_history.copy()


# Singleton-Instanz
_workflow_manager = None


def get_workflow_order_manager() -> WorkflowOrderManager:
    """Gibt die Singleton-Instanz des WorkflowOrderManager zurück"""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowOrderManager()
    return _workflow_manager
