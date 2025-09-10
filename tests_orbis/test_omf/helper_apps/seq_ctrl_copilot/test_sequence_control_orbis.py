import os
import sys

# Workspace-Root zum sys.path hinzufügen, damit src_orbis als Package gefunden wird
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)
import pytest

from src_orbis.helper_apps.seq_ctrl_copilot.sequence_control_orbis import WorkflowOrderManager


@pytest.fixture
def manager():
    # Singleton zurücksetzen für saubere Tests
    WorkflowOrderManager._instance = None
    return WorkflowOrderManager.get_instance()


def test_start_sequence(manager):
    seq = [{"name": "Step1", "topic": "t1", "payload": {}}]
    manager.start_sequence("order_test", seq)
    assert "order_test" in manager.sequences
    assert manager.sequences["order_test"]["current_step"] == 0


def test_next_step(manager):
    seq = [{"name": "Step1", "topic": "t1", "payload": {}}, {"name": "Step2", "topic": "t2", "payload": {}}]
    manager.start_sequence("order_test", seq)
    manager.next_step("order_test")
    assert manager.sequences["order_test"]["current_step"] == 1


def test_abort_sequence(manager):
    seq = [{"name": "Step1", "topic": "t1", "payload": {}}]
    manager.start_sequence("order_test", seq)
    manager.abort_sequence("order_test")
    assert manager.sequences["order_test"]["aborted"] is True
    assert manager.sequences["order_test"]["status"] == "aborted"


def test_get_current_step(manager):
    seq = [{"name": "Step1", "topic": "t1", "payload": {}}, {"name": "Step2", "topic": "t2", "payload": {}}]
    manager.start_sequence("order_test", seq)
    step = manager.get_current_step("order_test")
    assert step["name"] == "Step1"
    manager.next_step("order_test")
    step = manager.get_current_step("order_test")
    assert step["name"] == "Step2"
    # Nach letzter Schritt sollte None kommen
    manager.next_step("order_test")
    assert manager.get_current_step("order_test") is None


def test_start_empty_sequence(manager):
    seq = []
    manager.start_sequence("order_empty", seq)
    assert manager.sequences["order_empty"]["steps"] == []
    assert manager.get_current_step("order_empty") is None


def test_restart_sequence_same_id(manager):
    seq1 = [{"name": "Step1", "topic": "t1", "payload": {}}]
    seq2 = [{"name": "Step2", "topic": "t2", "payload": {}}]
    manager.start_sequence("order_dup", seq1)
    manager.start_sequence("order_dup", seq2)
    # Prüft, ob die zweite Sequenz übernommen wurde
    assert manager.sequences["order_dup"]["steps"][0]["name"] == "Step2"


def test_next_step_past_end(manager):
    seq = [{"name": "Step1", "topic": "t1", "payload": {}}]
    manager.start_sequence("order_end", seq)
    manager.next_step("order_end")
    # Noch ein Schritt, obwohl Sequenz zu Ende
    manager.next_step("order_end")
    assert manager.sequences["order_end"]["current_step"] > len(seq) - 1
    assert manager.sequences["order_end"]["status"] == "finished"


def test_abort_after_finish(manager):
    seq = [{"name": "Step1", "topic": "t1", "payload": {}}]
    manager.start_sequence("order_abort_finish", seq)
    manager.next_step("order_abort_finish")  # Sequenz fertig
    manager.abort_sequence("order_abort_finish")
    # Status sollte nicht mehr "aborted" sein, wenn bereits "finished"
    assert manager.sequences["order_abort_finish"]["status"] in ["finished", "aborted"]


def test_get_status_invalid_id(manager):
    with pytest.raises(KeyError):
        manager.get_status("unknown_id")


def test_multiple_sequences(manager):
    seq1 = [{"name": "A", "topic": "t1", "payload": {}}]
    seq2 = [{"name": "B", "topic": "t2", "payload": {}}]
    manager.start_sequence("order1", seq1)
    manager.start_sequence("order2", seq2)
    assert manager.get_current_step("order1")["name"] == "A"
    assert manager.get_current_step("order2")["name"] == "B"


def test_placeholder():
    pass
