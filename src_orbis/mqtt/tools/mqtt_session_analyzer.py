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
        
        # Suche in verschachtelten Objekten
        if 'action' in payload and isinstance(payload['action'], dict):
            for field in order_id_fields:
                if field in payload['action']:
                    return payload['action'][field]
        
        return None
    
    def _get_payload_structure(self, payload):
        """Ermittelt die Struktur eines Payloads"""
        if not payload:
            return {}
        
        structure = {}
        for key, value in payload.items():
            if isinstance(value, dict):
                structure[key] = 'object'
            elif isinstance(value, list):
                structure[key] = 'array'
            else:
                structure[key] = type(value).__name__
        
        return structure
    
    def analyze_module_status_patterns(self):
        """Analysiert Modul-Status Muster"""
        print("\n🔍 Analysiere Modul-Status Muster...")
        
        status_updates = []
        module_statuses = {}
        
        for _, row in self.df.iterrows():
            if row['payload_json']:
                # Suche nach Status-Informationen
                status_info = self._extract_status_info(row['payload_json'], row['topic'])
                if status_info:
                    status_updates.append({
                        'timestamp': row['timestamp'],
                        'topic': row['topic'],
                        'module': status_info.get('module'),
                        'status': status_info.get('status'),
                        'details': status_info.get('details')
                    })
                    
                    # Track Status pro Modul
                    module = status_info.get('module')
                    if module:
                        if module not in module_statuses:
                            module_statuses[module] = []
                        module_statuses[module].append({
                            'timestamp': row['timestamp'],
                            'status': status_info.get('status')
                        })
        
        self.analysis_results['status_analysis'] = {
            'status_updates': status_updates,
            'module_statuses': module_statuses,
            'status_transitions': self._analyze_status_transitions(module_statuses)
        }
        
        print(f"   📊 {len(status_updates)} Status-Updates gefunden")
        return status_updates
    
    def _extract_status_info(self, payload, topic):
        """Extrahiert Status-Informationen aus Payload und Topic"""
        status_info = {}
        
        # Extrahiere Modul aus Topic
        module_match = re.search(r'/([A-Z]+)/', topic)
        if module_match:
            status_info['module'] = module_match.group(1)
        
        # Suche nach Status-Feldern
        status_fields = ['status', 'state', 'availability', 'ready', 'busy', 'error']
        
        for field in status_fields:
            if field in payload:
                status_info['status'] = payload[field]
                status_info['details'] = payload
                return status_info
        
        # Suche in verschachtelten Objekten
        for key, value in payload.items():
            if isinstance(value, dict):
                for field in status_fields:
                    if field in value:
                        status_info['status'] = value[field]
                        status_info['details'] = value
                        return status_info
        
        return None
    
    def _analyze_status_transitions(self, module_statuses):
        """Analysiert Status-Übergänge pro Modul"""
        transitions = {}
        
        for module, statuses in module_statuses.items():
            transitions[module] = []
            for i in range(1, len(statuses)):
                prev_status = statuses[i-1]['status']
                curr_status = statuses[i]['status']
                if prev_status != curr_status:
                    transitions[module].append({
                        'from': prev_status,
                        'to': curr_status,
                        'timestamp': statuses[i]['timestamp']
                    })
        
        return transitions
    
    def analyze_command_patterns(self):
        """Analysiert Command-Muster"""
        print("\n🔍 Analysiere Command-Muster...")
        
        commands = []
        command_sequences = []
        
        for _, row in self.df.iterrows():
            if row['payload_json']:
                command_info = self._extract_command_info(row['payload_json'], row['topic'])
                if command_info:
                    commands.append({
                        'timestamp': row['timestamp'],
                        'topic': row['topic'],
                        'command': command_info.get('command'),
                        'module': command_info.get('module'),
                        'order_id': command_info.get('order_id'),
                        'metadata': command_info.get('metadata')
                    })
        
        # Analysiere Command-Sequenzen
        if commands:
            command_sequences = self._analyze_command_sequences(commands)
        
        self.analysis_results['command_analysis'] = {
            'commands': commands,
            'command_sequences': command_sequences,
            'command_frequency': self._analyze_command_frequency(commands)
        }
        
        print(f"   📊 {len(commands)} Commands gefunden")
        return commands
    
    def _extract_command_info(self, payload, topic):
        """Extrahiert Command-Informationen aus Payload und Topic"""
        command_info = {}
        
        # Extrahiere Modul aus Topic
        module_match = re.search(r'/([A-Z]+)/', topic)
        if module_match:
            command_info['module'] = module_match.group(1)
        
        # Suche nach Command-Feldern
        if 'action' in payload and isinstance(payload['action'], dict):
            action = payload['action']
            if 'command' in action:
                command_info['command'] = action['command']
                command_info['metadata'] = action.get('metadata', {})
                command_info['order_id'] = self._extract_order_id(payload)
                return command_info
        
        # Direkte Command-Felder
        command_fields = ['command', 'cmd', 'action']
        for field in command_fields:
            if field in payload:
                command_info['command'] = payload[field]
                command_info['metadata'] = payload
                command_info['order_id'] = self._extract_order_id(payload)
                return command_info
        
        return None
    
    def _analyze_command_sequences(self, commands):
        """Analysiert Command-Sequenzen"""
        sequences = []
        current_sequence = []
        
        for command in commands:
            if not current_sequence:
                current_sequence = [command]
            else:
                # Prüfe ob Command zur aktuellen Sequenz gehört (gleiche ORDER-ID)
                if (command.get('order_id') == current_sequence[0].get('order_id')):
                    current_sequence.append(command)
                else:
                    # Neue Sequenz
                    if len(current_sequence) > 1:
                        sequences.append(current_sequence)
                    current_sequence = [command]
        
        # Letzte Sequenz hinzufügen
        if len(current_sequence) > 1:
            sequences.append(current_sequence)
        
        return sequences
    
    def _analyze_command_frequency(self, commands):
        """Analysiert Command-Häufigkeit"""
        frequency = {}
        for command in commands:
            cmd = command.get('command')
            if cmd:
                frequency[cmd] = frequency.get(cmd, 0) + 1
        return frequency
    
    def analyze_error_patterns(self):
        """Analysiert Error-Muster"""
        print("\n🔍 Analysiere Error-Muster...")
        
        errors = []
        error_patterns = {}
        
        for _, row in self.df.iterrows():
            if row['payload_json']:
                error_info = self._extract_error_info(row['payload_json'], row['topic'])
                if error_info:
                    errors.append({
                        'timestamp': row['timestamp'],
                        'topic': row['topic'],
                        'error_type': error_info.get('error_type'),
                        'error_message': error_info.get('error_message'),
                        'module': error_info.get('module'),
                        'details': error_info.get('details')
                    })
        
        # Gruppiere Errors nach Typ
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            if error_type not in error_patterns:
                error_patterns[error_type] = []
            error_patterns[error_type].append(error)
        
        self.analysis_results['error_analysis'] = {
            'errors': errors,
            'error_patterns': error_patterns,
            'error_frequency': {k: len(v) for k, v in error_patterns.items()}
        }
        
        print(f"   📊 {len(errors)} Errors gefunden")
        return errors
    
    def _extract_error_info(self, payload, topic):
        """Extrahiert Error-Informationen aus Payload und Topic"""
        error_info = {}
        
        # Extrahiere Modul aus Topic
        module_match = re.search(r'/([A-Z]+)/', topic)
        if module_match:
            error_info['module'] = module_match.group(1)
        
        # Suche nach Error-Feldern
        error_fields = ['error', 'error_code', 'error_message', 'failed', 'failure']
        
        for field in error_fields:
            if field in payload:
                error_info['error_type'] = field
                error_info['error_message'] = str(payload[field])
                error_info['details'] = payload
                return error_info
        
        # Suche nach Error-Indikatoren in Payload
        payload_str = json.dumps(payload).lower()
        error_indicators = ['error', 'failed', 'failure', 'timeout', 'not ok']
        
        for indicator in error_indicators:
            if indicator in payload_str:
                error_info['error_type'] = 'indicator'
                error_info['error_message'] = f"Contains '{indicator}'"
                error_info['details'] = payload
                return error_info
        
        return None
    
    def generate_analysis_report(self):
        """Generiert einen detaillierten Analyse-Report"""
        print("\n📊 Generiere Analyse-Report...")
        
        report = {
            'session_info': {
                'database': self.session_db_path,
                'message_count': len(self.df) if self.df is not None else 0,
                'analysis_timestamp': datetime.now().isoformat()
            },
            'order_id_analysis': self.analysis_results.get('order_id_analysis', {}),
            'status_analysis': self.analysis_results.get('status_analysis', {}),
            'command_analysis': self.analysis_results.get('command_analysis', {}),
            'error_analysis': self.analysis_results.get('error_analysis', {}),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self):
        """Generiert Empfehlungen basierend auf der Analyse"""
        recommendations = []
        
        # ORDER-ID Empfehlungen
        order_analysis = self.analysis_results.get('order_id_analysis', {})
        if order_analysis.get('order_id_count', 0) == 0:
            recommendations.append("⚠️ Keine ORDER-IDs gefunden - Implementierung erforderlich")
        elif order_analysis.get('order_id_count', 0) < 5:
            recommendations.append("📊 Wenige ORDER-IDs - Mehr Sessions für bessere Analyse erforderlich")
        
        # Status-Monitoring Empfehlungen
        status_analysis = self.analysis_results.get('status_analysis', {})
        if not status_analysis.get('status_updates'):
            recommendations.append("⚠️ Keine Status-Updates gefunden - Status-Monitoring verbessern")
        
        # Command-Empfehlungen
        command_analysis = self.analysis_results.get('command_analysis', {})
        if not command_analysis.get('commands'):
            recommendations.append("⚠️ Keine Commands gefunden - Command-Monitoring implementieren")
        
        # Error-Empfehlungen
        error_analysis = self.analysis_results.get('error_analysis', {})
        if error_analysis.get('errors'):
            recommendations.append(f"🚨 {len(error_analysis['errors'])} Errors gefunden - Error-Handling verbessern")
        
        return recommendations
    
    def save_analysis_report(self, output_path):
        """Speichert den Analyse-Report als JSON"""
        report = self.generate_analysis_report()
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Analyse-Report gespeichert: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Speichern des Reports: {e}")
            return False

def main():
    """Hauptfunktion für Command-Line-Interface"""
    parser = argparse.ArgumentParser(description='MQTT Session Analyzer')
    parser.add_argument('session_db', help='Pfad zur Session-Datenbank (.db)')
    parser.add_argument('--output', '-o', help='Ausgabe-Pfad für Report (.json)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Detaillierte Ausgabe')
    
    args = parser.parse_args()
    
    # Prüfe ob Session-DB existiert
    if not Path(args.session_db).exists():
        print(f"❌ Session-Datenbank nicht gefunden: {args.session_db}")
        return 1
    
    # Erstelle Analyzer
    analyzer = MQTTSessionAnalyzer(args.session_db)
    
    # Lade Session-Daten
    if not analyzer.load_session_data():
        return 1
    
    # Führe Analysen durch
    analyzer.analyze_order_id_patterns()
    analyzer.analyze_module_status_patterns()
    analyzer.analyze_command_patterns()
    analyzer.analyze_error_patterns()
    
    # Generiere Report
    report = analyzer.generate_analysis_report()
    
    # Zeige Zusammenfassung
    print("\n" + "="*60)
    print("📊 MQTT-SESSION-ANALYSE ZUSAMMENFASSUNG")
    print("="*60)
    print(f"📁 Session-DB: {args.session_db}")
    print(f"📨 Nachrichten: {report['session_info']['message_count']}")
    print(f"🆔 ORDER-IDs: {report['order_id_analysis'].get('order_id_count', 0)}")
    print(f"📊 Status-Updates: {len(report['status_analysis'].get('status_updates', []))}")
    print(f"⚡ Commands: {len(report['command_analysis'].get('commands', []))}")
    print(f"🚨 Errors: {len(report['error_analysis'].get('errors', []))}")
    
    # Zeige Empfehlungen
    if report['recommendations']:
        print("\n💡 EMPFEHLUNGEN:")
        for rec in report['recommendations']:
            print(f"   {rec}")
    
    # Speichere Report
    if args.output:
        analyzer.save_analysis_report(args.output)
    else:
        # Standard-Ausgabe
        output_path = f"mqtt_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        analyzer.save_analysis_report(output_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
