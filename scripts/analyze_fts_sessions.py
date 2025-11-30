#!/usr/bin/env python3
"""
FTS Session Data Analyzer

Analysiert Session-Log-Dateien und extrahiert FTS-relevante Topics
für eine umfassende FTS-Auswertung.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse


# FTS-relevante Topic-Patterns
FTS_TOPIC_PATTERNS = [
    "fts/v1/ff/",  # Alle FTS Topics
    "ccu/order/",  # CCU Orders (relevant für FTS-Navigation)
    "module/v1/ff/",  # Module States (relevant für FTS-Interaktionen)
]

# Spezifische FTS-Topics (basierend auf fts.yml)
FTS_TOPICS = {
    "fts/v1/ff/5iO4/connection": "FTS Connection Status",
    "fts/v1/ff/5iO4/state": "FTS State Updates (position, battery, load, actionState)",
    "fts/v1/ff/5iO4/order": "FTS Navigation Order (VDA5050)",
    "fts/v1/ff/5iO4/instantAction": "FTS Instant Action Commands",
    "fts/v1/ff/5iO4/factsheet": "FTS Factsheet (capabilities)",
}

# Weitere relevante Topics für FTS-Auswertung
RELATED_TOPICS = {
    "ccu/order/active": "CCU Active Order",
    "ccu/order/completed": "CCU Completed Order",
    "module/v1/ff/SVR3QA0022/state": "HBW State (FTS Pick/Drop)",
    "module/v1/ff/SVR4H73275/state": "DPS State (FTS Pick/Drop)",
    "module/v1/ff/SVR4H76530/state": "AIQS State (FTS Pick/Drop)",
}


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


def is_fts_relevant(topic: str) -> bool:
    """Prüft ob ein Topic FTS-relevant ist"""
    # Direkte FTS-Topics
    if topic.startswith("fts/v1/ff/"):
        return True
    
    # CCU Orders (relevant für FTS-Navigation)
    if topic.startswith("ccu/order/"):
        return True
    
    # Module States (relevant für FTS-Interaktionen)
    if topic.startswith("module/v1/ff/"):
        return True
    
    return False


def categorize_topic(topic: str) -> str:
    """Kategorisiert ein Topic"""
    if topic.startswith("fts/v1/ff/"):
        if "/connection" in topic:
            return "fts_connection"
        elif "/state" in topic:
            return "fts_state"
        elif "/order" in topic:
            return "fts_order"
        elif "/instantAction" in topic:
            return "fts_instant_action"
        elif "/factsheet" in topic:
            return "fts_factsheet"
        else:
            return "fts_other"
    elif topic.startswith("ccu/order/"):
        return "ccu_order"
    elif topic.startswith("module/v1/ff/"):
        return "module_state"
    else:
        return "other"


def analyze_session(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analysiert eine Session und extrahiert FTS-relevante Informationen"""
    
    # Filtere FTS-relevante Messages
    fts_messages = [msg for msg in messages if is_fts_relevant(msg["topic"])]
    
    # Topic-Statistiken
    topic_counter = Counter(msg["topic"] for msg in fts_messages)
    topic_categories = defaultdict(list)
    
    for msg in fts_messages:
        category = categorize_topic(msg["topic"])
        topic_categories[category].append(msg)
    
    # Zeitbereich
    timestamps = [msg["timestamp"] for msg in fts_messages if "timestamp" in msg]
    start_time = min(timestamps) if timestamps else None
    end_time = max(timestamps) if timestamps else None
    
    # Payload-Analyse
    payload_stats = defaultdict(int)
    for msg in fts_messages:
        try:
            payload = json.loads(msg["payload"]) if isinstance(msg["payload"], str) else msg["payload"]
            if isinstance(payload, dict):
                # Zähle wichtige Felder
                if "orderId" in payload:
                    payload_stats["has_orderId"] += 1
                if "actionState" in payload:
                    payload_stats["has_actionState"] += 1
                if "batteryState" in payload:
                    payload_stats["has_batteryState"] += 1
                if "load" in payload:
                    payload_stats["has_load"] += 1
        except (json.JSONDecodeError, TypeError):
            pass
    
    return {
        "total_messages": len(messages),
        "fts_relevant_messages": len(fts_messages),
        "start_time": start_time,
        "end_time": end_time,
        "topic_counts": dict(topic_counter),
        "topic_categories": {cat: len(msgs) for cat, msgs in topic_categories.items()},
        "payload_stats": dict(payload_stats),
        "messages": fts_messages,
    }


def save_fts_data(analysis: Dict[str, Any], output_dir: Path, session_name: str):
    """Speichert FTS-Daten in strukturiertem Format"""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Gesamt-Analyse (Metadata)
    metadata_file = output_dir / f"{session_name}_metadata.json"
    metadata = {
        "session_name": session_name,
        "analysis_timestamp": datetime.now().isoformat(),
        "total_messages": analysis["total_messages"],
        "fts_relevant_messages": analysis["fts_relevant_messages"],
        "start_time": analysis["start_time"],
        "end_time": analysis["end_time"],
        "topic_counts": analysis["topic_counts"],
        "topic_categories": analysis["topic_categories"],
        "payload_stats": analysis["payload_stats"],
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
    
    # 3. Alle FTS-Messages (komplett)
    all_messages_file = output_dir / f"{session_name}_all_fts_messages.json"
    with open(all_messages_file, "w", encoding="utf-8") as f:
        json.dump(analysis["messages"], f, indent=2, ensure_ascii=False)
    print(f"✅ Alle FTS-Messages: {len(analysis['messages'])} → {all_messages_file}")


def main():
    parser = argparse.ArgumentParser(description="Analysiert Session-Daten für FTS-Auswertung")
    parser.add_argument("session_file", type=str, help="Pfad zur Session-Log-Datei")
    parser.add_argument("--output-dir", type=str, default="data/omf-data/fts-analysis",
                       help="Ausgabeverzeichnis (Standard: data/omf-data/fts-analysis)")
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
    
    # Lade Session-Daten
    messages = load_session_log(session_file)
    print(f"📥 {len(messages)} Messages geladen")
    
    if not messages:
        print("❌ Keine Messages gefunden!", file=sys.stderr)
        sys.exit(1)
    
    # Analysiere
    analysis = analyze_session(messages)
    print(f"🔍 {analysis['fts_relevant_messages']} FTS-relevante Messages gefunden")
    print(f"📈 Topic-Verteilung:")
    for topic, count in sorted(analysis["topic_counts"].items(), key=lambda x: x[1], reverse=True):
        print(f"   {topic}: {count}")
    
    # Speichere Ergebnisse
    output_dir = Path(args.output_dir)
    save_fts_data(analysis, output_dir, session_name)
    
    print(f"\n✅ Analyse abgeschlossen!")
    print(f"📂 Ergebnisse gespeichert in: {output_dir}")


if __name__ == "__main__":
    main()

