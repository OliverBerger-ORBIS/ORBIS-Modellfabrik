import pytest

from omf.tools.message_template_manager import OmfMessageTemplateManager
from omf.tools.validators import validate

class TestNodeRedTemplates:
    """Test Node-RED Template Migration"""

    def test_nodered_connection_dps_success(self):
        """Test erfolgreiche DPS Connection Validierung"""
        payload = {
            "connectionState": "ONLINE",
            "headerId": 2,
            "ip": "-1",
            "manufacturer": "Fischertechnik",
            "serialNumber": "SVR4H73275",
            "timestamp": "2025-08-19T09:08:58.660990Z",
            "version": "1.6.0+gitc321c85",
        }

        result = validate("module/v1/ff/NodeRed/SVR4H73275/connection", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_nodered_connection_dps_invalid_state(self):
        """Test DPS Connection mit ungültigem connectionState"""
        payload = {
            "connectionState": "OFFLINE",
            "headerId": 2,
            "ip": "-1",
            "manufacturer": "Fischertechnik",
            "serialNumber": "SVR4H73275",
            "timestamp": "2025-08-19T09:08:58.660990Z",
            "version": "1.6.0+gitc321c85",
        }

        result = validate("module/v1/ff/NodeRed/SVR4H73275/connection", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 1
        assert "connectionState should be 'ONLINE'" in result["warnings"][0]["msg"]

    def test_nodered_connection_aiqs_success(self):
        """Test erfolgreiche AIQS Connection Validierung"""
        payload = {
            "connectionState": "ONLINE",
            "headerId": 2,
            "manufacturer": "Fischertechnik",
            "serialNumber": "SVR4H76530",
            "timestamp": "2025-08-19T08:52:32.608107Z",
            "version": "1.0.0",
        }

        result = validate("module/v1/ff/NodeRed/SVR4H76530/connection", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_nodered_state_dps_success(self):
        """Test erfolgreiche DPS State Validierung"""
        payload = {
            "actionState": {
                "command": "PICK",
                "id": "327784cd-6abc-4a0b-870e-713694fdb1dd",
                "result": "PASSED",
                "state": "FINISHED",
                "timestamp": "2025-08-19T09:19:03.473043Z",
            },
            "actionStates": [
                {
                    "command": "PICK",
                    "id": "327784cd-6abc-4a0b-870e-713694fdb1dd",
                    "metadata": {
                        "workpiece": {
                            "history": [
                                {"code": 400, "ts": 1755595028336},
                                {"code": 600, "ts": 1755595064912},
                                {"code": 200, "ts": 1755595103032},
                            ],
                            "state": "PROCESSED",
                            "type": "RED",
                            "workpieceId": "040a8dca341291",
                        }
                    },
                    "result": "PASSED",
                    "state": "FINISHED",
                    "timestamp": "2025-08-19T09:19:03.473043Z",
                }
            ],
            "batteryState": {},
            "errors": [],
            "headerId": 15,
            "information": [],
            "operatingMode": "AUTOMATIC",
            "orderId": "8ae07a6e-d058-48de-9b4d-8d0176622abc",
            "orderUpdateId": 11,
            "paused": False,
            "serialNumber": "SVR4H73275",
            "timestamp": "2025-08-19T09:19:03.477244Z",
        }

        result = validate("module/v1/ff/NodeRed/SVR4H73275/state", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_nodered_state_aiqs_success(self):
        """Test erfolgreiche AIQS State Validierung"""
        payload = {
            "actionState": {
                "command": "CHECK_QUALITY",
                "id": "7b25fdfb-4a9e-419d-836c-c4348d9d9fd3",
                "result": "PASSED",
                "state": "FINISHED",
                "timestamp": "2025-08-19T09:18:22.005833Z",
            },
            "batteryState": {},
            "errors": [],
            "headerId": 7,
            "orderId": "8ae07a6e-d058-48de-9b4d-8d0176622abc",
            "orderUpdateId": 10,
            "paused": False,
            "serialNumber": "SVR4H76530",
            "timestamp": "2025-08-19T09:18:22.006119Z",
        }

        result = validate("module/v1/ff/NodeRed/SVR4H76530/state", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_nodered_factsheet_dps_success(self):
        """Test erfolgreiche DPS Factsheet Validierung"""
        payload = {
            "headerId": 1,
            "loadSpecification": {
                "loadSets": [
                    {"loadType": "WHITE", "setName": "WHITES"},
                    {"loadType": "RED", "setName": "REDS"},
                    {"loadType": "BLUE", "setName": "BLUES"},
                ]
            },
            "localizationParameters": {},
            "manufacturer": "Fischertechnik",
            "physicalParameters": {},
            "protocolFeatures": {
                "moduleActions": [
                    {
                        "actionParameters": [
                            {
                                "parameterDescription": "The load type to input",
                                "parameterName": "type",
                                "parameterType": "string",
                            }
                        ],
                        "actionType": "DROP",
                    }
                ]
            },
            "protocolLimits": {},
            "serialNumber": "SVR4H73275",
            "timestamp": "2025-08-19T09:13:34.529266Z",
            "typeSpecification": {"moduleClass": "DPS", "seriesName": "MOD-FF22+DPS"},
            "version": "1.6.0+gitc321c85",
        }

        result = validate("module/v1/ff/NodeRed/SVR4H73275/factsheet", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_nodered_factsheet_aiqs_success(self):
        """Test erfolgreiche AIQS Factsheet Validierung"""
        payload = {
            "headerId": 1,
            "loadSpecification": {"loadSets": []},
            "localizationParameters": {},
            "manufacturer": "Fischertechnik",
            "physicalParameters": {},
            "protocolFeatures": {
                "moduleActions": [
                    {
                        "actionParameters": [
                            {
                                "isOptional": True,
                                "parameterDescription": "Type of workpiece that should checked",
                                "parameterName": "type",
                                "parameterType": "string",
                            }
                        ],
                        "actionType": "CHECK_QUALITY",
                    }
                ]
            },
            "protocolLimits": {},
            "serialNumber": "SVR4H76530",
            "timestamp": "2025-08-19T09:13:34.247569Z",
            "typeSpecification": {"moduleClass": "AIQS24", "seriesName": "MOD-FF22+AIQS+24V+TXT"},
            "version": "1.3.0+git40c45a0",
        }

        result = validate("module/v1/ff/NodeRed/SVR4H76530/factsheet", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_nodered_missing_required_field(self):
        """Test fehlende required fields"""
        payload = {
            "connectionState": "ONLINE",
            "headerId": 2,
            # missing: ip, manufacturer, serialNumber, timestamp, version
        }

        result = validate("module/v1/ff/NodeRed/SVR4H73275/connection", payload)
        assert len(result["errors"]) > 0
        assert any("ip is required" in error["msg"] for error in result["errors"])
        assert any("manufacturer is required" in error["msg"] for error in result["errors"])

    def test_nodered_wrong_serial_number(self):
        """Test falsche Serial Number"""
        payload = {
            "connectionState": "ONLINE",
            "headerId": 2,
            "ip": "-1",
            "manufacturer": "Fischertechnik",
            "serialNumber": "WRONG_SERIAL",
            "timestamp": "2025-08-19T09:08:58.660990Z",
            "version": "1.6.0+gitc321c85",
        }

        result = validate("module/v1/ff/NodeRed/SVR4H73275/connection", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 1
        assert "serialNumber should be 'SVR4H73275'" in result["warnings"][0]["msg"]

class TestNodeRedMessageTemplateManager:
    """Test Node-RED Templates mit MessageTemplateManager"""

    def test_nodered_connection_dps_validation(self):
        """Test DPS Connection mit MessageTemplateManager"""
        manager = OmfMessageTemplateManager()

        payload = {
            "connectionState": "ONLINE",
            "headerId": 2,
            "ip": "-1",
            "manufacturer": "Fischertechnik",
            "serialNumber": "SVR4H73275",
            "timestamp": "2025-08-19T09:08:58.660990Z",
            "version": "1.6.0+gitc321c85",
        }

        result = manager.validate_payload("module/v1/ff/NodeRed/SVR4H73275/connection", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_nodered_connection_aiqs_validation(self):
        """Test AIQS Connection mit MessageTemplateManager"""
        manager = OmfMessageTemplateManager()

        payload = {
            "connectionState": "ONLINE",
            "headerId": 2,
            "manufacturer": "Fischertechnik",
            "serialNumber": "SVR4H76530",
            "timestamp": "2025-08-19T08:52:32.608107Z",
            "version": "1.0.0",
        }

        result = manager.validate_payload("module/v1/ff/NodeRed/SVR4H76530/connection", payload)
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0

    def test_nodered_unknown_template(self):
        """Test unbekanntes Template"""
        manager = OmfMessageTemplateManager()

        payload = {"test": "data"}
        result = manager.validate_payload("unknown/template", payload)
        # Sollte keine Errors/Warnings zurückgeben für unbekannte Templates
        assert isinstance(result, dict)
        assert "errors" in result
        assert "warnings" in result
