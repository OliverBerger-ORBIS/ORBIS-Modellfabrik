#!/usr/bin/env python3
"""
Unit Tests for NFC Code Manager
Tests the NFCCodeManager class functionality
"""

import unittest
import os
import sys
import tempfile
import yaml

# Add src_orbis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src_orbis'))

from mqtt.tools.nfc_code_manager import NFCCodeManager


class TestNFCCodeManager(unittest.TestCase):
    """Test cases for NFCCodeManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary YAML config for testing
        self.test_config = {
            'metadata': {
                'version': '2.0',
                'description': 'Test NFC Configuration'
            },
            'nfc_codes': {
                '040a8dca341291': {
                    'friendly_id': 'R1',
                    'color': 'RED',
                    'quality_check': 'OK',
                    'description': 'Rotes Werkstück 1'
                },
                '04798eca341290': {
                    'friendly_id': 'W1',
                    'color': 'WHITE',
                    'quality_check': 'OK',
                    'description': 'Weißes Werkstück 1'
                },
                '047389ca341291': {
                    'friendly_id': 'B1',
                    'color': 'BLUE',
                    'quality_check': 'OK',
                    'description': 'Blaues Werkstück 1'
                },
                '047f8cca341290': {
                    'friendly_id': 'R2',
                    'color': 'RED',
                    'quality_check': 'NOT-OK',
                    'description': 'Rotes Werkstück 2'
                }
            },
            'quality_check_options': ['OK', 'NOT-OK', 'PENDING', 'FAILED'],
            'colors': ['RED', 'WHITE', 'BLUE'],
            'template_placeholders': {
                'nfc_code': '<nfcCode>',
                'workpiece_id': '<workpieceId>',
                'color': '<color>',
                'quality': '<quality>'
            },
            'mqtt_paths': [
                ['workpieceId'],
                ['metadata', 'workpiece', 'workpieceId'],
                ['loadId']
            ]
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
        yaml.dump(self.test_config, self.temp_file)
        self.temp_file.close()
        
        # Initialize manager with test config
        self.manager = NFCCodeManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_init_with_valid_config(self):
        """Test initialization with valid YAML config"""
        self.assertIsNotNone(self.manager.config)
        self.assertEqual(len(self.manager.config['nfc_codes']), 4)
    
    def test_init_with_invalid_path(self):
        """Test initialization with invalid config path"""
        with self.assertRaises(ValueError):
            NFCCodeManager("/nonexistent/path/config.yml")
    
    def test_get_friendly_name(self):
        """Test getting friendly name for NFC code"""
        # Test valid NFC code
        friendly_name = self.manager.get_friendly_name('040a8dca341291')
        self.assertEqual(friendly_name, 'R1')
        
        # Test invalid NFC code
        friendly_name = self.manager.get_friendly_name('invalid_code')
        self.assertEqual(friendly_name, 'invalid_code')
    
    def test_get_nfc_code(self):
        """Test getting NFC code for friendly name"""
        # Test valid friendly name
        nfc_code = self.manager.get_nfc_code('R1')
        self.assertEqual(nfc_code, '040a8dca341291')
        
        # Test invalid friendly name
        nfc_code = self.manager.get_nfc_code('INVALID')
        self.assertEqual(nfc_code, 'INVALID')
    
    def test_get_nfc_info(self):
        """Test getting complete NFC code information"""
        info = self.manager.get_nfc_info('040a8dca341291')
        self.assertIsNotNone(info)
        self.assertEqual(info['friendly_id'], 'R1')
        self.assertEqual(info['color'], 'RED')
        self.assertEqual(info['quality_check'], 'OK')
        self.assertEqual(info['description'], 'Rotes Werkstück 1')
        
        # Test invalid NFC code
        info = self.manager.get_nfc_info('invalid_code')
        self.assertIsNone(info)
    
    def test_get_nfc_codes_by_color(self):
        """Test getting NFC codes by color"""
        red_codes = self.manager.get_nfc_codes_by_color('RED')
        self.assertEqual(len(red_codes), 2)
        self.assertIn('040a8dca341291', red_codes)
        self.assertIn('047f8cca341290', red_codes)
        
        white_codes = self.manager.get_nfc_codes_by_color('WHITE')
        self.assertEqual(len(white_codes), 1)
        self.assertIn('04798eca341290', white_codes)
        
        blue_codes = self.manager.get_nfc_codes_by_color('BLUE')
        self.assertEqual(len(blue_codes), 1)
        self.assertIn('047389ca341291', blue_codes)
        
        # Test case insensitive
        red_codes_upper = self.manager.get_nfc_codes_by_color('red')
        self.assertEqual(red_codes, red_codes_upper)
    
    def test_get_nfc_codes_by_quality(self):
        """Test getting NFC codes by quality check status"""
        ok_codes = self.manager.get_nfc_codes_by_quality('OK')
        self.assertEqual(len(ok_codes), 3)
        self.assertIn('040a8dca341291', ok_codes)
        self.assertIn('04798eca341290', ok_codes)
        self.assertIn('047389ca341291', ok_codes)
        
        not_ok_codes = self.manager.get_nfc_codes_by_quality('NOT-OK')
        self.assertEqual(len(not_ok_codes), 1)
        self.assertIn('047f8cca341290', not_ok_codes)
    
    def test_get_all_nfc_codes(self):
        """Test getting all NFC codes"""
        all_codes = self.manager.get_all_nfc_codes()
        self.assertEqual(len(all_codes), 4)
        expected_codes = [
            '040a8dca341291',
            '04798eca341290',
            '047389ca341291',
            '047f8cca341290'
        ]
        for code in expected_codes:
            self.assertIn(code, all_codes)
    
    def test_get_all_friendly_names(self):
        """Test getting all friendly names"""
        friendly_names = self.manager.get_all_friendly_names()
        self.assertEqual(len(friendly_names), 4)
        expected_names = ['R1', 'W1', 'B1', 'R2']
        for name in expected_names:
            self.assertIn(name, friendly_names)
    
    def test_is_nfc_code(self):
        """Test checking if value is a known NFC code"""
        self.assertTrue(self.manager.is_nfc_code('040a8dca341291'))
        self.assertFalse(self.manager.is_nfc_code('invalid_code'))
    
    def test_is_friendly_name(self):
        """Test checking if value is a known friendly name"""
        self.assertTrue(self.manager.is_friendly_name('R1'))
        self.assertFalse(self.manager.is_friendly_name('INVALID'))
    
    def test_validate_nfc_code(self):
        """Test NFC code validation"""
        self.assertTrue(self.manager.validate_nfc_code('040a8dca341291'))
        self.assertFalse(self.manager.validate_nfc_code('invalid_code'))
    
    def test_get_color_for_nfc_code(self):
        """Test getting color for NFC code"""
        color = self.manager.get_color_for_nfc_code('040a8dca341291')
        self.assertEqual(color, 'RED')
        
        color = self.manager.get_color_for_nfc_code('invalid_code')
        self.assertIsNone(color)
    
    def test_get_quality_for_nfc_code(self):
        """Test getting quality check status for NFC code"""
        quality = self.manager.get_quality_for_nfc_code('040a8dca341291')
        self.assertEqual(quality, 'OK')
        
        quality = self.manager.get_quality_for_nfc_code('047f8cca341290')
        self.assertEqual(quality, 'NOT-OK')
        
        quality = self.manager.get_quality_for_nfc_code('invalid_code')
        self.assertIsNone(quality)
    
    def test_get_description_for_nfc_code(self):
        """Test getting description for NFC code"""
        description = self.manager.get_description_for_nfc_code('040a8dca341291')
        self.assertEqual(description, 'Rotes Werkstück 1')
        
        description = self.manager.get_description_for_nfc_code('invalid_code')
        self.assertIsNone(description)
    
    def test_format_nfc_display_name(self):
        """Test formatting NFC code for display"""
        # Test with code included
        display_name = self.manager.format_nfc_display_name('040a8dca341291', include_code=True)
        self.assertEqual(display_name, 'R1 (040a8dca341291)')
        
        # Test without code
        display_name = self.manager.format_nfc_display_name('040a8dca341291', include_code=False)
        self.assertEqual(display_name, 'R1')
        
        # Test invalid code
        display_name = self.manager.format_nfc_display_name('invalid_code', include_code=True)
        self.assertEqual(display_name, 'invalid_code')
    
    def test_get_mqtt_paths(self):
        """Test getting MQTT paths"""
        paths = self.manager.get_mqtt_paths()
        self.assertEqual(len(paths), 3)
        self.assertIn(['workpieceId'], paths)
        self.assertIn(['metadata', 'workpiece', 'workpieceId'], paths)
        self.assertIn(['loadId'], paths)
    
    def test_get_template_placeholders(self):
        """Test getting template placeholders"""
        placeholders = self.manager.get_template_placeholders()
        self.assertEqual(placeholders['nfc_code'], '<nfcCode>')
        self.assertEqual(placeholders['workpiece_id'], '<workpieceId>')
        self.assertEqual(placeholders['color'], '<color>')
        self.assertEqual(placeholders['quality'], '<quality>')
    
    def test_get_quality_check_options(self):
        """Test getting quality check options"""
        options = self.manager.get_quality_check_options()
        expected_options = ['OK', 'NOT-OK', 'PENDING', 'FAILED']
        self.assertEqual(options, expected_options)
    
    def test_get_colors(self):
        """Test getting available colors"""
        colors = self.manager.get_colors()
        expected_colors = ['RED', 'WHITE', 'BLUE']
        self.assertEqual(colors, expected_colors)
    
    def test_get_statistics(self):
        """Test getting NFC code statistics"""
        stats = self.manager.get_statistics()
        
        self.assertEqual(stats['total_codes'], 4)
        self.assertEqual(stats['color_counts']['RED'], 2)
        self.assertEqual(stats['color_counts']['WHITE'], 1)
        self.assertEqual(stats['color_counts']['BLUE'], 1)
        self.assertEqual(stats['quality_counts']['OK'], 3)
        self.assertEqual(stats['quality_counts']['NOT-OK'], 1)
        
        self.assertIn('RED', stats['colors'])
        self.assertIn('WHITE', stats['colors'])
        self.assertIn('BLUE', stats['colors'])
        
        self.assertIn('OK', stats['quality_options'])
        self.assertIn('NOT-OK', stats['quality_options'])
    
    def test_reload_config(self):
        """Test reloading configuration"""
        # Modify config
        new_config = self.test_config.copy()
        new_config['nfc_codes']['999999999999999'] = {
            'friendly_id': 'TEST',
            'color': 'RED',
            'quality_check': 'OK',
            'description': 'Test Werkstück'
        }
        
        # Write new config
        with open(self.temp_file.name, 'w') as f:
            yaml.dump(new_config, f)
        
        # Reload and test
        success = self.manager.reload_config()
        self.assertTrue(success)
        
        # Check if new code is available
        self.assertTrue(self.manager.is_nfc_code('999999999999999'))
        self.assertEqual(self.manager.get_friendly_name('999999999999999'), 'TEST')


class TestNFCCodeManagerBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create minimal test config
        self.test_config = {
            'nfc_codes': {
                '040a8dca341291': {
                    'friendly_id': 'R1',
                    'color': 'RED',
                    'quality_check': 'OK',
                    'description': 'Rotes Werkstück 1'
                }
            }
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
        yaml.dump(self.test_config, self.temp_file)
        self.temp_file.close()
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_backward_compatibility_functions(self):
        """Test backward compatibility functions"""
        from mqtt.tools.nfc_code_manager import (
            get_friendly_name, get_nfc_code, is_nfc_code, 
            get_nfc_codes_by_color, get_all_nfc_codes
        )
        
        # Test backward compatibility functions
        friendly_name = get_friendly_name('040a8dca341291')
        self.assertEqual(friendly_name, 'R1')
        
        nfc_code = get_nfc_code('R1')
        self.assertEqual(nfc_code, '040a8dca341291')
        
        self.assertTrue(is_nfc_code('040a8dca341291'))
        self.assertFalse(is_nfc_code('invalid_code'))
        
        red_codes = get_nfc_codes_by_color('RED')
        self.assertIn('040a8dca341291', red_codes)
        
        all_codes = get_all_nfc_codes()
        self.assertIn('040a8dca341291', all_codes)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
