#!/usr/bin/env python3
"""
Analyze all flows from Node-RED flows.json to find MQTT and other important nodes
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

def analyze_all_flows(flows_file):
    """Analyze all flows to find MQTT nodes and topics"""
    
    print(f"Reading flows from: {flows_file}")
    
    with open(flows_file, 'r', encoding='utf-8') as f:
        flows = json.load(f)
    
    print(f"Total items in flows: {len(flows)}")
    
    # Separate tabs and nodes
    tabs = [item for item in flows if item.get('type') == 'tab']
    nodes = [item for item in flows if item.get('type') != 'tab']
    
    print(f"Tabs: {len(tabs)}")
    print(f"Nodes: {len(nodes)}")
    
    # Analyze node types
    node_types = Counter()
    for node in nodes:
        node_types[node.get('type', 'unknown')] += 1
    
    print("\n=== NODE TYPES ===")
    for node_type, count in node_types.most_common(20):
        print(f"{node_type}: {count}")
    
    # Find MQTT-related nodes
    mqtt_nodes = []
    for node in nodes:
        node_type = node.get('type', '').lower()
        if 'mqtt' in node_type or 'broker' in node_type:
            mqtt_nodes.append(node)
    
    print(f"\n=== MQTT NODES ({len(mqtt_nodes)}) ===")
    for node in mqtt_nodes:
        print(f"Type: {node.get('type')}")
        print(f"Name: {node.get('name', 'Unnamed')}")
        if 'topic' in node:
            print(f"Topic: {node['topic']}")
        if 'broker' in node:
            print(f"Broker: {node['broker']}")
        print(f"Tab: {node.get('z', 'No tab')}")
        print()
    
    # Find all topics
    all_topics = set()
    for node in nodes:
        if 'topic' in node and node['topic']:
            all_topics.add(node['topic'])
    
    print(f"=== ALL TOPICS ({len(all_topics)}) ===")
    for topic in sorted(all_topics):
        print(f"  {topic}")
    
    # Find MILL-related topics
    mill_topics = [topic for topic in all_topics if 'mill' in topic.lower() or 'SVR3QA2098' in topic]
    print(f"\n=== MILL-RELATED TOPICS ({len(mill_topics)}) ===")
    for topic in mill_topics:
        print(f"  {topic}")
    
    # Find OPC-UA nodes
    opcua_nodes = [node for node in nodes if 'opcua' in node.get('type', '').lower()]
    print(f"\n=== OPC-UA NODES ({len(opcua_nodes)}) ===")
    for node in opcua_nodes:
        print(f"Type: {node.get('type')}")
        print(f"Name: {node.get('name', 'Unnamed')}")
        if 'endpoint' in node:
            print(f"Endpoint: {node['endpoint']}")
        print(f"Tab: {node.get('z', 'No tab')}")
        print()

if __name__ == "__main__":
    flows_file = Path("integrations/node_red/backups/20250915T102133Z/flows.json")
    
    if not flows_file.exists():
        print(f"Error: {flows_file} not found")
        exit(1)
    
    analyze_all_flows(flows_file)

