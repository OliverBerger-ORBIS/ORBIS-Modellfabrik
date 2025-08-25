#!/usr/bin/env python3
"""
Auftrags-Workflow Analyse

Analysiert Auftrags-Sessions (auftrag-*) um den kompletten Produktions-Workflow zu verstehen:
1) Auftrag wird über Fischertechnik-Dashboard ausgelöst
2) HBW pickt Werkstück nach FIFO-Prinzip
3) FTS transportiert zu Produktions-Modulen
4) Module verrichten Arbeit (Bohren/Fräsen)
5) AIQS Qualitätsprüfung
6) DPS Warenausgang
"""

import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class AuftragWorkflowAnalyzer:
    """Analysiert Auftrags-Workflow Sessions"""
    
    def __init__(self, sessions_dir: str = "mqtt-data/sessions"):
        self.sessions_dir = sessions_dir
        self.analysis_results = {}
    
    def get_auftrag_sessions(self) -> List[str]:
        """Findet alle Auftrags-Sessions"""
        sessions = []
        if os.path.exists(self.sessions_dir):
            for file in os.listdir(self.sessions_dir):
                if file.endswith('.db') and 'auftrag' in file and 'aps_persistent_traffic_' in file:
                    session_name = file.replace('aps_persistent_traffic_', '').replace('.db', '')
                    sessions.append(session_name)
        return sorted(sessions)
    
    def load_session_data(self, session_name: str) -> pd.DataFrame:
        """Lädt Session-Daten"""
        db_path = os.path.join(self.sessions_dir, f"aps_persistent_traffic_{session_name}.db")
        
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Session {session_name} nicht gefunden")
        
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
        conn.close()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['session_label'] = session_name
        
        return df
    
    def analyze_order_triggering(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analysiert Order-Triggering (Schritt 1)"""
        print("\n🔍 1. Order-Triggering Analyse...")
        
        # Order-Triggering Messages
        order_messages = df[df['topic'].str.contains('order', na=False)]
        
        # Browser-Order (Fischertechnik Dashboard)
        browser_orders = df[df['topic'] == '/j1/txt/1/f/o/order']
        
        # CCU Order Management
        ccu_orders = df[df['topic'].str.contains('ccu/order', na=False)]
        
        results = {
            'total_order_messages': len(order_messages),
            'browser_orders': len(browser_orders),
            'ccu_orders': len(ccu_orders),
            'order_types': [],
            'workpieces': [],
            'trigger_timestamps': []
        }
        
        # Browser Order Details
        for idx, row in browser_orders.iterrows():
            try:
                payload = json.loads(row['payload'])
                results['trigger_timestamps'].append(row['timestamp'])
                
                if 'orderType' in payload:
                    results['order_types'].append(payload['orderType'])
                
                if 'workpieceId' in payload:
                    results['workpieces'].append(payload['workpieceId'])
                    
                print(f"   📋 Browser Order: {payload.get('orderType', 'Unknown')} - {payload.get('workpieceId', 'Unknown')}")
            except:
                pass
        
        # CCU Order Details
        for idx, row in ccu_orders.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'orderType' in payload:
                    results['order_types'].append(payload['orderType'])
                if 'workpieceId' in payload:
                    results['workpieces'].append(payload['workpieceId'])
            except:
                pass
        
        return results
    
    def analyze_hbw_pick_fifo(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analysiert HBW PICK nach FIFO-Prinzip (Schritt 2-3)"""
        print("\n🔍 2. HBW PICK FIFO-Analyse...")
        
        # HBW Messages
        hbw_messages = df[df['topic'].str.contains('SVR3QA0022', na=False)]
        
        # PICK Commands
        pick_messages = hbw_messages[hbw_messages['payload'].str.contains('PICK', na=False)]
        
        # HBW State Changes
        hbw_state = hbw_messages[hbw_messages['topic'].str.contains('/state', na=False)]
        
        results = {
            'total_hbw_messages': len(hbw_messages),
            'pick_commands': len(pick_messages),
            'state_changes': len(hbw_state),
            'picked_workpieces': [],
            'pick_sequence': [],
            'hbw_loads': []
        }
        
        # Analyze PICK sequence
        for idx, row in pick_messages.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'action' in payload and 'command' in payload['action']:
                    if payload['action']['command'] == 'PICK':
                        results['pick_sequence'].append({
                            'timestamp': row['timestamp'],
                            'orderId': payload.get('orderId', 'Unknown'),
                            'workpieceId': payload.get('workpieceId', 'Unknown')
                        })
            except:
                pass
        
        # Analyze HBW loads
        for idx, row in hbw_state.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'loads' in payload:
                    results['hbw_loads'].append({
                        'timestamp': row['timestamp'],
                        'loads': payload['loads']
                    })
            except:
                pass
        
        return results
    
    def analyze_fts_transport(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analysiert FTS Transport zu Modulen (Schritt 4)"""
        print("\n🔍 3. FTS Transport-Analyse...")
        
        # FTS Messages
        fts_messages = df[df['topic'].str.contains('5iO4', na=False)]
        
        # Navigation Commands
        navigation_messages = fts_messages[fts_messages['payload'].str.contains('NAVIGATION', na=False)]
        
        # Load Handling
        load_messages = fts_messages[fts_messages['payload'].str.contains('load', na=False)]
        
        results = {
            'total_fts_messages': len(fts_messages),
            'navigation_commands': len(navigation_messages),
            'load_handling': len(load_messages),
            'transport_routes': [],
            'load_transfers': []
        }
        
        # Analyze transport routes
        for idx, row in navigation_messages.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'type' in payload and payload['type'] == 'NAVIGATION':
                    results['transport_routes'].append({
                        'timestamp': row['timestamp'],
                        'source': payload.get('source', 'Unknown'),
                        'target': payload.get('target', 'Unknown'),
                        'state': payload.get('state', 'Unknown')
                    })
            except:
                pass
        
        # Analyze load transfers
        for idx, row in load_messages.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'load' in payload:
                    results['load_transfers'].append({
                        'timestamp': row['timestamp'],
                        'load': payload['load']
                    })
            except:
                pass
        
        return results
    
    def analyze_production_modules(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analysiert Produktions-Module (Schritt 5-6)"""
        print("\n🔍 4. Produktions-Module Analyse...")
        
        # Module Messages
        drill_messages = df[df['topic'].str.contains('SVR4H76449', na=False)]  # DRILL
        mill_messages = df[df['topic'].str.contains('SVR3QA2098', na=False)]   # MILL
        
        results = {
            'drill_messages': len(drill_messages),
            'mill_messages': len(mill_messages),
            'drill_commands': [],
            'mill_commands': [],
            'production_steps': []
        }
        
        # Analyze DRILL commands
        for idx, row in drill_messages.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'action' in payload and 'command' in payload['action']:
                    results['drill_commands'].append({
                        'timestamp': row['timestamp'],
                        'command': payload['action']['command'],
                        'orderId': payload.get('orderId', 'Unknown'),
                        'workpieceId': payload.get('workpieceId', 'Unknown')
                    })
            except:
                pass
        
        # Analyze MILL commands
        for idx, row in mill_messages.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'action' in payload and 'command' in payload['action']:
                    results['mill_commands'].append({
                        'timestamp': row['timestamp'],
                        'command': payload['action']['command'],
                        'orderId': payload.get('orderId', 'Unknown'),
                        'workpieceId': payload.get('workpieceId', 'Unknown')
                    })
            except:
                pass
        
        return results
    
    def analyze_aiqs_quality_check(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analysiert AIQS Qualitätsprüfung (Schritt 7-8)"""
        print("\n🔍 5. AIQS Qualitätsprüfung Analyse...")
        
        # AIQS Messages
        aiqs_messages = df[df['topic'].str.contains('SVR4H76530', na=False)]
        
        # Quality Check Commands
        quality_messages = aiqs_messages[aiqs_messages['payload'].str.contains('QUALITY', na=False)]
        
        results = {
            'total_aiqs_messages': len(aiqs_messages),
            'quality_checks': len(quality_messages),
            'quality_results': [],
            'aiqs_commands': []
        }
        
        # Analyze quality checks
        for idx, row in quality_messages.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'action' in payload and 'command' in payload['action']:
                    results['aiqs_commands'].append({
                        'timestamp': row['timestamp'],
                        'command': payload['action']['command'],
                        'orderId': payload.get('orderId', 'Unknown'),
                        'workpieceId': payload.get('workpieceId', 'Unknown')
                    })
            except:
                pass
        
        return results
    
    def analyze_dps_warenausgang(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analysiert DPS Warenausgang (Schritt 9-10)"""
        print("\n🔍 6. DPS Warenausgang Analyse...")
        
        # DPS Messages
        dps_messages = df[df['topic'].str.contains('SVR4H73275', na=False)]
        
        # DROP Commands (Warenausgang)
        drop_messages = dps_messages[dps_messages['payload'].str.contains('DROP', na=False)]
        
        # NFC Reading
        nfc_messages = df[df['topic'].str.contains('nfc|NFC', na=False)]
        
        results = {
            'total_dps_messages': len(dps_messages),
            'drop_commands': len(drop_messages),
            'nfc_readings': len(nfc_messages),
            'completed_orders': [],
            'nfc_codes': []
        }
        
        # Analyze DROP commands
        for idx, row in drop_messages.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'action' in payload and 'command' in payload['action']:
                    if payload['action']['command'] == 'DROP':
                        results['completed_orders'].append({
                            'timestamp': row['timestamp'],
                            'orderId': payload.get('orderId', 'Unknown'),
                            'workpieceId': payload.get('workpieceId', 'Unknown')
                        })
            except:
                pass
        
        # Analyze NFC readings
        for idx, row in nfc_messages.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'nfcCode' in payload or 'nfc_code' in payload:
                    results['nfc_codes'].append({
                        'timestamp': row['timestamp'],
                        'nfcCode': payload.get('nfcCode', payload.get('nfc_code', 'Unknown'))
                    })
            except:
                pass
        
        return results
    
    def analyze_workflow_sequence(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analysiert die komplette Workflow-Sequenz"""
        print("\n🔍 7. Workflow-Sequenz Analyse...")
        
        # Order completion tracking
        order_completion = df[df['topic'].str.contains('ccu/order/completed', na=False)]
        
        # Production steps tracking
        production_steps = df[df['topic'].str.contains('productionSteps', na=False)]
        
        results = {
            'completed_orders': len(order_completion),
            'production_workflows': [],
            'workflow_duration': {},
            'parallel_processing': []
        }
        
        # Analyze completed orders
        for idx, row in order_completion.iterrows():
            try:
                payload = json.loads(row['payload'])
                results['workflow_duration'][payload.get('orderId', 'Unknown')] = {
                    'completion_time': row['timestamp'],
                    'orderType': payload.get('orderType', 'Unknown'),
                    'workpieceId': payload.get('workpieceId', 'Unknown')
                }
            except:
                pass
        
        # Analyze production steps
        for idx, row in production_steps.iterrows():
            try:
                payload = json.loads(row['payload'])
                if 'productionSteps' in payload:
                    results['production_workflows'].append({
                        'timestamp': row['timestamp'],
                        'orderId': payload.get('orderId', 'Unknown'),
                        'steps': payload['productionSteps']
                    })
            except:
                pass
        
        return results
    
    def analyze_session(self, session_name: str) -> Dict[str, Any]:
        """Führt vollständige Session-Analyse durch"""
        print(f"\n🚀 Analysiere Auftrags-Session: {session_name}")
        print("=" * 60)
        
        try:
            df = self.load_session_data(session_name)
            
            analysis = {
                'session_name': session_name,
                'total_messages': len(df),
                'time_range': {
                    'start': df['timestamp'].min(),
                    'end': df['timestamp'].max(),
                    'duration': df['timestamp'].max() - df['timestamp'].min()
                },
                'order_triggering': self.analyze_order_triggering(df),
                'hbw_pick_fifo': self.analyze_hbw_pick_fifo(df),
                'fts_transport': self.analyze_fts_transport(df),
                'production_modules': self.analyze_production_modules(df),
                'aiqs_quality': self.analyze_aiqs_quality_check(df),
                'dps_warenausgang': self.analyze_dps_warenausgang(df),
                'workflow_sequence': self.analyze_workflow_sequence(df)
            }
            
            self.analysis_results[session_name] = analysis
            return analysis
            
        except Exception as e:
            print(f"❌ Fehler bei Analyse von {session_name}: {e}")
            return {}
    
    def print_summary(self, session_name: str):
        """Druckt Zusammenfassung der Analyse"""
        if session_name not in self.analysis_results:
            print(f"❌ Keine Analyse für {session_name} verfügbar")
            return
        
        analysis = self.analysis_results[session_name]
        
        print(f"\n📊 ZUSAMMENFASSUNG: {session_name}")
        print("=" * 60)
        
        # Basic Info
        print(f"📈 Nachrichten: {analysis['total_messages']}")
        print(f"⏱️  Dauer: {analysis['time_range']['duration']}")
        
        # Order Triggering
        order_info = analysis['order_triggering']
        print(f"\n🎯 Order-Triggering:")
        print(f"   📋 Browser Orders: {order_info['browser_orders']}")
        print(f"   🎛️  CCU Orders: {order_info['ccu_orders']}")
        print(f"   🏷️  Order Types: {', '.join(set(order_info['order_types']))}")
        print(f"   🔧 Werkstücke: {', '.join(set(order_info['workpieces']))}")
        
        # HBW PICK
        hbw_info = analysis['hbw_pick_fifo']
        print(f"\n🏗️  HBW PICK (FIFO):")
        print(f"   📤 PICK Commands: {hbw_info['pick_commands']}")
        print(f"   📊 State Changes: {hbw_info['state_changes']}")
        
        # FTS Transport
        fts_info = analysis['fts_transport']
        print(f"\n🚗 FTS Transport:")
        print(f"   🛣️  Navigation Commands: {fts_info['navigation_commands']}")
        print(f"   📦 Load Handling: {fts_info['load_handling']}")
        
        # Production Modules
        prod_info = analysis['production_modules']
        print(f"\n🏭 Produktions-Module:")
        print(f"   🔨 DRILL Commands: {len(prod_info['drill_commands'])}")
        print(f"   ⚙️  MILL Commands: {len(prod_info['mill_commands'])}")
        
        # AIQS Quality
        aiqs_info = analysis['aiqs_quality']
        print(f"\n🔍 AIQS Qualitätsprüfung:")
        print(f"   ✅ Quality Checks: {aiqs_info['quality_checks']}")
        
        # DPS Warenausgang
        dps_info = analysis['dps_warenausgang']
        print(f"\n📤 DPS Warenausgang:")
        print(f"   📥 DROP Commands: {dps_info['drop_commands']}")
        print(f"   🏷️  NFC Readings: {dps_info['nfc_readings']}")
        
        # Workflow Completion
        workflow_info = analysis['workflow_sequence']
        print(f"\n✅ Workflow-Abschluss:")
        print(f"   🎉 Completed Orders: {workflow_info['completed_orders']}")
        
        print("\n" + "=" * 60)

def main():
    """Hauptfunktion"""
    analyzer = AuftragWorkflowAnalyzer()
    
    # Verfügbare Auftrags-Sessions finden
    sessions = analyzer.get_auftrag_sessions()
    
    if not sessions:
        print("❌ Keine Auftrags-Sessions gefunden!")
        return
    
    print(f"📁 Gefundene Auftrags-Sessions: {len(sessions)}")
    for session in sessions:
        print(f"   - {session}")
    
    # Erste Session analysieren
    if sessions:
        first_session = sessions[0]
        print(f"\n🎯 Analysiere erste Session: {first_session}")
        
        analysis = analyzer.analyze_session(first_session)
        analyzer.print_summary(first_session)
        
        # Detaillierte Ergebnisse speichern
        output_file = f"auftrag_workflow_analysis_{first_session}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        print(f"💾 Detaillierte Analyse gespeichert: {output_file}")

if __name__ == "__main__":
    main()
