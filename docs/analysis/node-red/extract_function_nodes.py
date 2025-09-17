#!/usr/bin/env python3
"""
Extract and analyze function nodes from Node-RED flows
"""

import json
import re
from pathlib import Path

def extract_function_nodes(flows_file):
    """Extract function nodes and their code"""
    
    with open(flows_file, 'r', encoding='utf-8') as f:
        flows = json.load(f)
    
    # Find all function nodes
    function_nodes = []
    for item in flows:
        if item.get('type') == 'function':
            function_nodes.append({
                'id': item.get('id'),
                'name': item.get('name', 'Unnamed'),
                'tab': item.get('z', 'No tab'),
                'func': item.get('func', ''),
                'wires': item.get('wires', [])
            })
    
    print(f"=== FUNCTION NODES ANALYSIS ({len(function_nodes)}) ===")
    
    # Group by tab
    by_tab = {}
    for node in function_nodes:
        tab_id = node['tab']
        if tab_id not in by_tab:
            by_tab[tab_id] = []
        by_tab[tab_id].append(node)
    
    # Find tab names
    tab_names = {}
    for item in flows:
        if item.get('type') == 'tab':
            tab_names[item.get('id')] = item.get('label', 'Unknown')
    
    # Analyze each tab
    for tab_id, nodes in by_tab.items():
        tab_name = tab_names.get(tab_id, f"Tab {tab_id}")
        print(f"\n=== {tab_name} ({len(nodes)} function nodes) ===")
        
        for node in nodes[:5]:  # Show first 5 nodes per tab
            print(f"\n--- {node['name']} ---")
            if node['func']:
                # Clean up the function code
                func_code = node['func'].replace('\\n', '\n').replace('\\t', '\t')
                # Show first 200 characters
                print(func_code[:200] + "..." if len(func_code) > 200 else func_code)
            else:
                print("No function code")
    
    # Look for specific patterns
    print(f"\n=== PATTERN ANALYSIS ===")
    
    # Find order-related functions
    order_functions = [node for node in function_nodes if 'order' in node['name'].lower()]
    print(f"Order-related functions: {len(order_functions)}")
    for func in order_functions[:3]:
        print(f"  - {func['name']} (Tab: {tab_names.get(func['tab'], 'Unknown')})")
    
    # Find connection-related functions
    connection_functions = [node for node in function_nodes if 'connection' in node['name'].lower()]
    print(f"Connection-related functions: {len(connection_functions)}")
    for func in connection_functions[:3]:
        print(f"  - {func['name']} (Tab: {tab_names.get(func['tab'], 'Unknown')})")
    
    # Find state-related functions
    state_functions = [node for node in function_nodes if 'state' in node['name'].lower()]
    print(f"State-related functions: {len(state_functions)}")
    for func in state_functions[:3]:
        print(f"  - {func['name']} (Tab: {tab_names.get(func['tab'], 'Unknown')})")

if __name__ == "__main__":
    flows_file = Path("/Users/oliver/Projects/ORBIS-Modellfabrik/integrations/node_red/backups/20250915T102133Z/flows.json")
    
    if not flows_file.exists():
        print(f"Error: {flows_file} not found")
        exit(1)
    
    extract_function_nodes(flows_file)

