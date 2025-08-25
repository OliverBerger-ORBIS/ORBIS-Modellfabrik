#!/usr/bin/env python3
"""
Order-ID Wiederverwendung Analyse

Analysiert ob Order-IDs vom Wareneingang im HBW gespeichert und bei Aufträgen wiederverwendet werden.
"""

import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any

def analyze_order_id_reuse():
    """Analysiert Order-ID Wiederverwendung zwischen Wareneingang und Aufträgen"""
    
    sessions_dir = "mqtt-data/sessions"
    
    print("🔍 Analysiere Order-ID Wiederverwendung zwischen Wareneingang und Aufträgen")
    print("=" * 80)
    
    # 1. Finde Wareneingang-Sessions
    print("\n📥 1. Wareneingang-Sessions analysieren:")
    wareneingang_sessions = []
    for file in os.listdir(sessions_dir):
        if file.endswith('.db') and 'wareneingang' in file and 'aps_persistent_traffic_' in file:
            session_name = file.replace('aps_persistent_traffic_', '').replace('.db', '')
            wareneingang_sessions.append(session_name)
    
    print(f"   Gefundene Wareneingang-Sessions: {len(wareneingang_sessions)}")
    for session in wareneingang_sessions:
        print(f"   - {session}")
    
    # 2. Finde Auftrags-Sessions
    print("\n📤 2. Auftrags-Sessions analysieren:")
    auftrag_sessions = []
    for file in os.listdir(sessions_dir):
        if file.endswith('.db') and 'auftrag' in file and 'aps_persistent_traffic_' in file:
            session_name = file.replace('aps_persistent_traffic_', '').replace('.db', '')
            auftrag_sessions.append(session_name)
    
    print(f"   Gefundene Auftrags-Sessions: {len(auftrag_sessions)}")
    for session in auftrag_sessions:
        print(f"   - {session}")
    
    # 3. Analysiere Wareneingang Order-IDs
    print("\n🎯 3. Wareneingang Order-IDs:")
    wareneingang_order_ids = {}
    
    for session in wareneingang_sessions[:3]:  # Analysiere erste 3 Sessions
        db_path = os.path.join(sessions_dir, f"aps_persistent_traffic_{session}.db")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
                conn.close()
                
                # Finde Order-IDs in Wareneingang
                order_messages = df[df['topic'].str.contains('order', na=False)]
                
                for idx, row in order_messages.iterrows():
                    try:
                        payload = json.loads(row['payload'])
                        if 'orderId' in payload:
                            order_id = payload['orderId']
                            workpiece_id = payload.get('workpieceId', 'Unknown')
                            
                            wareneingang_order_ids[order_id] = {
                                'session': session,
                                'workpiece_id': workpiece_id,
                                'timestamp': row['timestamp'],
                                'topic': row['topic']
                            }
                            
                            print(f"   📋 {session}: Order-ID {order_id[:8]}... - Werkstück {workpiece_id}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ❌ Fehler bei {session}: {e}")
    
    print(f"   📊 Gefundene Wareneingang Order-IDs: {len(wareneingang_order_ids)}")
    
    # 4. Analysiere Auftrags Order-IDs
    print("\n🎯 4. Auftrags Order-IDs:")
    auftrag_order_ids = {}
    
    for session in auftrag_sessions[:3]:  # Analysiere erste 3 Sessions
        db_path = os.path.join(sessions_dir, f"aps_persistent_traffic_{session}.db")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
                conn.close()
                
                # Finde Order-IDs in Aufträgen
                order_messages = df[df['topic'].str.contains('order', na=False)]
                
                for idx, row in order_messages.iterrows():
                    try:
                        payload = json.loads(row['payload'])
                        if 'orderId' in payload:
                            order_id = payload['orderId']
                            workpiece_id = payload.get('workpieceId', 'Unknown')
                            
                            auftrag_order_ids[order_id] = {
                                'session': session,
                                'workpiece_id': workpiece_id,
                                'timestamp': row['timestamp'],
                                'topic': row['topic']
                            }
                            
                            print(f"   📋 {session}: Order-ID {order_id[:8]}... - Werkstück {workpiece_id}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ❌ Fehler bei {session}: {e}")
    
    print(f"   📊 Gefundene Auftrags Order-IDs: {len(auftrag_order_ids)}")
    
    # 5. Prüfe auf Wiederverwendung
    print("\n🔄 5. Order-ID Wiederverwendung Analyse:")
    
    reused_order_ids = set(wareneingang_order_ids.keys()) & set(auftrag_order_ids.keys())
    
    if reused_order_ids:
        print(f"   ✅ Wiederverwendete Order-IDs gefunden: {len(reused_order_ids)}")
        for order_id in reused_order_ids:
            wareneingang_info = wareneingang_order_ids[order_id]
            auftrag_info = auftrag_order_ids[order_id]
            
            print(f"   🔄 Order-ID {order_id[:8]}...:")
            print(f"      📥 Wareneingang: {wareneingang_info['session']} - {wareneingang_info['workpiece_id']}")
            print(f"      📤 Auftrag: {auftrag_info['session']} - {auftrag_info['workpiece_id']}")
    else:
        print("   ❌ Keine wiederverwendeten Order-IDs gefunden")
    
    # 6. Analysiere HBW Storage
    print("\n🏗️ 6. HBW Storage Analyse:")
    
    # Analysiere eine Wareneingang-Session für HBW Storage
    if wareneingang_sessions:
        sample_session = wareneingang_sessions[0]
        db_path = os.path.join(sessions_dir, f"aps_persistent_traffic_{sample_session}.db")
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
                conn.close()
                
                # HBW Messages
                hbw_messages = df[df['topic'].str.contains('SVR3QA0022', na=False)]
                
                print(f"   📊 HBW Nachrichten in {sample_session}: {len(hbw_messages)}")
                
                # HBW State Messages
                hbw_state = hbw_messages[hbw_messages['topic'].str.contains('/state', na=False)]
                
                for idx, row in hbw_state.iterrows():
                    try:
                        payload = json.loads(row['payload'])
                        if 'loads' in payload:
                            print(f"   📦 HBW Loads: {payload['loads']}")
                            
                            # Prüfe ob Order-IDs in HBW Loads gespeichert sind
                            for load in payload['loads']:
                                if 'orderId' in load:
                                    print(f"      ✅ Order-ID in HBW gespeichert: {load['orderId']}")
                                else:
                                    print(f"      ❌ Keine Order-ID in HBW Load: {load}")
                    except:
                        pass
                        
            except Exception as e:
                print(f"   ❌ Fehler bei HBW Analyse: {e}")
    
    # 7. Analysiere Werkstück-IDs
    print("\n🏷️ 7. Werkstück-ID Analyse:")
    
    wareneingang_workpieces = set()
    for order_info in wareneingang_order_ids.values():
        wareneingang_workpieces.add(order_info['workpiece_id'])
    
    auftrag_workpieces = set()
    for order_info in auftrag_order_ids.values():
        auftrag_workpieces.add(order_info['workpiece_id'])
    
    shared_workpieces = wareneingang_workpieces & auftrag_workpieces
    
    print(f"   📥 Wareneingang Werkstücke: {len(wareneingang_workpieces)}")
    print(f"   📤 Auftrag Werkstücke: {len(auftrag_workpieces)}")
    print(f"   🔄 Gemeinsame Werkstücke: {len(shared_workpieces)}")
    
    if shared_workpieces:
        print("   ✅ Werkstücke werden wiederverwendet:")
        for workpiece in shared_workpieces:
            print(f"      - {workpiece}")
    else:
        print("   ❌ Keine gemeinsamen Werkstücke gefunden")
    
    # 8. Zusammenfassung
    print("\n📊 ZUSAMMENFASSUNG:")
    print("=" * 80)
    
    print(f"📥 Wareneingang Order-IDs: {len(wareneingang_order_ids)}")
    print(f"📤 Auftrags Order-IDs: {len(auftrag_order_ids)}")
    print(f"🔄 Wiederverwendete Order-IDs: {len(reused_order_ids)}")
    print(f"🏷️ Gemeinsame Werkstücke: {len(shared_workpieces)}")
    
    if reused_order_ids:
        print("\n✅ ERGEBNIS: Order-IDs werden zwischen Wareneingang und Aufträgen wiederverwendet!")
        print("   📋 Jede Order-ID wird nur einmal vergeben und für das gesamte Werkstück-Lebenszyklus verwendet")
    else:
        print("\n❌ ERGEBNIS: Order-IDs werden NICHT wiederverwendet!")
        print("   📋 Jeder Auftrag erhält eine neue Order-ID, unabhängig vom Wareneingang")
    
    if shared_workpieces:
        print("   🏷️ Werkstück-IDs werden zwischen Wareneingang und Aufträgen verknüpft")
    else:
        print("   🏷️ Keine Verknüpfung über Werkstück-IDs nachweisbar")

def main():
    """Hauptfunktion"""
    analyze_order_id_reuse()

if __name__ == "__main__":
    main()
