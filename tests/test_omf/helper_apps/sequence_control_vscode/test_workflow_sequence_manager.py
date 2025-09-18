from pathlib import Path

# Workspace-Root zum sys.path hinzufügen, damit omf als Package gefunden wird
WORKSPACE_ROOT = os.path.abspath(str(Path(__file__).parent / ".." / ".." / ".."))
if WORKSPACE_ROOT not in sys.path:
    import pytest

from omf.helper_apps.sequence_control_vscode.workflow_sequence_manager import WorkflowSequenceManager

@pytest.fixture
def manager():
    """Test fixture für WorkflowSequenceManager."""
    return WorkflowSequenceManager("omf/helper_apps/sequence_control_vscode/recipes")

def test_manager_initialization(manager):
    """Test der Initialisierung des WorkflowSequenceManager."""
    assert manager.loader is not None
    assert manager.active_sequences == {}
    assert manager.lock is not None

def test_start_sequence(manager):
    """Test des Startens einer Sequenz."""
    # Mock sequence data
    test_sequence = {
        "name": "test_sequence",
        "steps": [{"name": "step1", "action": "test_action1"}, {"name": "step2", "action": "test_action2"}],
    }

    # Mock loader
    manager.loader.load_sequence = lambda name: test_sequence

    # Mock workflow manager
    class MockWorkflowManager:
        def start_workflow(self, module, steps):
            return "test_order_123"

    from omf.tools.workflow_order_manager import get_workflow_order_manager

    original_manager = get_workflow_order_manager

    def mock_get_workflow_order_manager():
        return MockWorkflowManager()

    get_workflow_order_manager = mock_get_workflow_order_manager

    try:
        order_id = manager.start_sequence("test_sequence", "test_module")
        # Der echte WorkflowOrderManager generiert UUIDs, daher prüfen wir nur dass eine ID zurückgegeben wird
        assert order_id is not None
        assert order_id in manager.active_sequences
        assert manager.active_sequences[order_id]["sequence"] == test_sequence
        assert manager.active_sequences[order_id]["context"]["module"] == "test_module"
        assert manager.active_sequences[order_id]["current_step"] == 0
    finally:
        get_workflow_order_manager = original_manager

def test_get_sequence_status(manager):
    """Test des Abrufens des Sequenz-Status."""
    # Mock active sequence
    test_sequence = {"name": "test_sequence", "steps": [{"name": "step1"}, {"name": "step2"}]}
    manager.active_sequences["test_order_123"] = {
        "sequence": test_sequence,
        "context": {"module": "test_module"},
        "current_step": 1,
        "status": "active",
    }

    status = manager.get_sequence_status("test_order_123")
    assert status is not None
    assert status["current_step"] == 1
    assert status["status"] == "active"
    assert len(status["sequence"]["steps"]) == 2

def test_get_sequence_status_not_found(manager):
    """Test des Abrufens des Status einer nicht existierenden Sequenz."""
    status = manager.get_sequence_status("nonexistent_order")
    assert status is None

def test_abort_sequence(manager):
    """Test des Abbrechens einer Sequenz."""
    # Mock active sequence
    test_sequence = {"name": "test_sequence", "steps": [{"name": "step1"}]}
    manager.active_sequences["test_order_123"] = {
        "sequence": test_sequence,
        "context": {"module": "test_module"},
        "current_step": 0,
        "status": "active",
    }

    manager.abort_sequence("test_order_123")
    assert manager.active_sequences["test_order_123"]["status"] == "aborted"

def test_abort_sequence_not_found(manager):
    """Test des Abbrechens einer nicht existierenden Sequenz."""
    # Sollte keinen Fehler werfen
    manager.abort_sequence("nonexistent_order")
    assert True  # Test bestanden wenn keine Exception geworfen wird
