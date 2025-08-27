#!/usr/bin/env python3
"""
Module Mapping Utilities - Provides access to centralized module and enum mappings
"""

import json
import os
from typing import Dict, List, Optional, Any

class ModuleMappingUtils:
    def __init__(self):
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_file = os.path.join(script_dir, 'module_mapping.json')
        
        with open(mapping_file, 'r', encoding='utf-8') as f:
            self.mapping_data = json.load(f)
    
    def get_module_info(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get complete module information by module ID"""
        # Check in modules first
        if module_id in self.mapping_data['modules']:
            return self.mapping_data['modules'][module_id]
        
        # Check in transports
        if module_id in self.mapping_data['transports']:
            return self.mapping_data['transports'][module_id]
        
        return None
    
    def get_module_name(self, module_id: str) -> str:
        """Get friendly module name by module ID"""
        module_info = self.get_module_info(module_id)
        if module_info:
            return module_info['moduleName']
        return module_id
    
    def get_module_name_long_de(self, module_id: str) -> str:
        """Get German long module name by module ID"""
        module_info = self.get_module_info(module_id)
        if module_info:
            return module_info.get('moduleNameLong_DE', module_id)
        return module_id
    
    def get_module_name_long_en(self, module_id: str) -> str:
        """Get English long module name by module ID"""
        module_info = self.get_module_info(module_id)
        if module_info:
            return module_info.get('moduleNameLong_EN', module_id)
        return module_id
    
    def get_module_ip(self, module_id: str) -> Optional[str]:
        """Get module IP address by module ID"""
        module_info = self.get_module_info(module_id)
        if module_info:
            return module_info.get('ip')
        return None
    
    def get_module_commands(self, module_id: str) -> List[str]:
        """Get available commands for a module"""
        module_info = self.get_module_info(module_id)
        if module_info:
            return module_info.get('commands', [])
        return []
    
    def get_enum_description(self, enum_type: str, enum_value: str) -> str:
        """Get description for an enum value"""
        if enum_type in self.mapping_data['enums']:
            enum_dict = self.mapping_data['enums'][enum_type]
            return enum_dict.get(enum_value, enum_value)
        return enum_value
    
    def get_all_module_ids(self) -> List[str]:
        """Get all available module IDs"""
        module_ids = list(self.mapping_data['modules'].keys())
        transport_ids = list(self.mapping_data['transports'].keys())
        return module_ids + transport_ids
    
    def get_modules_by_type(self, module_type: str) -> List[Dict[str, Any]]:
        """Get all modules of a specific type"""
        modules = []
        for module_id, module_info in self.mapping_data['modules'].items():
            if module_info.get('type') == module_type:
                modules.append(module_info)
        
        for transport_id, transport_info in self.mapping_data['transports'].items():
            if transport_info.get('type') == module_type:
                modules.append(transport_info)
        
        return modules
    
    def get_enum_values(self, enum_type: str) -> List[str]:
        """Get all values for an enum type"""
        if enum_type in self.mapping_data['enums']:
            return list(self.mapping_data['enums'][enum_type].keys())
        return []
    
    def get_enum_descriptions(self, enum_type: str) -> Dict[str, str]:
        """Get all descriptions for an enum type"""
        if enum_type in self.mapping_data['enums']:
            return self.mapping_data['enums'][enum_type]
        return {}
    
    def get_nfc_friendly_name(self, nfc_code: str) -> str:
        """Get friendly name for NFC code (e.g., '040a8dca341291' -> 'R1')"""
        if 'nfcCodes' in self.mapping_data['enums']:
            return self.mapping_data['enums']['nfcCodes'].get(nfc_code, nfc_code)
        return nfc_code
    
    def get_nfc_code_from_friendly(self, friendly_name: str) -> str:
        """Get NFC code from friendly name (e.g., 'R1' -> '040a8dca341291')"""
        if 'nfcCodes' in self.mapping_data['enums']:
            nfc_codes = self.mapping_data['enums']['nfcCodes']
            for nfc_code, friendly in nfc_codes.items():
                if friendly == friendly_name:
                    return nfc_code
        return friendly_name
    
    def get_all_nfc_codes(self) -> Dict[str, str]:
        """Get all NFC code mappings"""
        if 'nfcCodes' in self.mapping_data['enums']:
            return self.mapping_data['enums']['nfcCodes']
        return {}
    
    def get_nfc_codes_by_color(self, color: str) -> Dict[str, str]:
        """Get NFC codes for a specific color (RED, WHITE, BLUE)"""
        if 'nfcCodes' in self.mapping_data['enums']:
            nfc_codes = self.mapping_data['enums']['nfcCodes']
            color_codes = {}
            
            for nfc_code, friendly in nfc_codes.items():
                if color == "RED" and friendly.startswith("R"):
                    color_codes[nfc_code] = friendly
                elif color == "WHITE" and friendly.startswith("W"):
                    color_codes[nfc_code] = friendly
                elif color == "BLUE" and friendly.startswith("B"):
                    color_codes[nfc_code] = friendly
            
            return color_codes
        return {}
    
    def validate_nfc_code(self, nfc_code: str) -> bool:
        """Check if an NFC code exists in the mapping"""
        if 'nfcCodes' in self.mapping_data['enums']:
            return nfc_code in self.mapping_data['enums']['nfcCodes']
        return False
    
    def format_nfc_display_name(self, nfc_code: str, include_code: bool = True) -> str:
        """Format NFC code for display (e.g., 'R1 (040a8dca341291)')"""
        friendly_name = self.get_nfc_friendly_name(nfc_code)
        if include_code and friendly_name != nfc_code:
            return f"{friendly_name} ({nfc_code})"
        return friendly_name
    
    def format_module_display_name(self, module_id: str, include_id: bool = True) -> str:
        """Format module name for display (e.g., 'HBW (SVR3QA0022)')"""
        module_name = self.get_module_name(module_id)
        if include_id:
            return f"{module_name} ({module_id})"
        return module_name
    
    def get_module_by_name(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get module info by friendly name (e.g., 'HBW')"""
        for module_id, module_info in self.mapping_data['modules'].items():
            if module_info['moduleName'] == module_name:
                return module_info
        
        for transport_id, transport_info in self.mapping_data['transports'].items():
            if transport_info['moduleName'] == module_name:
                return transport_info
        
        return None
    
    def validate_module_id(self, module_id: str) -> bool:
        """Check if a module ID exists in the mapping"""
        return module_id in self.mapping_data['modules'] or module_id in self.mapping_data['transports']
    
    def get_mapping_summary(self) -> Dict[str, Any]:
        """Get a summary of all mappings"""
        return {
            'total_modules': len(self.mapping_data['modules']),
            'total_transports': len(self.mapping_data['transports']),
            'total_enum_types': len(self.mapping_data['enums']),
            'module_ids': list(self.mapping_data['modules'].keys()),
            'transport_ids': list(self.mapping_data['transports'].keys()),
            'enum_types': list(self.mapping_data['enums'].keys()),
            'metadata': self.mapping_data['metadata']
        }

def main():
    """Test the module mapping utilities"""
    utils = ModuleMappingUtils()
    
    print("🔧 Module Mapping Utilities Test")
    print("=" * 50)
    
    # Test module info
    print(f"📋 HBW Module Info: {utils.get_module_info('SVR3QA0022')}")
    print(f"📋 HBW Name: {utils.get_module_name('SVR3QA0022')}")
    print(f"📋 HBW Long Name (DE): {utils.get_module_name_long_de('SVR3QA0022')}")
    print(f"📋 HBW IP: {utils.get_module_ip('SVR3QA0022')}")
    print(f"📋 HBW Commands: {utils.get_module_commands('SVR3QA0022')}")
    
    # Test enum descriptions
    print(f"📋 RED Description: {utils.get_enum_description('workpieceTypes', 'RED')}")
    print(f"📋 IN_PROCESS Description: {utils.get_enum_description('workpieceStates', 'IN_PROCESS')}")
    
    # Test display formatting
    print(f"📋 Display Name: {utils.format_module_display_name('SVR3QA0022')}")
    
    # Test NFC code functions
    print(f"📋 NFC Code R1: {utils.get_nfc_friendly_name('040a8dca341291')}")
    print(f"📋 NFC Code B3: {utils.get_nfc_friendly_name('047389ca341291')}")
    print(f"📋 NFC Code W5: {utils.get_nfc_friendly_name('04ab8bca341290')}")
    print(f"📋 NFC Display: {utils.format_nfc_display_name('040a8dca341291')}")
    print(f"📋 RED NFC Codes: {utils.get_nfc_codes_by_color('RED')}")
    
    # Test summary
    summary = utils.get_mapping_summary()
    print(f"📊 Summary: {summary['total_modules']} modules, {summary['total_transports']} transports")
    print(f"📊 Enum Types: {summary['enum_types']}")

if __name__ == "__main__":
    main()
