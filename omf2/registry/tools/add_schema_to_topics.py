#!/usr/bin/env python3
"""
Add Schema and Description to all Topics
Schnelle Lösung um alle Topics mit Schema + Description zu erweitern
"""

import yaml
from pathlib import Path


def add_schema_to_topics():
    """Fügt Schema + Description zu allen Topics hinzu"""
    
    topics_dir = Path("omf2/registry/topics")
    
    # Schema-Mappings für verschiedene Topic-Typen
    schema_mappings = {
        # Module Topics
        "module/v1/ff": {
            "connection": "module_v1_ff_serial_connection.schema.json",
            "state": "module_v1_ff_serial_state.schema.json", 
            "order": "module_v1_ff_serial_order.schema.json",
            "factsheet": "module_v1_ff_serial_factsheet.schema.json",
            "instantAction": "module_v1_ff_serial_instantAction.schema.json"
        },
        # CCU Topics
        "ccu": {
            "order": "ccu_order_request.schema.json",
            "state": "ccu_global.schema.json",
            "control": "ccu_global.schema.json",
            "set": "ccu_set_reset.schema.json",
            "pairing": "ccu_pairing_state.schema.json"
        },
        # TXT Topics
        "/j1/txt": {
            "f/i": "j1_txt_1_f_i_order.schema.json",
            "f/o": "j1_txt_1_f_o_order.schema.json",
            "c/": "j1_txt_1_c_bme680.schema.json",
            "i/": "j1_txt_1_i_bme680.schema.json",
            "o/": "j1_txt_1_o_ptu.schema.json"
        },
        # FTS Topics
        "fts/v1/ff": {
            "connection": "fts_v1_ff_serial_connection.schema.json",
            "state": "fts_v1_ff_serial_state.schema.json",
            "order": "fts_v1_ff_serial_order.schema.json",
            "factsheet": "fts_v1_ff_serial_factsheet.schema.json",
            "instantAction": "fts_v1_ff_serial_instantAction.schema.json"
        }
    }
    
    # Description-Templates
    descriptions = {
        "connection": "Connection status with client information and IP address",
        "state": "State information with current status and processing state", 
        "order": "Order commands for processing tasks and workflow execution",
        "factsheet": "Factsheet with capabilities, specifications and configuration details",
        "instantAction": "Instant action commands for immediate operations",
        "control": "Control commands and system directives",
        "set": "System settings and configuration commands",
        "pairing": "Module pairing status and connection state"
    }
    
    for topic_file in topics_dir.glob("*.yml"):
        print(f"Processing {topic_file.name}...")
        
        try:
            with open(topic_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            
            # Process each topic section
            for section_name, topics_list in data.items():
                if section_name in ['metadata', 'category'] or not isinstance(topics_list, list):
                    continue
                
                for topic_data in topics_list:
                    if isinstance(topic_data, dict) and 'topic' in topic_data:
                        topic = topic_data['topic']
                        
                        # Find matching schema
                        schema = None
                        description = None
                        
                        for pattern, mappings in schema_mappings.items():
                            if topic.startswith(pattern):
                                # Find best match
                                for suffix, schema_file in mappings.items():
                                    if suffix in topic:
                                        schema = schema_file
                                        # Extract description type
                                        for desc_type, desc_text in descriptions.items():
                                            if desc_type in suffix or desc_type in topic:
                                                description = desc_text
                                                break
                                        break
                                break
                        
                        # Add schema and description if found
                        if schema:
                            topic_data['schema'] = schema
                        if description:
                            topic_data['description'] = description
                        else:
                            topic_data['description'] = f"Topic: {topic}"
            
            # Write back to file
            with open(topic_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            print(f"✅ Updated {topic_file.name}")
            
        except Exception as e:
            print(f"❌ Error processing {topic_file}: {e}")


if __name__ == "__main__":
    add_schema_to_topics()
