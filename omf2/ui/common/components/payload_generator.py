"""
Payload Generator Component
Generates schema-compliant payloads for MQTT topics
"""

import json
import streamlit as st
from typing import Dict, Any, Optional
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.common.logger import get_logger

logger = get_logger(__name__)


class PayloadGenerator:
    def __init__(self, registry_manager):
        self.registry_manager = registry_manager
    
    def generate_example_payload(self, topic: str) -> Optional[Dict[str, Any]]:
        """Generates an example payload for a given topic"""
        try:
            # Get schema for topic
            topic_schema = self.registry_manager.get_topic_schema(topic)
            
            if not topic_schema:
                return None
            
            # Load schema if it's a file path
            if isinstance(topic_schema, str):
                schema_path = self.registry_manager.registry_path / "schemas" / topic_schema
                if schema_path.exists():
                    with open(schema_path, 'r') as f:
                        schema = json.load(f)
                else:
                    return None
            else:
                schema = topic_schema
            
            if not isinstance(schema, dict):
                return None
            
            # Generate payload based on schema
            return self._generate_payload_from_schema(schema)
            
        except Exception as e:
            logger.error(f"❌ Error generating payload: {e}")
            st.error(f"❌ Error generating payload: {e}")
            return None
    
    def _generate_payload_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generates payload from schema definition"""
        payload = {}
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        # Handle wildcard schemas (no properties, but additionalProperties: true)
        if not properties and schema.get('additionalProperties', False):
            # Generate a simple payload for wildcard schemas
            return {
                "message": "test_message",
                "timestamp": "2024-01-01T00:00:00Z",
                "data": {}
            }
        
        for prop, prop_info in properties.items():
            # Generate all properties, not just required ones
            # This ensures protocolFeatures and other complex objects are generated
            logger.debug(f"Generating property: {prop}")
            payload[prop] = self._generate_property_value(prop, prop_info)
        
        return payload
    
    def _generate_property_value(self, prop: str, prop_info: Dict[str, Any]) -> Any:
        """Generates value for a specific property"""
        prop_type = prop_info.get('type')
        
        # Handle specific properties with known patterns
        if prop == 'orderUpdateId':
            return 0
        elif prop == 'protocolFeatures':
            # Handle protocol features for factsheets
            # Always generate both agvActions and moduleActions to cover all cases
            # This is a fallback approach since schema analysis is complex
            result = {}
            
            # Generate agvActions (for FTS factsheets)
            result["agvActions"] = [{
                "actionType": "test_action",
                "actionScopes": "test_scope"
            }]
            
            # Generate moduleActions (for Module factsheets)
            result["moduleActions"] = [{
                "actionType": "test_module_action",
                "actionParameters": [{
                    "parameterName": "test_param",
                    "parameterType": "string",
                    "parameterDescription": "Test parameter",
                    "isOptional": False
                }],
                "actionScopes": ["test_scope"]
            }]
            
            # Generate moduleParameters (for Module factsheets)
            result["moduleParameters"] = {
                "clearModuleOnPick": True
            }
            
            return result
        elif prop == 'orderId':
            return "test_order_123"
        elif prop == 'operatingMode':
            return "AUTOMATIC"
        elif prop == 'paused':
            return False
        elif prop == 'loads':
            return [{
                "loadType": "WHITE",
                "loadId": "047c8bca341291",
                "loadPosition": "A1",
                "loadTimestamp": 1759220483909
            }]
        elif prop == 'actionStates':
            return [{
                "id": "test_action",
                "state": "FINISHED",
                "command": "test_command",
                "timestamp": "2024-01-01T00:00:00Z",
                "metadata": {
                    "workpiece": {
                        "workpieceId": "test_workpiece_id",
                        "type": "test_type",
                        "state": "test_state",
                        "history": [{"ts": 1234567890, "code": 1}]
                    }
                }
            }]
        elif prop == 'actionState':
            return {
                "id": "test_action_state",
                "state": "FINISHED",
                "command": "test_command",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        elif prop == 'metadata':
            return {"opcuaState": "connected"}
        elif prop == 'batteryState':
            return {
                "charging": True,
                "currentVoltage": 12.0,
                "maxVolt": 14.4,
                "minVolt": 10.0,
                "percentage": 85
            }
        elif prop == 'navigationTypes':
            return ["example_nav1", "example_nav2"]
        elif prop == 'typeSpecification':
            # Handle different typeSpecification requirements
            if 'agvClass' in prop_info.get('properties', {}):
                return {
                    "agvClass": "test_agv_class",
                    "seriesName": "test_series",
                    "navigationTypes": ["example_nav1", "example_nav2"]
                }
            elif 'moduleClass' in prop_info.get('properties', {}):
                return {
                    "moduleClass": "test_module_class",
                    "seriesName": "test_series"
                }
            else:
                return {}
        elif prop == 'action':
            return {
                "id": "test_action_id",
                "command": "test_command",
                "metadata": {
                    "type": "test_type",
                    "workpieceId": "test_workpiece",
                    "duration": 1000,
                    "workpiece": {
                        "workpieceId": "test_workpiece",
                        "type": "test_type",
                        "state": "test_state",
                        "history": [{"ts": 1234567890, "code": 1}]
                    }
                }
            }
        elif prop == 'protocolFeatures':
            # Handle protocol features for factsheets
            # Always generate both agvActions and moduleActions to cover all cases
            # This is a fallback approach since schema analysis is complex
            result = {}
            
            # Generate agvActions (for FTS factsheets)
            result["agvActions"] = [{
                "actionType": "test_action",
                "actionScopes": "test_scope"
            }]
            
            # Generate moduleActions (for Module factsheets)
            result["moduleActions"] = [{
                "actionType": "test_module_action",
                "actionParameters": [{
                    "parameterName": "test_param",
                    "parameterType": "string",
                    "parameterDescription": "Test parameter",
                    "isOptional": False
                }],
                "actionScopes": ["test_scope"]
            }]
            
            # Generate moduleParameters (for Module factsheets)
            result["moduleParameters"] = {
                "clearModuleOnPick": True
            }
            
            return result
        elif prop == 'loadSpecification':
            return {
                "loadSets": [{
                    "setName": "test_load_set",
                    "loadType": "WHITE",
                    "maxAmount": 1
                }],
                "loadPositions": ["A1", "A2"]
            }
        
        # Handle by type
        if isinstance(prop_type, list):
            prop_type = prop_type[0]  # Take first type from union
        
        if prop_type == 'string':
            return f"test_{prop}"
        elif prop_type == 'integer':
            return 0
        elif prop_type == 'number':
            return 0.0
        elif prop_type == 'boolean':
            return False
        elif prop_type == 'array':
            items = prop_info.get('items', {})
            if items.get('type') == 'string':
                return ["example_item1", "example_item2"]
            return []
        elif prop_type == 'object':
            return {}
        
        return None
