#!/usr/bin/env python3
"""
Findet die erste gültige OrderID in einer Session und listet alle Messages mit dieser OrderID auf.

Ziel: Welches Topic ist das erste mit einer "gültigen orderID"?

Gültige OrderIDs:
- UUID-Format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
- Mehr als 10 Messages (vollständige Order-Sequenzen)
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict


def load_session_from_db(db_path: Path) -> List[Dict[str, Any]]:
    """Lädt Messages aus SQLite-Session-Datei"""
    messages = []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Messages laden (sortiert nach timestamp und id)
        cursor.execute("""
            SELECT topic, payload, timestamp, id 
            FROM mqtt_messages 
            ORDER BY timestamp, id
        """)
        
        for row in cursor.fetchall():
            topic, payload, timestamp, msg_id = row
            messages.append({
                'topic': topic,
                'payload': payload,
                'timestamp': timestamp,
                'id': msg_id
            })
        
        conn.close()
        return messages
    except Exception as e:
        print(f"❌ Fehler beim Laden der DB: {e}")
        return []


def load_session_from_log(log_path: Path) -> List[Dict[str, Any]]:
    """Lädt Messages aus Log-Datei"""
    messages = []
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                # Format: timestamp|topic|payload
                parts = line.split('|', 2)
                if len(parts) >= 3:
                    timestamp, topic, payload = parts
                    messages.append({
                        'topic': topic.strip(),
                        'payload': payload.strip(),
                        'timestamp': timestamp.strip(),
                        'sequence': line_num
                    })
        
        return messages
    except Exception as e:
        print(f"❌ Fehler beim Laden der Log-Datei: {e}")
        return []


def extract_payload_json(payload_str: str) -> Optional[Dict[str, Any]]:
    """Extrahiert JSON aus Payload-String"""
    if not payload_str:
        return None
    
    try:
        # Wenn bereits JSON-String
        if isinstance(payload_str, str):
            return json.loads(payload_str)
        return payload_str
    except json.JSONDecodeError:
        return None


def is_uuid(value: str) -> bool:
    """Prüft ob ein String ein gültiges UUID-Format hat"""
    if not isinstance(value, str):
        return False
    
    # UUID-Pattern: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, value, re.IGNORECASE))


def is_valid_order_id(order_id: Any) -> bool:
    """
    Prüft ob OrderID gültig ist.
    
    Gültig = UUID-Format (Test-IDs wie '1001' sind NICHT gültig)
    """
    if order_id is None:
        return False
    if order_id == "":
        return False
    if order_id == 0:
        return False
    if isinstance(order_id, str) and order_id.strip() == "":
        return False
    
    # UUID-Validierung
    return is_uuid(str(order_id))


def find_first_order_id(messages: List[Dict[str, Any]]) -> Optional[tuple]:
    """
    Findet die erste gültige OrderID in den Messages.
    
    Returns: (order_id, message_with_order_id) oder None
    """
    for idx, msg in enumerate(messages):
        payload = extract_payload_json(msg.get('payload', ''))
        
        if payload and isinstance(payload, dict):
            order_id = payload.get('orderId')
            
            if is_valid_order_id(order_id):
                print(f"\n✅ Erste gültige OrderID gefunden bei Message #{idx + 1}")
                print(f"   OrderID: {order_id}")
                print(f"   Topic: {msg['topic']}")
                print(f"   Timestamp: {msg.get('timestamp', 'N/A')}")
                return (order_id, msg, idx + 1)
    
    return None


def find_all_order_sequences(messages: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Findet alle OrderID-Sequenzen in den Messages.
    
    Returns: Dict[order_id -> List[messages]]
    """
    order_sequences = defaultdict(list)
    
    for idx, msg in enumerate(messages):
        payload = extract_payload_json(msg.get('payload', ''))
        
        if payload and isinstance(payload, dict):
            order_id = payload.get('orderId')
            
            if is_valid_order_id(order_id):
                msg_copy = msg.copy()
                msg_copy['message_number'] = idx + 1
                msg_copy['payload_parsed'] = payload
                order_sequences[order_id].append(msg_copy)
    
    return dict(order_sequences)


def find_all_messages_with_order_id(messages: List[Dict[str, Any]], target_order_id: str) -> List[Dict[str, Any]]:
    """Findet alle Messages mit der angegebenen OrderID"""
    matching_messages = []
    
    for idx, msg in enumerate(messages):
        payload = extract_payload_json(msg.get('payload', ''))
        
        if payload and isinstance(payload, dict):
            order_id = payload.get('orderId')
            
            if order_id == target_order_id:
                msg_copy = msg.copy()
                msg_copy['message_number'] = idx + 1
                msg_copy['payload_parsed'] = payload
                matching_messages.append(msg_copy)
    
    return matching_messages


def analyze_session(session_path: Path):
    """Analysiert eine Session und findet alle OrderID-Sequenzen"""
    print(f"\n{'='*80}")
    print(f"📊 ANALYSE: {session_path.name}")
    print(f"{'='*80}")
    
    # Session laden
    if session_path.suffix == '.db':
        messages = load_session_from_db(session_path)
    elif session_path.suffix == '.log':
        messages = load_session_from_log(session_path)
    else:
        print(f"❌ Unbekanntes Format: {session_path.suffix}")
        return
    
    if not messages:
        print("❌ Keine Messages gefunden")
        return
    
    print(f"📁 Gesamt Messages: {len(messages)}")
    
    # Alle OrderID-Sequenzen finden
    order_sequences = find_all_order_sequences(messages)
    
    if not order_sequences:
        print("\n❌ Keine gültigen OrderIDs (UUIDs) in dieser Session gefunden")
        return
    
    print(f"\n🔍 Gefundene OrderID-Sequenzen: {len(order_sequences)}")
    
    # Nach Anzahl Messages sortieren
    sorted_orders = sorted(order_sequences.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Übersicht aller OrderIDs
    print(f"\n{'='*80}")
    print("ORDER-SEQUENZEN ÜBERSICHT (sortiert nach Message-Count)")
    print(f"{'='*80}")
    
    for idx, (order_id, msgs) in enumerate(sorted_orders, 1):
        first_msg = msgs[0]
        marker = "⭐" if len(msgs) > 10 else "  "
        print(f"{marker} {idx}. OrderID: {order_id}")
        print(f"     Messages: {len(msgs)}")
        print(f"     Erste Message: #{first_msg['message_number']} - {first_msg['topic']}")
        print(f"     Timestamp: {first_msg.get('timestamp', 'N/A')}")
        print()
    
    # Primäre OrderID (höchste Message-Count)
    primary_order_id, primary_messages = sorted_orders[0]
    
    print(f"{'='*80}")
    print("PRIMÄRE ORDER-ID (höchste Message-Count)")
    print(f"{'='*80}")
    print(f"OrderID: {primary_order_id}")
    print(f"Messages: {len(primary_messages)}")
    
    first_msg = primary_messages[0]
    print(f"Erste Message: #{first_msg['message_number']}")
    print(f"Erstes Topic: {first_msg['topic']}")
    print(f"Timestamp: {first_msg.get('timestamp', 'N/A')}")
    
    # OrderIDs mit >10 Messages hervorheben
    significant_orders = [(oid, msgs) for oid, msgs in sorted_orders if len(msgs) > 10]
    
    if significant_orders:
        print(f"\n{'='*80}")
        print(f"SIGNIFIKANTE ORDERS (>10 Messages) - vermutlich 'echte' Orders")
        print(f"{'='*80}")
        
        for order_id, msgs in significant_orders:
            first_msg = msgs[0]
            print(f"\n✅ OrderID: {order_id}")
            print(f"   Messages: {len(msgs)}")
            print(f"   Erste Message: #{first_msg['message_number']} - {first_msg['topic']}")
            
            # Topic-Verteilung
            topic_counts = {}
            for msg in msgs:
                topic = msg['topic']
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            print(f"   Topic-Verteilung:")
            for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"      - {topic}: {count} Messages")
    
    # Detaillierte Ausgabe der primären Order
    print(f"\n{'='*80}")
    print(f"DETAILLIERTE ANALYSE: Primäre OrderID")
    print(f"{'='*80}")
    
    # Topic-Verteilung
    print(f"\n📊 Topic-Verteilung für OrderID {primary_order_id}:")
    topic_counts = {}
    for msg in primary_messages:
        topic = msg['topic']
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {topic}: {count} Messages")
    
    # Erste 10 Messages
    print(f"\n📋 Erste 10 Messages mit OrderID {primary_order_id}:")
    print(f"{'-'*80}")
    for idx, msg in enumerate(primary_messages[:10], 1):
        print(f"\n#{msg['message_number']} - {msg['topic']}")
        print(f"   Timestamp: {msg.get('timestamp', 'N/A')}")
        
        # Wichtige Payload-Felder anzeigen
        payload = msg.get('payload_parsed', {})
        if payload:
            # OrderID
            if 'orderId' in payload:
                print(f"   OrderID: {payload['orderId']}")
            # WorkpieceId
            if 'workpieceId' in payload:
                print(f"   WorkpieceId: {payload['workpieceId']}")
            # Status/State
            if 'status' in payload:
                print(f"   Status: {payload['status']}")
            if 'state' in payload:
                print(f"   State: {payload['state']}")
            # Command
            if 'command' in payload:
                print(f"   Command: {payload['command']}")


def main():
    """Hauptfunktion - analysiert Sessions"""
    
    # Session-Verzeichnis
    sessions_dir = Path("/Users/oliver/Projects/ORBIS-Modellfabrik/data/omf-data/sessions")
    
    if not sessions_dir.exists():
        print(f"❌ Sessions-Verzeichnis nicht gefunden: {sessions_dir}")
        return
    
    # Suche nach auftrag_blau Sessions
    session_patterns = [
        "auftrag-blau*.db",
        "auftrag-rot*.db",
        "auftrag-weiss*.db"
    ]
    
    found_sessions = []
    for pattern in session_patterns:
        found_sessions.extend(sessions_dir.glob(pattern))
    
    if not found_sessions:
        print("❌ Keine auftrag-*.db Sessions gefunden")
        return
    
    print(f"\n🔍 Gefundene Sessions: {len(found_sessions)}")
    for session in sorted(found_sessions):
        print(f"   - {session.name}")
    
    # Analysiere jede Session
    for session in sorted(found_sessions):
        analyze_session(session)
        print("\n")


if __name__ == "__main__":
    main()

