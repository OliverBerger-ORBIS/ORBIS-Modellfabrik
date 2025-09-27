#!/usr/bin/env python3
"""
Pre-commit Hook: Check for forbidden st.rerun() usage
"""

import sys
import re
from pathlib import Path


def check_file_for_st_rerun(file_path: Path) -> list[str]:
    """Check a single file for forbidden st.rerun() usage."""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Check for forbidden patterns
        forbidden_patterns = [
            r'st\.rerun\s*\(',
            r'streamlit\.rerun\s*\(',
            r'\.rerun\s*\(',
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in forbidden_patterns:
                if re.search(pattern, line):
                    # Check if this is the allowed consume_refresh() pattern
                    if i > 1:  # Check previous line
                        prev_line = lines[i-2].strip()
                        if 'consume_refresh()' in prev_line and 'if' in prev_line:
                            continue  # This is allowed
                    
                    # Check if on same line or next line
                    if 'consume_refresh()' in line:
                        continue  # This is allowed
                    
                    violations.append(f"{file_path}:{i}: {line.strip()}")
                    
    except Exception as e:
        violations.append(f"{file_path}: Error reading file: {e}")
    
    return violations


def main():
    """Main function to check all Python files for st.rerun() usage."""
    violations = []
    
    # Get all Python files from command line arguments
    for file_path in sys.argv[1:]:
        path = Path(file_path)
        if path.suffix == '.py':
            violations.extend(check_file_for_st_rerun(path))
    
    if violations:
        print("🚨 FORBIDDEN st.rerun() USAGE DETECTED!")
        print("=" * 50)
        for violation in violations:
            print(f"❌ {violation}")
        print("=" * 50)
        print("💡 SOLUTION: Use request_refresh() from omf.dashboard.utils.ui_refresh instead!")
        print("💡 EXAMPLE: request_refresh()  # ✅ Correct")
        print("💡 EXAMPLE: st.rerun()         # ❌ FORBIDDEN")
        sys.exit(1)
    else:
        print("✅ No forbidden st.rerun() usage found")
        sys.exit(0)


if __name__ == "__main__":
    main()
