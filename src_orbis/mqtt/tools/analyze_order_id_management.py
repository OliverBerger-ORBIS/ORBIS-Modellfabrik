#!/usr/bin/env python3
"""
Order-ID und Action-ID Management Analyse

Analysiert wer die Order-IDs und Action-IDs vergibt und wie sie verwendet werden.
"""

import sqlite3
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Any

def analyze_order_id_management(session_name: str = "auftrag-B1B2B3"):
    """Analysiert Order-ID und Action-ID Management"""
    
    db_path = f"mqtt-data/sessions/aps_persistent_traffic_{session_name}.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Session {session_name} nicht gefunden")
        return
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM mqtt_messages ORDER BY timestamp", conn)
    conn.close()
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"🔍 Analysiere Order-ID Management für Session: {session_name}")
    print("=" * 60)
    
    # 1. Browser Order Trigger (Dashboard)
    print("\n🎯 1. Browser Order Trigger (Dashboard):")
    browser_orders = df[df['topic'] == '/j1/txt/1/f/o/order']
    
    for idx, row in browser_orders.iterrows():
        try:
            payload = json.loads(row['payload'])
            print(f"   📋 {row['timestamp']}: {payload}")
            
            # Prüfe ob Order-ID im Trigger enthalten ist
            if 'orderId' in payload:
                print(f"      ✅ Order-ID im Trigger: {payload['orderId']}")
            else:
                print(f"      ❌ Keine Order-ID im Trigger")
                
        except Exception as e:
            print(f"   ❌ Fehler beim Parsen: {e}")
    
    # 2. CCU Order Management
    print("\n🎛️ 2. CCU Order Management:")
    ccu_orders = df[df['topic'].str.contains('ccu/order', na=False)]
    
    order_ids = set()
    for idx, row in ccu_orders.iterrows():
        try:
            payload = json.loads(row['payload'])
            if 'orderId' in payload:
                order_ids.add(payload['orderId'])
                print(f"   📋 {row['timestamp']}: Order-ID {payload['orderId'][:8]}...")
        except:
            pass
    
    print(f"   📊 Gefundene Order-IDs: {len(order_ids)}")
    for order_id in order_ids:
        print(f"      - {order_id}")
    
    # 3. Module Commands mit Order-ID
    print("\n🏭 3. Module Commands mit Order-ID:")
    module_orders = df[df['topic'].str.contains('module/v1/ff/.*/order', na=False)]
    
    for idx, row in module_orders.iterrows():
        try:
            payload = json.loads(row['payload'])
            if 'orderId' in payload:
                module = row['topic'].split('/')[3]
                action_id = payload.get('action', {}).get('id', 'Unknown')
                command = payload.get('action', {}).get('command', 'Unknown')
                
                print(f"   🔧 {row['timestamp']}: {module} - Order-ID: {payload['orderId'][:8]}... - Action-ID: {action_id[:8]}... - Command: {command}")
        except:
            pass
    
    # 4. Action-ID Analyse
    print("\n🔧 4. Action-ID Analyse:")
    action_ids = set()
    
    for idx, row in module_orders.iterrows():
        try:
            payload = json.loads(row['payload'])
            if 'action' in payload and 'id' in payload['action']:
                action_ids.add(payload['action']['id'])
                module = row['topic'].split('/')[3]
                command = payload['action'].get('command', 'Unknown')
                print(f"   🔧 {module} - Action-ID: {payload['action']['id']} - Command: {command}")
        except:
            pass
    
    print(f"   📊 Gefundene Action-IDs: {len(action_ids)}")
    
    # 5. Dependent Actions
    print("\n🔗 5. Dependent Actions Analyse:")
    dependent_actions = df[df['payload'].str.contains('dependentAction', na=False)]
    
    for idx, row in dependent_actions.iterrows():
        try:
            payload = json.loads(row['payload'])
            if 'dependentAction' in payload:
                print(f"   🔗 {row['timestamp']}: Dependent Action gefunden")
                print(f"      Payload: {payload}")
        except:
            pass
    
    # 6. Order Completion
    print("\n✅ 6. Order Completion:")
    completed_orders = df[df['topic'].str.contains('ccu/order/completed', na=False)]
    
    for idx, row in completed_orders.iterrows():
        try:
            payload = json.loads(row['payload'])
            if 'orderId' in payload:
                print(f"   ✅ {row['timestamp']}: Order {payload['orderId'][:8]}... completed")
        except:
            pass
    
    # 7. Zusammenfassung
    print("\n📊 ZUSAMMENFASSUNG:")
    print("=" * 60)
    
    print(f"🎯 Browser Orders: {len(browser_orders)}")
    print(f"🎛️  CCU Orders: {len(ccu_orders)}")
    print(f"🏭 Module Commands: {len(module_orders)}")
    print(f"📋 Unique Order-IDs: {len(order_ids)}")
    print(f"🔧 Unique Action-IDs: {len(action_ids)}")
    print(f"✅ Completed Orders: {len(completed_orders)}")
    
    # 8. Order-ID Vergabe Analyse
    print("\n🔍 Order-ID Vergabe Analyse:")
    
    # Prüfe ob Order-IDs im Browser Trigger enthalten sind
    browser_order_ids = []
    for idx, row in browser_orders.iterrows():
        try:
            payload = json.loads(row['payload'])
            if 'orderId' in payload:
                browser_order_ids.append(payload['orderId'])
        except:
            pass
    
    if browser_order_ids:
        print("   ✅ Order-IDs werden im Browser Trigger vergeben")
        for order_id in browser_order_ids:
            print(f"      - {order_id}")
    else:
        print("   ❌ Order-IDs werden NICHT im Browser Trigger vergeben")
        print("   🎛️  Order-IDs werden von der CCU vergeben")
    
    # 9. Action-ID Vergabe Analyse
    print("\n🔧 Action-ID Vergabe Analyse:")
    
    # Prüfe ob Action-IDs im Browser Trigger enthalten sind
    browser_action_ids = []
    for idx, row in browser_orders.iterrows():
        try:
            payload = json.loads(row['payload'])
            if 'actionId' in payload:
                browser_action_ids.append(payload['actionId'])
        except:
            pass
    
    if browser_action_ids:
        print("   ✅ Action-IDs werden im Browser Trigger vergeben")
        for action_id in browser_action_ids:
            print(f"      - {action_id}")
    else:
        print("   ❌ Action-IDs werden NICHT im Browser Trigger vergeben")
        print("   🎛️  Action-IDs werden von der CCU vergeben")

def main():
    """Hauptfunktion"""
    # Analysiere Auftrags-Session
    analyze_order_id_management("auftrag-B1B2B3")
    
    print("\n" + "=" * 60)
    print("🔍 Analysiere auch Wareneingang-Session zum Vergleich:")
    print("=" * 60)
    
    # Analysiere Wareneingang-Session zum Vergleich
    analyze_order_id_management("wareneingang-blau_1")

if __name__ == "__main__":
    main()
