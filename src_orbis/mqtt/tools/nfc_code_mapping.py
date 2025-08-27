#!/usr/bin/env python3
"""
NFC Code Mapping
Central definition of NFC codes with friendly names for consistent use across analyzers
"""

# NFC Code to friendly name mapping
NFC_CODE_MAPPING = {
    # RED Workpieces (R1-R8)
    "040a8dca341291": "R1",
    "047f8cca341290": "R2", 
    "04808dca341291": "R3",
    "04818dca341290": "R4",
    "04828dca341291": "R5",
    "04838dca341290": "R6",
    "04848dca341291": "R7",
    "04858dca341290": "R8",
    
    # WHITE Workpieces (W1-W8)
    "04798eca341290": "W1",
    "04ab8bca341290": "W2",
    "04ac8bca341291": "W3", 
    "04ad8bca341290": "W4",
    "04ae8bca341291": "W5",
    "04af8bca341290": "W6",
    "04b08bca341291": "W7",
    "04b18bca341290": "W8",
    
    # BLUE Workpieces (B1-B8)
    "047389ca341291": "B1",
    "047489ca341290": "B2",
    "047589ca341291": "B3",
    "047689ca341290": "B4", 
    "047789ca341291": "B5",
    "047889ca341290": "B6",
    "047989ca341291": "B7",
    "047a89ca341290": "B8"
}

# Reverse mapping (friendly name to NFC code)
FRIENDLY_TO_NFC = {v: k for k, v in NFC_CODE_MAPPING.items()}

# NFC codes by color
RED_NFC_CODES = [code for code, name in NFC_CODE_MAPPING.items() if name.startswith('R')]
WHITE_NFC_CODES = [code for code, name in NFC_CODE_MAPPING.items() if name.startswith('W')]
BLUE_NFC_CODES = [code for code, name in NFC_CODE_MAPPING.items() if name.startswith('B')]

# All NFC codes
ALL_NFC_CODES = list(NFC_CODE_MAPPING.keys())

def get_friendly_name(nfc_code: str) -> str:
    """Get friendly name for NFC code"""
    return NFC_CODE_MAPPING.get(nfc_code, nfc_code)

def get_nfc_code(friendly_name: str) -> str:
    """Get NFC code for friendly name"""
    return FRIENDLY_TO_NFC.get(friendly_name, friendly_name)

def is_nfc_code(value: str) -> bool:
    """Check if value is a known NFC code"""
    return value in ALL_NFC_CODES

def get_nfc_codes_by_color(color: str) -> list:
    """Get all NFC codes for a specific color"""
    color = color.upper()
    if color == 'RED':
        return RED_NFC_CODES
    elif color == 'WHITE':
        return WHITE_NFC_CODES
    elif color == 'BLUE':
        return BLUE_NFC_CODES
    else:
        return []
