#!/usr/bin/env python3
"""
Pre-commit Hook: Check for MQTT Connection-Loop anti-patterns
"""

import sys
import re
from pathlib import Path


def check_file_for_mqtt_violations(file_path: Path) -> list[str]:
    """Check a single file for MQTT Connection-Loop anti-patterns."""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Check for forbidden patterns
        forbidden_patterns = [
            # Direct MQTT client creation in components
            (r'OmfMqttClient\s*\(', "Direct MQTT client creation in component"),
            (r'create_ephemeral\s*\(', "Ephemeral MQTT client creation in component"),
            (r'get_omf_mqtt_client\s*\(', "Direct MQTT client retrieval in component"),
            
            # Multiple ensure_dashboard_client calls
            (r'ensure_dashboard_client\s*\(.*ensure_dashboard_client\s*\(', "Multiple ensure_dashboard_client calls"),
        ]
        
        # Check if this is a component file (not omf_dashboard.py or omf_mqtt_factory.py)
        is_component = (
            'components' in str(file_path) or 
            'helper_apps' in str(file_path)
        ) and 'omf_dashboard.py' not in str(file_path) and 'omf_mqtt_factory.py' not in str(file_path)
        
        for i, line in enumerate(lines, 1):
            for pattern, description in forbidden_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if is_component:
                        violations.append(f"{file_path}:{i}: {description} - {line.strip()}")
                    elif 'ensure_dashboard_client' in pattern:
                        violations.append(f"{file_path}:{i}: {description} - {line.strip()}")
                        
    except Exception as e:
        violations.append(f"{file_path}: Error reading file: {e}")
    
    return violations


def check_mqtt_imports(file_path: Path) -> list[str]:
    """Check for proper MQTT imports in components."""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if this is a component file
        is_component = (
            'components' in str(file_path) or 
            'helper_apps' in str(file_path)
        ) and 'omf_dashboard.py' not in str(file_path) and 'omf_mqtt_factory.py' not in str(file_path)
        
        if is_component:
            # Check for forbidden imports
            forbidden_imports = [
                r'from.*omf_mqtt_factory.*import.*ensure_dashboard_client',
                r'from.*omf_mqtt_factory.*import.*create_ephemeral',
                r'from.*omf_mqtt_factory.*import.*get_omf_mqtt_client',
                r'import.*omf_mqtt_factory',
            ]
            
            for pattern in forbidden_imports:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(f"{file_path}: Forbidden MQTT factory import: {pattern}")
                    
    except Exception as e:
        violations.append(f"{file_path}: Error reading file: {e}")
    
    return violations


def main():
    """Main function to check all Python files for MQTT Connection-Loop anti-patterns."""
    violations = []
    
    # Get all Python files from command line arguments
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if path.suffix == '.py':
            violations.extend(check_file_for_mqtt_violations(path))
            violations.extend(check_mqtt_imports(path))
    
    if violations:
        print("🚨 MQTT CONNECTION-LOOP ANTI-PATTERNS DETECTED!")
        print("=" * 60)
        for violation in violations:
            print(f"❌ {violation}")
        print("=" * 60)
        print("💡 SOLUTION: Use st.session_state.get('mqtt_client') in components!")
        print("💡 EXAMPLE: mqtt_client = st.session_state.get('mqtt_client')  # ✅ Correct")
        print("💡 EXAMPLE: client = OmfMqttClient(cfg)                      # ❌ FORBIDDEN")
        print("💡 EXAMPLE: client = ensure_dashboard_client(env, store)     # ❌ FORBIDDEN in components")
        print("💡 RULES:")
        print("   - Only omf_dashboard.py should call ensure_dashboard_client()")
        print("   - Components must use st.session_state.get('mqtt_client')")
        print("   - No direct OmfMqttClient() creation in components")
        print("   - No create_ephemeral() or get_omf_mqtt_client() in components")
        sys.exit(1)
    else:
        print("✅ No MQTT Connection-Loop anti-patterns found")
        sys.exit(0)


if __name__ == "__main__":
    main()
