#!/usr/bin/env python3
"""
Template Validator - Verifies template structures against example messages
"""

import json
import re
from typing import Dict, List, Any, Tuple

class TemplateValidator:
    def __init__(self):
        self.module_id_pattern = r'^SVR[0-9A-Z]+$'
        self.uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        self.datetime_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$'
        
    def validate_template_against_examples(self, template_structure: Dict, examples: List[Dict]) -> Dict:
        """Validate template structure against example messages"""
        issues = []
        corrections = {}
        
        for i, example in enumerate(examples):
            example_issues = self._validate_single_example(template_structure, example, f"Beispiel {i+1}")
            issues.extend(example_issues)
            
            # Collect corrections from this example
            for issue in example_issues:
                if 'correction' in issue:
                    field_path = issue['field_path']
                    if field_path not in corrections:
                        corrections[field_path] = []
                    corrections[field_path].append(issue['correction'])
        
        # Generate corrected template
        corrected_template = self._generate_corrected_template(template_structure, corrections)
        
        return {
            'issues': issues,
            'corrections': corrections,
            'corrected_template': corrected_template,
            'is_valid': len(issues) == 0
        }
    
    def _validate_single_example(self, template: Dict, example: Dict, example_name: str) -> List[Dict]:
        """Validate a single example against the template"""
        issues = []
        
        # Handle different example formats
        if isinstance(example, list):
            # Array of objects
            for i, item in enumerate(example):
                if isinstance(item, dict):
                    item_issues = self._validate_object_against_template(template, item, f"{example_name}[{i}]")
                    issues.extend(item_issues)
        else:
            # Single object
            issues = self._validate_object_against_template(template, example, example_name)
        
        return issues
    
    def _validate_object_against_template(self, template: Dict, obj: Dict, path: str) -> List[Dict]:
        """Validate an object against template structure"""
        issues = []
        
        for field, template_value in template.items():
            if field not in obj:
                continue
                
            actual_value = obj[field]
            field_path = f"{path}.{field}"
            
            # Check if template value matches actual value
            if isinstance(template_value, str):
                if template_value.startswith('[') and template_value.endswith(']'):
                    # ENUM field - check if actual value is in the enum
                    enum_values = self._extract_enum_values(template_value)
                    if actual_value not in enum_values:
                        issues.append({
                            'type': 'enum_mismatch',
                            'field_path': field_path,
                            'template_value': template_value,
                            'actual_value': actual_value,
                            'correction': self._suggest_correction(actual_value, field)
                        })
                elif template_value.startswith('<') and template_value.endswith('>'):
                    # Placeholder field - check if it's appropriate
                    if not self._validate_placeholder(template_value, actual_value):
                        issues.append({
                            'type': 'placeholder_mismatch',
                            'field_path': field_path,
                            'template_value': template_value,
                            'actual_value': actual_value,
                            'correction': self._suggest_correction(actual_value, field)
                        })
            elif isinstance(template_value, dict) and isinstance(actual_value, dict):
                # Nested object
                nested_issues = self._validate_object_against_template(template_value, actual_value, field_path)
                issues.extend(nested_issues)
            elif isinstance(template_value, list) and isinstance(actual_value, list):
                # Array
                if template_value and isinstance(template_value[0], dict):
                    for i, item in enumerate(actual_value):
                        if isinstance(item, dict):
                            nested_issues = self._validate_object_against_template(template_value[0], item, f"{field_path}[{i}]")
                            issues.extend(nested_issues)
        
        return issues
    
    def _extract_enum_values(self, enum_string: str) -> List[str]:
        """Extract enum values from string like '[RED, WHITE, BLUE]'"""
        if not (enum_string.startswith('[') and enum_string.endswith(']')):
            return []
        
        content = enum_string[1:-1]
        return [value.strip() for value in content.split(',')]
    
    def _validate_placeholder(self, placeholder: str, value: Any) -> bool:
        """Validate if a value matches the placeholder type"""
        if placeholder == '<ts>' or placeholder == '<datetime>':
            return bool(re.match(self.datetime_pattern, str(value)))
        elif placeholder == '<uuid>':
            return bool(re.match(self.uuid_pattern, str(value)))
        elif placeholder == '<moduleId>':
            return bool(re.match(self.module_id_pattern, str(value)))
        elif placeholder == '<nfcCode>':
            return len(str(value)) == 14 and str(value).startswith('04')
        elif placeholder == '<number>':
            return isinstance(value, (int, float)) or str(value).replace('.', '').replace('-', '').isdigit()
        elif placeholder == '<boolean>':
            return isinstance(value, bool) or str(value).lower() in ['true', 'false', '1', '0']
        else:
            return True  # Unknown placeholder type
    
    def _suggest_correction(self, value: Any, field_name: str) -> str:
        """Suggest correction for template field"""
        if isinstance(value, bool) or str(value).lower() in ['true', 'false', '1', '0']:
            return '<boolean>'
        elif isinstance(value, (int, float)) or str(value).replace('.', '').replace('-', '').isdigit():
            return '<number>'
        elif re.match(self.datetime_pattern, str(value)):
            return '<datetime>'
        elif re.match(self.uuid_pattern, str(value)):
            return '<uuid>'
        elif re.match(self.module_id_pattern, str(value)):
            return '<moduleId>'
        elif len(str(value)) == 14 and str(value).startswith('04'):
            return '<nfcCode>'
        else:
            # For string values, we need to collect more examples to determine if it's an enum
            return f'<string> or potential enum: [{value}]'
    
    def _generate_corrected_template(self, original_template: Dict, corrections: Dict) -> Dict:
        """Generate corrected template based on validation issues"""
        corrected = original_template.copy()
        
        for field_path, correction_list in corrections.items():
            # Find the most common correction
            correction_counts = {}
            for correction in correction_list:
                correction_counts[correction] = correction_counts.get(correction, 0) + 1
            
            most_common = max(correction_counts.items(), key=lambda x: x[1])[0]
            
            # Apply correction to template
            self._set_nested_value(corrected, field_path, most_common)
        
        return corrected
    
    def _set_nested_value(self, obj: Dict, path: str, value: Any):
        """Set value in nested dictionary using dot notation"""
        parts = path.split('.')
        current = obj
        
        for part in parts[:-1]:
            if '[' in part:
                # Handle array access
                field_name, index_str = part.split('[')
                index = int(index_str.rstrip(']'))
                if field_name not in current:
                    current[field_name] = []
                while len(current[field_name]) <= index:
                    current[field_name].append({})
                current = current[field_name][index]
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
        
        # Set final value
        last_part = parts[-1]
        if '[' in last_part:
            field_name, index_str = last_part.split('[')
            index = int(index_str.rstrip(']'))
            if field_name not in current:
                current[field_name] = []
            while len(current[field_name]) <= index:
                current[field_name].append({})
            current[field_name][index] = value
        else:
            current[last_part] = value

def main():
    """Test the template validator"""
    validator = TemplateValidator()
    
    # Test with TXT order template
    template = {
        "ts": "<ts>",
        "state": "[RAW]"
    }
    
    examples = [
        {
            "ts": "2025-08-19T09:16:14.679Z",
            "type": "RED",
            "state": "IN_PROCESS"
        },
        {
            "ts": "2025-08-19T09:16:15.123Z",
            "type": "WHITE",
            "state": "WAITING_FOR_ORDER"
        }
    ]
    
    result = validator.validate_template_against_examples(template, examples)
    
    print("🔍 Template Validation Results:")
    print(f"Valid: {result['is_valid']}")
    print(f"Issues found: {len(result['issues'])}")
    
    for issue in result['issues']:
        print(f"❌ {issue['field_path']}: {issue['template_value']} != {issue['actual_value']}")
        print(f"   Suggestion: {issue['correction']}")
    
    print("\n✅ Corrected Template:")
    print(json.dumps(result['corrected_template'], indent=2))

if __name__ == "__main__":
    main()
