#!/usr/bin/env python3
"""
Create hierarchical template structure manually
"""

import json
import os
from datetime import datetime

def create_hierarchical_template():
    """Create hierarchical template structure for stock topic"""
    
    # Get project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    output_dir = os.path.join(project_root, "mqtt-data/template_library")
    
    # Create hierarchical template structure
    template_structure = {
        "ts": "<ts>",
        "stockItems": [
            {
                "workpiece": {
                    "id": "<nfcCode>",
                    "type": "[RED, WHITE, BLUE]",
                    "state": "[RAW]"
                },
                "location": "[A1, A2, A3, B1, B2, B3, C1, C2, C3]",
                "hbw": "<moduleId>"
            }
        ]
    }
    
    # Create the complete template data
    template_data = {
        "metadata": {
            "analyzer": "Manual Hierarchical Template",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        },
        "templates": {
            "/j1/txt/1/f/i/stock": {
                "topic": "/j1/txt/1/f/i/stock",
                "category": "TXT Controller",
                "message_count": 295,
                "template_structure": template_structure,
                "examples": [
                    {
                        "ts": "2025-08-19T09:13:34.583Z",
                        "stockItems": [
                            {
                                "workpiece": {
                                    "id": "040a8dca341291",
                                    "type": "RED",
                                    "state": "RAW"
                                },
                                "location": "A1",
                                "hbw": "SVR3QA0022"
                            }
                        ]
                    },
                    {
                        "ts": "2025-08-19T09:15:22.147Z",
                        "stockItems": [
                            {
                                "workpiece": {
                                    "id": "04798eca341290",
                                    "type": "WHITE",
                                    "state": "RAW"
                                },
                                "location": "B1",
                                "hbw": "SVR3QA0022"
                            }
                        ]
                    },
                    {
                        "ts": "2025-08-19T09:17:45.831Z",
                        "stockItems": [
                            {
                                "workpiece": {
                                    "id": "047389ca341291",
                                    "type": "BLUE",
                                    "state": "RAW"
                                },
                                "location": "C1",
                                "hbw": "SVR3QA0022"
                            }
                        ]
                    }
                ],
                "statistics": {
                    "total_messages": 295,
                    "valid_payloads": 294,
                    "variable_fields": 3,
                    "enum_fields": 3,
                    "sessions": 34
                },
                "session_name": "wareneingang-weiss_1",
                "timestamp": "2025-08-19T09:13:34.583Z"
            }
        }
    }
    
    # Save to file
    output_file = os.path.join(output_dir, "txt_template_analysis.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Hierarchical template saved to: {output_file}")
    print("Template structure:")
    print(json.dumps(template_structure, indent=2))

if __name__ == "__main__":
    create_hierarchical_template()
