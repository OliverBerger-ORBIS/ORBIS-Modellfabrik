#!/usr/bin/env python3
"""
Unit Tests for Unified Type Recognition Strategy
Tests both TXT and CCU analyzers to ensure consistent type recognition
"""

import sys
import os
import unittest
from typing import Set, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(project_root)

from src_orbis.mqtt.tools.txt_template_analyzer import TXTTemplateAnalyzer
from src_orbis.mqtt.tools.ccu_template_analyzer import CCUTemplateAnalyzer
from src_orbis.mqtt.tools.module_mapping_utils import ModuleMappingUtils

class TestUnifiedTypeRecognition(unittest.TestCase):
    """Test unified type recognition across TXT and CCU analyzers"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.module_mapping = ModuleMappingUtils()
        self.txt_analyzer = TXTTemplateAnalyzer()
        self.ccu_analyzer = CCUTemplateAnalyzer()
    
    def test_number_recognition(self):
        """Test number recognition is consistent"""
        test_cases = [
            ({"1", "2", "3"}, "<number>"),
            ({1, 2, 3}, "<number>"),
            ({1.5, 2.5, 3.5}, "<number>"),
            ({"1.5", "2.5", "3.5"}, "<number>"),
            ({"-1", "-2", "-3"}, "<number>"),
        ]
        
        for values, expected in test_cases:
            with self.subTest(values=values):
                txt_result = self.txt_analyzer.get_placeholder_for_field("count", values)
                ccu_result = self.ccu_analyzer.get_placeholder_for_field("count", values)
                
                self.assertEqual(txt_result, expected, f"TXT failed for {values}")
                self.assertEqual(ccu_result, expected, f"CCU failed for {values}")
                self.assertEqual(txt_result, ccu_result, f"Results differ for {values}")
    
    def test_boolean_recognition(self):
        """Test boolean recognition is consistent"""
        test_cases = [
            ({"true", "false"}, "<boolean>"),
            ({True, False}, "<boolean>"),
            ({"1", "0"}, "<boolean>"),
            ({"true", "false", "1", "0"}, "<boolean>"),
        ]
        
        for values, expected in test_cases:
            with self.subTest(values=values):
                txt_result = self.txt_analyzer.get_placeholder_for_field("connected", values)
                ccu_result = self.ccu_analyzer.get_placeholder_for_field("connected", values)
                
                self.assertEqual(txt_result, expected, f"TXT failed for {values}")
                self.assertEqual(ccu_result, expected, f"CCU failed for {values}")
                self.assertEqual(txt_result, ccu_result, f"Results differ for {values}")
    
    def test_datetime_recognition(self):
        """Test datetime recognition is consistent"""
        test_cases = [
            ({"2025-08-19T09:16:14.679Z"}, "<datetime>"),
            ({"2025-08-19T09:16:14.679+02:00"}, "<datetime>"),
        ]
        
        for values, expected in test_cases:
            with self.subTest(values=values):
                txt_result = self.txt_analyzer.get_placeholder_for_field("timestamp", values)
                ccu_result = self.ccu_analyzer.get_placeholder_for_field("timestamp", values)
                
                self.assertEqual(txt_result, expected, f"TXT failed for {values}")
                self.assertEqual(ccu_result, expected, f"CCU failed for {values}")
                self.assertEqual(txt_result, ccu_result, f"Results differ for {values}")
    
    def test_uuid_recognition(self):
        """Test UUID recognition is consistent"""
        test_cases = [
            ({"123e4567-e89b-12d3-a456-426614174000"}, "<uuid>"),
            ({"987fcdeb-51a2-43c1-b567-890123456789"}, "<uuid>"),
        ]
        
        for values, expected in test_cases:
            with self.subTest(values=values):
                txt_result = self.txt_analyzer.get_placeholder_for_field("orderId", values)
                ccu_result = self.ccu_analyzer.get_placeholder_for_field("orderId", values)
                
                self.assertEqual(txt_result, expected, f"TXT failed for {values}")
                self.assertEqual(ccu_result, expected, f"CCU failed for {values}")
                self.assertEqual(txt_result, ccu_result, f"Results differ for {values}")
    
    def test_module_id_recognition(self):
        """Test module ID recognition is consistent"""
        test_cases = [
            ({"SVR3QA0022"}, "<moduleId>"),
            ({"SVR123456789"}, "<moduleId>"),
        ]
        
        for values, expected in test_cases:
            with self.subTest(values=values):
                txt_result = self.txt_analyzer.get_placeholder_for_field("serialNumber", values)
                ccu_result = self.ccu_analyzer.get_placeholder_for_field("serialNumber", values)
                
                self.assertEqual(txt_result, expected, f"TXT failed for {values}")
                self.assertEqual(ccu_result, expected, f"CCU failed for {values}")
                self.assertEqual(txt_result, ccu_result, f"Results differ for {values}")
    
    def test_nfc_code_recognition(self):
        """Test NFC code recognition is consistent"""
        test_cases = [
            ({"040a8dca341291"}, "<nfcCode>"),
            ({"04d78cca341290"}, "<nfcCode>"),
        ]
        
        for values, expected in test_cases:
            with self.subTest(values=values):
                txt_result = self.txt_analyzer.get_placeholder_for_field("workpieceId", values)
                ccu_result = self.ccu_analyzer.get_placeholder_for_field("workpieceId", values)
                
                self.assertEqual(txt_result, expected, f"TXT failed for {values}")
                self.assertEqual(ccu_result, expected, f"CCU failed for {values}")
                self.assertEqual(txt_result, ccu_result, f"Results differ for {values}")
    
    def test_txt_specific_enums(self):
        """Test TXT-specific ENUM recognition"""
        # Test workpiece types
        type_values = {"RED", "WHITE", "BLUE"}
        result = self.txt_analyzer.get_placeholder_for_field("type", type_values)
        self.assertIn("RED", result)
        self.assertIn("WHITE", result)
        self.assertIn("BLUE", result)
        self.assertTrue(result.startswith("[") and result.endswith("]"))
        
        # Test workpiece states (TXT-specific)
        state_values = {"RAW", "IN_PROCESS", "WAITING_FOR_ORDER"}
        result = self.txt_analyzer.get_placeholder_for_field("state", state_values)
        self.assertIn("RAW", result)
        self.assertIn("IN_PROCESS", result)
        self.assertIn("WAITING_FOR_ORDER", result)
        self.assertTrue(result.startswith("[") and result.endswith("]"))
        
        # Test locations
        location_values = {"A1", "B2", "C3"}
        result = self.txt_analyzer.get_placeholder_for_field("location", location_values)
        self.assertIn("A1", result)
        self.assertIn("B2", result)
        self.assertIn("C3", result)
        self.assertTrue(result.startswith("[") and result.endswith("]"))
    
    def test_ccu_specific_enums(self):
        """Test CCU-specific ENUM recognition"""
        # Test order types
        order_values = {"STORAGE", "PRODUCTION"}
        result = self.ccu_analyzer.get_placeholder_for_field("orderType", order_values)
        self.assertIn("STORAGE", result)
        self.assertIn("PRODUCTION", result)
        self.assertTrue(result.startswith("[") and result.endswith("]"))
        
        # Test action states (CCU-specific)
        state_values = {"IN_PROGRESS", "ENQUEUED", "COMPLETED"}
        result = self.ccu_analyzer.get_placeholder_for_field("state", state_values)
        self.assertIn("IN_PROGRESS", result)
        self.assertIn("ENQUEUED", result)
        self.assertIn("COMPLETED", result)
        self.assertTrue(result.startswith("[") and result.endswith("]"))
    
    def test_generic_enum_recognition(self):
        """Test generic ENUM recognition for unknown fields"""
        test_cases = [
            ({"value1", "value2", "value3"}, "[value1, value2, value3]"),
            ({"optionA", "optionB"}, "[optionA, optionB]"),
        ]
        
        for values, expected in test_cases:
            with self.subTest(values=values):
                txt_result = self.txt_analyzer.get_placeholder_for_field("unknown", values)
                ccu_result = self.ccu_analyzer.get_placeholder_for_field("unknown", values)
                
                self.assertEqual(txt_result, expected, f"TXT failed for {values}")
                self.assertEqual(ccu_result, expected, f"CCU failed for {values}")
                self.assertEqual(txt_result, ccu_result, f"Results differ for {values}")
    
    def test_priority_order(self):
        """Test that type recognition follows the correct priority order"""
        # Mixed values should default to string (not ENUM)
        mixed_values = {"1", "2", "3", "value1", "value2"}
        result = self.txt_analyzer.get_placeholder_for_field("mixed", mixed_values)
        self.assertEqual(result, "<string>", "Mixed values should default to string")
        
        # Mixed boolean-like values should default to string
        bool_like_values = {"true", "false", "other"}
        result = self.txt_analyzer.get_placeholder_for_field("bool_like", bool_like_values)
        self.assertEqual(result, "<string>", "Mixed boolean-like values should default to string")
    
    def test_context_aware_recognition(self):
        """Test context-aware recognition for CCU"""
        # Test context-aware type field
        context_values = {("productionSteps.type", "NAVIGATION"), ("productionSteps.type", "MANUFACTURE")}
        result = self.ccu_analyzer.get_placeholder_for_field("type", context_values)
        self.assertIn("NAVIGATION", result)
        self.assertIn("MANUFACTURE", result)
        self.assertTrue(result.startswith("[") and result.endswith("]"))
    
    def test_empty_values(self):
        """Test handling of empty values"""
        empty_values = set()
        txt_result = self.txt_analyzer.get_placeholder_for_field("empty", empty_values)
        ccu_result = self.ccu_analyzer.get_placeholder_for_field("empty", empty_values)
        
        self.assertEqual(txt_result, "<string>")
        self.assertEqual(ccu_result, "<string>")
        self.assertEqual(txt_result, ccu_result)
    
    def test_single_value(self):
        """Test handling of single values"""
        single_values = {"single"}
        txt_result = self.txt_analyzer.get_placeholder_for_field("single", single_values)
        ccu_result = self.ccu_analyzer.get_placeholder_for_field("single", single_values)
        
        self.assertEqual(txt_result, "[single]")
        self.assertEqual(ccu_result, "[single]")
        self.assertEqual(txt_result, ccu_result)

def run_comprehensive_test():
    """Run a comprehensive test with real-world examples"""
    print("🧪 Comprehensive Type Recognition Test")
    print("=" * 60)
    
    module_mapping = ModuleMappingUtils()
    txt_analyzer = TXTTemplateAnalyzer()
    ccu_analyzer = CCUTemplateAnalyzer()
    
    test_cases = [
        # Field name, values, expected result
        ("timestamp", {"2025-08-19T09:16:14.679Z"}, "<datetime>"),
        ("orderId", {"123e4567-e89b-12d3-a456-426614174000"}, "<uuid>"),
        ("type", {"RED", "WHITE", "BLUE"}, "[BLUE, RED, WHITE]"),
        ("state", {"IN_PROCESS", "WAITING_FOR_ORDER"}, "[COMPLETED, FINISHED, IN_PROCESS, RAW, RESERVED, WAITING_FOR_ORDER]"),  # TXT workpieceStates
        ("connected", {"true", "false"}, "<boolean>"),
        ("count", {1, 2, 3}, "<number>"),
        ("serialNumber", {"SVR3QA0022"}, "<moduleId>"),
        ("workpieceId", {"040a8dca341291"}, "<nfcCode>"),
        ("unknown", {"value1", "value2", "value3"}, "[value1, value2, value3]"),
        ("orderType", {"STORAGE", "PRODUCTION"}, "[PRODUCTION, STORAGE]"),
    ]
    
    all_passed = True
    
    for field_name, values, expected in test_cases:
        txt_result = txt_analyzer.get_placeholder_for_field(field_name, values)
        ccu_result = ccu_analyzer.get_placeholder_for_field(field_name, values)
        
        # Handle different expected results for TXT vs CCU
        if field_name == "state" and "IN_PROCESS" in values:
            # TXT uses workpieceStates, CCU uses actionStates
            # But IN_PROCESS and WAITING_FOR_ORDER are workpieceStates, not actionStates
            txt_expected = "[COMPLETED, FINISHED, IN_PROCESS, RAW, RESERVED, WAITING_FOR_ORDER]"
            ccu_expected = "[IN_PROCESS, WAITING_FOR_ORDER]"  # Generic ENUM since not in actionStates
        else:
            txt_expected = expected
            ccu_expected = expected
        
        txt_match = txt_result == txt_expected
        ccu_match = ccu_result == ccu_expected
        consistency = txt_result == ccu_result
        
        status = "✅" if txt_match and ccu_match else "❌"
        
        print(f"{status} {field_name}: {values}")
        print(f"   TXT Expected: {txt_expected}")
        print(f"   CCU Expected: {ccu_expected}")
        print(f"   TXT Result:   {txt_result}")
        print(f"   CCU Result:   {ccu_result}")
        print(f"   Match:        TXT={txt_match}, CCU={ccu_match}, Consistent={consistency}")
        print()
        
        if not (txt_match and ccu_match):
            all_passed = False
    
    if all_passed:
        print("🎉 ALL TESTS PASSED! Type recognition is unified and consistent.")
    else:
        print("⚠️  Some tests failed. Check the results above.")
    
    return all_passed

if __name__ == "__main__":
    # Run comprehensive test first
    print("Running comprehensive test...")
    comprehensive_passed = run_comprehensive_test()
    
    print("\n" + "=" * 60)
    print("Running unit tests...")
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    if comprehensive_passed:
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n⚠️  Some comprehensive tests failed!")
