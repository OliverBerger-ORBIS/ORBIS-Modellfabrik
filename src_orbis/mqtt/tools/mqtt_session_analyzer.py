#!/usr/bin/env python3
"""
MQTT Session Analyzer - Automatisierte Analyse von MQTT-Sessions

Dieses Tool analysiert MQTT-Session-Daten und identifiziert Muster für:
- ORDER-ID Management
- Modul-Status-Monitoring
- Workflow-Dependencies
- Error-Handling
"""

import argparse
import sqlite3
import pandas as pd
import json
import re
from datetime import datetime
from pathlib import Path
import sys
import os
import glob

# Add src_orbis to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

class MQTTSessionAnalyzer:
    """Analysiert MQTT-Session-Daten und identifiziert Muster"""
    
    def __init__(self, session_db_path):
        """Initialisiert den Analyzer mit einer Session-Datenbank"""
        self.session_db_path = session_db_path
        self.df = None
        self.analysis_results = {}
        
    def load_session_data(self):
        """Lädt die Session-Daten aus der SQLite-Datenbank"""
        try:
            conn = sqlite3.connect(self.session_db_path)
            query = """
                SELECT timestamp, topic, payload, qos
                FROM mqtt_messages
                ORDER BY timestamp
            """
            self.df = pd.read_sql_query(query, conn)
            conn.close()
            
            # Parse JSON payloads
            self.df['payload_json'] = self.df['payload'].apply(self._safe_json_parse)
            
            print(f"✅ Session-Daten geladen: {len(self.df)} Nachrichten")
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Session-Daten: {e}")
            return False
    
    def _safe_json_parse(self, payload):
        """Sicherer JSON-Parser für Payload-Daten"""
        try:
            return json.loads(payload) if payload else None
        except:
            return None
    
    def analyze_order_id_patterns(self):
        """Analysiert ORDER-ID Muster"""
        print("\n🔍 Analysiere ORDER-ID Muster...")
        
        order_ids = set()
        order_id_patterns = []
        
        for _, row in self.df.iterrows():
            if row['payload_json']:
                # Suche nach orderId in verschiedenen Feldern
                order_id = self._extract_order_id(row['payload_json'])
                if order_id:
                    order_ids.add(order_id)
                    order_id_patterns.append({
                        'timestamp': row['timestamp'],
                        'topic': row['topic'],
                        'order_id': order_id,
                        'payload_structure': self._get_payload_structure(row['payload_json'])
                    })
        
        self.analysis_results['order_id_analysis'] = {
            'unique_order_ids': list(order_ids),
            'order_id_count': len(order_ids),
            'order_id_patterns': order_id_patterns
        }
        
        print(f"   📊 {len(order_ids)} eindeutige ORDER-IDs gefunden")
        return order_id_patterns
    
    def _extract_order_id(self, payload):
        """Extrahiert ORDER-ID aus Payload"""
        # Verschiedene mögliche Felder für ORDER-ID
        order_id_fields = ['orderId', 'order_id', 'orderID', 'id', 'uuid']
        
        for field in order_id_fields:
            if field in payload:
                return payload[field]
        
        return None
    
    def _get_payload_structure(self, payload):
        """Ermittelt die Struktur des Payloads"""
        if isinstance(payload, dict):
            return list(payload.keys())
        return []
    
    def analyze_module_status_patterns(self):
        """Analysiert Modul-Status-Muster"""
        print("\n🏭 Analysiere Modul-Status-Muster...")
        
        module_status = {}
        status_transitions = []
        
        for _, row in self.df.iterrows():
            if row['payload_json']:
                module_id = self._extract_module_id(row['topic'])
                status = self._extract_status(row['payload_json'])
                
                if module_id and status:
                    if module_id not in module_status:
                        module_status[module_id] = []
                    
                    module_status[module_id].append({
                        'timestamp': row['timestamp'],
                        'status': status,
                        'topic': row['topic']
                    })
                    
                    # Status-Übergänge verfolgen
                    if len(module_status[module_id]) > 1:
                        prev_status = module_status[module_id][-2]['status']
                        if prev_status != status:
                            status_transitions.append({
                                'module_id': module_id,
                                'from_status': prev_status,
                                'to_status': status,
                                'timestamp': row['timestamp']
                            })
        
        self.analysis_results['module_status_analysis'] = {
            'module_status': module_status,
            'status_transitions': status_transitions
        }
        
        print(f"   📊 {len(module_status)} Module mit Status-Updates")
        print(f"   🔄 {len(status_transitions)} Status-Übergänge")
        return module_status
    
    def _extract_module_id(self, topic):
        """Extrahiert Module-ID aus Topic"""
        # Topic-Pattern: .../module_id/...
        parts = topic.split('/')
        for part in parts:
            if part in ['HBW', 'VGR', 'DPS', 'DRILL', 'MILL', 'AIQS', 'FTS']:
                return part
        return None
    
    def _extract_status(self, payload):
        """Extrahiert Status aus Payload"""
        status_fields = ['status', 'state', 'availability', 'activity']
        
        for field in status_fields:
            if field in payload:
                return payload[field]
        
        return None
    
    def analyze_workflow_patterns(self):
        """Analysiert Workflow-Muster"""
        print("\n🔄 Analysiere Workflow-Muster...")
        
        workflow_sequences = []
        command_sequences = []
        
        # Gruppiere Nachrichten nach Zeitfenstern
        self.df['timestamp_dt'] = pd.to_datetime(self.df['timestamp'])
        self.df = self.df.sort_values('timestamp_dt')
        
        # Suche nach Command-Sequenzen
        for i in range(len(self.df) - 1):
            current_msg = self.df.iloc[i]
            next_msg = self.df.iloc[i + 1]
            
            time_diff = (next_msg['timestamp_dt'] - current_msg['timestamp_dt']).total_seconds()
            
            # Wenn Nachrichten innerhalb von 5 Sekunden sind, könnten sie zusammengehören
            if time_diff <= 5:
                command_sequences.append({
                    'first_topic': current_msg['topic'],
                    'second_topic': next_msg['topic'],
                    'time_diff': time_diff,
                    'first_payload': current_msg['payload_json'],
                    'second_payload': next_msg['payload_json']
                })
        
        self.analysis_results['workflow_analysis'] = {
            'command_sequences': command_sequences
        }
        
        print(f"   📊 {len(command_sequences)} Command-Sequenzen gefunden")
        return command_sequences
    
    def analyze_error_patterns(self):
        """Analysiert Error-Muster"""
        print("\n❌ Analysiere Error-Muster...")
        
        error_messages = []
        error_topics = []
        
        for _, row in self.df.iterrows():
            # Suche nach Error-indikatoren in Topics
            if any(error_term in row['topic'].lower() for error_term in ['error', 'fail', 'nok', 'not_ok']):
                error_topics.append({
                    'timestamp': row['timestamp'],
                    'topic': row['topic'],
                    'payload': row['payload_json']
                })
            
            # Suche nach Error-indikatoren in Payload
            if row['payload_json']:
                if any(error_term in str(row['payload_json']).lower() for error_term in ['error', 'fail', 'nok', 'not_ok']):
                    error_messages.append({
                        'timestamp': row['timestamp'],
                        'topic': row['topic'],
                        'payload': row['payload_json']
                    })
        
        self.analysis_results['error_analysis'] = {
            'error_topics': error_topics,
            'error_messages': error_messages
        }
        
        print(f"   📊 {len(error_topics)} Error-Topics gefunden")
        print(f"   📊 {len(error_messages)} Error-Nachrichten gefunden")
        return error_messages
    
    def generate_report(self):
        """Generiert einen detaillierten Analyse-Report"""
        print("\n📋 Generiere Analyse-Report...")
        
        report = {
            'session_info': {
                'session_name': os.path.basename(self.session_db_path),
                'total_messages': len(self.df),
                'time_span': {
                    'start': self.df['timestamp'].min() if len(self.df) > 0 else None,
                    'end': self.df['timestamp'].max() if len(self.df) > 0 else None
                }
            },
            'analysis_results': self.analysis_results
        }
        
        return report
    
    def print_summary(self):
        """Druckt eine Zusammenfassung der Analyse"""
        print(f"\n📊 Analyse-Zusammenfassung für {os.path.basename(self.session_db_path)}")
        print("=" * 60)
        
        if 'order_id_analysis' in self.analysis_results:
            order_analysis = self.analysis_results['order_id_analysis']
            print(f"🔍 ORDER-IDs: {order_analysis['order_id_count']} eindeutige IDs")
        
        if 'module_status_analysis' in self.analysis_results:
            status_analysis = self.analysis_results['module_status_analysis']
            print(f"🏭 Module: {len(status_analysis['module_status'])} Module mit Status-Updates")
            print(f"🔄 Übergänge: {len(status_analysis['status_transitions'])} Status-Übergänge")
        
        if 'workflow_analysis' in self.analysis_results:
            workflow_analysis = self.analysis_results['workflow_analysis']
            print(f"🔄 Workflows: {len(workflow_analysis['command_sequences'])} Command-Sequenzen")
        
        if 'error_analysis' in self.analysis_results:
            error_analysis = self.analysis_results['error_analysis']
            print(f"❌ Errors: {len(error_analysis['error_topics'])} Error-Topics, {len(error_analysis['error_messages'])} Error-Nachrichten")

class SystematicSessionAnalyzer:
    """Systematische Analyse aller verfügbaren Sessions"""
    
    def __init__(self, sessions_directory):
        """Initialisiert den systematischen Analyzer"""
        self.sessions_directory = sessions_directory
        self.session_reports = {}
        
    def find_all_sessions(self):
        """Findet alle verfügbaren Sessions"""
        db_files = glob.glob(os.path.join(self.sessions_directory, "aps_persistent_traffic_*.db"))
        return sorted(db_files)
    
    def categorize_sessions(self, session_files):
        """Kategorisiert Sessions nach Typ"""
        categories = {
            'wareneingang': [],
            'auftrag': [],
            'ai_error': [],
            'fts': [],
            'other': []
        }
        
        for session_file in session_files:
            session_name = os.path.basename(session_file)
            
            if 'wareneingang' in session_name:
                categories['wareneingang'].append(session_file)
            elif 'auftrag' in session_name:
                categories['auftrag'].append(session_file)
            elif 'ai-not-ok' in session_name:
                categories['ai_error'].append(session_file)
            elif 'fts' in session_name:
                categories['fts'].append(session_file)
            else:
                categories['other'].append(session_file)
        
        return categories
    
    def analyze_session_category(self, category_name, session_files):
        """Analysiert eine Kategorie von Sessions"""
        print(f"\n🔍 Analysiere {category_name.upper()} Sessions...")
        print("=" * 50)
        
        category_results = []
        
        for session_file in session_files:
            print(f"\n📊 Analysiere: {os.path.basename(session_file)}")
            
            analyzer = MQTTSessionAnalyzer(session_file)
            if analyzer.load_session_data():
                analyzer.analyze_order_id_patterns()
                analyzer.analyze_module_status_patterns()
                analyzer.analyze_workflow_patterns()
                analyzer.analyze_error_patterns()
                
                report = analyzer.generate_report()
                category_results.append(report)
                analyzer.print_summary()
            else:
                print(f"❌ Konnte Session nicht laden: {session_file}")
        
        return category_results
    
    def run_systematic_analysis(self):
        """Führt eine systematische Analyse aller Sessions durch"""
        print("🚀 Starte systematische MQTT-Session-Analyse")
        print("=" * 60)
        
        # Finde alle Sessions
        session_files = self.find_all_sessions()
        print(f"📁 Gefundene Sessions: {len(session_files)}")
        
        # Kategorisiere Sessions
        categories = self.categorize_sessions(session_files)
        
        # Analysiere jede Kategorie
        for category_name, category_sessions in categories.items():
            if category_sessions:
                self.session_reports[category_name] = self.analyze_session_category(
                    category_name, category_sessions
                )
        
        # Generiere Gesamt-Report
        self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self):
        """Generiert einen umfassenden Report aller Analysen"""
        print(f"\n📋 Generiere umfassenden Analyse-Report...")
        print("=" * 60)
        
        # Speichere Report in Datei
        report_file = os.path.join(self.sessions_directory, "systematic_analysis_report.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_reports, f, indent=2, default=str)
        
        print(f"✅ Umfassender Report gespeichert: {report_file}")
        
        # Drucke Zusammenfassung
        self.print_comprehensive_summary()
    
    def print_comprehensive_summary(self):
        """Druckt eine umfassende Zusammenfassung"""
        print(f"\n📊 UMFASSENDE ANALYSE-ZUSAMMENFASSUNG")
        print("=" * 60)
        
        for category_name, category_reports in self.session_reports.items():
            print(f"\n🔍 {category_name.upper()}: {len(category_reports)} Sessions")
            
            total_messages = sum(report['session_info']['total_messages'] for report in category_reports)
            total_order_ids = sum(len(report['analysis_results'].get('order_id_analysis', {}).get('unique_order_ids', [])) for report in category_reports)
            
            print(f"   📊 Gesamt-Nachrichten: {total_messages}")
            print(f"   🔍 Gesamt-ORDER-IDs: {total_order_ids}")

def main():
    """Hauptfunktion für Kommandozeilen-Interface"""
    parser = argparse.ArgumentParser(description='MQTT Session Analyzer')
    parser.add_argument('--session', help='Pfad zur Session-Datenbank')
    parser.add_argument('--sessions-dir', help='Verzeichnis mit allen Sessions für systematische Analyse')
    parser.add_argument('--compare', help='Vergleiche zwei Sessions')
    
    args = parser.parse_args()
    
    if args.sessions_dir:
        # Systematische Analyse aller Sessions
        systematic_analyzer = SystematicSessionAnalyzer(args.sessions_dir)
        systematic_analyzer.run_systematic_analysis()
    
    elif args.session:
        # Einzelne Session analysieren
        analyzer = MQTTSessionAnalyzer(args.session)
        if analyzer.load_session_data():
            analyzer.analyze_order_id_patterns()
            analyzer.analyze_module_status_patterns()
            analyzer.analyze_workflow_patterns()
            analyzer.analyze_error_patterns()
            analyzer.print_summary()
        else:
            print("❌ Konnte Session nicht laden")
    
    else:
        print("❌ Bitte --session oder --sessions-dir angeben")

if __name__ == "__main__":
    main()
