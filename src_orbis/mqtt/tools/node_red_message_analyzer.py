#!/usr/bin/env python3
"""
Node-RED Message Analyzer
Analysiert Node-RED Nachrichten aus MQTT Session-Daten
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime
import argparse
import os
from typing import Dict, List, Optional

class NodeRedMessageAnalyzer:
    def __init__(self, db_file: str):
        self.db_file = db_file
        self.connection = None
        
    def connect(self):
        """Verbindung zur SQLite-Datenbank herstellen"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            print(f"✅ Verbunden mit: {self.db_file}")
        except Exception as e:
            print(f"❌ Verbindungsfehler: {e}")
            return False
        return True
    
    def disconnect(self):
        """Verbindung schließen"""
        if self.connection:
            self.connection.close()
    
    def get_node_red_messages(self) -> pd.DataFrame:
        """Node-RED Nachrichten aus der Datenbank extrahieren"""
        query = """
        SELECT timestamp, topic, payload, message_type, module_type, serial_number, status, process_label
        FROM mqtt_messages 
        WHERE topic LIKE '%NodeRed%' 
           OR topic LIKE '%factsheet%' 
           OR topic LIKE '%connection%'
        ORDER BY timestamp DESC
        """
        
        try:
            df = pd.read_sql_query(query, self.connection)
            print(f"📊 {len(df)} Node-RED Nachrichten gefunden")
            return df
        except Exception as e:
            print(f"❌ Fehler beim Laden der Node-RED Nachrichten: {e}")
            return pd.DataFrame()
    
    def analyze_node_red_topics(self, df: pd.DataFrame) -> Dict:
        """Node-RED Topics analysieren"""
        if df.empty:
            return {}
        
        analysis = {
            'total_messages': len(df),
            'unique_topics': df['topic'].nunique(),
            'topic_distribution': df['topic'].value_counts().to_dict(),
            'message_types': df['message_type'].value_counts().to_dict(),
            'modules': df['module_type'].value_counts().to_dict(),
            'statuses': df['status'].value_counts().to_dict()
        }
        
        return analysis
    
    def extract_node_red_state_messages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Node-RED State-Nachrichten extrahieren"""
        state_df = df[df['topic'].str.contains('NodeRed.*state', na=False)]
        print(f"🔍 {len(state_df)} Node-RED State-Nachrichten gefunden")
        return state_df
    
    def extract_factsheet_messages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Factsheet-Nachrichten extrahieren"""
        factsheet_df = df[df['topic'].str.contains('factsheet', na=False)]
        print(f"📋 {len(factsheet_df)} Factsheet-Nachrichten gefunden")
        return factsheet_df
    
    def extract_connection_messages(self, df: pd.DataFrame) -> pd.DataFrame:
        """Connection-Nachrichten extrahieren"""
        connection_df = df[df['topic'].str.contains('connection', na=False)]
        print(f"🔗 {len(connection_df)} Connection-Nachrichten gefunden")
        return connection_df
    
    def parse_payload(self, payload_str: str) -> Dict:
        """JSON Payload parsen"""
        try:
            if isinstance(payload_str, str):
                return json.loads(payload_str)
            return payload_str
        except:
            return {}
    
    def analyze_payload_structure(self, df: pd.DataFrame) -> Dict:
        """Payload-Struktur analysieren"""
        payload_analysis = {}
        
        for _, row in df.iterrows():
            payload = self.parse_payload(row['payload'])
            if payload:
                payload_keys = list(payload.keys())
                key_str = ', '.join(sorted(payload_keys))
                
                if key_str not in payload_analysis:
                    payload_analysis[key_str] = {
                        'count': 0,
                        'examples': [],
                        'topics': set()
                    }
                
                payload_analysis[key_str]['count'] += 1
                payload_analysis[key_str]['topics'].add(row['topic'])
                
                if len(payload_analysis[key_str]['examples']) < 3:
                    payload_analysis[key_str]['examples'].append({
                        'topic': row['topic'],
                        'payload': payload
                    })
        
        # Sets zu Listen konvertieren für JSON-Serialisierung
        for key in payload_analysis:
            payload_analysis[key]['topics'] = list(payload_analysis[key]['topics'])
        
        return payload_analysis
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict:
        """Vollständigen Analyse-Report generieren"""
        if not self.connect():
            return {}
        
        # Node-RED Nachrichten laden
        df = self.get_node_red_messages()
        
        if df.empty:
            print("❌ Keine Node-RED Nachrichten gefunden")
            return {}
        
        # Analysen durchführen
        topic_analysis = self.analyze_node_red_topics(df)
        state_messages = self.extract_node_red_state_messages(df)
        factsheet_messages = self.extract_factsheet_messages(df)
        connection_messages = self.extract_connection_messages(df)
        
        # Payload-Analyse
        payload_analysis = self.analyze_payload_structure(df)
        
        # Report zusammenstellen
        report = {
            'session_file': self.db_file,
            'analysis_timestamp': datetime.now().isoformat(),
            'overview': topic_analysis,
            'node_red_state_messages': {
                'count': len(state_messages),
                'topics': state_messages['topic'].unique().tolist() if not state_messages.empty else [],
                'sample_messages': state_messages.head(5).to_dict('records') if not state_messages.empty else []
            },
            'factsheet_messages': {
                'count': len(factsheet_messages),
                'topics': factsheet_messages['topic'].unique().tolist() if not factsheet_messages.empty else [],
                'sample_messages': factsheet_messages.head(5).to_dict('records') if not factsheet_messages.empty else []
            },
            'connection_messages': {
                'count': len(connection_messages),
                'topics': connection_messages['topic'].unique().tolist() if not connection_messages.empty else [],
                'sample_messages': connection_messages.head(5).to_dict('records') if not connection_messages.empty else []
            },
            'payload_analysis': payload_analysis
        }
        
        # Report ausgeben
        self.print_report(report)
        
        # Report speichern
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📄 Report gespeichert: {output_file}")
        
        self.disconnect()
        return report
    
    def print_report(self, report: Dict):
        """Report in der Konsole ausgeben"""
        print("\n" + "="*60)
        print("🔍 NODE-RED MESSAGE ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📁 Session: {os.path.basename(report['session_file'])}")
        print(f"⏰ Analyse: {report['analysis_timestamp']}")
        
        # Overview
        overview = report['overview']
        print(f"\n📊 OVERVIEW:")
        print(f"   Gesamt-Nachrichten: {overview.get('total_messages', 0)}")
        print(f"   Eindeutige Topics: {overview.get('unique_topics', 0)}")
        
        # Topic Distribution
        if 'topic_distribution' in overview:
            print(f"\n📋 TOPIC DISTRIBUTION:")
            for topic, count in list(overview['topic_distribution'].items())[:10]:
                print(f"   {topic}: {count}")
        
        # Node-RED State Messages
        state_info = report['node_red_state_messages']
        print(f"\n🔍 NODE-RED STATE MESSAGES: {state_info['count']}")
        if state_info['topics']:
            print(f"   Topics: {', '.join(state_info['topics'])}")
        
        # Factsheet Messages
        factsheet_info = report['factsheet_messages']
        print(f"\n📋 FACTSHEET MESSAGES: {factsheet_info['count']}")
        if factsheet_info['topics']:
            print(f"   Topics: {', '.join(factsheet_info['topics'])}")
        
        # Connection Messages
        connection_info = report['connection_messages']
        print(f"\n🔗 CONNECTION MESSAGES: {connection_info['count']}")
        if connection_info['topics']:
            print(f"   Topics: {', '.join(connection_info['topics'])}")
        
        # Payload Analysis
        if report['payload_analysis']:
            print(f"\n📦 PAYLOAD STRUCTURES:")
            for structure, info in list(report['payload_analysis'].items())[:5]:
                print(f"   {structure}: {info['count']} Nachrichten")
                print(f"     Topics: {', '.join(info['topics'][:3])}")
        
        print("\n" + "="*60)

def main():
    parser = argparse.ArgumentParser(description='Node-RED Message Analyzer')
    parser.add_argument('--session', required=True, help='Session-Datenbank-Datei')
    parser.add_argument('--output', help='Output-Datei für Report (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.session):
        print(f"❌ Session-Datei nicht gefunden: {args.session}")
        return
    
    analyzer = NodeRedMessageAnalyzer(args.session)
    analyzer.generate_report(args.output)

if __name__ == "__main__":
    main()
