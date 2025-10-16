"""
Tests für ModuleStateManager

Testet das automatische Timing-Management für Modul-Sequenzen.
"""

from unittest.mock import Mock

import pytest
from omf.tools.module_state_manager import (
    CommandType,
    ModuleInfo,
    ModuleSequence,
    ModuleState,
    ModuleStateManager,
    SequenceStep,
    get_module_state_manager,
)


class TestModuleStateManager:
    """Test-Klasse für ModuleStateManager"""

    def setup_method(self):
        """Setup für jeden Test"""
        # Singleton zurücksetzen
        from omf.tools.module_state_manager import ModuleStateManager

        ModuleStateManager._instance = None

        # Mock MQTT-Client und Gateway
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client.get_messages.return_value = []  # Leere Liste für get_messages
        self.mock_gateway = Mock()

        # ModuleStateManager initialisieren
        self.state_manager = get_module_state_manager()
        self.state_manager.initialize(self.mock_mqtt_client, self.mock_gateway)

        # Alle Sequenzen zurücksetzen
        self.state_manager._sequences.clear()

    def test_singleton_pattern(self):
        """Testet Singleton-Pattern"""
        manager1 = get_module_state_manager()
        manager2 = get_module_state_manager()

        assert manager1 is manager2
        assert isinstance(manager1, ModuleStateManager)

    def test_module_initialization(self):
        """Testet Modul-Initialisierung"""
        modules = self.state_manager.get_all_module_status()

        # Alle erwarteten Module sollten vorhanden sein
        expected_modules = ["AIQS", "MILL", "DRILL", "HBW", "DPS", "FTS"]
        assert all(module_id in modules for module_id in expected_modules)

        # AIQS-Modul prüfen
        aiqs = modules["AIQS"]
        assert aiqs.module_id == "AIQS"
        assert aiqs.module_name == "Qualitätsprüfung"
        assert aiqs.serial_number == "SVR4H76530"
        assert aiqs.current_state == ModuleState.IDLE

    def test_sequence_creation(self):
        """Testet Sequenz-Erstellung"""
        commands = [CommandType.PICK, CommandType.MILL, CommandType.DROP]
        sequence_id = self.state_manager.start_sequence(
            module_id="MILL", sequence_name="test_sequence", commands=commands, order_id="test_order_123"
        )

        assert sequence_id is not None
        assert sequence_id in self.state_manager._sequences

        sequence = self.state_manager._sequences[sequence_id]
        assert sequence.module_id == "MILL"
        assert sequence.sequence_name == "test_sequence"
        assert len(sequence.steps) == 3
        assert sequence.order_id == "test_order_123"
        assert sequence.status == "running"

    def test_sequence_steps(self):
        """Testet Sequenz-Schritte"""
        commands = [CommandType.PICK, CommandType.MILL, CommandType.DROP]
        sequence_id = self.state_manager.start_sequence("MILL", "test", commands)
        sequence = self.state_manager._sequences[sequence_id]

        # PICK-Schritt
        assert sequence.steps[0].command == CommandType.PICK
        assert sequence.steps[0].expected_state == ModuleState.PICKBUSY

        # MILL-Schritt
        assert sequence.steps[1].command == CommandType.MILL
        assert sequence.steps[1].expected_state == ModuleState.WAITING_AFTER_PICK

        # DROP-Schritt
        assert sequence.steps[2].command == CommandType.DROP
        assert sequence.steps[2].expected_state == ModuleState.DROPBUSY

    def test_module_ready_for_command(self):
        """Testet Modul-Bereitschaft für Commands"""
        module = self.state_manager._modules["MILL"]

        # Modul im IDLE-Zustand
        module.current_state = ModuleState.IDLE
        module.is_available = True

        # PICK sollte möglich sein
        assert self.state_manager._is_module_ready_for_command(module, CommandType.PICK)

        # MILL sollte nicht möglich sein
        assert not self.state_manager._is_module_ready_for_command(module, CommandType.MILL)

        # Modul nach PICK
        module.current_state = ModuleState.WAITING_AFTER_PICK

        # MILL sollte jetzt möglich sein
        assert self.state_manager._is_module_ready_for_command(module, CommandType.MILL)

        # DROP sollte auch möglich sein (nach WAITING_AFTER_PICK)
        assert self.state_manager._is_module_ready_for_command(module, CommandType.DROP)

    def test_command_sending(self):
        """Testet Command-Versand"""
        # Gateway-Mock konfigurieren
        self.mock_gateway.send.return_value = True

        # Sequenz erstellen
        commands = [CommandType.PICK]
        sequence_id = self.state_manager.start_sequence("MILL", "test", commands)
        sequence = self.state_manager._sequences[sequence_id]

        # Modul bereit machen
        module = self.state_manager._modules["MILL"]
        module.current_state = ModuleState.IDLE
        module.is_available = True

        # Command senden
        step = sequence.steps[0]
        success = self.state_manager._send_module_command(sequence, step)

        assert success
        self.mock_gateway.send.assert_called_once()

        # Prüfen ob korrekte Parameter übergeben wurden
        call_args = self.mock_gateway.send.call_args
        assert call_args[1]["topic"] == "module/v1/ff/SVR3QA2098/order"

        # Payload prüfen
        payload = call_args[1]["builder"]()
        assert payload["serialNumber"] == "SVR3QA2098"
        assert payload["action"]["command"] == "PICK"

    def test_sequence_monitoring(self):
        """Testet Sequenz-Überwachung"""
        # Sequenz erstellen
        commands = [CommandType.PICK, CommandType.MILL]
        sequence_id = self.state_manager.start_sequence("MILL", "test", commands)
        sequence = self.state_manager._sequences[sequence_id]

        # Gateway-Mock konfigurieren
        self.mock_gateway.send.return_value = True

        # Modul bereit machen
        module = self.state_manager._modules["MILL"]
        module.current_state = ModuleState.IDLE
        module.is_available = True

        # Sequenz-Schritt verarbeiten
        self.state_manager._process_sequence_step(sequence)

        # Prüfen ob Command gesendet wurde
        assert self.mock_gateway.send.called
        assert sequence.current_step == 1  # Nächster Schritt

    def test_sequence_completion(self):
        """Testet Sequenz-Abschluss"""
        # Sequenz mit einem Schritt erstellen
        commands = [CommandType.PICK]
        sequence_id = self.state_manager.start_sequence("MILL", "test", commands)
        sequence = self.state_manager._sequences[sequence_id]

        # Gateway-Mock konfigurieren
        self.mock_gateway.send.return_value = True

        # Modul bereit machen
        module = self.state_manager._modules["MILL"]
        module.current_state = ModuleState.IDLE
        module.is_available = True

        # Sequenz-Schritt verarbeiten
        self.state_manager._process_sequence_step(sequence)

        # Sequenz sollte abgeschlossen sein
        assert sequence.status == "completed"
        assert sequence.current_step == 1

    def test_sequence_stop(self):
        """Testet Sequenz-Stopp"""
        commands = [CommandType.PICK, CommandType.MILL]
        sequence_id = self.state_manager.start_sequence("MILL", "test", commands)

        # Sequenz stoppen
        self.state_manager.stop_sequence(sequence_id)

        sequence = self.state_manager._sequences[sequence_id]
        assert sequence.status == "cancelled"

    def test_running_sequences(self):
        """Testet laufende Sequenzen"""
        # Mehrere Sequenzen erstellen
        seq1 = self.state_manager.start_sequence("MILL", "test1", [CommandType.PICK])
        seq2 = self.state_manager.start_sequence("DRILL", "test2", [CommandType.PICK])

        # Eine Sequenz stoppen
        self.state_manager.stop_sequence(seq1)

        # Nur eine Sequenz sollte laufen
        running = self.state_manager.get_running_sequences()
        assert len(running) == 1
        assert seq2 in running

        # Alle Sequenzen stoppen für sauberen Zustand
        self.state_manager.stop_sequence(seq2)

    def test_module_status_updates(self):
        """Testet Modul-Status-Updates"""
        module = self.state_manager._modules["MILL"]

        # Mock-MQTT-Nachricht
        message = {"payload": {"state": "PICKBUSY", "status": "OK"}}

        # Status aktualisieren
        self.state_manager._update_module_state(module, message)

        # Prüfen ob Status aktualisiert wurde
        assert module.current_state == ModuleState.PICKBUSY
        assert module.is_available is True
        assert module.last_update is not None

    def test_error_handling(self):
        """Testet Fehlerbehandlung"""
        # Sequenz mit ungültigem Modul erstellen
        with pytest.raises(ValueError):
            self.state_manager.start_sequence("INVALID", "test", [CommandType.PICK])

        # Gateway-Fehler simulieren
        self.mock_gateway.send.return_value = False

        commands = [CommandType.PICK]
        sequence_id = self.state_manager.start_sequence("MILL", "test", commands)
        sequence = self.state_manager._sequences[sequence_id]

        module = self.state_manager._modules["MILL"]
        module.current_state = ModuleState.IDLE
        module.is_available = True

        # Command senden sollte fehlschlagen
        step = sequence.steps[0]
        success = self.state_manager._send_module_command(sequence, step)

        assert not success

    def test_shutdown(self):
        """Testet ordnungsgemäßes Herunterfahren"""
        # State Manager herunterfahren
        self.state_manager.shutdown()

        # Prüfen ob Thread gestoppt wurde
        assert not self.state_manager._running
        assert self.state_manager._stop_event.is_set()


class TestModuleState:
    """Test-Klasse für ModuleState Enum"""

    def test_module_state_values(self):
        """Testet ModuleState Werte"""
        assert ModuleState.IDLE.value == "IDLE"
        assert ModuleState.PICKBUSY.value == "PICKBUSY"
        assert ModuleState.ERROR.value == "ERROR"


class TestCommandType:
    """Test-Klasse für CommandType Enum"""

    def test_command_type_values(self):
        """Testet CommandType Werte"""
        assert CommandType.PICK.value == "PICK"
        assert CommandType.MILL.value == "MILL"
        assert CommandType.DROP.value == "DROP"


class TestModuleInfo:
    """Test-Klasse für ModuleInfo Dataclass"""

    def test_module_info_creation(self):
        """Testet ModuleInfo Erstellung"""
        module = ModuleInfo(
            module_id="TEST", module_name="Test Module", module_type="Processing", serial_number="TEST123"
        )

        assert module.module_id == "TEST"
        assert module.current_state == ModuleState.IDLE
        assert module.is_available is True


class TestSequenceStep:
    """Test-Klasse für SequenceStep Dataclass"""

    def test_sequence_step_creation(self):
        """Testet SequenceStep Erstellung"""
        step = SequenceStep(command=CommandType.PICK, expected_state=ModuleState.PICKBUSY, timeout=30)

        assert step.command == CommandType.PICK
        assert step.expected_state == ModuleState.PICKBUSY
        assert step.timeout == 30
        assert step.metadata == {}


class TestModuleSequence:
    """Test-Klasse für ModuleSequence Dataclass"""

    def test_module_sequence_creation(self):
        """Testet ModuleSequence Erstellung"""
        steps = [
            SequenceStep(CommandType.PICK, ModuleState.PICKBUSY),
            SequenceStep(CommandType.MILL, ModuleState.WAITING_AFTER_PICK),
        ]

        sequence = ModuleSequence(module_id="MILL", sequence_name="test_sequence", steps=steps, order_id="test_order")

        assert sequence.module_id == "MILL"
        assert sequence.sequence_name == "test_sequence"
        assert len(sequence.steps) == 2
        assert sequence.current_step == 0
        assert sequence.status == "pending"
        assert sequence.order_id == "test_order"
