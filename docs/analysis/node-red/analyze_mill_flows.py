#!/usr/bin/env python3
"""
Analyze MILL flows from Node-RED flows.json
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

def analyze_mill_flows(flows_file):
    """Analyze MILL flows and create a summary"""
    
    with open(flows_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tabs = data['tabs']
    nodes = data['nodes']
    
    print("=== MILL FLOWS ANALYSIS ===\n")
    
    # Analyze each MILL tab
    for tab in tabs:
        tab_id = tab['id']
        tab_label = tab['label']
        tab_info = tab.get('info', '').strip()
        
        print(f"## {tab_label}")
        print(f"Tab ID: {tab_id}")
        if tab_info:
            print(f"Info: {tab_info}")
        print()
        
        # Find nodes in this tab
        tab_nodes = [node for node in nodes if node.get('z') == tab_id]
        
        # Group nodes by type
        node_types = Counter()
        mqtt_topics = set()
        opcua_endpoints = set()
        
        for node in tab_nodes:
            node_type = node.get('type', 'unknown')
            node_types[node_type] += 1
            
            # Extract MQTT topics
            if 'topic' in node:
                mqtt_topics.add(node['topic'])
            
            # Extract OPC-UA endpoints
            if 'endpoint' in node:
                opcua_endpoints.add(node['endpoint'])
        
        print("### Node Types:")
        for node_type, count in node_types.most_common():
            print(f"  - {node_type}: {count}")
        
        if mqtt_topics:
            print("\n### MQTT Topics:")
            for topic in sorted(mqtt_topics):
                print(f"  - {topic}")
        
        if opcua_endpoints:
            print("\n### OPC-UA Endpoints:")
            for endpoint in sorted(opcua_endpoints):
                print(f"  - {endpoint}")
        
        print("\n" + "="*50 + "\n")
    
    # Overall summary
    print("## OVERALL SUMMARY")
    print(f"Total MILL tabs: {len(tabs)}")
    print(f"Total MILL nodes: {len(nodes)}")
    
    # All node types across all MILL tabs
    all_node_types = Counter()
    all_mqtt_topics = set()
    all_opcua_endpoints = set()
    
    for node in nodes:
        all_node_types[node.get('type', 'unknown')] += 1
        
        if 'topic' in node:
            all_mqtt_topics.add(node['topic'])
        
        if 'endpoint' in node:
            all_opcua_endpoints.add(node['endpoint'])
    
    print("\n### All Node Types (across all MILL tabs):")
    for node_type, count in all_node_types.most_common():
        print(f"  - {node_type}: {count}")
    
    if all_mqtt_topics:
        print("\n### All MQTT Topics (across all MILL tabs):")
        for topic in sorted(all_mqtt_topics):
            print(f"  - {topic}")
    
    if all_opcua_endpoints:
        print("\n### All OPC-UA Endpoints (across all MILL tabs):")
        for endpoint in sorted(all_opcua_endpoints):
            print(f"  - {endpoint}")

if __name__ == "__main__":
    flows_file = Path("data/aps-data/txt-controllers/mill_flows_extracted.json")
    
    if not flows_file.exists():
        print(f"Error: {flows_file} not found")
        exit(1)
    
    analyze_mill_flows(flows_file)

