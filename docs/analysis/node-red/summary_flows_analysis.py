#!/usr/bin/env python3
"""
Summary analysis of Node-RED flows focusing on key information
"""

import json
from pathlib import Path
from collections import Counter, defaultdict

def summary_flows_analysis(flows_file):
    """Summary analysis of flows"""
    
    with open(flows_file, 'r', encoding='utf-8') as f:
        flows = json.load(f)
    
    # Separate tabs and nodes
    tabs = [item for item in flows if item.get('type') == 'tab']
    nodes = [item for item in flows if item.get('type') != 'tab']
    
    print("=== NODE-RED FLOWS SUMMARY ===")
    print(f"Total tabs: {len(tabs)}")
    print(f"Total nodes: {len(nodes)}")
    
    # Show all tabs
    print("\n=== ALL TABS ===")
    for tab in tabs:
        print(f"  - {tab['label']} (ID: {tab['id']})")
        if tab.get('info'):
            print(f"    Info: {tab['info'].strip()}")
    
    # Analyze node types
    node_types = Counter()
    for node in nodes:
        node_types[node.get('type', 'unknown')] += 1
    
    print(f"\n=== TOP 15 NODE TYPES ===")
    for node_type, count in node_types.most_common(15):
        print(f"  {node_type}: {count}")
    
    # Find MQTT nodes
    mqtt_nodes = [node for node in nodes if 'mqtt' in node.get('type', '').lower()]
    print(f"\n=== MQTT NODES ({len(mqtt_nodes)}) ===")
    
    if mqtt_nodes:
        for node in mqtt_nodes[:10]:  # Show first 10
            print(f"  Type: {node.get('type')}")
            print(f"  Name: {node.get('name', 'Unnamed')}")
            if 'topic' in node:
                print(f"  Topic: {node['topic']}")
            print(f"  Tab: {node.get('z', 'No tab')}")
            print()
    else:
        print("  No MQTT nodes found")
    
    # Find all topics
    all_topics = set()
    for node in nodes:
        if 'topic' in node and node['topic'] and node['topic'].strip():
            all_topics.add(node['topic'])
    
    print(f"=== ALL TOPICS ({len(all_topics)}) ===")
    for topic in sorted(all_topics):
        print(f"  {topic}")
    
    # Find OPC-UA connectors
    opcua_connectors = [node for node in nodes if node.get('type') == 'OPCUA-IIoT-Connector']
    print(f"\n=== OPC-UA CONNECTORS ({len(opcua_connectors)}) ===")
    for connector in opcua_connectors:
        print(f"  Name: {connector.get('name', 'Unnamed')}")
        if 'endpoint' in connector:
            print(f"  Endpoint: {connector['endpoint']}")
        print(f"  Tab: {connector.get('z', 'No tab')}")
        print()
    
    # Find function nodes (likely contain business logic)
    function_nodes = [node for node in nodes if node.get('type') == 'function']
    print(f"\n=== FUNCTION NODES ({len(function_nodes)}) ===")
    for func in function_nodes[:5]:  # Show first 5
        print(f"  Name: {func.get('name', 'Unnamed')}")
        print(f"  Tab: {func.get('z', 'No tab')}")
        if 'func' in func:
            # Show first 100 chars of function code
            func_code = func['func'][:100].replace('\n', ' ')
            print(f"  Code: {func_code}...")
        print()

if __name__ == "__main__":
    flows_file = Path("/Users/oliver/Projects/ORBIS-Modellfabrik/integrations/node_red/backups/20250915T102133Z/flows.json")
    
    if not flows_file.exists():
        print(f"Error: {flows_file} not found")
        exit(1)
    
    summary_flows_analysis(flows_file)
