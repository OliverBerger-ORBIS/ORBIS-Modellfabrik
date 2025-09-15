#!/usr/bin/env python3
"""
Validate Observations against JSON Schema
Validates all YAML files in registry/observations/ against observation.schema.json
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

import yaml
import jsonschema
from jsonschema import validate, ValidationError

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def load_schema() -> Dict[str, Any]:
    """Load the observation schema"""
    schema_path = PROJECT_ROOT / "registry" / "observations" / "observation.schema.json"
    
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        return {}
    
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
        return {}


def validate_observation_file(file_path: Path, schema: Dict[str, Any]) -> List[str]:
    """Validate a single observation file against the schema"""
    errors = []
    
    try:
        # Load YAML file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate against schema
        validate(instance=data, schema=schema)
        
        # Additional validation: Check status workflow
        status = data.get('metadata', {}).get('status', '')
        if status not in ['open', 'reviewed', 'migrated', 'discarded']:
            errors.append(f"❌ Invalid status '{status}' - must be one of: open, reviewed, migrated, discarded")
        
        # Check date format
        date = data.get('metadata', {}).get('date', '')
        if date and not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            errors.append(f"❌ Invalid date format '{date}' - must be YYYY-MM-DD")
        
        # Check filename matches date
        filename_date = file_path.stem.split('_')[0]
        if date and filename_date != date:
            errors.append(f"❌ Date mismatch: filename '{filename_date}' vs metadata '{date}'")
        
        if not errors:
            print(f"✅ {file_path.name}")
        
    except ValidationError as e:
        errors.append(f"❌ Schema validation error: {e.message}")
    except yaml.YAMLError as e:
        errors.append(f"❌ YAML parsing error: {e}")
    except Exception as e:
        errors.append(f"❌ Unexpected error: {e}")
    
    return errors


def validate_observations() -> bool:
    """Validate all observations in registry/observations/"""
    print("🔍 Validating Observations...")
    print("=" * 50)
    
    # Load schema
    schema = load_schema()
    if not schema:
        return False
    
    # Find all YAML files in observations directory
    observations_dir = PROJECT_ROOT / "registry" / "observations"
    if not observations_dir.exists():
        print(f"❌ Observations directory not found: {observations_dir}")
        return False
    
    yaml_files = list(observations_dir.rglob("*.yml"))
    yaml_files = [f for f in yaml_files if f.name != "observation-template.yml"]  # Skip template
    
    if not yaml_files:
        print("⚠️  No observation files found")
        return True
    
    print(f"📁 Found {len(yaml_files)} observation files")
    print()
    
    all_errors = []
    
    for file_path in sorted(yaml_files):
        errors = validate_observation_file(file_path, schema)
        if errors:
            print(f"❌ {file_path.name}")
            for error in errors:
                print(f"   {error}")
            all_errors.extend(errors)
        print()
    
    # Summary
    print("=" * 50)
    if all_errors:
        print(f"❌ Validation failed: {len(all_errors)} errors found")
        return False
    else:
        print(f"✅ All {len(yaml_files)} observations are valid")
        return True


def main():
    """Main function"""
    success = validate_observations()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
