#!/usr/bin/env python3
"""
MQTT Client Subscription Analyzer

Analysiert Mosquitto-Logs um Client-Subscription-Patterns zu identifizieren:
- Welche Clients publizieren welche Topics
- Welche Clients abonnieren welche Topics
- Client-zu-Topic-Mapping
"""

import re
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, List, Tuple

def parse_mosquitto_log(log_file: str) -> Dict:
    """Parst Mosquitto-Log und extrahiert Client-Subscription-Informationen."""
    
    publishers = defaultdict(set)  # client -> topics published
    subscribers = defaultdict(set)  # client -> topics subscribed
    
    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Parse PUBLISH operations
            if 'PUBLISH' in line:
                # Extract client and topic
                if 'Received PUBLISH from' in line:
                    # Client publishes topic
                    match = re.search(r'Received PUBLISH from (\S+) .*?\'([^\']+)\'', line)
                    if match:
                        client = match.group(1)
                        topic = match.group(2)
                        publishers[client].add(topic)
                        
                elif 'Sending PUBLISH to' in line:
                    # Broker sends to subscriber
                    match = re.search(r'Sending PUBLISH to (\S+) .*?\'([^\']+)\'', line)
                    if match:
                        client = match.group(1)
                        topic = match.group(2)
                        subscribers[client].add(topic)
            
            # Parse SUBSCRIBE operations (if present)
            elif 'SUBSCRIBE' in line:
                match = re.search(r'Received SUBSCRIBE from (\S+) .*?\'([^\']+)\'', line)
                if match:
                    client = match.group(1)
                    topic = match.group(2)
                    subscribers[client].add(topic)
    
    return {
        'publishers': dict(publishers),
        'subscribers': dict(subscribers)
    }

def analyze_client_patterns(data: Dict) -> Dict:
    """Analysiert Client-Patterns und erstellt Übersichten."""
    
    publishers = data['publishers']
    subscribers = data['subscribers']
    
    # Alle Clients identifizieren
    all_clients = set(publishers.keys()) | set(subscribers.keys())
    
    # Client-Typen identifizieren
    client_types = {}
    for client in all_clients:
        if 'nodered' in client.lower():
            client_types[client] = 'Node-RED (CCU)'
        elif 'mqttjs' in client.lower():
            client_types[client] = 'MQTT.js (Dashboard/Web)'
        elif 'auto-' in client.lower():
            client_types[client] = 'Auto-Generated (Module/System)'
        else:
            client_types[client] = 'Unknown'
    
    # Topic-Kategorien
    topic_categories = defaultdict(set)
    for client, topics in publishers.items():
        for topic in topics:
            if topic.startswith('ccu/'):
                topic_categories['CCU'].add(topic)
            elif topic.startswith('module/'):
                topic_categories['Module'].add(topic)
            elif topic.startswith('fts/'):
                topic_categories['FTS'].add(topic)
            elif topic.startswith('/j1/txt/'):
                topic_categories['TXT'].add(topic)
            else:
                topic_categories['Other'].add(topic)
    
    return {
        'all_clients': all_clients,
        'client_types': client_types,
        'publishers': publishers,
        'subscribers': subscribers,
        'topic_categories': dict(topic_categories)
    }

def generate_report(analysis: Dict) -> str:
    """Generiert einen detaillierten Analyse-Report."""
    
    report = []
    report.append("# MQTT Client Subscription Analysis")
    report.append("=" * 50)
    report.append("")
    
    # Client-Übersicht
    report.append("## Identifizierte Clients")
    report.append("")
    for client in sorted(analysis['all_clients']):
        client_type = analysis['client_types'].get(client, 'Unknown')
        report.append(f"- **{client}** - {client_type}")
    report.append("")
    
    # Publisher-Analyse
    report.append("## Publishers (Wer publiziert was)")
    report.append("")
    for client in sorted(analysis['publishers'].keys()):
        client_type = analysis['client_types'].get(client, 'Unknown')
        report.append(f"### {client} ({client_type})")
        topics = sorted(analysis['publishers'][client])
        for topic in topics:
            report.append(f"- `{topic}`")
        report.append("")
    
    # Subscriber-Analyse
    report.append("## Subscribers (Wer abonniert was)")
    report.append("")
    for client in sorted(analysis['subscribers'].keys()):
        client_type = analysis['client_types'].get(client, 'Unknown')
        report.append(f"### {client} ({client_type})")
        topics = sorted(analysis['subscribers'][client])
        for topic in topics:
            report.append(f"- `{topic}`")
        report.append("")
    
    # Topic-Kategorien
    report.append("## Topic-Kategorien")
    report.append("")
    for category, topics in analysis['topic_categories'].items():
        report.append(f"### {category} Topics")
        for topic in sorted(topics):
            report.append(f"- `{topic}`")
        report.append("")
    
    return "\n".join(report)

def main():
    """Hauptfunktion."""
    log_file = "data/aps-data/mosquitto/mosquitto_detailed.log"
    
    if not Path(log_file).exists():
        print(f"Log-Datei nicht gefunden: {log_file}")
        return
    
    print("Analysiere MQTT-Logs...")
    data = parse_mosquitto_log(log_file)
    
    print("Erstelle Client-Pattern-Analyse...")
    analysis = analyze_client_patterns(data)
    
    print("Generiere Report...")
    report = generate_report(analysis)
    
    # Report speichern
    output_file = "data/aps-data/mosquitto/client_subscription_analysis.md"
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"Analyse abgeschlossen! Report gespeichert: {output_file}")
    
    # Kurze Zusammenfassung
    print("\n" + "="*50)
    print("KURZE ZUSAMMENFASSUNG:")
    print("="*50)
    print(f"Anzahl Clients: {len(analysis['all_clients'])}")
    print(f"Publishers: {len(analysis['publishers'])}")
    print(f"Subscribers: {len(analysis['subscribers'])}")
    
    for client_type in set(analysis['client_types'].values()):
        count = sum(1 for ct in analysis['client_types'].values() if ct == client_type)
        print(f"- {client_type}: {count}")

if __name__ == "__main__":
    main()
