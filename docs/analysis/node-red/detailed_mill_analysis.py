#!/usr/bin/env python3
"""
Detailed analysis of MILL flows focusing on MQTT topics and connections
"""

import json
from pathlib import Path
from collections import defaultdict

def detailed_mill_analysis(flows_file):
    """Detailed analysis of MILL flows"""
    
    with open(flows_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tabs = data['tabs']
    nodes = data['nodes']
    
    print("=== DETAILED MILL FLOWS ANALYSIS ===\n")
    
    # Create a mapping of node IDs to nodes for easier lookup
    node_map = {node['id']: node for node in nodes}
    
    # Analyze each MILL tab in detail
    for tab in tabs:
        tab_id = tab['id']
        tab_label = tab['label']
        
        print(f"## {tab_label}")
        print(f"Tab ID: {tab_id}")
        print()
        
        # Find nodes in this tab
        tab_nodes = [node for node in nodes if node.get('z') == tab_id]
        
        # Find MQTT nodes and their topics
        mqtt_nodes = []
        opcua_connectors = []
        function_nodes = []
        
        for node in tab_nodes:
            node_type = node.get('type', '')
            
            if 'mqtt' in node_type.lower():
                mqtt_nodes.append(node)
            elif 'OPCUA-IIoT-Connector' in node_type:
                opcua_connectors.append(node)
            elif 'function' in node_type:
                function_nodes.append(node)
        
        # Analyze MQTT nodes
        if mqtt_nodes:
            print("### MQTT Nodes:")
            for node in mqtt_nodes:
                print(f"  - {node.get('name', 'Unnamed')} ({node['type']})")
                if 'topic' in node:
                    print(f"    Topic: {node['topic']}")
                if 'broker' in node:
                    print(f"    Broker: {node['broker']}")
                print()
        
        # Analyze OPC-UA connectors
        if opcua_connectors:
            print("### OPC-UA Connectors:")
            for connector in opcua_connectors:
                print(f"  - {connector.get('name', 'Unnamed')}")
                if 'endpoint' in connector:
                    print(f"    Endpoint: {connector['endpoint']}")
                print()
        
        # Find nodes that might be publishing to MQTT
        print("### Potential MQTT Publishers:")
        for node in tab_nodes:
            # Look for nodes that might be connected to MQTT nodes
            if 'wires' in node and node['wires']:
                for wire_group in node['wires']:
                    for target_id in wire_group:
                        if target_id in node_map:
                            target_node = node_map[target_id]
                            if 'mqtt' in target_node.get('type', '').lower():
                                print(f"  - {node.get('name', 'Unnamed')} ({node['type']}) → {target_node.get('name', 'Unnamed')} ({target_node['type']})")
                                if 'topic' in target_node:
                                    print(f"    Publishes to: {target_node['topic']}")
        
        print("\n" + "="*60 + "\n")
    
    # Look for specific MQTT topics related to MILL
    print("## MQTT TOPICS ANALYSIS")
    
    all_mqtt_topics = set()
    mqtt_publishers = defaultdict(list)
    mqtt_subscribers = defaultdict(list)
    
    for node in nodes:
        if 'mqtt' in node.get('type', '').lower():
            if 'topic' in node:
                topic = node['topic']
                all_mqtt_topics.add(topic)
                
                # Determine if it's a publisher or subscriber
                if 'mqtt in' in node.get('type', '').lower():
                    mqtt_subscribers[topic].append(node)
                elif 'mqtt out' in node.get('type', '').lower():
                    mqtt_publishers[topic].append(node)
    
    print("### All MQTT Topics found:")
    for topic in sorted(all_mqtt_topics):
        if topic.strip():  # Skip empty topics
            print(f"  - {topic}")
            if topic in mqtt_publishers:
                print(f"    Publishers: {len(mqtt_publishers[topic])}")
            if topic in mqtt_subscribers:
                print(f"    Subscribers: {len(mqtt_subscribers[topic])}")
    
    # Look for specific MILL-related topics
    print("\n### MILL-specific topics:")
    mill_topics = [topic for topic in all_mqtt_topics if 'mill' in topic.lower() or 'SVR3QA2098' in topic]
    for topic in mill_topics:
        print(f"  - {topic}")

if __name__ == "__main__":
    flows_file = Path("data/aps-data/txt-controllers/mill_flows_extracted.json")
    
    if not flows_file.exists():
        print(f"Error: {flows_file} not found")
        exit(1)
    
    detailed_mill_analysis(flows_file)

