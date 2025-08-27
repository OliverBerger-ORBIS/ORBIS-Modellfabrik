#!/usr/bin/env python3
"""
CCU Template Analyzer
Analyzes CCU (Central Control Unit) MQTT messages and generates templates
"""

import json
import sqlite3
import os
import glob
import re
from datetime import datetime
from typing import Dict, List, Any, Set
from module_manager import get_module_manager
import copy
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src_orbis.mqtt.tools.nfc_code_manager import get_nfc_manager

class CCUTemplateAnalyzer:
    def __init__(self):
        self.target_topics = [
            "ccu/global",
            "ccu/order/active",
            "ccu/order/completed",
            "ccu/order/request",
            "ccu/order/response",
            "ccu/pairing/pair_fts",
            "ccu/pairing/state",
            "ccu/set/charge",
            "ccu/set/reset",
            "ccu/state/config",
            "ccu/state/flows",
            "ccu/state/layout",
            "ccu/state/stock",
            "ccu/state/version-mismatch"
        ]
        
        # Initialize module mapping utilities
        self.module_mapping = get_module_manager()
        # Get project root (3 levels up from tools directory)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        
        # Set paths relative to project root
        self.output_dir = os.path.join(project_root, "mqtt-data/template_library")
        self.session_dir = os.path.join(project_root, "mqtt-data/sessions")
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("🔧 CCU Template Analyzer initialisiert")
        print(f"📁 Ausgabe-Verzeichnis: {self.output_dir}")
        print(f"📁 Session-Verzeichnis: {self.session_dir}")

    def get_placeholder_for_field(self, field_name: str, values: Set) -> str:
        """Generate placeholder for field based on values using unified type recognition"""
        if not values:
            return "<string>"
        
        # Handle context-aware values (tuples with path)
        context_values = {v for v in values if isinstance(v, tuple)}
        simple_values = {v for v in values if not isinstance(v, tuple)}
        
        # Convert all values to strings for analysis
        str_values = {str(v) for v in simple_values}
        
        # 1. Check for booleans (exact match) - PRIORITY over numbers
        bool_values = {v.lower() for v in str_values}
        if bool_values.issubset({"true", "false", "1", "0"}) and len(bool_values) > 0:
            # Double-check that these are actually boolean values
            actual_bool_count = 0
            for value in simple_values:
                if isinstance(value, bool) or str(value).lower() in ["true", "false", "1", "0"]:
                    actual_bool_count += 1
            
            if actual_bool_count == len(simple_values):
                return "<boolean>"
        
        # 2. Check for numbers (exact match)
        numeric_values = {v for v in simple_values if isinstance(v, (int, float)) or 
                         (isinstance(v, str) and v.replace('.', '').replace('-', '').isdigit())}
        if numeric_values and len(numeric_values) == len(simple_values):
            return "<number>"
        
        # 3. Check for datetime (regex + field-based)
        datetime_fields = {"timestamp", "ts", "startedAt", "receivedAt", "createdAt", "updatedAt", "stoppedAt", "time", "date"}
        if (field_name in datetime_fields or 
            any(re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$', v) for v in str_values)):
            return "<datetime>"
        
        # 4. Check for UUIDs (regex + field-based)
        uuid_fields = {"orderId", "actionId", "dependentActionId", "id", "uuid", "requestId", "sessionId", "transactionId"}
        if (field_name in uuid_fields or 
            any(re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', v) for v in str_values)):
            return "<uuid>"
        
        # 5. Check for module IDs (regex)
        module_id_values = {v for v in str_values if re.match(r'^SVR[0-9A-Z]+$', v)}
        if module_id_values and len(module_id_values) == len(simple_values):
            return "<moduleId>"
        
        # 6. Check for NFC codes (regex + YAML config)
        nfc_manager = get_nfc_manager()
        nfc_values = {v for v in str_values if nfc_manager.is_nfc_code(v)}
        if nfc_values and len(nfc_values) == len(simple_values):
            return "<nfcCode>"
        
        # 7. Check for specific ENUMs using module mapping
        enum_result = self._check_specific_enums(field_name, str_values, context_values)
        if enum_result:
            return enum_result
        
        # 8. Check for generic ENUMs (small sets of unique values)
        if len(str_values) <= 10:
            # Don't treat specific field types as generic ENUMs
            specific_fields = datetime_fields | uuid_fields | {"maxParallelOrders", "chargeThresholdPercent", "priority", "count", "index", "port", "number", "amount", "quantity", "batteryVoltage", "batteryPercentage", "temperature", "humidity"} | {"connected", "available", "assigned", "hasCalibration", "charging", "enabled", "active", "ready", "busy", "error"}
            if field_name not in specific_fields:
                # Check if all values are of the same type (all strings, all numbers, etc.)
                all_strings = all(isinstance(v, str) for v in simple_values)
                all_numbers = all(isinstance(v, (int, float)) for v in simple_values)
                
                # Only treat as ENUM if ALL values are of the same type
                if all_strings and not all_numbers:
                    # Check if these are actually mixed types (numbers as strings + text)
                    numeric_strings = {v for v in str_values if v.replace('.', '').replace('-', '').isdigit()}
                    text_strings = str_values - numeric_strings
                    
                    # Check if these are boolean-like mixed values
                    boolean_like = {v.lower() for v in str_values}
                    boolean_strings = {v for v in str_values if v.lower() in ["true", "false", "1", "0"]}
                    non_boolean_strings = str_values - boolean_strings
                    
                    if (numeric_strings and text_strings) or (boolean_strings and non_boolean_strings):
                        # Mixed types - treat as string
                        return "<string>"
                    else:
                        # All same type - treat as ENUM
                        unique_values = sorted(list(str_values))
                        return f"[{', '.join(unique_values)}]"
                elif all_numbers and not all_strings:
                    unique_values = sorted(list(str_values))
                    return f"[{', '.join(unique_values)}]"
        
        # 9. Default to string
        return "<string>"
    
    def _check_specific_enums(self, field_name: str, str_values: Set[str], context_values: Set[tuple]) -> str:
        """Check for specific ENUMs based on field name and module mapping"""
        
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
            # Check if any of the values match action states
            if any(state in valid_states for state in state_values):
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

    def analyze_payload_structure(self, payloads: List[Dict]) -> Dict:
        """Analyze structure of payloads and create hierarchical template"""
        if not payloads:
            return {}
        
        # Handle array payloads (like ccu/order/active)
        if isinstance(payloads[0], list):
            # Take the first dictionary from the array for structure analysis
            first_dict = None
            for payload in payloads:
                if isinstance(payload, list) and len(payload) > 0:
                    if isinstance(payload[0], dict):
                        first_dict = payload[0]
                        break
            
            if first_dict:
                # Analyze the structure of the first dictionary
                return self._analyze_field_structure("array_element", first_dict, payloads)
        
        # Handle regular dictionary payloads
        first_payload = payloads[0] if payloads else {}
        template = {}
        
        for key, value in first_payload.items():
            if isinstance(value, dict):
                # Nested object
                nested_template = {}
                for sub_key, sub_value in value.items():
                    nested_template[sub_key] = self._analyze_field_structure(sub_key, sub_value, payloads)
                template[key] = nested_template
            elif isinstance(value, list) and value:
                # Array
                first_element = value[0]
                if isinstance(first_element, dict):
                    # Array of objects
                    element_template = {}
                    for sub_key, sub_value in first_element.items():
                        element_template[sub_key] = self._analyze_field_structure(sub_key, sub_value, payloads)
                    template[key] = [element_template]
                else:
                    # Array of simple values
                    template[key] = [self._analyze_field_structure(key, first_element, payloads)]
            else:
                # Simple value
                template[key] = self._analyze_field_structure(key, value, payloads)
        
        return template
    
    def _analyze_field_structure(self, field_name: str, value, all_payloads: List[Dict]) -> any:
        """Analyze structure of a specific field across all payloads"""
        if isinstance(value, dict):
            # Nested object - analyze recursively
            nested_template = {}
            for sub_key, sub_value in value.items():
                nested_template[sub_key] = self._analyze_field_structure(sub_key, sub_value, all_payloads)
            return nested_template
        elif isinstance(value, list) and value:
            # Array - analyze first element
            first_element = value[0]
            if isinstance(first_element, dict):
                # Array of objects
                element_template = {}
                for sub_key, sub_value in first_element.items():
                    element_template[sub_key] = self._analyze_field_structure(sub_key, sub_value, all_payloads)
                return [element_template]  # Return as list with one element template
            else:
                # Array of simple values
                return [self._analyze_field_structure(field_name, first_element, all_payloads)]
        else:
            # Simple value - collect all values for this field across all payloads
            all_values = set()
            for payload in all_payloads:
                if isinstance(payload, dict) and field_name in payload:
                    field_value = payload[field_name]
                    if isinstance(field_value, (list, dict)):
                        all_values.add(str(field_value))
                    else:
                        all_values.add(field_value)
                elif isinstance(payload, list):
                    # Handle array payloads - extract values from nested structures
                    for item in payload:
                        if isinstance(item, dict):
                            # Extract values from nested objects with context
                            self._extract_values_from_nested(item, field_name, all_values)
                        elif field_name in item:
                            field_value = item[field_name]
                            if isinstance(field_value, (list, dict)):
                                all_values.add(str(field_value))
                            else:
                                all_values.add(field_value)
            
            return self.get_placeholder_for_field(field_name, all_values)
    
    def _extract_values_from_nested(self, obj: dict, target_field: str, all_values: set, field_path: str = ""):
        """Recursively extract values for a specific field from nested structures with context"""
        current_path = f"{field_path}.{target_field}" if field_path else target_field
        
        for key, value in obj.items():
            if key == target_field:
                if isinstance(value, (list, dict)):
                    all_values.add(str(value))
                else:
                    # Store value with context path
                    all_values.add((current_path, value))
            elif isinstance(value, dict):
                self._extract_values_from_nested(value, target_field, all_values, current_path)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._extract_values_from_nested(item, target_field, all_values, current_path)

    def analyze_topic_structure(self, topic: str, messages: List[Dict]) -> Dict:
        """Analyze structure for a specific topic"""
        print(f"  📊 Analysiere {len(messages)} Nachrichten für {topic}")
        
        # Extract payloads
        payloads = []
        for msg in messages:
            try:
                payload = json.loads(msg['payload'])
                payloads.append(payload)
            except (json.JSONDecodeError, KeyError):
                continue
        
        if not payloads:
            print(f"  ⚠️  Keine gültigen Payloads für {topic}")
            return {
                "topic": topic,
                "category": "CCU (Central Control Unit)",
                "message_count": len(messages),
                "template_structure": {},
                "examples": [],
                "statistics": {
                    "total_messages": len(messages),
                    "valid_payloads": 0,
                    "variable_fields": 0,
                    "enum_fields": 0
                }
            }
        
        # Analyze structure
        template_structure = self.analyze_payload_structure(payloads)
        
        # Count field types
        variable_fields = 0
        enum_fields = 0
        for placeholder in template_structure.values():
            if isinstance(placeholder, str):
                if placeholder.startswith("<"):
                    variable_fields += 1
                elif placeholder.startswith("["):
                    enum_fields += 1
            elif isinstance(placeholder, list):
                # Count nested fields in arrays
                for item in placeholder:
                    if isinstance(item, dict):
                        for sub_placeholder in item.values():
                            if isinstance(sub_placeholder, str):
                                if sub_placeholder.startswith("<"):
                                    variable_fields += 1
                                elif sub_placeholder.startswith("["):
                                    enum_fields += 1
            elif isinstance(placeholder, dict):
                # Count nested fields in objects
                for sub_placeholder in placeholder.values():
                    if isinstance(sub_placeholder, str):
                        if sub_placeholder.startswith("<"):
                            variable_fields += 1
                        elif sub_placeholder.startswith("["):
                            enum_fields += 1
        
        # Select diverse examples (up to 5) with focus on first ENUM types
        examples = []
        if payloads:
            # Try to get examples with different enum combinations
            unique_examples = []
            seen_combinations = set()
            
            # Get first few ENUM fields for diversity focus
            enum_fields = []
            for key, value in template_structure.items():
                if isinstance(value, str) and value.startswith("["):
                    enum_fields.append(key)
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, str) and sub_value.startswith("["):
                            enum_fields.append(f"{key}.{sub_key}")
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    for sub_key, sub_value in value[0].items():
                        if isinstance(sub_value, str) and sub_value.startswith("["):
                            enum_fields.append(f"{key}.{sub_key}")
            
            # Focus on first 3 ENUM fields to avoid too many combinations
            focus_enum_fields = enum_fields[:3]
            
            for payload in payloads:
                if len(unique_examples) >= 5:
                    break
                
                # Skip empty arrays
                if isinstance(payload, list) and len(payload) == 0:
                    continue
                    
                # Create a key for this payload's enum combination (focused on first ENUMs)
                enum_key = []
                if isinstance(payload, list):
                    # Handle array payloads
                    for item in payload:
                        if isinstance(item, dict):
                            for key, value in item.items():
                                if key in focus_enum_fields:
                                    enum_key.append(f"{key}:{value}")
                else:
                    # Handle dictionary payloads
                    for key, value in payload.items():
                        if key in focus_enum_fields:
                            enum_key.append(f"{key}:{value}")
                
                enum_key = tuple(sorted(enum_key))
                if enum_key not in seen_combinations:
                    seen_combinations.add(enum_key)
                    unique_examples.append(payload)
            
            # If we don't have enough diverse examples, add more
            for payload in payloads:
                if len(unique_examples) >= 5:
                    break
                # Skip empty arrays
                if isinstance(payload, list) and len(payload) == 0:
                    continue
                if payload not in unique_examples:
                    unique_examples.append(payload)
            
            examples = unique_examples[:5]
        
        return {
            "topic": topic,
            "category": "CCU (Central Control Unit)", 
            "message_count": len(messages),
            "template_structure": template_structure,
            "examples": examples,
            "session_name": messages[0].get('session_name', 'Unknown') if messages else 'Unknown',
            "timestamp": messages[0].get('timestamp', 'Unknown') if messages else 'Unknown',
            "statistics": {
                "total_messages": len(messages),
                "valid_payloads": len(payloads),
                "variable_fields": variable_fields,
                "enum_fields": enum_fields
            }
        }

    def load_all_sessions(self) -> List[Dict]:
        """Load messages from all session databases"""
        print("📂 Lade alle Session-Datenbanken...")
        
        all_messages = []
        session_files = glob.glob(f"{self.session_dir}/aps_persistent_traffic_*.db")
        
        print(f"  📁 Gefunden: {len(session_files)} Session-Dateien")
        
        for session_file in session_files:
            try:
                session_name = os.path.basename(session_file).replace('.db', '')
                print(f"  📊 Lade Session: {session_name}")
                
                conn = sqlite3.connect(session_file)
                cursor = conn.cursor()
                
                # Get messages for target topics
                placeholders = ','.join(['?' for _ in self.target_topics])
                cursor.execute(f"""
                    SELECT topic, payload, timestamp, session_label 
                    FROM mqtt_messages 
                    WHERE topic IN ({placeholders})
                    ORDER BY timestamp
                """, self.target_topics)
                
                session_messages = cursor.fetchall()
                print(f"    ✅ {len(session_messages)} Nachrichten geladen")
                
                for row in session_messages:
                    all_messages.append({
                        'topic': row[0],
                        'payload': row[1],
                        'timestamp': row[2],
                        'session_name': row[3] or session_name
                    })
                
                conn.close()
                
            except Exception as e:
                print(f"  ❌ Fehler beim Laden von {session_file}: {e}")
        
        print(f"📊 Insgesamt {len(all_messages)} Nachrichten aus allen Sessions geladen")
        return all_messages

    def analyze_all_topics(self) -> Dict:
        """Analyze all target topics"""
        print("🚀 Starte CCU Template Analyse...")
        
        # Load all messages
        all_messages = self.load_all_sessions()
        
        if not all_messages:
            print("❌ Keine Nachrichten gefunden!")
            return {}
        
        # Group messages by topic
        topic_messages = {}
        for msg in all_messages:
            topic = msg['topic']
            if topic not in topic_messages:
                topic_messages[topic] = []
            topic_messages[topic].append(msg)
        
        # Analyze each topic
        results = {}
        for topic in self.target_topics:
            print(f"\n🔍 Analysiere Topic: {topic}")
            
            if topic in topic_messages:
                messages = topic_messages[topic]
                result = self.analyze_topic_structure(topic, messages)
                results[topic] = result
                print(f"  ✅ Template erstellt mit {len(result['examples'])} Beispielen")
            else:
                print(f"  ⚠️  Keine Nachrichten für Topic: {topic}")
        
        return results

    def save_results(self, results: Dict):
        """Save analysis results to JSON file"""
        output_file = f"{self.output_dir}/ccu_template_analysis.json"
        
        # Add metadata
        output_data = {
            "metadata": {
                "analyzer": "CCU Template Analyzer",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            },
            "templates": results
        }
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Ergebnisse gespeichert in: {output_file}")
        return output_file

    def run_analysis(self):
        """Run complete analysis"""
        print("=" * 60)
        print("🔧 CCU TEMPLATE ANALYZER")
        print("=" * 60)
        
        try:
            # Analyze all topics
            results = self.analyze_all_topics()
            
            if not results:
                print("❌ Keine Ergebnisse erstellt!")
                return False
            
            # Save results
            output_file = self.save_results(results)
            
            # Print summary
            print("\n" + "=" * 60)
            print("📊 ANALYSE ZUSAMMENFASSUNG")
            print("=" * 60)
            
            total_topics = len(results)
            total_messages = sum(template['statistics']['total_messages'] for template in results.values())
            
            print(f"✅ Erfolgreich analysiert: {total_topics} Topics")
            print(f"📨 Gesamt Nachrichten: {total_messages}")
            print(f"💾 Ergebnisse: {output_file}")
            
            for topic, template in results.items():
                stats = template['statistics']
                print(f"  📋 {topic}: {stats['total_messages']} Nachrichten, {stats['enum_fields']} ENUMs, {stats['variable_fields']} Variablen")
            
            print("\n✅ CCU Template Analyse erfolgreich abgeschlossen!")
            return True
            
        except Exception as e:
            print(f"❌ Fehler bei der Analyse: {e}")
            return False

def main():
    """Main function"""
    analyzer = CCUTemplateAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("🎉 Script erfolgreich beendet!")
        exit(0)
    else:
        print("💥 Script mit Fehlern beendet!")
        exit(1)

if __name__ == "__main__":
    main()
