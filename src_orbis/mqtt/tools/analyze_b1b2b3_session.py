#!/usr/bin/env python3
"""
Analyse der Session 'auftrag-B1B2B3'
Extrahiert NFC-Codes und vergleicht sie mit unserem Mapping
"""

import sqlite3
import pandas as pd
import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import NFC mapping directly
import sys
sys.path.append(str(project_root / 'src_orbis' / 'mqtt' / 'tools'))

try:
    from nfc_workpiece_mapping import NFC_WORKPIECE_MAPPING
except ImportError:
    # Fallback: define mapping directly
    NFC_WORKPIECE_MAPPING = {
        # 🔵 Blaue Werkstücke (8/8)
        "B1": "04a189ca341290",  # ✅ Eingelagert (Session nfc-lesen-blau)
        "B2": "048989ca341290",  # ✅ Eingelagert (Session nfc-lesen-blau)
        "B3": "047389ca341291",  # ✅ Eingelagert (Session nfc-lesen-blau)
        "B4": "040c89ca341291",  # ✅ Gefunden (Session nfc-lesen-blau)
        "B5": "04a289ca341290",  # ✅ Gefunden (Session nfc-lesen-blau)
        "B6": "04c489ca341290",  # ✅ Gefunden (Session nfc-lesen-blau)
        "B7": "048089ca341290",  # ✅ Gefunden (Session nfc-lesen-blau)
        "B8": "042c88ca341291",  # ✅ Gefunden (Session nfc-lesen-blau)
    }


def analyze_b1b2b3_session():
    """Analysiert die Session auftrag-B1B2B3"""
    
    # Session database path
    session_db = Path('mqtt-data/sessions/aps_persistent_traffic_auftrag-B1B2B3.db')
    
    if not session_db.exists():
        print(f"❌ Session nicht gefunden: {session_db}")
        return
    
    print("🔍 Analysiere Session: auftrag-B1B2B3")
    print("=" * 60)
    
    # Connect to database
    conn = sqlite3.connect(session_db)
    
    # Get message count
    count = pd.read_sql_query('SELECT COUNT(*) as count FROM mqtt_messages', conn)
    print(f"📊 Nachrichten: {count.iloc[0]['count']:,}")
    
    # 1. Suche nach HBW State Messages mit loadId (NFC-Codes)
    print("\n🔍 1. Suche nach HBW State Messages mit loadId (NFC-Codes)...")
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT topic, payload, timestamp 
        FROM mqtt_messages 
        WHERE topic = 'module/v1/ff/SVR3QA0022/state' AND payload LIKE "%loadId%"
        ORDER BY timestamp
    ''')
    
    hbw_state_messages = cursor.fetchall()
    print(f"   Gefunden: {len(hbw_state_messages)} HBW State Messages mit loadId")
    
    # Extract NFC codes from HBW state messages
    nfc_codes_found = []
    for topic, payload, timestamp in hbw_state_messages:
        try:
            data = json.loads(payload)
            if 'loads' in data:
                for load in data['loads']:
                    if isinstance(load, dict) and 'loadId' in load:
                        nfc_code = load['loadId']
                        load_type = load.get('loadType', 'UNKNOWN')
                        load_position = load.get('loadPosition', 'N/A')
                        nfc_codes_found.append({
                            'nfc_code': nfc_code,
                            'timestamp': timestamp,
                            'topic': topic,
                            'load_type': load_type,
                            'load_position': load_position
                        })
        except json.JSONDecodeError:
            continue
    
    print(f"   NFC-Codes extrahiert: {len(nfc_codes_found)}")
    
    # 2. Suche nach ccu/order/completed Messages
    print("\n🔍 2. Suche nach ccu/order/completed Messages...")
    
    cursor.execute('''
        SELECT topic, payload, timestamp 
        FROM mqtt_messages 
        WHERE topic = 'ccu/order/completed'
        ORDER BY timestamp
    ''')
    
    completed_orders = cursor.fetchall()
    print(f"   Gefunden: {len(completed_orders)} completed orders")
    
    # Extract workpiece IDs from completed orders
    completed_workpieces = []
    for topic, payload, timestamp in completed_orders:
        try:
            data = json.loads(payload)
            if 'workpieceId' in data:
                completed_workpieces.append({
                    'workpieceId': data['workpieceId'],
                    'timestamp': timestamp,
                    'orderId': data.get('orderId', 'N/A')
                })
        except json.JSONDecodeError:
            continue
    
    print(f"   Werkstück-IDs extrahiert: {len(completed_workpieces)}")
    
    # 3. Suche nach ccu/order/request Messages
    print("\n🔍 3. Suche nach ccu/order/request Messages...")
    
    cursor.execute('''
        SELECT topic, payload, timestamp 
        FROM mqtt_messages 
        WHERE topic = 'ccu/order/request'
        ORDER BY timestamp
    ''')
    
    requested_orders = cursor.fetchall()
    print(f"   Gefunden: {len(requested_orders)} requested orders")
    
    # Extract workpiece IDs from requested orders
    requested_workpieces = []
    for topic, payload, timestamp in requested_orders:
        try:
            data = json.loads(payload)
            if 'workpieceId' in data:
                requested_workpieces.append({
                    'workpieceId': data['workpieceId'],
                    'timestamp': timestamp,
                    'orderId': data.get('orderId', 'N/A')
                })
        except json.JSONDecodeError:
            continue
    
    print(f"   Werkstück-IDs extrahiert: {len(requested_workpieces)}")
    
    # 4. Analyse der gefundenen NFC-Codes
    print("\n🔍 4. Analyse der gefundenen NFC-Codes...")
    
    if nfc_codes_found:
        print("   Gefundene NFC-Codes:")
        unique_nfc_codes = set()
        for item in nfc_codes_found:
            nfc_code = item['nfc_code']
            unique_nfc_codes.add(nfc_code)
            load_type = item.get('load_type', 'UNKNOWN')
            load_position = item.get('load_position', 'N/A')
            print(f"     📱 {nfc_code} ({load_type}, Pos: {load_position}) - {item['timestamp']}")
        
        print(f"\n   Eindeutige NFC-Codes: {len(unique_nfc_codes)}")
        
        # 5. Vergleich mit unserem Mapping
        print("\n🔍 5. Vergleich mit unserem NFC-Mapping...")
        
        # Get our blue workpiece codes
        our_blue_codes = []
        for workpiece_id, nfc_code in NFC_WORKPIECE_MAPPING.items():
            if workpiece_id.startswith('B'):
                our_blue_codes.append(nfc_code)
        
        print(f"   Unser Mapping - Blaue Werkstücke:")
        for i, code in enumerate(our_blue_codes, 1):
            print(f"     B{i}: {code}")
        
        print(f"\n   Gefundene NFC-Codes in Session:")
        for code in unique_nfc_codes:
            print(f"     📱 {code}")
        
        # Check matches
        matches = []
        for session_code in unique_nfc_codes:
            for workpiece_id, mapped_code in NFC_WORKPIECE_MAPPING.items():
                if mapped_code == session_code:
                    matches.append((workpiece_id, session_code))
        
        print(f"\n   ✅ Übereinstimmungen:")
        if matches:
            for workpiece_id, nfc_code in matches:
                print(f"     {workpiece_id} ↔ {nfc_code}")
        else:
            print("     ❌ Keine Übereinstimmungen gefunden!")
        
        # Check for missing codes
        session_codes_set = set(unique_nfc_codes)
        our_blue_codes_set = set(our_blue_codes)
        
        missing_in_session = our_blue_codes_set - session_codes_set
        missing_in_mapping = session_codes_set - our_blue_codes_set
        
        if missing_in_session:
            print(f"\n   ⚠️  In Session fehlende Codes (aus unserem Mapping):")
            for code in missing_in_session:
                for workpiece_id, mapped_code in NFC_WORKPIECE_MAPPING.items():
                    if mapped_code == code:
                        print(f"     {workpiece_id}: {code}")
        
        if missing_in_mapping:
            print(f"\n   ⚠️  In Mapping fehlende Codes (aus Session):")
            for code in missing_in_mapping:
                print(f"     📱 {code}")
    
    # 6. Analyse der Werkstück-Reihenfolge
    print("\n🔍 6. Analyse der Werkstück-Reihenfolge...")
    
    if completed_workpieces:
        print("   Completed Orders (Reihenfolge):")
        for i, item in enumerate(completed_workpieces, 1):
            print(f"     {i}. {item['workpieceId']} (Order: {item['orderId']}) - {item['timestamp']}")
    
    if requested_workpieces:
        print("\n   Requested Orders (Reihenfolge):")
        for i, item in enumerate(requested_workpieces, 1):
            print(f"     {i}. {item['workpieceId']} (Order: {item['orderId']}) - {item['timestamp']}")
    
    # 7. Timeline-Analyse
    print("\n🔍 7. Timeline-Analyse...")
    
    if nfc_codes_found:
        print("   NFC-Lesungen Timeline:")
        for i, item in enumerate(nfc_codes_found, 1):
            load_type = item.get('load_type', 'UNKNOWN')
            load_position = item.get('load_position', 'N/A')
            print(f"     {i}. {item['timestamp']} - {item['nfc_code']} ({load_type}, Pos: {load_position})")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Analyse abgeschlossen!")


if __name__ == "__main__":
    analyze_b1b2b3_session()
