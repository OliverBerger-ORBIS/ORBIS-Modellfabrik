#!/usr/bin/env python3
"""
DPS Session Data Analyzer

Analysiert Session-Log-Dateien und extrahiert DPS-relevante Topics
für eine umfassende DPS-Auswertung.
Fokus: STORAGE-ORDER (Farberkennung, NFC-Code) und PRODUCTION-ORDER (NFC-Auslesen)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

# DPS Serial ID
DPS_SERIAL = "SVR4H73275"

# DPS-relevante Topic-Patterns
DPS_TOPIC_PATTERNS = [
    f"module/v1/ff/{DPS_SERIAL}/",  # Alle DPS Topics
    f"module/v1/ff/NodeRed/{DPS_SERIAL}/",  # NodeRed enriched DPS Topics
    "ccu/order/",  # CCU Orders (relevant für DPS-Interaktionen)
    "ccu/state/calibration/",  # CCU Calibration State (enthält DPS)
    "ccu/set/calibration",  # CCU Calibration Commands
    "ccu/pairing/state",  # CCU Pairing State (enthält DPS Info)
    "/j1/txt/1/",  # TXT Topics (DPS hat TXT-Controller)
]

# Spezifische DPS-Topics
DPS_TOPICS = {
    f"module/v1/ff/{DPS_SERIAL}/connection": "DPS Connection Status",
    f"module/v1/ff/{DPS_SERIAL}/state": "DPS State Updates",
    f"module/v1/ff/{DPS_SERIAL}/order": "DPS Order Commands",
    f"module/v1/ff/{DPS_SERIAL}/instantAction": "DPS Instant Actions",
    f"module/v1/ff/{DPS_SERIAL}/factsheet": "DPS Factsheet",
    f"module/v1/ff/NodeRed/{DPS_SERIAL}/connection": "DPS Connection (NodeRed enriched)",
    f"module/v1/ff/NodeRed/{DPS_SERIAL}/state": "DPS State (NodeRed enriched)",
    f"module/v1/ff/NodeRed/{DPS_SERIAL}/factsheet": "DPS Factsheet (NodeRed)",
}

# Weitere relevante Topics für DPS-Auswertung
RELATED_TOPICS = {
    "ccu/order/active": "CCU Active Order",
    "ccu/order/completed": "CCU Completed Order",
    "ccu/order/request": "CCU Order Request",
    f"ccu/state/calibration/{DPS_SERIAL}": "DPS Calibration State",
    "ccu/set/calibration": "CCU Calibration Commands",
    "ccu/pairing/state": "CCU Pairing State (enthält DPS Info)",
    "/j1/txt/1/f/i/stock": "DPS Stock Information",
    "/j1/txt/1/i/cam": "DPS Camera Data",
}

# DPS-spezifische Commands
DPS_COMMANDS = ["PICK", "DROP", "INPUT_RGB", "RGB_NFC"]


def load_session_log(log_file: Path) -> List[Dict[str, Any]]:
    """Lädt eine Session-Log-Datei und gibt Messages zurück"""
    messages = []
    
    try:
        with open(log_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    if "timestamp" in data and "topic" in data and "payload" in data:
                        messages.append(data)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Zeile {line_num} konnte nicht geparst werden: {e}", file=sys.stderr)
                    continue
    except Exception as e:
        print(f"❌ Fehler beim Laden der Datei {log_file}: {e}", file=sys.stderr)
        return []
    
    return messages


def is_dps_relevant(topic: str) -> bool:
    """Prüft ob ein Topic DPS-relevant ist"""
    # Direkte DPS-Topics
    if DPS_SERIAL in topic:
        return True
    
    # CCU Orders (relevant für DPS-Interaktionen)
    if topic.startswith("ccu/order/"):
        return True
    
    # CCU Calibration (enthält DPS)
    if topic.startswith("ccu/state/calibration/") and DPS_SERIAL in topic:
        return True
    if topic == "ccu/set/calibration":
        return True
    
    # CCU Pairing State (enthält DPS Info)
    if topic == "ccu/pairing/state":
        return True
    
    # TXT Topics (DPS hat TXT-Controller)
    if topic.startswith("/j1/txt/1/"):
        return True
    
    return False


def categorize_topic(topic: str) -> str:
    """Kategorisiert ein Topic"""
    if f"/{DPS_SERIAL}/" in topic:
        if "/connection" in topic:
            return "dps_connection"
        elif "/state" in topic:
            return "dps_state"
        elif "/order" in topic:
            return "dps_order"
        elif "/instantAction" in topic:
            return "dps_instant_action"
        elif "/factsheet" in topic:
            return "dps_factsheet"
        else:
            return "dps_other"
    elif topic.startswith("ccu/order/"):
        if "/active" in topic:
            return "ccu_order_active"
        elif "/completed" in topic:
            return "ccu_order_completed"
        elif "/request" in topic:
            return "ccu_order_request"
        else:
            return "ccu_order_other"
    elif topic.startswith("ccu/state/calibration/"):
        return "ccu_calibration_state"
    elif topic == "ccu/set/calibration":
        return "ccu_calibration_set"
    elif topic == "ccu/pairing/state":
        return "ccu_pairing_state"
    elif topic.startswith("/j1/txt/1/"):
        return "txt_controller"
    else:
        return "other"


def extract_order_context(messages: List[Dict[str, Any]], order_type: str) -> List[Dict[str, Any]]:
    """
    Extrahiert Messages im Kontext von STORAGE-ORDER oder PRODUCTION-ORDER
    
    Args:
        messages: Alle Messages
        order_type: "STORAGE" oder "PRODUCTION"
    
    Returns:
        Liste von Messages im Kontext der Order
    """
    context_messages = []
    
    for i, msg in enumerate(messages):
        try:
            payload = json.loads(msg["payload"]) if isinstance(msg["payload"], str) else msg["payload"]
            
            # Prüfe ob es eine Order-Message ist
            if isinstance(payload, dict):
                # CCU Order Messages
                if "orderType" in payload and payload["orderType"] == order_type:
                    # Sammle Messages vor und nach dieser Order
                    # Vor: 50 Messages, Nach: 100 Messages
                    start_idx = max(0, i - 50)
                    end_idx = min(len(messages), i + 100)
                    
                    for j in range(start_idx, end_idx):
                        if is_dps_relevant(messages[j]["topic"]):
                            context_messages.append(messages[j])
                
                # Prüfe auch in Arrays (ccu/order/completed ist ein Array)
                elif isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict) and "orderType" in item and item["orderType"] == order_type:
                            start_idx = max(0, i - 50)
                            end_idx = min(len(messages), i + 100)
                            
                            for j in range(start_idx, end_idx):
                                if is_dps_relevant(messages[j]["topic"]):
                                    context_messages.append(messages[j])
                            break
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    
    # Entferne Duplikate (behalte erste Vorkommen)
    seen = set()
    unique_messages = []
    for msg in context_messages:
        msg_id = (msg["topic"], msg.get("timestamp", ""))
        if msg_id not in seen:
            seen.add(msg_id)
            unique_messages.append(msg)
    
    return unique_messages


def analyze_session(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analysiert eine Session und extrahiert DPS-relevante Informationen"""
    
    # Filtere DPS-relevante Messages
    dps_messages = [msg for msg in messages if is_dps_relevant(msg["topic"])]
    
    # Topic-Statistiken
    topic_counter = Counter(msg["topic"] for msg in dps_messages)
    topic_categories = defaultdict(list)
    
    for msg in dps_messages:
        category = categorize_topic(msg["topic"])
        topic_categories[category].append(msg)
    
    # Zeitbereich
    timestamps = [msg["timestamp"] for msg in dps_messages if "timestamp" in msg]
    start_time = min(timestamps) if timestamps else None
    end_time = max(timestamps) if timestamps else None
    
    # Payload-Analyse
    payload_stats = defaultdict(int)
    commands_found = Counter()
    
    for msg in dps_messages:
        try:
            payload = json.loads(msg["payload"]) if isinstance(msg["payload"], str) else msg["payload"]
            if isinstance(payload, dict):
                # Zähle wichtige Felder
                if "orderId" in payload:
                    payload_stats["has_orderId"] += 1
                if "actionState" in payload:
                    payload_stats["has_actionState"] += 1
                    # Extrahiere Command
                    action_state = payload.get("actionState", {})
                    if isinstance(action_state, dict) and "command" in action_state:
                        commands_found[action_state["command"]] += 1
                if "actionStates" in payload:
                    # Array von ActionStates
                    for action in payload.get("actionStates", []):
                        if isinstance(action, dict) and "command" in action:
                            commands_found[action["command"]] += 1
                if "workpieceId" in payload or (isinstance(payload, dict) and any("workpieceId" in str(v) for v in payload.values())):
                    payload_stats["has_workpieceId"] += 1
                if "type" in payload:
                    payload_stats["has_type"] += 1
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Extrahiere STORAGE-ORDER Kontext
    storage_order_context = extract_order_context(messages, "STORAGE")
    
    # Extrahiere PRODUCTION-ORDER Kontext
    production_order_context = extract_order_context(messages, "PRODUCTION")
    
    return {
        "total_messages": len(messages),
        "dps_relevant_messages": len(dps_messages),
        "start_time": start_time,
        "end_time": end_time,
        "topic_counts": dict(topic_counter),
        "topic_categories": {cat: len(msgs) for cat, msgs in topic_categories.items()},
        "payload_stats": dict(payload_stats),
        "commands_found": dict(commands_found),
        "storage_order_context_count": len(storage_order_context),
        "production_order_context_count": len(production_order_context),
        "messages": dps_messages,
        "storage_order_context": storage_order_context,
        "production_order_context": production_order_context,
    }


def save_dps_data(analysis: Dict[str, Any], output_dir: Path, session_name: str):
    """Speichert DPS-Daten in strukturiertem Format"""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Gesamt-Analyse (Metadata)
    metadata_file = output_dir / f"{session_name}_metadata.json"
    metadata = {
        "session_name": session_name,
        "analysis_timestamp": datetime.now().isoformat(),
        "dps_serial": DPS_SERIAL,
        "total_messages": analysis["total_messages"],
        "dps_relevant_messages": analysis["dps_relevant_messages"],
        "start_time": analysis["start_time"],
        "end_time": analysis["end_time"],
        "topic_counts": analysis["topic_counts"],
        "topic_categories": analysis["topic_categories"],
        "payload_stats": analysis["payload_stats"],
        "commands_found": analysis["commands_found"],
        "storage_order_context_count": analysis["storage_order_context_count"],
        "production_order_context_count": analysis["production_order_context_count"],
    }
    
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Metadata gespeichert: {metadata_file}")
    
    # 2. Nach Topic kategorisiert
    topic_categories = defaultdict(list)
    for msg in analysis["messages"]:
        category = categorize_topic(msg["topic"])
        topic_categories[category].append(msg)
    
    for category, msgs in topic_categories.items():
        category_file = output_dir / f"{session_name}_{category}.json"
        with open(category_file, "w", encoding="utf-8") as f:
            json.dump(msgs, f, indent=2, ensure_ascii=False)
        print(f"✅ {category}: {len(msgs)} Messages → {category_file}")
    
    # 3. Alle DPS-Messages (komplett)
    all_messages_file = output_dir / f"{session_name}_all_dps_messages.json"
    with open(all_messages_file, "w", encoding="utf-8") as f:
        json.dump(analysis["messages"], f, indent=2, ensure_ascii=False)
    print(f"✅ Alle DPS-Messages: {len(analysis['messages'])} → {all_messages_file}")
    
    # 4. STORAGE-ORDER Kontext (Farberkennung, NFC)
    if analysis["storage_order_context"]:
        storage_file = output_dir / f"{session_name}_storage_order_context.json"
        with open(storage_file, "w", encoding="utf-8") as f:
            json.dump(analysis["storage_order_context"], f, indent=2, ensure_ascii=False)
        print(f"✅ STORAGE-ORDER Kontext: {len(analysis['storage_order_context'])} Messages → {storage_file}")
    
    # 5. PRODUCTION-ORDER Kontext (NFC-Auslesen)
    if analysis["production_order_context"]:
        production_file = output_dir / f"{session_name}_production_order_context.json"
        with open(production_file, "w", encoding="utf-8") as f:
            json.dump(analysis["production_order_context"], f, indent=2, ensure_ascii=False)
        print(f"✅ PRODUCTION-ORDER Kontext: {len(analysis['production_order_context'])} Messages → {production_file}")


def main():
    parser = argparse.ArgumentParser(description="Analysiert Session-Daten für DPS-Auswertung")
    parser.add_argument("session_file", type=str, help="Pfad zur Session-Log-Datei")
    parser.add_argument("--output-dir", type=str, default="data/omf-data/dps-analysis",
                       help="Ausgabeverzeichnis (Standard: data/omf-data/dps-analysis)")
    parser.add_argument("--session-name", type=str, help="Session-Name (wird aus Dateiname extrahiert wenn nicht angegeben)")
    
    args = parser.parse_args()
    
    session_file = Path(args.session_file)
    if not session_file.exists():
        print(f"❌ Datei nicht gefunden: {session_file}", file=sys.stderr)
        sys.exit(1)
    
    # Session-Name extrahieren
    if args.session_name:
        session_name = args.session_name
    else:
        session_name = session_file.stem
    
    print(f"📊 Analysiere Session: {session_file}")
    print(f"📁 Session-Name: {session_name}")
    print(f"🔍 DPS Serial: {DPS_SERIAL}")
    
    # Lade Session-Daten
    messages = load_session_log(session_file)
    print(f"📥 {len(messages)} Messages geladen")
    
    if not messages:
        print("❌ Keine Messages gefunden!", file=sys.stderr)
        sys.exit(1)
    
    # Analysiere
    analysis = analyze_session(messages)
    print(f"🔍 {analysis['dps_relevant_messages']} DPS-relevante Messages gefunden")
    print(f"📈 Topic-Verteilung:")
    for topic, count in sorted(analysis["topic_counts"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {topic}: {count}")
    
    print(f"🎯 Commands gefunden:")
    for command, count in sorted(analysis["commands_found"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {command}: {count}")
    
    print(f"📦 STORAGE-ORDER Kontext: {analysis['storage_order_context_count']} Messages")
    print(f"🏭 PRODUCTION-ORDER Kontext: {analysis['production_order_context_count']} Messages")
    
    # Speichere Ergebnisse
    output_dir = Path(args.output_dir)
    save_dps_data(analysis, output_dir, session_name)
    
    print(f"\n✅ Analyse abgeschlossen!")
    print(f"📂 Ergebnisse gespeichert in: {output_dir}")


if __name__ == "__main__":
    main()
