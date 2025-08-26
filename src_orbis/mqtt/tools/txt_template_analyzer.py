#!/usr/bin/env python3
"""
TXT Template Analyzer
Analyzes TXT controller messages to create templates for f/i and f/o topics
"""

import os
import sqlite3
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any
import glob

class TXTTemplateAnalyzer:
    def __init__(self, sessions_dir: str = "mqtt-data/sessions"):
        self.sessions_dir = sessions_dir
        self.target_topics = [
            # Function Input Topics (f/i)
            "/j1/txt/1/f/i/stock",
            "/j1/txt/1/f/i/order", 
            "/j1/txt/1/f/i/status",
            "/j1/txt/1/f/i/error",
            "/j1/txt/1/f/i/config/hbw",
            "/j1/txt/1/f/i/config/dps",
            "/j1/txt/1/f/i/config/aiqs",
            "/j1/txt/1/f/i/config/mill",
            "/j1/txt/1/f/i/config/drill",
            
            # Function Output Topics (f/o)
            "/j1/txt/1/f/o/order",
            "/j1/txt/1/f/o/stock",
            "/j1/txt/1/f/o/status",
            "/j1/txt/1/f/o/error"
        ]
        
    def get_available_sessions(self) -> List[str]:
        """Get list of available session databases"""
        session_files = glob.glob(os.path.join(self.sessions_dir, "*.db"))
        sessions = []
        for file in session_files:
            session_name = os.path.basename(file).replace(".db", "")
            sessions.append(session_name)
        return sorted(sessions)
    
    def load_topic_messages(self, topic: str) -> List[Dict[str, Any]]:
        """Load all messages for a specific topic from all sessions"""
        messages = []
        
        for session_file in glob.glob(os.path.join(self.sessions_dir, "*.db")):
            session_name = os.path.basename(session_file).replace(".db", "")
            
            try:
                conn = sqlite3.connect(session_file)
                query = """
                    SELECT timestamp, topic, payload, qos, retain, session_label
                    FROM mqtt_messages 
                    WHERE topic = ?
                    ORDER BY timestamp
                """
                
                df = pd.read_sql_query(query, conn, params=(topic,))
                conn.close()
                
                for _, row in df.iterrows():
                    try:
                        payload_data = json.loads(row['payload']) if row['payload'] else {}
                    except json.JSONDecodeError:
                        payload_data = {"raw_payload": row['payload']}
                    
                    messages.append({
                        'session': session_name,
                        'timestamp': row['timestamp'],
                        'topic': row['topic'],
                        'payload': payload_data,
                        'qos': row['qos'],
                        'retain': row['retain'],
                        'session_label': row['session_label']
                    })
                    
            except Exception as e:
                print(f"Error loading session {session_name}: {e}")
                
        return messages
    
    def analyze_topic_structure(self, topic: str) -> Dict[str, Any]:
        """Analyze message structure for a specific topic"""
        messages = self.load_topic_messages(topic)
        
        if not messages:
            return {
                'topic': topic,
                'message_count': 0,
                'sessions': [],
                'template': None,
                'variable_fields': [],
                'examples': []
            }
        
        # Analyze payload structure
        payload_structures = []
        variable_fields = set()
        examples = []
        
        for msg in messages:
            payload = msg['payload']
            if isinstance(payload, dict):
                payload_structures.append(payload)
                examples.append({
                    'session': msg['session'],
                    'timestamp': msg['timestamp'],
                    'payload': payload
                })
                
                # Identify potential variable fields
                for key, value in payload.items():
                    if isinstance(value, (str, int, float)):
                        # Check if this field varies across messages
                        variable_fields.add(key)
        
        # Create template by finding common structure
        template = self.create_template(payload_structures, variable_fields)
        
        # Analyze enum fields
        enum_fields = {}
        for field in variable_fields:
            field_values = [msg['payload'].get(field) for msg in messages if isinstance(msg['payload'], dict) and field in msg['payload']]
            unique_values = set(str(v) for v in field_values if v is not None)
            if len(unique_values) <= 10:  # Consider as enum if <= 10 unique values
                enum_fields[field] = sorted(list(unique_values))
        
        # Add detailed descriptions and usage information for known topics
        topic_info = {
            "/j1/txt/1/f/i/stock": {
                "description": "Verwenden für Status-Anzeige Lagerbestand. Nur was im Lager ist kann bestellt werden",
                "usage": "Fertigungsschritt-Tracking: Lagerbestand prüfen vor Auftragsstart",
                "critical_for": ["Fertigungsschritte", "Auftragsvalidierung", "Lagerstatus"],
                "workflow_step": "HBW PICK/DROP Status"
            },
            "/j1/txt/1/f/i/order": {
                "description": "Auftragsstatus und -informationen vom TXT Controller",
                "usage": "Fertigungsschritt-Tracking: Auftragsfortschritt verfolgen",
                "critical_for": ["Fertigungsschritte", "Auftragsstatus", "Workflow-Tracking"],
                "workflow_step": "Auftragsausführung"
            },
            "/j1/txt/1/f/i/config/hbw": {
                "description": "Konfiguration der Hochregallager (HBW) Module",
                "usage": "System-Initialisierung und Modul-Status",
                "critical_for": ["System-Setup", "Modul-Konfiguration"],
                "workflow_step": "System-Start"
            },
            "/j1/txt/1/f/o/order": {
                "description": "Auftragsausgabe vom TXT Controller an andere Module",
                "usage": "Fertigungsschritt-Tracking: Auftragsweiterleitung an Module",
                "critical_for": ["Fertigungsschritte", "Modul-Steuerung", "Workflow-Orchestration"],
                "workflow_step": "Auftragsverteilung"
            }
        }
        
        # Get topic information
        topic_data = topic_info.get(topic, {})
        
        return {
            'topic': topic,
            'message_count': len(messages),
            'sessions': list(set(msg['session'] for msg in messages)),
            'template': template,
            'variable_fields': list(variable_fields),
            'enum_fields': enum_fields,
            'description': topic_data.get('description', ''),
            'usage': topic_data.get('usage', ''),
            'critical_for': topic_data.get('critical_for', []),
            'workflow_step': topic_data.get('workflow_step', ''),
            'examples': examples[:5]  # First 5 examples
        }
    
    def create_template(self, payloads: List[Dict], variable_fields: set) -> Dict[str, Any]:
        """Create a template from multiple payloads"""
        if not payloads:
            return {}
        
        # Use the first payload as base template
        template = payloads[0].copy()
        
        # Special handling for stock items structure
        if 'stockItems' in template and isinstance(template['stockItems'], list):
            # Create a template stock item
            if template['stockItems']:
                first_stock_item = template['stockItems'][0]
                template_stock_item = self.create_stock_item_template(first_stock_item)
                template['stockItems'] = [template_stock_item]  # Show one template item
            else:
                template['stockItems'] = []
        elif 'stockItems' in template and isinstance(template['stockItems'], str):
            # If stockItems is a string, it means it was already processed as a placeholder
            # We need to create a proper template structure
            template['stockItems'] = [
                {
                    "workpiece": {
                        "id": "<nfcCode>",
                        "type": "<workpieceType: RED, WHITE, BLUE>",
                        "state": "<state: RAW>"
                    },
                    "location": "<location: A1, A2, A3, B1, B2, B3, C1, C2, C3>",
                    "hbw": "<hbwId>"
                }
            ]
        
        # Analyze field variability across all payloads
        field_values = {}
        for payload in payloads:
            for key, value in payload.items():
                if key not in field_values:
                    field_values[key] = []
                field_values[key].append(value)
        
        # Replace variable fields with placeholders
        for field in template.keys():
            if field in field_values and field != 'stockItems':  # Skip stockItems as it's handled specially
                values = field_values[field]
                unique_values = set(str(v) for v in values)
                
                # Determine if field is variable
                if len(unique_values) > 1:
                    placeholder = self.get_placeholder_for_field(field, values)
                    template[field] = placeholder
                # Keep constant values as they are
        
        return template
    
    def create_stock_item_template(self, stock_item: Dict) -> Dict[str, Any]:
        """Create a template for a stock item"""
        template_item = stock_item.copy()
        
        # Handle workpiece structure
        if 'workpiece' in template_item and isinstance(template_item['workpiece'], dict):
            workpiece = template_item['workpiece']
            
            # Handle workpiece ID (NFC code)
            if 'id' in workpiece:
                if workpiece['id'] == "":
                    template_item['workpiece']['id'] = "<nfcCode>"  # Empty = free slot
                else:
                    template_item['workpiece']['id'] = "<nfcCode>"
            
            # Handle workpiece type
            if 'type' in workpiece:
                template_item['workpiece']['type'] = "<workpieceType: RED, WHITE, BLUE>"
            
            # Handle workpiece state
            if 'state' in workpiece:
                template_item['workpiece']['state'] = "<state: RAW>"
        
        # Handle location
        if 'location' in template_item:
            template_item['location'] = "<location: A1, A2, A3, B1, B2, B3, C1, C2, C3>"
        
        # Handle HBW
        if 'hbw' in template_item:
            template_item['hbw'] = "<hbwId>"
        
        return template_item
    
    def get_placeholder_for_field(self, field_name: str, values: List[Any]) -> str:
        """Get appropriate placeholder for a field based on its values"""
        if not values:
            return f"<{field_name}>"
        
        # Analyze value patterns
        unique_values = set(str(v) for v in values)
        
        # Common patterns with enum detection
        if field_name.lower() in ['workpieceid', 'workpiece_id', 'id']:
            return "<workpieceId>"
        elif field_name.lower() in ['orderid', 'order_id']:
            return "<orderId>"
        elif field_name.lower() in ['type', 'color']:
            if len(unique_values) <= 10:  # Enum for workpiece types
                return f"<workpieceType: {', '.join(sorted(unique_values))}>"
            else:
                return "<workpieceType>"
        elif field_name.lower() in ['status', 'state']:
            if len(unique_values) <= 10:  # Enum for status values
                return f"<status: {', '.join(sorted(unique_values))}>"
            else:
                return "<status>"
        elif field_name.lower() in ['timestamp', 'time', 'ts']:
            return "<timestamp>"
        elif field_name.lower() in ['error', 'message']:
            return "<message>"
        elif field_name.lower() in ['location', 'pos']:
            if len(unique_values) <= 20:  # Enum for locations
                return f"<location: {', '.join(sorted(unique_values))}>"
            else:
                return "<location>"
        elif field_name.lower() in ['hbw', 'warehouse']:
            if len(unique_values) <= 5:  # Enum for warehouse IDs
                return f"<hbwId: {', '.join(sorted(unique_values))}>"
            else:
                return "<hbwId>"
        elif len(unique_values) <= 8:
            # Small set of values, show as enum
            return f"<{field_name}: {', '.join(sorted(unique_values))}>"
        else:
            # Generic placeholder
            return f"<{field_name}>"
    
    def analyze_all_txt_topics(self) -> Dict[str, Any]:
        """Analyze all TXT f/i and f/o topics"""
        results = {}
        
        print(f"🔍 Analyzing {len(self.target_topics)} TXT topics...")
        
        for topic in self.target_topics:
            print(f"  📡 Analyzing: {topic}")
            results[topic] = self.analyze_topic_structure(topic)
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a formatted report of the analysis"""
        report = []
        report.append("# TXT Controller Template Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_messages = sum(r['message_count'] for r in results.values())
        active_topics = sum(1 for r in results.values() if r['message_count'] > 0)
        
        report.append("## 📊 Summary")
        report.append(f"- **Total Topics Analyzed:** {len(self.target_topics)}")
        report.append(f"- **Active Topics:** {active_topics}")
        report.append(f"- **Total Messages:** {total_messages}")
        report.append("")
        
        # Function Input Topics (f/i)
        report.append("## 📥 Function Input Topics (f/i)")
        fi_topics = [topic for topic in self.target_topics if "/f/i/" in topic]
        for topic in fi_topics:
            result = results[topic]
            report.append(f"### {topic}")
            report.append(f"- **Messages:** {result['message_count']}")
            report.append(f"- **Sessions:** {len(result['sessions'])}")
            if result['template']:
                report.append(f"- **Template:** ```json\n{json.dumps(result['template'], indent=2)}\n```")
            if result['variable_fields']:
                report.append(f"- **Variable Fields:** {', '.join(result['variable_fields'])}")
            report.append("")
        
        # Function Output Topics (f/o)
        report.append("## 📤 Function Output Topics (f/o)")
        fo_topics = [topic for topic in self.target_topics if "/f/o/" in topic]
        for topic in fo_topics:
            result = results[topic]
            report.append(f"### {topic}")
            report.append(f"- **Messages:** {result['message_count']}")
            report.append(f"- **Sessions:** {len(result['sessions'])}")
            if result['template']:
                report.append(f"- **Template:** ```json\n{json.dumps(result['template'], indent=2)}\n```")
            if result['variable_fields']:
                report.append(f"- **Variable Fields:** {', '.join(result['variable_fields'])}")
            report.append("")
        
        return "\n".join(report)
    
    def save_report(self, results: Dict[str, Any], filename: str = None):
        """Save analysis report to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"txt_template_analysis_{timestamp}.md"
        
        report = self.generate_report(results)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved to: {filename}")
        return filename

def main():
    """Main function to run the TXT template analysis"""
    analyzer = TXTTemplateAnalyzer()
    
    # Check available sessions
    sessions = analyzer.get_available_sessions()
    print(f"📁 Found {len(sessions)} sessions: {sessions}")
    
    # Analyze all TXT topics
    results = analyzer.analyze_all_txt_topics()
    
    # Generate and save report
    report_file = analyzer.save_report(results)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 ANALYSIS SUMMARY")
    print("="*50)
    
    total_messages = sum(r['message_count'] for r in results.values())
    active_topics = sum(1 for r in results.values() if r['message_count'] > 0)
    
    print(f"📡 Topics analyzed: {len(analyzer.target_topics)}")
    print(f"✅ Active topics: {active_topics}")
    print(f"📨 Total messages: {total_messages}")
    print(f"📄 Report: {report_file}")
    
    # Show top topics by message count
    print("\n🏆 Top topics by message count:")
    sorted_topics = sorted(results.items(), key=lambda x: x[1]['message_count'], reverse=True)
    for topic, result in sorted_topics[:5]:
        if result['message_count'] > 0:
            print(f"  {topic}: {result['message_count']} messages")

if __name__ == "__main__":
    main()
