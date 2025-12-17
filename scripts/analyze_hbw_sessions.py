#!/usr/bin/env python3
"""
HBW Session Data Analyzer

Analysiert Session-Log-Dateien und extrahiert HBW-relevante Topics
für eine umfassende HBW-Auswertung.
Fokus: STORE, PICK, DROP Commands und Lager-Operationen (Storage Slots, Inventory)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

# HBW Serial ID
HBW_SERIAL = "SVR3QA0022"

# HBW-relevante Topic-Patterns
HBW_TOPIC_PATTERNS = [
    f"module/v1/ff/{HBW_SERIAL}/",  # Alle HBW Topics
    f"module/v1/ff/NodeRed/{HBW_SERIAL}/",  # NodeRed enriched HBW Topics
    "ccu/order/",  # CCU Orders (relevant für HBW-Interaktionen)
    "ccu/state/calibration/",  # CCU Calibration State (enthält HBW)
    "ccu/set/calibration",  # CCU Calibration Commands
    "ccu/pairing/state",  # CCU Pairing State (enthält HBW Info)
]

# Spezifische HBW-Topics
HBW_TOPICS = {
    f"module/v1/ff/{HBW_SERIAL}/connection": "HBW Connection Status",
    f"module/v1/ff/{HBW_SERIAL}/state": "HBW State Updates",
    f"module/v1/ff/{HBW_SERIAL}/order": "HBW Order Commands",
    f"module/v1/ff/{HBW_SERIAL}/instantAction": "HBW Instant Actions",
    f"module/v1/ff/{HBW_SERIAL}/factsheet": "HBW Factsheet",
    f"module/v1/ff/NodeRed/{HBW_SERIAL}/connection": "HBW Connection (NodeRed enriched)",
    f"module/v1/ff/NodeRed/{HBW_SERIAL}/state": "HBW State (NodeRed enriched)",
    f"module/v1/ff/NodeRed/{HBW_SERIAL}/factsheet": "HBW Factsheet (NodeRed)",
}

# Weitere relevante Topics für HBW-Auswertung
RELATED_TOPICS = {
    "ccu/order/active": "CCU Active Order",
    "ccu/order/completed": "CCU Completed Order",
    "ccu/order/request": "CCU Order Request",
    f"ccu/state/calibration/{HBW_SERIAL}": "HBW Calibration State",
    "ccu/set/calibration": "CCU Calibration Commands",
    "ccu/pairing/state": "CCU Pairing State (enthält HBW Info)",
}

# HBW-spezifische Commands
HBW_COMMANDS = ["PICK", "DROP", "STORE"]


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


def is_hbw_relevant(topic: str) -> bool:
    """Prüft ob ein Topic HBW-relevant ist"""
    # Direkte HBW-Topics
    if HBW_SERIAL in topic:
        return True
    
    # CCU Orders (relevant für HBW-Interaktionen)
    if topic.startswith("ccu/order/"):
        return True
    
    # CCU Calibration (enthält HBW)
    if topic.startswith("ccu/state/calibration/") and HBW_SERIAL in topic:
        return True
    if topic == "ccu/set/calibration":
        return True
    
    # CCU Pairing State (enthält HBW Info)
    if topic == "ccu/pairing/state":
        return True
    
    return False


def categorize_topic(topic: str) -> str:
    """Kategorisiert ein Topic"""
    if f"/{HBW_SERIAL}/" in topic:
        if "/connection" in topic:
            return "hbw_connection"
        elif "/state" in topic:
            return "hbw_state"
        elif "/order" in topic:
            return "hbw_order"
        elif "/instantAction" in topic:
            return "hbw_instant_action"
        elif "/factsheet" in topic:
            return "hbw_factsheet"
        else:
            return "hbw_other"
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


def extract_storage_order_context(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrahiert Messages im Kontext von STORAGE-ORDER
    HBW ist primär für Storage-Operationen zuständig
    
    Returns:
        Liste von Messages im Kontext von STORAGE-ORDER
    """
    context_messages = []
    
    for i, msg in enumerate(messages):
        try:
            payload = json.loads(msg["payload"]) if isinstance(msg["payload"], str) else msg["payload"]
            
            # Prüfe ob es eine STORAGE-ORDER Message ist
            if isinstance(payload, dict):
                # CCU Order Messages
                if "orderType" in payload and payload["orderType"] == "STORAGE":
                    # Sammle Messages vor und nach dieser Order
                    # Vor: 50 Messages, Nach: 100 Messages
                    start_idx = max(0, i - 50)
                    end_idx = min(len(messages), i + 100)
                    
                    for j in range(start_idx, end_idx):
                        if is_hbw_relevant(messages[j]["topic"]):
                            context_messages.append(messages[j])
                
                # Prüfe auch in Arrays (ccu/order/completed ist ein Array)
                elif isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict) and "orderType" in item and item["orderType"] == "STORAGE":
                            start_idx = max(0, i - 50)
                            end_idx = min(len(messages), i + 100)
                            
                            for j in range(start_idx, end_idx):
                                if is_hbw_relevant(messages[j]["topic"]):
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


def extract_storage_commands_context(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrahiert Messages im Kontext von STORE, PICK, DROP Commands
    
    Returns:
        Liste von Messages im Kontext von Storage-Commands
    """
    context_messages = []
    storage_command_indices = []
    
    # Finde alle STORE/PICK/DROP Messages
    for i, msg in enumerate(messages):
        try:
            payload = json.loads(msg["payload"]) if isinstance(msg["payload"], str) else msg["payload"]
            
            # Prüfe ob es eine Storage-Command Message ist
            if isinstance(payload, dict):
                # Direkt in actionState
                if "actionState" in payload:
                    action_state = payload.get("actionState", {})
                    if isinstance(action_state, dict) and action_state.get("command") in HBW_COMMANDS:
                        storage_command_indices.append(i)
                
                # In actionStates Array
                if "actionStates" in payload:
                    for action in payload.get("actionStates", []):
                        if isinstance(action, dict) and action.get("command") in HBW_COMMANDS:
                            storage_command_indices.append(i)
                            break
                
                # In action (order payload)
                if "action" in payload:
                    action = payload.get("action", {})
                    if isinstance(action, dict) and action.get("command") in HBW_COMMANDS:
                        storage_command_indices.append(i)
                
                # In CCU Order completed (productionSteps)
                if "productionSteps" in payload:
                    for step in payload.get("productionSteps", []):
                        if isinstance(step, dict) and step.get("command") in HBW_COMMANDS:
                            storage_command_indices.append(i)
                            break
                
                # In CCU Order completed Array
                if isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict) and "productionSteps" in item:
                            for step in item.get("productionSteps", []):
                                if isinstance(step, dict) and step.get("command") in HBW_COMMANDS:
                                    storage_command_indices.append(i)
                                    break
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
    
    # Sammle Messages vor und nach Storage-Commands
    for idx in storage_command_indices:
        # Vor: 30 Messages, Nach: 50 Messages
        start_idx = max(0, idx - 30)
        end_idx = min(len(messages), idx + 50)
        
        for j in range(start_idx, end_idx):
            if is_hbw_relevant(messages[j]["topic"]):
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
    """Analysiert eine Session und extrahiert HBW-relevante Informationen"""
    
    # Filtere HBW-relevante Messages
    hbw_messages = [msg for msg in messages if is_hbw_relevant(msg["topic"])]
    
    # Topic-Statistiken
    topic_counter = Counter(msg["topic"] for msg in hbw_messages)
    topic_categories = defaultdict(list)
    
    for msg in hbw_messages:
        category = categorize_topic(msg["topic"])
        topic_categories[category].append(msg)
    
    # Zeitbereich
    timestamps = [msg["timestamp"] for msg in hbw_messages if "timestamp" in msg]
    start_time = min(timestamps) if timestamps else None
    end_time = max(timestamps) if timestamps else None
    
    # Payload-Analyse
    payload_stats = defaultdict(int)
    commands_found = Counter()
    storage_operations = []
    
    for msg in hbw_messages:
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
                        # Speichere Storage-Operationen
                        if command in HBW_COMMANDS:
                            storage_operations.append({
                                "timestamp": msg.get("timestamp"),
                                "topic": msg["topic"],
                                "command": command,
                                "state": action_state.get("state"),
                                "id": action_state.get("id"),
                                "workpieceId": action_state.get("metadata", {}).get("workpieceId") if isinstance(action_state.get("metadata"), dict) else None,
                                "type": action_state.get("metadata", {}).get("type") if isinstance(action_state.get("metadata"), dict) else None,
                            })
                if "actionStates" in payload:
                    # Array von ActionStates
                    for action in payload.get("actionStates", []):
                        if isinstance(action, dict) and "command" in action:
                            command = action["command"]
                            commands_found[command] += 1
                            # Speichere Storage-Operationen
                            if command in HBW_COMMANDS:
                                storage_operations.append({
                                    "timestamp": msg.get("timestamp"),
                                    "topic": msg["topic"],
                                    "command": command,
                                    "state": action.get("state"),
                                    "id": action.get("id"),
                                    "workpieceId": action.get("metadata", {}).get("workpieceId") if isinstance(action.get("metadata"), dict) else None,
                                    "type": action.get("metadata", {}).get("type") if isinstance(action.get("metadata"), dict) else None,
                                })
                # Prüfe auch action in order payload
                if "action" in payload:
                    action = payload.get("action", {})
                    if isinstance(action, dict) and "command" in action:
                        command = action["command"]
                        commands_found[command] += 1
                        if command in HBW_COMMANDS:
                            storage_operations.append({
                                "timestamp": msg.get("timestamp"),
                                "topic": msg["topic"],
                                "command": command,
                                "id": action.get("id"),
                                "workpieceId": action.get("metadata", {}).get("workpieceId") if isinstance(action.get("metadata"), dict) else None,
                                "type": action.get("metadata", {}).get("type") if isinstance(action.get("metadata"), dict) else None,
                            })
                if "workpieceId" in payload or (isinstance(payload, dict) and any("workpieceId" in str(v) for v in payload.values())):
                    payload_stats["has_workpieceId"] += 1
                if "type" in payload:
                    payload_stats["has_type"] += 1
                # Prüfe auf Storage-Slot-Informationen
                if "slots" in payload or "inventory" in payload or "stock" in payload:
                    payload_stats["has_storage_info"] += 1
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Extrahiere STORAGE-ORDER Kontext
    storage_order_context = extract_storage_order_context(messages)
    
    # Extrahiere Storage-Commands Kontext
    storage_commands_context = extract_storage_commands_context(messages)
    
    return {
        "total_messages": len(messages),
        "hbw_relevant_messages": len(hbw_messages),
        "start_time": start_time,
        "end_time": end_time,
        "topic_counts": dict(topic_counter),
        "topic_categories": {cat: len(msgs) for cat, msgs in topic_categories.items()},
        "payload_stats": dict(payload_stats),
        "commands_found": dict(commands_found),
        "storage_operations_count": len(storage_operations),
        "storage_order_context_count": len(storage_order_context),
        "storage_commands_context_count": len(storage_commands_context),
        "messages": hbw_messages,
        "storage_operations": storage_operations,
        "storage_order_context": storage_order_context,
        "storage_commands_context": storage_commands_context,
    }


def save_hbw_data(analysis: Dict[str, Any], output_dir: Path, session_name: str):
    """Speichert HBW-Daten in strukturiertem Format"""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Gesamt-Analyse (Metadata)
    metadata_file = output_dir / f"{session_name}_metadata.json"
    metadata = {
        "session_name": session_name,
        "analysis_timestamp": datetime.now().isoformat(),
        "hbw_serial": HBW_SERIAL,
        "total_messages": analysis["total_messages"],
        "hbw_relevant_messages": analysis["hbw_relevant_messages"],
        "start_time": analysis["start_time"],
        "end_time": analysis["end_time"],
        "topic_counts": analysis["topic_counts"],
        "topic_categories": analysis["topic_categories"],
        "payload_stats": analysis["payload_stats"],
        "commands_found": analysis["commands_found"],
        "storage_operations_count": analysis["storage_operations_count"],
        "storage_order_context_count": analysis["storage_order_context_count"],
        "storage_commands_context_count": analysis["storage_commands_context_count"],
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
    
    # 3. Alle HBW-Messages (komplett)
    all_messages_file = output_dir / f"{session_name}_all_hbw_messages.json"
    with open(all_messages_file, "w", encoding="utf-8") as f:
        json.dump(analysis["messages"], f, indent=2, ensure_ascii=False)
    print(f"✅ Alle HBW-Messages: {len(analysis['messages'])} → {all_messages_file}")
    
    # 4. Storage-Operationen (STORE, PICK, DROP)
    if analysis["storage_operations"]:
        storage_ops_file = output_dir / f"{session_name}_storage_operations.json"
        with open(storage_ops_file, "w", encoding="utf-8") as f:
            json.dump(analysis["storage_operations"], f, indent=2, ensure_ascii=False)
        print(f"✅ Storage-Operationen: {len(analysis['storage_operations'])} → {storage_ops_file}")
    
    # 5. STORAGE-ORDER Kontext
    if analysis["storage_order_context"]:
        storage_order_file = output_dir / f"{session_name}_storage_order_context.json"
        with open(storage_order_file, "w", encoding="utf-8") as f:
            json.dump(analysis["storage_order_context"], f, indent=2, ensure_ascii=False)
        print(f"✅ STORAGE-ORDER Kontext: {len(analysis['storage_order_context'])} Messages → {storage_order_file}")
    
    # 6. Storage-Commands Kontext (STORE/PICK/DROP)
    if analysis["storage_commands_context"]:
        storage_commands_file = output_dir / f"{session_name}_storage_commands_context.json"
        with open(storage_commands_file, "w", encoding="utf-8") as f:
            json.dump(analysis["storage_commands_context"], f, indent=2, ensure_ascii=False)
        print(f"✅ Storage-Commands Kontext: {len(analysis['storage_commands_context'])} Messages → {storage_commands_file}")


def main():
    parser = argparse.ArgumentParser(description="Analysiert Session-Daten für HBW-Auswertung")
    parser.add_argument("session_file", type=str, help="Pfad zur Session-Log-Datei")
    parser.add_argument("--output-dir", type=str, default="data/omf-data/hbw-analysis",
                       help="Ausgabeverzeichnis (Standard: data/omf-data/hbw-analysis)")
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
    print(f"🔍 HBW Serial: {HBW_SERIAL}")
    
    # Lade Session-Daten
    messages = load_session_log(session_file)
    print(f"📥 {len(messages)} Messages geladen")
    
    if not messages:
        print("❌ Keine Messages gefunden!", file=sys.stderr)
        sys.exit(1)
    
    # Analysiere
    analysis = analyze_session(messages)
    print(f"🔍 {analysis['hbw_relevant_messages']} HBW-relevante Messages gefunden")
    print(f"📈 Topic-Verteilung:")
    for topic, count in sorted(analysis["topic_counts"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {topic}: {count}")
    
    print(f"🎯 Commands gefunden:")
    for command, count in sorted(analysis["commands_found"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {command}: {count}")
    
    print(f"📦 Storage-Operationen: {analysis['storage_operations_count']}")
    print(f"🏭 STORAGE-ORDER Kontext: {analysis['storage_order_context_count']} Messages")
    print(f"🔧 Storage-Commands Kontext: {analysis['storage_commands_context_count']} Messages")
    
    # Speichere Ergebnisse
    output_dir = Path(args.output_dir)
    save_hbw_data(analysis, output_dir, session_name)
    
    print(f"\n✅ Analyse abgeschlossen!")
    print(f"📂 Ergebnisse gespeichert in: {output_dir}")


if __name__ == "__main__":
    main()
