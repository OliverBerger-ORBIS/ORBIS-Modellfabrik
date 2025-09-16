"""
WorkflowOrderManager - Singleton für ID-Management von Sequenzen
Verwaltet orderId und orderUpdateId für konsistente Sequenz-Ausführung
"""

import uuid
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class WorkflowOrder:
    """Repräsentiert eine Workflow-Order mit ID-Management"""

    order_id: str
    order_update_id: int
    sequence_name: str
    status: str  # "running", "completed", "cancelled", "error"
    current_step: int = 0
    total_steps: int = 0
    context: Dict = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


class WorkflowOrderManager:
    """Singleton für Workflow-Order-Management"""

    _instance = None
    _orders: Dict[str, WorkflowOrder] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_order(self, sequence_name: str) -> WorkflowOrder:
        """Erstellt eine neue Workflow-Order"""
        order_id = str(uuid.uuid4())
        order = WorkflowOrder(
            order_id=order_id,
            order_update_id=0,
            sequence_name=sequence_name,
            status="running",
            current_step=0,
            total_steps=0,
        )
        self._orders[order_id] = order
        return order

    def get_order(self, order_id: str) -> Optional[WorkflowOrder]:
        """Holt eine Workflow-Order"""
        return self._orders.get(order_id)

    def increment_update_id(self, order_id: str) -> int:
        """Inkrementiert orderUpdateId für nächsten Schritt"""
        order = self._orders.get(order_id)
        if order:
            order.order_update_id += 1
            return order.order_update_id
        return 0

    def update_step(self, order_id: str, step: int, total_steps: int = None):
        """Aktualisiert aktuellen Schritt"""
        order = self._orders.get(order_id)
        if order:
            order.current_step = step
            if total_steps is not None:
                order.total_steps = total_steps

    def complete_order(self, order_id: str):
        """Markiert Order als abgeschlossen"""
        order = self._orders.get(order_id)
        if order:
            order.status = "completed"

    def cancel_order(self, order_id: str):
        """Bricht Order ab"""
        order = self._orders.get(order_id)
        if order:
            order.status = "cancelled"

    def set_error(self, order_id: str):
        """Markiert Order als Fehler"""
        order = self._orders.get(order_id)
        if order:
            order.status = "error"

    def start_workflow(self, module_name: str, commands: list) -> str:
        """Startet einen neuen Workflow für ein Modul"""
        order = self.create_order(f"{module_name}_workflow")
        order.context = {"module": module_name, "commands": commands, "current_command_index": 0}
        return order.order_id

    def execute_command(self, order_id: str, command: str) -> dict:
        """Führt einen Befehl aus und gibt Workflow-Info zurück"""
        order = self._orders.get(order_id)
        if not order:
            return {"orderUpdateId": 0}

        # orderUpdateId inkrementieren
        order_update_id = self.increment_update_id(order_id)

        # Aktuellen Schritt aktualisieren
        if order.context and "current_command_index" in order.context:
            order.context["current_command_index"] += 1

        return {"orderUpdateId": order_update_id, "orderId": order_id, "command": command}

    def get_next_order_update_id(self, order_id: str) -> int:
        """Gibt die nächste orderUpdateId zurück"""
        return self.increment_update_id(order_id)

    def get_active_workflows(self) -> Dict[str, WorkflowOrder]:
        """Gibt alle aktiven Workflows zurück"""
        return {order_id: order for order_id, order in self._orders.items() if order.status == "running"}

    def get_all_orders(self) -> Dict[str, WorkflowOrder]:
        """Gibt alle Orders zurück"""
        return self._orders.copy()

    def clear_completed_orders(self):
        """Löscht abgeschlossene Orders"""
        self._orders = {order_id: order for order_id, order in self._orders.items() if order.status == "running"}


# Singleton-Instanz
workflow_order_manager = WorkflowOrderManager()


def get_workflow_order_manager() -> WorkflowOrderManager:
    """Gibt die Singleton-Instanz des WorkflowOrderManager zurück"""
    return workflow_order_manager
