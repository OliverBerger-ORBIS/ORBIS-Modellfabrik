#!/usr/bin/env python3
"""
Dashboard Logging Fix Script
Repariert print() zu logger.debug() in Dashboard-Komponenten
"""

import os
from pathlib import Path

def fix_dashboard_component(file_path):
    """Repariert eine Dashboard-Komponente"""
    print(f"🔧 Fixing {file_path}")
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has logger import
    if 'from omf.tools.logging_config import get_logger' in content:
        print(f"  ✅ Already has logger import")
        # Just replace print() with logger.debug()
        content = content.replace('print(', 'logger.debug(')
    else:
        # Add logger import after streamlit import
        if 'import streamlit as st' in content:
            content = content.replace(
                'import streamlit as st',
                'import streamlit as st\n\nfrom omf.tools.logging_config import get_logger\n\nlogger = get_logger("omf.dashboard.components.' + Path(file_path).stem + '")'
            )
            # Replace print() with logger.debug()
            content = content.replace('print(', 'logger.debug(')
        else:
            print(f"  ❌ No streamlit import found")
            return False
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Fixed")
    return True

def main():
    """Main function"""
    dashboard_components = [
        'omf/dashboard/components/steering_sequence.py',
        'omf/dashboard/components/ccu_pairing.py', 
        'omf/dashboard/components/ccu_state.py',
        'omf/dashboard/components/fts_factsheet.py',
        'omf/dashboard/components/fts_instantaction.py',
        'omf/dashboard/components/fts_state.py'
    ]
    
    for component in dashboard_components:
        if os.path.exists(component):
            fix_dashboard_component(component)
        else:
            print(f"❌ File not found: {component}")

if __name__ == "__main__":
    main()
