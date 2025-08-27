#!/usr/bin/env python3
"""
Unified Type Recognition Strategy
Provides consistent type recognition across all analyzers (TXT, CCU, MODUL, etc.)
"""

import re
from typing import Set, Any, Dict, List
from module_mapping_utils import ModuleMappingUtils

class UnifiedTypeRecognition:
    def __init__(self, module_mapping: ModuleMappingUtils):
        self.module_mapping = module_mapping
        
        # Regex patterns for type recognition
        self.datetime_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$'
        self.uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        self.module_id_pattern = r'^SVR[0-9A-Z]+$'
        self.nfc_code_pattern = r'^04[0-9a-f]{12}$'
        
        # Field-specific type mappings
        self.datetime_fields = {
            "timestamp", "ts", "startedAt", "receivedAt", "createdAt", 
            "updatedAt", "stoppedAt", "time", "date"
        }
        
        self.uuid_fields = {
            "orderId", "actionId", "dependentActionId", "id", "uuid", 
            "requestId", "sessionId", "transactionId"
        }
        
        self.numeric_fields = {
            "maxParallelOrders", "chargeThresholdPercent", "priority", 
            "count", "index", "port", "number", "amount", "quantity",
            "batteryVoltage", "batteryPercentage", "temperature", "humidity"
        }
        
        self.boolean_fields = {
            "connected", "available", "assigned", "hasCalibration", 
            "charging", "enabled", "active", "ready", "busy", "error"
        }
    
    def get_placeholder_for_field(self, field_name: str, values: Set[Any]) -> str:
        """
        Unified type recognition strategy with consistent order:
        1. Numbers (exact match)
        2. Booleans (exact match)
        3. Datetime (regex + field-based)
        4. UUIDs (regex + field-based)
        5. Module IDs (regex)
        6. NFC Codes (regex)
        7. Specific ENUMs (module mapping)
        8. Generic ENUMs (small sets)
        9. String (default)
        """
        if not values:
            return "<string>"
        
        # Handle context-aware values (tuples with path)
        context_values = {v for v in values if isinstance(v, tuple)}
        simple_values = {v for v in values if not isinstance(v, tuple)}
        
        # Convert all values to strings for analysis
        str_values = {str(v) for v in simple_values}
        
        # 1. Check for numbers (exact match)
        numeric_values = {v for v in simple_values if isinstance(v, (int, float)) or 
                         (isinstance(v, str) and v.replace('.', '').replace('-', '').isdigit())}
        if numeric_values and len(numeric_values) == len(simple_values):
            return "<number>"
        
        # 2. Check for booleans (exact match)
        bool_values = {v.lower() for v in str_values}
        if bool_values.issubset({"true", "false", "1", "0"}) and len(bool_values) > 0:
            # Double-check that these are actually boolean values
            actual_bool_count = 0
            for value in simple_values:
                if isinstance(value, bool) or str(value).lower() in ["true", "false", "1", "0"]:
                    actual_bool_count += 1
            
            if actual_bool_count == len(simple_values):
                return "<boolean>"
        
        # 3. Check for datetime (regex + field-based)
        if (field_name in self.datetime_fields or 
            any(re.match(self.datetime_pattern, v) for v in str_values)):
            return "<datetime>"
        
        # 4. Check for UUIDs (regex + field-based)
        if (field_name in self.uuid_fields or 
            any(re.match(self.uuid_pattern, v) for v in str_values)):
            return "<uuid>"
        
        # 5. Check for module IDs (regex)
        module_id_values = {v for v in str_values if re.match(self.module_id_pattern, v)}
        if module_id_values and len(module_id_values) == len(simple_values):
            return "<moduleId>"
        
        # 6. Check for NFC codes (regex)
        nfc_values = {v for v in str_values if re.match(self.nfc_code_pattern, v)}
        if nfc_values and len(nfc_values) == len(simple_values):
            return "<nfcCode>"
        
        # 7. Check for specific ENUMs using module mapping
        enum_result = self._check_specific_enums(field_name, str_values, context_values)
        if enum_result:
            return enum_result
        
        # 8. Check for generic ENUMs (small sets of unique values)
        if len(str_values) <= 10:
            # Don't treat specific field types as generic ENUMs
            if field_name not in self.datetime_fields | self.uuid_fields | self.numeric_fields | self.boolean_fields:
                unique_values = sorted(list(str_values))
                return f"[{', '.join(unique_values)}]"
        
        # 9. Default to string
        return "<string>"
    
    def _check_specific_enums(self, field_name: str, str_values: Set[str], context_values: Set[tuple]) -> str:
        """Check for specific ENUMs based on field name and module mapping"""
        
        # TXT-specific ENUMs
        if field_name == "type":
            type_values = {v.upper() for v in str_values}
            valid_types = set(self.module_mapping.get_enum_values('workpieceTypes'))
            if type_values.issubset(valid_types):
                return f"[{', '.join(sorted(valid_types))}]"
        
        if field_name == "state":
            state_values = {v.upper() for v in str_values}
            valid_states = set(self.module_mapping.get_enum_values('workpieceStates'))
            if state_values.issubset(valid_states):
                return f"[{', '.join(sorted(valid_states))}]"
        
        if field_name == "location":
            location_values = {v.upper() for v in str_values}
            valid_locations = set(self.module_mapping.get_enum_values('locations'))
            if location_values.issubset(valid_locations):
                return f"[{', '.join(sorted(valid_locations))}]"
        
        # CCU-specific ENUMs
        if field_name == "orderType":
            order_values = {v.upper() for v in str_values}
            valid_order_types = set(self.module_mapping.get_enum_values('orderTypes'))
            if order_values.issubset(valid_order_types):
                return f"[{', '.join(sorted(valid_order_types))}]"
        
        # Context-aware type field (CCU)
        if field_name == "type" and context_values:
            # Extract values by context
            production_step_types = {v[1] for v in context_values if "productionSteps" in v[0]}
            top_level_types = {v[1] for v in context_values if "productionSteps" not in v[0]}
            
            if production_step_types:
                production_type_values = {v.upper() for v in production_step_types}
                valid_action_types = set(self.module_mapping.get_enum_values('actionTypes'))
                if production_type_values.issubset(valid_action_types):
                    return f"[{', '.join(sorted(valid_action_types))}]"
            
            if top_level_types:
                top_type_values = {v.upper() for v in top_level_types}
                valid_workpiece_types = set(self.module_mapping.get_enum_values('workpieceTypes'))
                if top_type_values.issubset(valid_workpiece_types):
                    return f"[{', '.join(sorted(valid_workpiece_types))}]"
        
        # Action states
        if field_name == "state":
            state_values = {v.upper() for v in str_values}
            valid_states = set(self.module_mapping.get_enum_values('actionStates'))
            if state_values.issubset(valid_states):
                return f"[{', '.join(sorted(valid_states))}]"
        
        # Commands
        if field_name == "command":
            command_values = {v.upper() for v in str_values}
            valid_commands = set(self.module_mapping.get_enum_values('commands'))
            if command_values.issubset(valid_commands):
                return f"[{', '.join(sorted(valid_commands))}]"
        
        # Module types
        if field_name == "moduleType":
            module_values = {v.upper() for v in str_values}
            valid_module_types = set(self.module_mapping.get_enum_values('moduleSubTypes'))
            if module_values.issubset(valid_module_types):
                return f"[{', '.join(sorted(valid_module_types))}]"
        
        # Sources/targets
        if field_name in ["source", "target"]:
            location_values = {v.upper() for v in str_values}
            valid_locations = set(self.module_mapping.get_enum_values('moduleSubTypes')) | {"START"}
            if location_values.issubset(valid_locations):
                return f"[{', '.join(sorted(valid_locations))}]"
        
        return None

def main():
    """Test the unified type recognition"""
    module_mapping = ModuleMappingUtils()
    type_recognition = UnifiedTypeRecognition(module_mapping)
    
    print("🧪 Unified Type Recognition Test")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        ("timestamp", {"2025-08-19T09:16:14.679Z"}),
        ("orderId", {"123e4567-e89b-12d3-a456-426614174000"}),
        ("type", {"RED", "WHITE", "BLUE"}),
        ("state", {"IN_PROCESS", "WAITING_FOR_ORDER"}),
        ("connected", {"true", "false"}),
        ("count", {1, 2, 3}),
        ("serialNumber", {"SVR3QA0022"}),
        ("workpieceId", {"040a8dca341291"}),
        ("unknown", {"value1", "value2", "value3"}),
    ]
    
    for field_name, values in test_cases:
        result = type_recognition.get_placeholder_for_field(field_name, values)
        print(f"📋 {field_name}: {values} → {result}")

if __name__ == "__main__":
    main()
