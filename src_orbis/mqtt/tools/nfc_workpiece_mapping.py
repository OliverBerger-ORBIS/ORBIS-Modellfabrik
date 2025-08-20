#!/usr/bin/env python3
"""
NFC Workpiece Mapping
Maps NFC codes to user-friendly workpiece IDs
"""

from typing import Dict, Optional, List

# NFC-Code zu Werkstück-ID Zuordnung (basierend auf tatsächlichen Session-Daten)
NFC_WORKPIECE_MAPPING = {
    # 🔴 Rote Werkstücke (MILL - Fräsen)
    "R1": "040a8dca341291",  # ✅ Eingelagert (Session nfc-lesen-rot)
    "R2": "04d78cca341290",  # ✅ Eingelagert (Session nfc-lesen-rot)
    "R3": "04808dca341291",  # ✅ Eingelagert (Session nfc-lesen-rot)
    "R4": "04f08dca341290",  # ✅ Gefunden (Session nfc-lesen-rot)
    "R5": "04158cca341291",  # ✅ Gefunden (Session nfc-lesen-rot)
    "R6": "04fa8cca341290",  # ✅ Gefunden (Session nfc-lesen-rot)
    "R7": "047f8cca341290",  # ✅ Gefunden (Session nfc-lesen-rot)
    "R8": "048a8cca341290",  # ✅ Gefunden (Session nfc-lesen-rot)
    
    # ⚪ Weiße Werkstücke (DRILL - Bohren)
    "W1": "04798eca341290",  # ✅ Eingelagert (Session nfc-lesen-weiss)
    "W2": "047c8bca341291",  # ✅ Eingelagert (Session nfc-lesen-weiss)
    "W3": "047b8bca341291",  # ✅ Eingelagert (Session nfc-lesen-weiss)
    "W4": "04c38bca341290",  # ✅ Gefunden (Session nfc-lesen-weiss)
    "W5": "04ab8bca341290",  # ✅ Gefunden (Session nfc-lesen-weiss)
    "W6": "04368bca341291",  # ✅ Gefunden (Session nfc-lesen-weiss)
    "W7": "04c090ca341290",  # ✅ Gefunden (Session nfc-lesen-weiss)
    "W8": "042c8aca341291",  # ✅ Gefunden (Session nfc-lesen-weiss)
    
    # 🔵 Blaue Werkstücke (DRILL + MILL - Bohren + Fräsen)
    "B1": "04a189ca341290",  # ✅ Eingelagert (Session nfc-lesen-blau)
    "B2": "048989ca341290",  # ✅ Eingelagert (Session nfc-lesen-blau)
    "B3": "047389ca341291",  # ✅ Eingelagert (Session nfc-lesen-blau)
    "B4": "040c89ca341291",  # ✅ Gefunden (Session nfc-lesen-blau)
    "B5": "04a289ca341290",  # ✅ Gefunden (Session nfc-lesen-blau)
    "B6": "04c489ca341290",  # ✅ Gefunden (Session nfc-lesen-blau)
    "B7": "048089ca341290",  # ✅ Gefunden (Session nfc-lesen-blau)
    "B8": "042c88ca341291",  # ✅ Gefunden (Session nfc-lesen-blau)
}

# Reverse mapping (NFC-Code → ID)
NFC_TO_ID_MAPPING = {v: k for k, v in NFC_WORKPIECE_MAPPING.items() if v is not None}

# Farb-Zuordnung
WORKPIECE_COLORS = {
    "R1": "RED", "R2": "RED", "R3": "RED", "R4": "RED", 
    "R5": "RED", "R6": "RED", "R7": "RED", "R8": "RED",
    "W1": "WHITE", "W2": "WHITE", "W3": "WHITE", "W4": "WHITE",
    "W5": "WHITE", "W6": "WHITE", "W7": "WHITE", "W8": "WHITE",
    "B1": "BLUE", "B2": "BLUE", "B3": "BLUE", "B4": "BLUE",
    "B5": "BLUE", "B6": "BLUE", "B7": "BLUE", "B8": "BLUE",
}

class NFCWorkpieceMapper:
    """Maps NFC codes to user-friendly workpiece IDs"""
    
    def __init__(self):
        self.mapping = NFC_WORKPIECE_MAPPING
        self.reverse_mapping = NFC_TO_ID_MAPPING
        self.colors = WORKPIECE_COLORS
    
    def get_nfc_code(self, workpiece_id: str) -> Optional[str]:
        """Get NFC code for workpiece ID"""
        return self.mapping.get(workpiece_id)
    
    def get_workpiece_id(self, nfc_code: str) -> Optional[str]:
        """Get workpiece ID for NFC code"""
        return self.reverse_mapping.get(nfc_code)
    
    def get_color(self, workpiece_id: str) -> Optional[str]:
        """Get color for workpiece ID"""
        return self.colors.get(workpiece_id)
    
    def get_available_workpieces(self, color: str = None) -> List[str]:
        """Get list of available workpiece IDs"""
        if color is None:
            return [wid for wid, nfc in self.mapping.items() if nfc is not None]
        else:
            return [wid for wid, nfc in self.mapping.items() 
                   if nfc is not None and self.colors.get(wid) == color]
    
    def get_red_workpieces(self) -> List[str]:
        """Get list of red workpieces"""
        return self.get_available_workpieces("RED")
    
    def get_white_workpieces(self) -> List[str]:
        """Get list of white workpieces"""
        return self.get_available_workpieces("WHITE")
    
    def get_blue_workpieces(self) -> List[str]:
        """Get list of blue workpieces"""
        return self.get_available_workpieces("BLUE")
    
    def is_valid_workpiece_id(self, workpiece_id: str) -> bool:
        """Check if workpiece ID is valid and has NFC code"""
        return workpiece_id in self.mapping and self.mapping[workpiece_id] is not None
    
    def get_workpiece_info(self, workpiece_id: str) -> Dict:
        """Get complete workpiece information"""
        nfc_code = self.get_nfc_code(workpiece_id)
        color = self.get_color(workpiece_id)
        
        if nfc_code is None:
            return None
            
        return {
            "id": workpiece_id,
            "nfc_code": nfc_code,
            "color": color,
            "processing": self._get_processing_info(color)
        }
    
    def _get_processing_info(self, color: str) -> str:
        """Get processing information for color"""
        processing_map = {
            "RED": "MILL (Fräsen)",
            "WHITE": "DRILL (Bohren)", 
            "BLUE": "DRILL + MILL (Bohren + Fräsen)"
        }
        return processing_map.get(color, "Unknown")
    
    def get_statistics(self) -> Dict:
        """Get mapping statistics"""
        total_workpieces = len(self.mapping)
        available_workpieces = len([wid for wid, nfc in self.mapping.items() if nfc is not None])
        
        red_count = len(self.get_red_workpieces())
        white_count = len(self.get_white_workpieces())
        blue_count = len(self.get_blue_workpieces())
        
        return {
            "total_workpieces": total_workpieces,
            "available_workpieces": available_workpieces,
            "missing_workpieces": total_workpieces - available_workpieces,
            "red_workpieces": red_count,
            "white_workpieces": white_count,
            "blue_workpieces": blue_count,
            "completion_percentage": (available_workpieces / total_workpieces) * 100
        }


def create_nfc_mapper() -> NFCWorkpieceMapper:
    """Create NFC workpiece mapper instance"""
    return NFCWorkpieceMapper()


if __name__ == "__main__":
    # Test des NFC Mappers
    print("🧪 NFC Workpiece Mapper Test")
    print("=" * 50)
    
    mapper = create_nfc_mapper()
    
    # Statistiken
    stats = mapper.get_statistics()
    print(f"📊 Statistiken:")
    print(f"  Gesamt Werkstücke: {stats['total_workpieces']}")
    print(f"  Verfügbar: {stats['available_workpieces']}")
    print(f"  Fehlend: {stats['missing_workpieces']}")
    print(f"  Vervollständigung: {stats['completion_percentage']:.1f}%")
    
    # Farb-Verteilung
    print(f"\n🎨 Farb-Verteilung:")
    print(f"  🔴 Rot: {stats['red_workpieces']}/8")
    print(f"  ⚪ Weiß: {stats['white_workpieces']}/8")
    print(f"  🔵 Blau: {stats['blue_workpieces']}/8")
    
    # Verfügbare Werkstücke
    print(f"\n✅ Verfügbare Werkstücke:")
    for color in ["RED", "WHITE", "BLUE"]:
        workpieces = mapper.get_available_workpieces(color)
        color_emoji = {"RED": "🔴", "WHITE": "⚪", "BLUE": "🔵"}[color]
        print(f"  {color_emoji} {color}: {', '.join(workpieces)}")
    
    # Test Mapping
    print(f"\n🔍 Mapping Tests:")
    test_id = "R1"
    nfc_code = mapper.get_nfc_code(test_id)
    color = mapper.get_color(test_id)
    info = mapper.get_workpiece_info(test_id)
    
    print(f"  {test_id} → NFC: {nfc_code}")
    print(f"  {test_id} → Farbe: {color}")
    print(f"  {test_id} → Info: {info}")
    
    print("\n✅ NFC Workpiece Mapper Test abgeschlossen")
