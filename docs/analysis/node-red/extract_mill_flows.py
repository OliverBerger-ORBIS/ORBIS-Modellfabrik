#!/usr/bin/env python3
"""
Extract MILL-related flows from Node-RED flows.json
"""

import json
import sys
from pathlib import Path

def extract_mill_flows(flows_file, output_file):
    """Extract all MILL-related tabs from flows.json"""
    
    print(f"Reading flows from: {flows_file}")
    
    with open(flows_file, 'r', encoding='utf-8') as f:
        flows = json.load(f)
    
    # Find all MILL-related tabs
    mill_tabs = []
    mill_nodes = []
    
    for item in flows:
        if item.get('type') == 'tab' and 'MILL' in item.get('label', ''):
            mill_tabs.append(item)
            print(f"Found MILL tab: {item['label']} (ID: {item['id']})")
    
    # Find all nodes that belong to MILL tabs
    mill_tab_ids = [tab['id'] for tab in mill_tabs]
    
    for item in flows:
        if item.get('z') in mill_tab_ids:  # z is the tab ID for nodes
            mill_nodes.append(item)
    
    # Create output structure
    output = {
        "tabs": mill_tabs,
        "nodes": mill_nodes,
        "total_tabs": len(mill_tabs),
        "total_nodes": len(mill_nodes)
    }
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nExtracted {len(mill_tabs)} MILL tabs and {len(mill_nodes)} nodes")
    print(f"Output saved to: {output_file}")
    
    # Print summary
    print("\nMILL Tabs found:")
    for tab in mill_tabs:
        print(f"  - {tab['label']} (ID: {tab['id']})")
        if tab.get('info'):
            print(f"    Info: {tab['info'].strip()}")

if __name__ == "__main__":
    flows_file = Path("integrations/node_red/backups/20250915T102133Z/flows.json")
    output_file = Path("data/aps-data/txt-controllers/mill_flows_extracted.json")
    
    if not flows_file.exists():
        print(f"Error: {flows_file} not found")
        sys.exit(1)
    
    extract_mill_flows(flows_file, output_file)

