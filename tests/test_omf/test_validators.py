#!/usr/bin/env python3
"""
Tests für die OMF Validierungsschicht
"""

import pytest

from omf.tools.message_template_manager import OmfMessageTemplateManager
from omf.tools.validators import validate


class TestValidators:
    """Test-Klasse für die Validator-Funktionen"""

    def test_drill_validation_success(self):
        """Test erfolgreiche DRILL-Validierung"""
        payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "actionState": {"command": "DRILL", "state": "RUNNING", "id": "123e4567-e89b-12d3-a456-426614174000"},
            "loads": [{"loadType": "RED", "duration": 5000}],
        }

        result = validate("module.state.drill", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_drill_validation_invalid_command(self):
        """Test DRILL-Validierung mit ungültigem Command"""
        payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "actionState": {"command": "INVALID_COMMAND", "state": "RUNNING"},
        }

        result = validate("module.state.drill", payload)
        assert len(result["errors"]) > 0
        assert any("invalid command" in error["msg"] for error in result["errors"])

    def test_drill_validation_missing_timestamp(self):
        """Test DRILL-Validierung ohne Timestamp"""
        payload = {"actionState": {"command": "DRILL", "state": "RUNNING"}}

        result = validate("module.state.drill", payload)
        assert len(result["errors"]) > 0
        assert any("missing required 'timestamp'" in error["msg"] for error in result["errors"])

    def test_hbw_inventory_validation_success(self):
        """Test erfolgreiche HBW Inventory-Validierung"""
        payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "loads": [{"loadPosition": "A1", "loadType": "RED", "loadTimestamp": 1642248600}],
            "actionState": {"command": "PICK", "state": "RUNNING"},
        }

        result = validate("module.state.hbw_inventory", payload)
        assert len(result["errors"]) == 0

    def test_hbw_inventory_validation_invalid_position(self):
        """Test HBW Inventory-Validierung mit ungültiger Position"""
        payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "loads": [{"loadPosition": "INVALID_POS", "loadType": "RED", "loadTimestamp": 1642248600}],
        }

        result = validate("module.state.hbw_inventory", payload)
        assert len(result["errors"]) > 0
        assert any("invalid loadPosition" in error["msg"] for error in result["errors"])

    def test_aiqs_validation_quality_check(self):
        """Test AIQS-Validierung für Quality Check"""
        payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "actionState": {
                "command": "CHECK_QUALITY",
                "state": "FINISHED",
                "result": "PASSED",
                "metadata": {"workpieceId": "1234567890ABCD"},
            },
        }

        result = validate("module.state.aiqs", payload)
        assert len(result["errors"]) == 0

    def test_aiqs_validation_invalid_result(self):
        """Test AIQS-Validierung mit ungültigem Result"""
        payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "actionState": {"command": "CHECK_QUALITY", "state": "FINISHED", "result": "INVALID_RESULT"},
        }

        result = validate("module.state.aiqs", payload)
        assert len(result["errors"]) > 0
        assert any("CHECK_QUALITY → muss result ∈ {PASSED,FAILED}" in error["msg"] for error in result["errors"])

    def test_ccu_pairing_validation_success(self):
        """Test erfolgreiche CCU Pairing-Validierung"""
        payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "modules": [{"available": "READY", "connected": True}],
            "transports": [{"batteryPercentage": 85}],
        }

        result = validate("ccu.state.pairing", payload)
        assert len(result["errors"]) == 0

    def test_ccu_pairing_validation_invalid_available(self):
        """Test CCU Pairing-Validierung mit ungültigem Available-Status"""
        payload = {"timestamp": "2024-01-15T10:30:00Z", "modules": [{"available": "INVALID_STATUS", "connected": True}]}

        result = validate("ccu.state.pairing", payload)
        assert len(result["errors"]) > 0
        assert any("CCU Pairing: available ∈ {READY,BUSY,BLOCKED}" in error["msg"] for error in result["errors"])

    def test_ccu_status_validation_success(self):
        """Test erfolgreiche CCU Status-Validierung"""
        payload = {
            "timestamp": "2024-01-15T10:30:00Z",
            "systemStatus": "RUNNING",
            "availableWorkpieces": [{"type": "RED", "workpieceId": "1234567890ABCD"}],
        }

        result = validate("ccu.state.status", payload)
        assert len(result["errors"]) == 0

    def test_ccu_status_validation_invalid_system_status(self):
        """Test CCU Status-Validierung mit ungültigem System-Status"""
        payload = {"timestamp": "2024-01-15T10:30:00Z", "systemStatus": "INVALID_STATUS"}

        result = validate("ccu.state.status", payload)
        assert len(result["errors"]) > 0
        assert any("invalid systemStatus" in error["msg"] for error in result["errors"])

    def test_unknown_template_key(self):
        """Test Validierung mit unbekanntem Template-Key"""
        payload = {"timestamp": "2024-01-15T10:30:00Z"}

        result = validate("unknown.template.key", payload)
        # Sollte nur generische Validierung durchführen
        assert "timestamp" in result or "errors" in result


class TestMessageTemplateManagerValidation:
    """Test-Klasse für die MessageTemplateManager-Validierung"""

    def setup_method(self):
        """Setup für jeden Test"""
        self.manager = OmfMessageTemplateManager()

    def test_validate_payload_success(self):
        """Test erfolgreiche Payload-Validierung über Manager"""
        payload = {"timestamp": "2024-01-15T10:30:00Z", "actionState": {"command": "DRILL", "state": "RUNNING"}}

        result = self.manager.validate_payload("module.state.drill", payload)
        assert "errors" in result
        assert "warnings" in result
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)

    def test_validate_payload_with_errors(self):
        """Test Payload-Validierung mit Fehlern"""
        payload = {"actionState": {"command": "INVALID_COMMAND", "state": "RUNNING"}}

        result = self.manager.validate_payload("module.state.drill", payload)
        assert len(result["errors"]) > 0
        assert any("missing required 'timestamp'" in error for error in result["errors"])
        assert any("invalid command" in error for error in result["errors"])

    def test_validate_payload_unknown_template(self):
        """Test Payload-Validierung mit unbekanntem Template"""
        payload = {"timestamp": "2024-01-15T10:30:00Z"}

        result = self.manager.validate_payload("unknown.template", payload)
        # Sollte trotzdem funktionieren (nur generische Validierung)
        assert "errors" in result
        assert "warnings" in result


class TestModuleConnectionValidation:
    """Test-Klasse für module/connection Validierung"""

    def test_module_connection_online_success(self):
        """Test erfolgreiche ONLINE-Validierung"""
        payload = {
            "connectionState": "ONLINE",
            "timestamp": "2024-01-15T10:30:00Z",
            "moduleId": "SVR3QA0022",
            "errors": [],
            "information": [],
        }

        result = validate("module.connection.hbw", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_module_connection_offline_success(self):
        """Test erfolgreiche OFFLINE-Validierung"""
        payload = {"connectionState": "OFFLINE", "timestamp": "2024-01-15T10:35:00Z", "moduleId": "SVR3QA0022"}

        result = validate("module.connection.hbw", payload)
        assert len(result["errors"]) == 0

    def test_module_connection_broken_success(self):
        """Test erfolgreiche CONNECTIONBROKEN-Validierung"""
        payload = {
            "connectionState": "CONNECTIONBROKEN",
            "timestamp": "2024-01-15T10:40:00Z",
            "moduleId": "SVR3QA0022",
            "errors": ["Network timeout after 30s"],
            "information": ["Last seen: 2024-01-15T10:39:30Z"],
        }

        result = validate("module.connection.hbw", payload)
        assert len(result["errors"]) == 0

    def test_module_connection_invalid_state(self):
        """Test Validierung mit ungültigem Connection State"""
        payload = {"connectionState": "INVALID_STATE", "timestamp": "2024-01-15T10:30:00Z"}

        result = validate("module.connection.hbw", payload)
        assert len(result["errors"]) > 0
        assert any("invalid connectionState" in error["msg"] for error in result["errors"])

    def test_module_connection_invalid_errors_type(self):
        """Test Validierung mit ungültigem Errors-Typ"""
        payload = {"connectionState": "ONLINE", "timestamp": "2024-01-15T10:30:00Z", "errors": "not_an_array"}

        result = validate("module.connection.hbw", payload)
        assert len(result["errors"]) > 0
        assert any("errors must be array" in error["msg"] for error in result["errors"])

    def test_module_connection_invalid_information_type(self):
        """Test Validierung mit ungültigem Information-Typ"""
        payload = {"connectionState": "ONLINE", "timestamp": "2024-01-15T10:30:00Z", "information": "not_an_array"}

        result = validate("module.connection.hbw", payload)
        assert len(result["warnings"]) > 0
        assert any("information should be array" in warning["msg"] for warning in result["warnings"])


if __name__ == "__main__":
    pytest.main([__file__])
