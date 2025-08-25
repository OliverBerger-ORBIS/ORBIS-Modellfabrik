#!/usr/bin/env python3
"""
Wareneingang Workflow Analysis
Analyse der MQTT-Nachrichten für den Wareneingang-Workflow
"""

import os
import sys
import sqlite3
import pandas as pd
import json
from datetime import datetime
import re

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def load_session_data(session_name):
    """Load MQTT data from session database."""
    db_path = f"mqtt-data/sessions/aps_persistent_traffic_{session_name}.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Session nicht gefunden: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
        conn.close()
        
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"❌ Fehler beim Laden der Session: {e}")
        return None

def analyze_order_id_creation(df):
    """1) Wann wird ein Order-ID erstellt und wann wird sie an die Module weitergegeben."""
    print("\n" + "="*80)
    print("1️⃣ ORDER-ID ERSTELLUNG UND WEITERGABE")
    print("="*80)
    
    # Find order-related messages
    order_messages = df[df['topic'].str.contains('order', na=False)]
    
    if len(order_messages) == 0:
        print("❌ Keine Order-Nachrichten gefunden")
        return
    
    print(f"✅ {len(order_messages)} Order-Nachrichten gefunden")
    
    # Analyze order creation
    for idx, row in order_messages.iterrows():
        print(f"\n📋 {row['timestamp']} - {row['topic']}")
        try:
            payload = json.loads(row['payload'])
            if 'orderId' in payload:
                print(f"   🆔 Order-ID: {payload['orderId']}")
            if 'orderType' in payload:
                print(f"   📝 Order-Type: {payload['orderType']}")
            if 'workpieceId' in payload:
                print(f"   🏷️ Workpiece-ID: {payload['workpieceId']}")
            if 'workpieceColor' in payload:
                print(f"   🎨 Color: {payload['workpieceColor']}")
        except:
            print(f"   📄 Payload: {row['payload'][:100]}...")

def analyze_module_status(df):
    """2) Welchen Status senden die Module."""
    print("\n" + "="*80)
    print("2️⃣ MODULE STATUS NACHRICHTEN")
    print("="*80)
    
    # Find module status messages
    module_status = df[df['topic'].str.contains('module/v1/ff/.*/state', na=False)]
    
    if len(module_status) == 0:
        print("❌ Keine Module-Status-Nachrichten gefunden")
        return
    
    print(f"✅ {len(module_status)} Module-Status-Nachrichten gefunden")
    
    # Group by module
    for module_id in module_status['topic'].str.extract(r'module/v1/ff/([^/]+)')[0].unique():
        module_messages = module_status[module_status['topic'].str.contains(module_id)]
        print(f"\n🏭 {module_id} ({len(module_messages)} Nachrichten):")
        
        for idx, row in module_messages.head(5).iterrows():
            print(f"   📊 {row['timestamp']} - {row['topic']}")
            try:
                payload = json.loads(row['payload'])
                if 'state' in payload:
                    print(f"      🔄 State: {payload['state']}")
                if 'status' in payload:
                    print(f"      📈 Status: {payload['status']}")
            except:
                print(f"      📄 Payload: {row['payload'][:100]}...")

def analyze_status_queries(df):
    """3) Welcher Status wird abgefragt, um zu wissen ob die nächste Aktion bereit ist."""
    print("\n" + "="*80)
    print("3️⃣ STATUS-ABFRAGEN FÜR BEREITSCHAFT")
    print("="*80)
    
    # Find status query messages
    status_queries = df[df['topic'].str.contains('status|ready|available|factsheet', na=False)]
    
    if len(status_queries) == 0:
        print("❌ Keine Status-Abfragen gefunden")
        return
    
    print(f"✅ {len(status_queries)} Status-Abfragen gefunden")
    
    for idx, row in status_queries.iterrows():
        print(f"\n❓ {row['timestamp']} - {row['topic']}")
        try:
            payload = json.loads(row['payload'])
            print(f"   📋 Query: {payload}")
        except:
            print(f"   📄 Payload: {row['payload'][:100]}...")

def analyze_fts_communication(df):
    """4) Welche Information sendet das FTS und wie wird es gesteuert."""
    print("\n" + "="*80)
    print("4️⃣ FTS KOMMUNIKATION UND STEUERUNG")
    print("="*80)
    
    # Find FTS messages
    fts_messages = df[df['topic'].str.contains('fts|5iO4', na=False)]
    
    if len(fts_messages) == 0:
        print("❌ Keine FTS-Nachrichten gefunden")
        return
    
    print(f"✅ {len(fts_messages)} FTS-Nachrichten gefunden")
    
    # Group by message type
    fts_control = fts_messages[fts_messages['topic'].str.contains('instantAction|control', na=False)]
    fts_status = fts_messages[fts_messages['topic'].str.contains('state|status', na=False)]
    
    print(f"\n🎮 FTS Control ({len(fts_control)} Nachrichten):")
    for idx, row in fts_control.iterrows():
        print(f"   🎯 {row['timestamp']} - {row['topic']}")
        try:
            payload = json.loads(row['payload'])
            print(f"      📋 Command: {payload}")
        except:
            print(f"      📄 Payload: {row['payload'][:100]}...")
    
    print(f"\n📊 FTS Status ({len(fts_status)} Nachrichten):")
    for idx, row in fts_status.iterrows():
        print(f"   📈 {row['timestamp']} - {row['topic']}")
        try:
            payload = json.loads(row['payload'])
            print(f"      📋 Status: {payload}")
        except:
            print(f"      📄 Payload: {row['payload'][:100]}...")

def analyze_ccu_communication(df):
    """5) Welche Info kommt von der CCU."""
    print("\n" + "="*80)
    print("5️⃣ CCU KOMMUNIKATION")
    print("="*80)
    
    # Find CCU messages
    ccu_messages = df[df['topic'].str.contains('ccu', na=False)]
    
    if len(ccu_messages) == 0:
        print("❌ Keine CCU-Nachrichten gefunden")
        return
    
    print(f"✅ {len(ccu_messages)} CCU-Nachrichten gefunden")
    
    for idx, row in ccu_messages.iterrows():
        print(f"\n🎛️ {row['timestamp']} - {row['topic']}")
        try:
            payload = json.loads(row['payload'])
            print(f"   📋 CCU Info: {payload}")
        except:
            print(f"   📄 Payload: {row['payload'][:100]}...")

def analyze_nodered_flow(df):
    """6) Könnte der Node-RED Flow die Verarbeitung steuern."""
    print("\n" + "="*80)
    print("6️⃣ NODE-RED FLOW ANALYSE")
    print("="*80)
    
    # Find Node-RED related messages
    nodered_messages = df[df['topic'].str.contains('NodeRed|nodered|workflow', na=False)]
    
    if len(nodered_messages) == 0:
        print("❌ Keine Node-RED-Nachrichten gefunden")
        print("💡 Node-RED könnte über andere Topics kommunizieren")
        return
    
    print(f"✅ {len(nodered_messages)} Node-RED-Nachrichten gefunden")
    
    for idx, row in nodered_messages.iterrows():
        print(f"\n🔄 {row['timestamp']} - {row['topic']}")
        try:
            payload = json.loads(row['payload'])
            print(f"   📋 Node-RED Flow: {payload}")
        except:
            print(f"   📄 Payload: {row['payload'][:100]}...")

def analyze_persistence(df):
    """7) Wo werden die Lagerplätze persistiert."""
    print("\n" + "="*80)
    print("7️⃣ LAGERPLATZ PERSISTIERUNG")
    print("="*80)
    
    # Find storage/persistence related messages
    storage_messages = df[df['topic'].str.contains('storage|persist|save|load|position|slot', na=False)]
    
    if len(storage_messages) == 0:
        print("❌ Keine Storage-Nachrichten gefunden")
        print("💡 Lagerplätze könnten in anderen Topics gespeichert werden")
        return
    
    print(f"✅ {len(storage_messages)} Storage-Nachrichten gefunden")
    
    for idx, row in storage_messages.iterrows():
        print(f"\n💾 {row['timestamp']} - {row['topic']}")
        try:
            payload = json.loads(row['payload'])
            print(f"   📋 Storage Info: {payload}")
        except:
            print(f"   📄 Payload: {row['payload'][:100]}...")

def analyze_workflow_sequence(df):
    """Analyze the complete workflow sequence."""
    print("\n" + "="*80)
    print("🔄 WAREINEINGANG WORKFLOW SEQUENZ")
    print("="*80)
    
    # Create timeline of events
    df_sorted = df.sort_values('timestamp')
    
    print("📅 Workflow Timeline:")
    for idx, row in df_sorted.iterrows():
        # Extract module from topic
        module_match = re.search(r'module/v1/ff/([^/]+)', row['topic'])
        module = module_match.group(1) if module_match else "Unknown"
        
        print(f"   {row['timestamp'].strftime('%H:%M:%S.%f')[:-3]} - {module} - {row['topic']}")
        
        # Show payload for important messages
        if any(keyword in row['topic'] for keyword in ['order', 'state', 'instantAction']):
            try:
                payload = json.loads(row['payload'])
                print(f"      📋 {payload}")
            except:
                print(f"      📄 {row['payload'][:100]}...")

def main():
    """Main analysis function."""
    print("🏭 WAREINEINGANG WORKFLOW ANALYSE")
    print("="*80)
    
    # Available sessions
    sessions = [
        "wareneingang-blau_1",
        "wareneingang-blau_2", 
        "wareneingang-blau_3",
        "wareneingang-weiss_1",
        "wareneingang-weiss_2",
        "wareneingang-weiss_3",
        "wareneingang-rot_1",
        "wareneingang-rot_2",
        "wareneingang-rot_3"
    ]
    
    print("📁 Verfügbare Sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"   {i}. {session}")
    
    # Analyze first session as example
    session_name = sessions[0]
    print(f"\n🔍 Analysiere Session: {session_name}")
    
    df = load_session_data(session_name)
    if df is None:
        return
    
    print(f"✅ {len(df)} MQTT-Nachrichten geladen")
    print(f"📅 Zeitraum: {df['timestamp'].min()} bis {df['timestamp'].max()}")
    
    # Run all analyses
    analyze_order_id_creation(df)
    analyze_module_status(df)
    analyze_status_queries(df)
    analyze_fts_communication(df)
    analyze_ccu_communication(df)
    analyze_nodered_flow(df)
    analyze_persistence(df)
    analyze_workflow_sequence(df)
    
    print("\n" + "="*80)
    print("✅ ANALYSE ABGESCHLOSSEN")
    print("="*80)

if __name__ == "__main__":
    main()
