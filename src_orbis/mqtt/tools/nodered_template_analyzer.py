#!/usr/bin/env python3
"""
Node-RED Template Analyzer for ORBIS Modellfabrik

Analyzes MQTT message templates for Node-RED topics from session data.
Extracts template structures, examples, and validation rules.
"""

import json
import glob
import re
import yaml
from datetime import datetime
from typing import Dict, List, Any, Set
from pathlib import Path
try:
    from .module_manager import get_module_manager
    from .message_template_manager import get_message_template_manager
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from module_manager import get_module_manager
    from message_template_manager import get_message_template_manager
import copy
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src_orbis.mqtt.tools.nfc_code_manager import get_nfc_manager
import sqlite3
import pandas as pd


class NodeRedTemplateAnalyzer:
    """Analyzer for Node-RED MQTT message templates"""
    
    def __init__(self, session_dir: str = None, output_dir: str = None):
        """Initialize the analyzer"""
        self.session_dir = session_dir or os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mqtt-data', 'sessions')
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), '..', '..', '..', 'mqtt-data', 'template_library')
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize managers
        self.nfc_manager = get_nfc_manager()
        self.module_mapping = get_module_manager()
        self.message_template_manager = get_message_template_manager()
        
        # Node-RED topic patterns (based on actual session data)
        self.nodered_topics = [
            # Node-RED specific topics
            "ccu/state/flows",
            "ccu/state/dashboard",
            "ccu/state/ui",
            
            # Node-RED module topics (already covered by module analyzer)
            "module/v1/ff/NodeRed/*/connection",
            "module/v1/ff/NodeRed/*/state",
            "module/v1/ff/NodeRed/*/order",
            "module/v1/ff/NodeRed/*/factsheet",
            "module/v1/ff/NodeRed/*/instantAction",
            "module/v1/ff/NodeRed/status",
            
            # Node-RED flow topics
            "flows/*/status",
            "flows/*/config",
            "flows/*/data",
            
            # Node-RED dashboard topics
            "dashboard/*/status",
            "dashboard/*/config",
            "dashboard/*/data",
            
            # Node-RED UI topics
            "ui/*/status",
            "ui/*/config",
            "ui/*/data"
        ]
        
        # Module IDs from configuration
        self.module_ids = self.module_mapping.get_all_module_ids()
        # Add NodeRed as a special module
        self.module_ids.append("NodeRed")
        
        print(f"🔧 Node-RED Template Analyzer initialisiert")
        print(f"   📁 Session-Verzeichnis: {self.session_dir}")
        print(f"   📁 Ausgabe-Verzeichnis: {self.output_dir}")
        print(f"   🏭 Module-IDs: {len(self.module_ids)} gefunden")
        print(f"   📡 Topic-Patterns: {len(self.nodered_topics)} definiert")
    
    def _determine_sub_category(self, topic: str) -> str:
        """Determine sub-category based on topic"""
        if "connection" in topic:
            return "Connection"
        elif "state" in topic:
            return "State"
        elif "order" in topic:
            return "Order"
        elif "factsheet" in topic:
            return "Factsheet"
        elif "instantAction" in topic:
            return "InstantAction"
        elif "flows" in topic:
            return "Flows"
        elif "dashboard" in topic:
            return "Dashboard"
        elif "ui" in topic:
            return "UI"
        elif "status" in topic and not any(x in topic for x in ["connection", "state", "order", "factsheet"]):
            return "Status"
        else:
            return "General"
    
    def _determine_module_id(self, topic: str) -> str:
        """Extract module ID from topic"""
        # Pattern: module/v1/ff/NodeRed/{module_id}/...
        match = re.match(r'module/v1/ff/NodeRed/([^/]+)/', topic)
        if match:
            module_id = match.group(1)
            if module_id in self.module_ids:
                return module_id
        
        # Pattern: module/v1/ff/NodeRed/status
        if topic == "module/v1/ff/NodeRed/status":
            return "NodeRed"
        
        # Pattern: ccu/state/flows
        if topic == "ccu/state/flows":
            return "CCU"
        
        # Pattern: flows/{flow_id}/...
        match = re.match(r'flows/([^/]+)/', topic)
        if match:
            return "Flow"
        
        # Pattern: dashboard/{dashboard_id}/...
        match = re.match(r'dashboard/([^/]+)/', topic)
        if match:
            return "Dashboard"
        
        # Pattern: ui/{ui_id}/...
        match = re.match(r'ui/([^/]+)/', topic)
        if match:
            return "UI"
        
        return "unknown"
    
    def _get_placeholder_for_field(self, field_name: str, values: Set[str], module_id: str = None) -> str:
        """Generate placeholder for field based on values and field name"""
        if not values:
            return "<string>"
        
        # Check for specific patterns
        if field_name.lower() in ['timestamp', 'time', 'date']:
            return "<datetime>"
        elif field_name.lower() in ['id', 'uuid', 'guid']:
            return "<uuid>"
        elif field_name.lower() in ['nfc', 'nfc_code', 'workpiece_id']:
            return "<nfcCode>"
        elif field_name.lower() in ['module', 'module_id', 'moduleid']:
            return "<moduleId>"
        elif field_name.lower() in ['status', 'state']:
            # Check if it's a known enum
            if len(values) <= 10:  # Reasonable enum size
                return f"[{', '.join(sorted(values))}]"
            else:
                return "<string>"
        elif field_name.lower() in ['type', 'order_type', 'action_type']:
            # Check for known enums
            if len(values) <= 10:
                return f"[{', '.join(sorted(values))}]"
            else:
                return "<string>"
        elif field_name.lower() in ['position', 'pos']:
            return "<position>"
        elif field_name.lower() in ['error', 'error_code']:
            return "<errorCode>"
        elif field_name.lower() in ['message', 'msg']:
            return "<message>"
        elif field_name.lower() in ['data', 'payload']:
            return "<data>"
        elif field_name.lower() in ['flow', 'flow_id']:
            return "<flowId>"
        elif field_name.lower() in ['dashboard', 'dashboard_id']:
            return "<dashboardId>"
        elif field_name.lower() in ['ui', 'ui_id']:
            return "<uiId>"
        else:
            # Check if it's a small set of values (likely enum)
            if len(values) <= 5:
                return f"[{', '.join(sorted(values))}]"
            else:
                return "<string>"
    
    def _analyze_topic_structure(self, topic: str, messages: List[Dict]) -> Dict:
        """Analyze structure for a specific topic"""
        if not messages:
            return {
                "template_structure": {},
                "examples": [],
                "statistics": {
                    "total_messages": 0,
                    "enum_fields": 0,
                    "variable_fields": 0
                }
            }
        
        # Collect all field values
        field_values = {}
        examples = []
        
        for msg in messages:
            payload = msg.get('payload', {})
            if isinstance(payload, dict):
                examples.append(payload)
                
                for field, value in payload.items():
                    if field not in field_values:
                        field_values[field] = set()
                    field_values[field].add(str(value))
        
        # Generate template structure
        template_structure = {}
        enum_fields = 0
        variable_fields = 0
        
        module_id = self._determine_module_id(topic)
        
        for field, values in field_values.items():
            placeholder = self._get_placeholder_for_field(field, values, module_id)
            template_structure[field] = placeholder
            
            if placeholder.startswith('[') and placeholder.endswith(']'):
                enum_fields += 1
            else:
                variable_fields += 1
        
        return {
            "template_structure": template_structure,
            "examples": examples[:5],  # Keep first 5 examples
            "statistics": {
                "total_messages": len(messages),
                "enum_fields": enum_fields,
                "variable_fields": variable_fields
            }
        }
    
    def _generate_validation_rules(self, template_structure: Dict) -> List[str]:
        """Generate validation rules for template structure"""
        rules = []
        
        def add_rules_for_structure(structure, prefix=""):
            for field, placeholder in structure.items():
                field_path = f"{prefix}.{field}" if prefix else field
                
                if isinstance(placeholder, str):
                    if placeholder.startswith("["):
                        # ENUM validation
                        enum_values = placeholder[1:-1].split(", ")
                        rules.append(f"{field} muss in {placeholder} sein")
                    elif placeholder == "<datetime>":
                        rules.append(f"{field} muss ISO 8601 Format haben")
                    elif placeholder == "<uuid>":
                        rules.append(f"{field} muss UUID Format haben")
                    elif placeholder == "<nfcCode>":
                        rules.append(f"{field} muss gültiger NFC-Code sein")
                    elif placeholder == "<moduleId>":
                        rules.append(f"{field} muss gültige Modul-ID sein")
                    elif placeholder == "<position>":
                        rules.append(f"{field} muss gültige Position sein")
                    elif placeholder == "<errorCode>":
                        rules.append(f"{field} muss gültiger Fehler-Code sein")
                    elif placeholder == "<data>":
                        rules.append(f"{field} muss gültige Daten sein")
                    elif placeholder == "<flowId>":
                        rules.append(f"{field} muss gültige Flow-ID sein")
                    elif placeholder == "<dashboardId>":
                        rules.append(f"{field} muss gültige Dashboard-ID sein")
                    elif placeholder == "<uiId>":
                        rules.append(f"{field} muss gültige UI-ID sein")
                elif isinstance(placeholder, dict):
                    add_rules_for_structure(placeholder, field_path)
                elif isinstance(placeholder, list):
                    if placeholder and isinstance(placeholder[0], dict):
                        add_rules_for_structure(placeholder[0], f"{field_path}[0]")
        
        add_rules_for_structure(template_structure)
        return rules
    
    def load_all_sessions(self) -> List[str]:
        """Load all available session databases"""
        session_files = glob.glob(os.path.join(self.session_dir, "*.db"))
        sessions = []
        
        for session_file in session_files:
            try:
                conn = sqlite3.connect(session_file)
                cursor = conn.cursor()
                
                # Check if table exists and has data
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mqtt_messages'")
                if cursor.fetchone():
                    cursor.execute("SELECT COUNT(*) FROM mqtt_messages")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        sessions.append(session_file)
                
                conn.close()
            except Exception as e:
                print(f"⚠️ Fehler beim Laden von {session_file}: {e}")
        
        print(f"📊 {len(sessions)} Session-Dateien gefunden")
        return sessions
    
    def analyze_topic_structure(self, topic: str, sessions: List[str]) -> Dict:
        """Analyze structure for a specific topic across all sessions"""
        all_messages = []
        
        for session_file in sessions:
            try:
                conn = sqlite3.connect(session_file)
                cursor = conn.cursor()
                
                # Get messages for this topic
                cursor.execute("""
                    SELECT topic, payload, timestamp 
                    FROM mqtt_messages 
                    WHERE topic = ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                """, (topic,))
                
                messages = cursor.fetchall()
                for msg in messages:
                    try:
                        payload = json.loads(msg[1]) if msg[1] else {}
                        all_messages.append({
                            'topic': msg[0],
                            'payload': payload,
                            'timestamp': msg[2]
                        })
                    except json.JSONDecodeError:
                        continue
                
                conn.close()
            except Exception as e:
                print(f"⚠️ Fehler beim Analysieren von {topic} in {session_file}: {e}")
        
        return self._analyze_topic_structure(topic, all_messages)
    
    def analyze_all_topics(self, sessions: List[str]) -> Dict:
        """Analyze all Node-RED topics"""
        results = {}
        
        # Generate all possible topic combinations
        all_topics = set()
        for pattern in self.nodered_topics:
            if "*" in pattern:
                # Handle wildcard patterns
                if "module/v1/ff/NodeRed/*/" in pattern:
                    for module_id in self.module_ids:
                        topic = pattern.replace('*', module_id)
                        all_topics.add(topic)
                elif "flows/*/" in pattern:
                    all_topics.add(pattern.replace('*', 'default'))
                elif "dashboard/*/" in pattern:
                    all_topics.add(pattern.replace('*', 'default'))
                elif "ui/*/" in pattern:
                    all_topics.add(pattern.replace('*', 'default'))
            else:
                all_topics.add(pattern)
        
        print(f"🔍 Analysiere {len(all_topics)} Node-RED Topics...")
        
        for i, topic in enumerate(sorted(all_topics), 1):
            print(f"   [{i:2d}/{len(all_topics)}] {topic}")
            
            result = self.analyze_topic_structure(topic, sessions)
            if result["statistics"]["total_messages"] > 0:
                results[topic] = result
        
        return results
    
    def save_results(self, results: Dict) -> str:
        """Save analysis results to JSON file"""
        output_file = f"{self.output_dir}/nodered_template_analysis.json"
        
        output_data = {
            "metadata": {
                "analyzer": "Node-RED Template Analyzer",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "total_topics": len(results),
                "total_messages": sum(template['statistics']['total_messages'] for template in results.values())
            },
            "templates": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 JSON-Ergebnisse gespeichert in: {output_file}")
        return output_file
    
    def save_results_to_yaml(self, results: Dict):
        """Save analysis results to YAML file"""
        output_file = f"{self.output_dir}/nodered_analysis_results.yml"
        
        # Convert results to YAML format
        yaml_data = {
            "metadata": {
                "analyzer": "Node-RED Template Analyzer",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0",
                "total_topics": len(results),
                "total_messages": sum(template['statistics']['total_messages'] for template in results.values())
            },
            "templates": {}
        }
        
        for topic, template in results.items():
            yaml_data["templates"][topic] = {
                "category": "Node-RED",
                "sub_category": self._determine_sub_category(topic),
                "module": self._determine_module_id(topic),
                "description": f"Node-RED {self._determine_module_id(topic)} {self._determine_sub_category(topic)}",
                "template_structure": template["template_structure"],
                "examples": template["examples"],
                "validation_rules": self._generate_validation_rules(template["template_structure"]),
                "statistics": template["statistics"]
            }
        
        # Save to YAML file
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        print(f"💾 YAML-Ergebnisse gespeichert in: {output_file}")
        return output_file
    
    def update_message_templates_yaml(self, results: Dict):
        """Update the main message_templates.yml with Node-RED analysis results"""
        try:
            # Load existing message templates
            config_file = Path(__file__).parent.parent / "config" / "message_templates.yml"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    templates_data = yaml.safe_load(f)
            else:
                templates_data = {
                    "metadata": {"version": "1.0"},
                    "topics": {},
                    "categories": {},
                    "validation_patterns": {}
                }
            
            # Update with Node-RED templates
            for topic, template in results.items():
                templates_data["topics"][topic] = {
                    "category": "Node-RED",
                    "sub_category": self._determine_sub_category(topic),
                    "module": self._determine_module_id(topic),
                    "description": f"Node-RED {self._determine_module_id(topic)} {self._determine_sub_category(topic)}",
                    "template_structure": template["template_structure"],
                    "examples": template["examples"],
                    "validation_rules": self._generate_validation_rules(template["template_structure"])
                }
            
            # Save updated templates
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(templates_data, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            print(f"✅ Message Templates YAML aktualisiert: {config_file}")
            
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der YAML-Datei: {e}")
    
    def run_analysis(self):
        """Run complete Node-RED template analysis"""
        print("🚀 Starte Node-RED Template Analyse...")
        
        # Load sessions
        sessions = self.load_all_sessions()
        if not sessions:
            print("❌ Keine Session-Dateien gefunden!")
            return
        
        # Analyze all topics
        results = self.analyze_all_topics(sessions)
        
        if results:
            # Save results
            output_file = self.save_results(results)
            
            # Save to YAML
            yaml_file = self.save_results_to_yaml(results)
            
            # Update main message templates
            self.update_message_templates_yaml(results)
            
            # Print summary
            total_messages = sum(template['statistics']['total_messages'] for template in results.values())
            total_enum_fields = sum(template['statistics']['enum_fields'] for template in results.values())
            total_variable_fields = sum(template['statistics']['variable_fields'] for template in results.values())
            
            print("\n" + "="*60)
            print("📊 NODE-RED TEMPLATE ANALYSE ABGESCHLOSSEN")
            print("="*60)
            print(f"✅ Analysierte Topics: {len(results)}")
            print(f"📨 Gesamt Nachrichten: {total_messages}")
            print(f"🔢 ENUM-Felder: {total_enum_fields}")
            print(f"📝 Variable Felder: {total_variable_fields}")
            print(f"💾 JSON-Ergebnisse: {output_file}")
            print(f"💾 YAML-Ergebnisse: {yaml_file}")
            print("="*60)
            
            # Show topic breakdown
            print("\n📋 Topic-Übersicht:")
            for topic, template in results.items():
                module_id = self._determine_module_id(topic)
                sub_category = self._determine_sub_category(topic)
                msg_count = template['statistics']['total_messages']
                print(f"   • {topic} ({module_id}/{sub_category}): {msg_count} Nachrichten")
        else:
            print("❌ Keine Node-RED Topics mit Daten gefunden!")


def main():
    """Main function for standalone execution"""
    analyzer = NodeRedTemplateAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
