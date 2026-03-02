#!/usr/bin/env python3
"""
AIQS Session Data Analyzer

Analysiert Session-Log-Dateien und extrahiert AIQS-relevante Topics
für eine umfassende AIQS-Auswertung.
Fokus: CHECK_QUALITY und ML-basierte Qualitätsprüfung (Photo, Mustererkennung)
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# AIQS Serial ID
AIQS_SERIAL = "SVR4H76530"

# AIQS-relevante Topic-Patterns
AIQS_TOPIC_PATTERNS = [
    f"module/v1/ff/{AIQS_SERIAL}/",  # Alle AIQS Topics
    f"module/v1/ff/NodeRed/{AIQS_SERIAL}/",  # NodeRed enriched AIQS Topics
    "ccu/order/",  # CCU Orders (relevant für AIQS-Interaktionen)
    "ccu/state/calibration/",  # CCU Calibration State (enthält AIQS)
    "ccu/set/calibration",  # CCU Calibration Commands
    "ccu/pairing/state",  # CCU Pairing State (enthält AIQS Info)
    "/j1/txt/1/",  # TXT Topics (AIQS hat TXT-Controller)
]

# Spezifische AIQS-Topics
AIQS_TOPICS = {
    f"module/v1/ff/{AIQS_SERIAL}/connection": "AIQS Connection Status",
    f"module/v1/ff/{AIQS_SERIAL}/state": "AIQS State Updates",
    f"module/v1/ff/{AIQS_SERIAL}/order": "AIQS Order Commands",
    f"module/v1/ff/{AIQS_SERIAL}/instantAction": "AIQS Instant Actions",
    f"module/v1/ff/{AIQS_SERIAL}/factsheet": "AIQS Factsheet",
    f"module/v1/ff/NodeRed/{AIQS_SERIAL}/connection": "AIQS Connection (NodeRed enriched)",
    f"module/v1/ff/NodeRed/{AIQS_SERIAL}/state": "AIQS State (NodeRed enriched)",
    f"module/v1/ff/NodeRed/{AIQS_SERIAL}/factsheet": "AIQS Factsheet (NodeRed)",
}

# Weitere relevante Topics für AIQS-Auswertung
RELATED_TOPICS = {
    "ccu/order/active": "CCU Active Order",
    "ccu/order/completed": "CCU Completed Order",
    "ccu/order/request": "CCU Order Request",
    f"ccu/state/calibration/{AIQS_SERIAL}": "AIQS Calibration State",
    "ccu/set/calibration": "CCU Calibration Commands",
    "ccu/pairing/state": "CCU Pairing State (enthält AIQS Info)",
    "/j1/txt/1/i/bme680": "AIQS Environmental Sensor",
}

# AIQS-spezifische Commands
AIQS_COMMANDS = ["PICK", "DROP", "CHECK_QUALITY"]


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


def is_aiqs_relevant(topic: str) -> bool:
    """Prüft ob ein Topic AIQS-relevant ist"""
    # Direkte AIQS-Topics
    if AIQS_SERIAL in topic:
        return True

    # CCU Orders (relevant für AIQS-Interaktionen)
    if topic.startswith("ccu/order/"):
        return True

    # CCU Calibration (enthält AIQS)
    if topic.startswith("ccu/state/calibration/") and AIQS_SERIAL in topic:
        return True
    if topic == "ccu/set/calibration":
        return True

    # CCU Pairing State (enthält AIQS Info)
    if topic == "ccu/pairing/state":
        return True

    # TXT Topics (AIQS hat TXT-Controller)
    if topic.startswith("/j1/txt/1/"):
        return True

    return False


def categorize_topic(topic: str) -> str:
    """Kategorisiert ein Topic"""
    if f"/{AIQS_SERIAL}/" in topic:
        if "/connection" in topic:
            return "aiqs_connection"
        elif "/state" in topic:
            return "aiqs_state"
        elif "/order" in topic:
            return "aiqs_order"
        elif "/instantAction" in topic:
            return "aiqs_instant_action"
        elif "/factsheet" in topic:
            return "aiqs_factsheet"
        else:
            return "aiqs_other"
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


def extract_check_quality_context(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extrahiert Messages im Kontext von CHECK_QUALITY

    Returns:
        Liste von Messages im Kontext von CHECK_QUALITY
    """
    context_messages = []
    check_quality_indices = []

    # Finde alle CHECK_QUALITY Messages
    for i, msg in enumerate(messages):
        try:
            payload = json.loads(msg["payload"]) if isinstance(msg["payload"], str) else msg["payload"]

            # Prüfe ob es eine CHECK_QUALITY Message ist
            if isinstance(payload, dict):
                # Direkt in actionState
                if "actionState" in payload:
                    action_state = payload.get("actionState", {})
                    if isinstance(action_state, dict) and action_state.get("command") == "CHECK_QUALITY":
                        check_quality_indices.append(i)

                # In actionStates Array
                if "actionStates" in payload:
                    for action in payload.get("actionStates", []):
                        if isinstance(action, dict) and action.get("command") == "CHECK_QUALITY":
                            check_quality_indices.append(i)
                            break

                # In CCU Order completed (productionSteps)
                if "productionSteps" in payload:
                    for step in payload.get("productionSteps", []):
                        if isinstance(step, dict) and step.get("command") == "CHECK_QUALITY":
                            check_quality_indices.append(i)
                            break

                # In CCU Order completed Array
                if isinstance(payload, list):
                    for item in payload:
                        if isinstance(item, dict) and "productionSteps" in item:
                            for step in item.get("productionSteps", []):
                                if isinstance(step, dict) and step.get("command") == "CHECK_QUALITY":
                                    check_quality_indices.append(i)
                                    break
        except (json.JSONDecodeError, TypeError, KeyError):
            pass

    # Sammle Messages vor und nach CHECK_QUALITY
    for idx in check_quality_indices:
        # Vor: 30 Messages, Nach: 50 Messages
        start_idx = max(0, idx - 30)
        end_idx = min(len(messages), idx + 50)

        for j in range(start_idx, end_idx):
            if is_aiqs_relevant(messages[j]["topic"]):
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
    """Analysiert eine Session und extrahiert AIQS-relevante Informationen"""

    # Filtere AIQS-relevante Messages
    aiqs_messages = [msg for msg in messages if is_aiqs_relevant(msg["topic"])]

    # Topic-Statistiken
    topic_counter = Counter(msg["topic"] for msg in aiqs_messages)
    topic_categories = defaultdict(list)

    for msg in aiqs_messages:
        category = categorize_topic(msg["topic"])
        topic_categories[category].append(msg)

    # Zeitbereich
    timestamps = [msg["timestamp"] for msg in aiqs_messages if "timestamp" in msg]
    start_time = min(timestamps) if timestamps else None
    end_time = max(timestamps) if timestamps else None

    # Payload-Analyse
    payload_stats = defaultdict(int)
    commands_found = Counter()
    check_quality_results = []

    for msg in aiqs_messages:
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
                    if isinstance(action_state, dict):
                        if "command" in action_state:
                            commands_found[action_state["command"]] += 1
                            # Speichere CHECK_QUALITY Ergebnisse
                            if action_state["command"] == "CHECK_QUALITY":
                                check_quality_results.append(
                                    {
                                        "timestamp": msg.get("timestamp"),
                                        "topic": msg["topic"],
                                        "result": action_state.get("result"),
                                        "state": action_state.get("state"),
                                        "id": action_state.get("id"),
                                    }
                                )
                if "actionStates" in payload:
                    # Array von ActionStates
                    for action in payload.get("actionStates", []):
                        if isinstance(action, dict):
                            if "command" in action:
                                commands_found[action["command"]] += 1
                                # Speichere CHECK_QUALITY Ergebnisse
                                if action["command"] == "CHECK_QUALITY":
                                    check_quality_results.append(
                                        {
                                            "timestamp": msg.get("timestamp"),
                                            "topic": msg["topic"],
                                            "result": action.get("result"),
                                            "state": action.get("state"),
                                            "id": action.get("id"),
                                        }
                                    )
                if "workpieceId" in payload or (
                    isinstance(payload, dict) and any("workpieceId" in str(v) for v in payload.values())
                ):
                    payload_stats["has_workpieceId"] += 1
                if "type" in payload:
                    payload_stats["has_type"] += 1
        except (json.JSONDecodeError, TypeError):
            pass

    # Extrahiere CHECK_QUALITY Kontext
    check_quality_context = extract_check_quality_context(messages)

    return {
        "total_messages": len(messages),
        "aiqs_relevant_messages": len(aiqs_messages),
        "start_time": start_time,
        "end_time": end_time,
        "topic_counts": dict(topic_counter),
        "topic_categories": {cat: len(msgs) for cat, msgs in topic_categories.items()},
        "payload_stats": dict(payload_stats),
        "commands_found": dict(commands_found),
        "check_quality_results": check_quality_results,
        "check_quality_context_count": len(check_quality_context),
        "messages": aiqs_messages,
        "check_quality_context": check_quality_context,
    }


def save_aiqs_data(analysis: Dict[str, Any], output_dir: Path, session_name: str):
    """Speichert AIQS-Daten in strukturiertem Format"""

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Gesamt-Analyse (Metadata)
    metadata_file = output_dir / f"{session_name}_metadata.json"
    metadata = {
        "session_name": session_name,
        "analysis_timestamp": datetime.now().isoformat(),
        "aiqs_serial": AIQS_SERIAL,
        "total_messages": analysis["total_messages"],
        "aiqs_relevant_messages": analysis["aiqs_relevant_messages"],
        "start_time": analysis["start_time"],
        "end_time": analysis["end_time"],
        "topic_counts": analysis["topic_counts"],
        "topic_categories": analysis["topic_categories"],
        "payload_stats": analysis["payload_stats"],
        "commands_found": analysis["commands_found"],
        "check_quality_results_count": len(analysis["check_quality_results"]),
        "check_quality_context_count": analysis["check_quality_context_count"],
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

    # 3. Alle AIQS-Messages (komplett)
    all_messages_file = output_dir / f"{session_name}_all_aiqs_messages.json"
    with open(all_messages_file, "w", encoding="utf-8") as f:
        json.dump(analysis["messages"], f, indent=2, ensure_ascii=False)
    print(f"✅ Alle AIQS-Messages: {len(analysis['messages'])} → {all_messages_file}")

    # 4. CHECK_QUALITY Ergebnisse
    if analysis["check_quality_results"]:
        check_quality_file = output_dir / f"{session_name}_check_quality_results.json"
        with open(check_quality_file, "w", encoding="utf-8") as f:
            json.dump(analysis["check_quality_results"], f, indent=2, ensure_ascii=False)
        print(f"✅ CHECK_QUALITY Ergebnisse: {len(analysis['check_quality_results'])} → {check_quality_file}")

    # 5. CHECK_QUALITY Kontext (Photo, ML, Mustererkennung)
    if analysis["check_quality_context"]:
        check_quality_context_file = output_dir / f"{session_name}_check_quality_context.json"
        with open(check_quality_context_file, "w", encoding="utf-8") as f:
            json.dump(analysis["check_quality_context"], f, indent=2, ensure_ascii=False)
        print(
            f"✅ CHECK_QUALITY Kontext: {len(analysis['check_quality_context'])} Messages → {check_quality_context_file}"
        )


def main():
    parser = argparse.ArgumentParser(description="Analysiert Session-Daten für AIQS-Auswertung")
    parser.add_argument("session_file", type=str, help="Pfad zur Session-Log-Datei")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/osf-data/aiqs-analysis",
        help="Ausgabeverzeichnis (Standard: data/osf-data/aiqs-analysis)",
    )
    parser.add_argument(
        "--session-name", type=str, help="Session-Name (wird aus Dateiname extrahiert wenn nicht angegeben)"
    )

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
    print(f"🔍 AIQS Serial: {AIQS_SERIAL}")

    # Lade Session-Daten
    messages = load_session_log(session_file)
    print(f"📥 {len(messages)} Messages geladen")

    if not messages:
        print("❌ Keine Messages gefunden!", file=sys.stderr)
        sys.exit(1)

    # Analysiere
    analysis = analyze_session(messages)
    print(f"🔍 {analysis['aiqs_relevant_messages']} AIQS-relevante Messages gefunden")
    print("📈 Topic-Verteilung:")
    for topic, count in sorted(analysis["topic_counts"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {topic}: {count}")

    print("🎯 Commands gefunden:")
    for command, count in sorted(analysis["commands_found"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {command}: {count}")

    print(f"🔬 CHECK_QUALITY Ergebnisse: {len(analysis['check_quality_results'])}")
    print(f"📸 CHECK_QUALITY Kontext: {analysis['check_quality_context_count']} Messages")

    # Speichere Ergebnisse
    output_dir = Path(args.output_dir)
    save_aiqs_data(analysis, output_dir, session_name)

    print("\n✅ Analyse abgeschlossen!")
    print(f"📂 Ergebnisse gespeichert in: {output_dir}")


if __name__ == "__main__":
    main()
