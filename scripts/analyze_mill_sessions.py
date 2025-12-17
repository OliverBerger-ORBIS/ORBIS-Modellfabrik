#!/usr/bin/env python3
"""
MILL Session Data Analyzer

Analysiert Session-Log-Dateien und extrahiert MILL-relevante Topics
für eine umfassende MILL-Auswertung.
Fokus: MILL-Commands (PICK, MILL, DROP) und Production-Operationen
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

# MILL Serial ID
MILL_SERIAL = "SVR3QA2098"

# MILL-relevante Topic-Patterns
MILL_TOPIC_PATTERNS = [
    f"module/v1/ff/{MILL_SERIAL}/",  # Alle MILL Topics
    f"module/v1/ff/NodeRed/{MILL_SERIAL}/",  # NodeRed enriched MILL Topics
    "ccu/order/",  # CCU Orders (relevant für MILL-Interaktionen)
    "ccu/state/calibration/",  # CCU Calibration State (enthält MILL)
    "ccu/set/calibration",  # CCU Calibration Commands
    "ccu/pairing/state",  # CCU Pairing State (enthält MILL Info)
]

# Spezifische MILL-Topics
MILL_TOPICS = {
    f"module/v1/ff/{MILL_SERIAL}/connection": "MILL Connection Status",
    f"module/v1/ff/{MILL_SERIAL}/state": "MILL State Updates",
    f"module/v1/ff/{MILL_SERIAL}/order": "MILL Order Commands",
    f"module/v1/ff/{MILL_SERIAL}/instantAction": "MILL Instant Actions",
    f"module/v1/ff/{MILL_SERIAL}/factsheet": "MILL Factsheet",
    f"module/v1/ff/NodeRed/{MILL_SERIAL}/connection": "MILL Connection (NodeRed enriched)",
    f"module/v1/ff/NodeRed/{MILL_SERIAL}/state": "MILL State (NodeRed enriched)",
    f"module/v1/ff/NodeRed/{MILL_SERIAL}/factsheet": "MILL Factsheet (NodeRed)",
}

# Weitere relevante Topics für MILL-Auswertung
RELATED_TOPICS = {
    "ccu/order/active": "CCU Active Order",
    "ccu/order/completed": "CCU Completed Order",
    "ccu/order/request": "CCU Order Request",
    f"ccu/state/calibration/{MILL_SERIAL}": "MILL Calibration State",
    "ccu/set/calibration": "CCU Calibration Commands",
    "ccu/pairing/state": "CCU Pairing State (enthält MILL Info)",
}

# MILL-spezifische Commands
MILL_COMMANDS = ["PICK", "DROP", "MILL"]


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


def is_mill_relevant(topic: str) -> bool:
    """Prüft ob ein Topic MILL-relevant ist"""
    # Direkte MILL-Topics
    if MILL_SERIAL in topic:
        return True
    
    # CCU Orders (relevant für MILL-Interaktionen)
    if topic.startswith("ccu/order/"):
        return True
    
    # CCU Calibration (enthält MILL)
    if topic.startswith("ccu/state/calibration/") and MILL_SERIAL in topic:
        return True
    if topic == "ccu/set/calibration":
        return True
    
    # CCU Pairing State (enthält MILL Info)
    if topic == "ccu/pairing/state":
        return True
    
    return False


def categorize_topic(topic: str) -> str:
    """Kategorisiert ein Topic"""
    if f"/{MILL_SERIAL}/" in topic:
        if "/connection" in topic:
            return "mill_connection"
        elif "/state" in topic:
            return "mill_state"
        elif "/order" in topic:
            return "mill_order"
        elif "/instantAction" in topic:
            return "mill_instant_action"
        elif "/factsheet" in topic:
            return "mill_factsheet"
        else:
            return "mill_other"
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
    else:
        return "other"


def extract_production_order_context(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrahiert Messages im Kontext von PRODUCTION-ORDER
    MILL ist primär für Production-Operationen zuständig
    
    Returns:
        Liste von Messages im Kontext von PRODUCTION-ORDER
    """
    context_messages = []
    
    for i, msg in enumerate(messages):
        try:
            payload = json.loads(msg["payload"]) if isinstance(msg["payload"], str) else msg["payload"]
            
            # Prüfe ob es eine PRODUCTION-ORDER Message ist
            if isinstance(payload, dict):
                # CCU Order Messages
                if "orderType" in payload and payload["orderType"] == "PRODUCTION":
                    # Sammle Messages vor und nach dieser Order
                    # Vor: 50 Messages, Nach: 100 Messages
                    start_idx = max(0, i - 50)
                    end_idx = min(len(messages), i + 100)
                    
                    for j in range(start_idx, end_idx):
                        if is_mill_relevant(messages[j]["topic"]):
                            context_messages.append(messages[j])
                
                # Prüfe auch in Arrays (ccu/order/completed ist ein Array)
                elif isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict) and "orderType" in item and item["orderType"] == "PRODUCTION":
                            start_idx = max(0, i - 50)
                            end_idx = min(len(messages), i + 100)
                            
                            for j in range(start_idx, end_idx):
                                if is_mill_relevant(messages[j]["topic"]):
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


def extract_mill_commands_context(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrahiert Messages im Kontext von MILL-Commands (PICK, MILL, DROP)
    
    Returns:
        Liste von Messages im Kontext von MILL-Commands
    """
    context_messages = []
    mill_command_indices = []
    
    # Finde alle MILL-Command Messages
    for i, msg in enumerate(messages):
        try:
            payload = json.loads(msg["payload"]) if isinstance(msg["payload"], str) else msg["payload"]
            
            # Prüfe ob es eine MILL-Command Message ist
            if isinstance(payload, dict):
                # Direkt in actionState
                if "actionState" in payload:
                    action_state = payload.get("actionState", {})
                    if isinstance(action_state, dict) and action_state.get("command") in MILL_COMMANDS:
                        mill_command_indices.append(i)
                
                # In actionStates Array
                if "actionStates" in payload:
                    for action in payload.get("actionStates", []):
                        if isinstance(action, dict) and action.get("command") in MILL_COMMANDS:
                            mill_command_indices.append(i)
                            break
                
                # In action (order payload)
                if "action" in payload:
                    action = payload.get("action", {})
                    if isinstance(action, dict) and action.get("command") in MILL_COMMANDS:
                        mill_command_indices.append(i)
                
                # In CCU Order completed (productionSteps)
                if "productionSteps" in payload:
                    for step in payload.get("productionSteps", []):
                        if isinstance(step, dict) and step.get("command") in MILL_COMMANDS:
                            mill_command_indices.append(i)
                            break
                
                # In CCU Order completed Array
                if isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict) and "productionSteps" in item:
                            for step in item.get("productionSteps", []):
                                if isinstance(step, dict) and step.get("command") in MILL_COMMANDS:
                                    mill_command_indices.append(i)
                                    break
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    
    # Sammle Messages vor und nach MILL-Commands
    for idx in mill_command_indices:
        # Vor: 30 Messages, Nach: 50 Messages
        start_idx = max(0, idx - 30)
        end_idx = min(len(messages), idx + 50)
        
        for j in range(start_idx, end_idx):
            if is_mill_relevant(messages[j]["topic"]):
                context_messages.append(messages[j])
    
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
    """Analysiert eine Session und extrahiert MILL-relevante Informationen"""
    
    # Filtere MILL-relevante Messages
    mill_messages = [msg for msg in messages if is_mill_relevant(msg["topic"])]
    
    # Topic-Statistiken
    topic_counter = Counter(msg["topic"] for msg in mill_messages)
    topic_categories = defaultdict(list)
    
    for msg in mill_messages:
        category = categorize_topic(msg["topic"])
        topic_categories[category].append(msg)
    
    # Zeitbereich
    timestamps = [msg["timestamp"] for msg in mill_messages if "timestamp" in msg]
    start_time = min(timestamps) if timestamps else None
    end_time = max(timestamps) if timestamps else None
    
    # Payload-Analyse
    payload_stats = defaultdict(int)
    commands_found = Counter()
    mill_operations = []
    
    for msg in mill_messages:
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
                        command = action_state["command"]
                        commands_found[command] += 1
                        # Speichere MILL-Operationen
                        if command in MILL_COMMANDS:
                            mill_operations.append({
                                "timestamp": msg.get("timestamp"),
                                "topic": msg["topic"],
                                "command": command,
                                "state": action_state.get("state"),
                                "id": action_state.get("id"),
                                "workpieceId": action_state.get("metadata", {}).get("workpieceId") if isinstance(action_state.get("metadata"), dict) else None,
                                "type": action_state.get("metadata", {}).get("type") if isinstance(action_state.get("metadata"), dict) else None,
                                "duration": action_state.get("metadata", {}).get("duration") if isinstance(action_state.get("metadata"), dict) else None,
                            })
                if "actionStates" in payload:
                    # Array von ActionStates
                    for action in payload.get("actionStates", []):
                        if isinstance(action, dict) and "command" in action:
                            command = action["command"]
                            commands_found[command] += 1
                            # Speichere MILL-Operationen
                            if command in MILL_COMMANDS:
                                mill_operations.append({
                                    "timestamp": msg.get("timestamp"),
                                    "topic": msg["topic"],
                                    "command": command,
                                    "state": action.get("state"),
                                    "id": action.get("id"),
                                    "workpieceId": action.get("metadata", {}).get("workpieceId") if isinstance(action.get("metadata"), dict) else None,
                                    "type": action.get("metadata", {}).get("type") if isinstance(action.get("metadata"), dict) else None,
                                    "duration": action.get("metadata", {}).get("duration") if isinstance(action.get("metadata"), dict) else None,
                                })
                # Prüfe auch action in order payload
                if "action" in payload:
                    action = payload.get("action", {})
                    if isinstance(action, dict) and "command" in action:
                        command = action["command"]
                        commands_found[command] += 1
                        if command in MILL_COMMANDS:
                            mill_operations.append({
                                "timestamp": msg.get("timestamp"),
                                "topic": msg["topic"],
                                "command": command,
                                "id": action.get("id"),
                                "workpieceId": action.get("metadata", {}).get("workpieceId") if isinstance(action.get("metadata"), dict) else None,
                                "type": action.get("metadata", {}).get("type") if isinstance(action.get("metadata"), dict) else None,
                                "duration": action.get("metadata", {}).get("duration") if isinstance(action.get("metadata"), dict) else None,
                            })
                if "workpieceId" in payload or (isinstance(payload, dict) and any("workpieceId" in str(v) for v in payload.values())):
                    payload_stats["has_workpieceId"] += 1
                if "type" in payload:
                    payload_stats["has_type"] += 1
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Extrahiere PRODUCTION-ORDER Kontext
    production_order_context = extract_production_order_context(messages)
    
    # Extrahiere MILL-Commands Kontext
    mill_commands_context = extract_mill_commands_context(messages)
    
    return {
        "total_messages": len(messages),
        "mill_relevant_messages": len(mill_messages),
        "start_time": start_time,
        "end_time": end_time,
        "topic_counts": dict(topic_counter),
        "topic_categories": {cat: len(msgs) for cat, msgs in topic_categories.items()},
        "payload_stats": dict(payload_stats),
        "commands_found": dict(commands_found),
        "mill_operations_count": len(mill_operations),
        "production_order_context_count": len(production_order_context),
        "mill_commands_context_count": len(mill_commands_context),
        "messages": mill_messages,
        "mill_operations": mill_operations,
        "production_order_context": production_order_context,
        "mill_commands_context": mill_commands_context,
    }


def save_mill_data(analysis: Dict[str, Any], output_dir: Path, session_name: str):
    """Speichert MILL-Daten in strukturiertem Format"""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Gesamt-Analyse (Metadata)
    metadata_file = output_dir / f"{session_name}_metadata.json"
    metadata = {
        "session_name": session_name,
        "analysis_timestamp": datetime.now().isoformat(),
        "mill_serial": MILL_SERIAL,
        "total_messages": analysis["total_messages"],
        "mill_relevant_messages": analysis["mill_relevant_messages"],
        "start_time": analysis["start_time"],
        "end_time": analysis["end_time"],
        "topic_counts": analysis["topic_counts"],
        "topic_categories": analysis["topic_categories"],
        "payload_stats": analysis["payload_stats"],
        "commands_found": analysis["commands_found"],
        "mill_operations_count": analysis["mill_operations_count"],
        "production_order_context_count": analysis["production_order_context_count"],
        "mill_commands_context_count": analysis["mill_commands_context_count"],
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
    
    # 3. Alle MILL-Messages (komplett)
    all_messages_file = output_dir / f"{session_name}_all_mill_messages.json"
    with open(all_messages_file, "w", encoding="utf-8") as f:
        json.dump(analysis["messages"], f, indent=2, ensure_ascii=False)
    print(f"✅ Alle MILL-Messages: {len(analysis['messages'])} → {all_messages_file}")
    
    # 4. MILL-Operationen (PICK, MILL, DROP)
    if analysis["mill_operations"]:
        mill_ops_file = output_dir / f"{session_name}_mill_operations.json"
        with open(mill_ops_file, "w", encoding="utf-8") as f:
            json.dump(analysis["mill_operations"], f, indent=2, ensure_ascii=False)
        print(f"✅ MILL-Operationen: {len(analysis['mill_operations'])} → {mill_ops_file}")
    
    # 5. PRODUCTION-ORDER Kontext
    if analysis["production_order_context"]:
        production_order_file = output_dir / f"{session_name}_production_order_context.json"
        with open(production_order_file, "w", encoding="utf-8") as f:
            json.dump(analysis["production_order_context"], f, indent=2, ensure_ascii=False)
        print(f"✅ PRODUCTION-ORDER Kontext: {len(analysis['production_order_context'])} Messages → {production_order_file}")
    
    # 6. MILL-Commands Kontext (PICK/MILL/DROP)
    if analysis["mill_commands_context"]:
        mill_commands_file = output_dir / f"{session_name}_mill_commands_context.json"
        with open(mill_commands_file, "w", encoding="utf-8") as f:
            json.dump(analysis["mill_commands_context"], f, indent=2, ensure_ascii=False)
        print(f"✅ MILL-Commands Kontext: {len(analysis['mill_commands_context'])} Messages → {mill_commands_file}")


def main():
    parser = argparse.ArgumentParser(description="Analysiert Session-Daten für MILL-Auswertung")
    parser.add_argument("session_file", type=str, help="Pfad zur Session-Log-Datei")
    parser.add_argument("--output-dir", type=str, default="data/omf-data/mill-analysis",
                       help="Ausgabeverzeichnis (Standard: data/omf-data/mill-analysis)")
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
    print(f"🔍 MILL Serial: {MILL_SERIAL}")
    
    # Lade Session-Daten
    messages = load_session_log(session_file)
    print(f"📥 {len(messages)} Messages geladen")
    
    if not messages:
        print("❌ Keine Messages gefunden!", file=sys.stderr)
        sys.exit(1)
    
    # Analysiere
    analysis = analyze_session(messages)
    print(f"🔍 {analysis['mill_relevant_messages']} MILL-relevante Messages gefunden")
    print(f"📈 Topic-Verteilung:")
    for topic, count in sorted(analysis["topic_counts"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {topic}: {count}")
    
    print(f"🎯 Commands gefunden:")
    for command, count in sorted(analysis["commands_found"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {command}: {count}")
    
    print(f"🔧 MILL-Operationen: {analysis['mill_operations_count']}")
    print(f"🏭 PRODUCTION-ORDER Kontext: {analysis['production_order_context_count']} Messages")
    print(f"⚙️  MILL-Commands Kontext: {analysis['mill_commands_context_count']} Messages")
    
    # Speichere Ergebnisse
    output_dir = Path(args.output_dir)
    save_mill_data(analysis, output_dir, session_name)
    
    print(f"\n✅ Analyse abgeschlossen!")
    print(f"📂 Ergebnisse gespeichert in: {output_dir}")


if __name__ == "__main__":
    main()
