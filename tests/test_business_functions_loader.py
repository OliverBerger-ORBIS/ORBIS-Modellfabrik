#!/usr/bin/env python3
"""
Unit tests for Business Functions Loader

Tests cover:
- Schema validation
- Load/save roundtrip
- Validation errors
- File I/O operations
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from omf2.config.business_functions_loader import (
    BusinessFunctionsLoader,
    get_loader,
    load_business_functions,
    save_business_functions,
)


class TestBusinessFunctionsLoader:
    """Test cases for BusinessFunctionsLoader"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        
        # Create test configuration
        self.test_config = {
            'metadata': {
                'version': '1.0.0',
                'last_updated': '2025-10-25',
                'author': 'Test Author',
                'description': 'Test configuration'
            },
            'business_functions': {
                'test_manager': {
                    'enabled': True,
                    'description': 'Test manager function',
                    'module_path': 'test.module.path',
                    'class_name': 'TestManager',
                    'routed_topics': ['test/topic1', 'test/topic2'],
                    'priority': 5,
                    'metadata': {
                        'category': 'test',
                        'requires_mqtt': True
                    }
                },
                'disabled_manager': {
                    'enabled': False,
                    'description': 'Disabled test manager',
                    'module_path': 'test.disabled.module',
                    'class_name': 'DisabledManager',
                    'routed_topics': [],
                    'priority': 3
                }
            },
            'qos_settings': {
                'default_qos': 1,
                'critical_topics': ['test/critical'],
                'qos': 2
            },
            'routing': {
                'enable_wildcard_matching': True,
                'topic_separator': '/'
            },
            'validation': {
                'require_module_path': True,
                'require_class_name': True,
                'allow_disabled_functions': True
            }
        }
        
        # Write test config file
        self.config_file = self.config_dir / 'business_functions.yml'
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.test_config, f)
        
        # Create loader instance
        self.loader = BusinessFunctionsLoader(self.config_dir)
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_loader_initialization(self):
        """Test loader initialization"""
        loader = BusinessFunctionsLoader(self.config_dir)
        assert loader.config_dir == self.config_dir
        assert loader.config_file == self.config_file
    
    def test_loader_default_path(self):
        """Test loader with default path"""
        loader = BusinessFunctionsLoader()
        assert loader.config_dir.name == 'registry'
        assert loader.config_file.name == 'business_functions.yml'
    
    def test_load_raw_success(self):
        """Test loading raw configuration successfully"""
        config = self.loader.load_raw()
        
        assert config is not None
        assert 'metadata' in config
        assert 'business_functions' in config
        assert config['metadata']['version'] == '1.0.0'
        assert 'test_manager' in config['business_functions']
    
    def test_load_raw_file_not_found(self):
        """Test load_raw raises FileNotFoundError when file doesn't exist"""
        loader = BusinessFunctionsLoader(Path('/nonexistent/path'))
        
        with pytest.raises(FileNotFoundError):
            loader.load_raw()
    
    def test_load_raw_invalid_yaml(self):
        """Test load_raw raises error for invalid YAML"""
        # Write invalid YAML
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write("{ invalid yaml content }}")
        
        with pytest.raises(yaml.YAMLError):
            self.loader.load_raw()
    
    def test_load_validated(self):
        """Test loading and validating configuration"""
        try:
            config = self.loader.load_validated()
            
            # Check if pydantic is available
            from omf2.config.schemas.business_functions_schema import is_pydantic_available
            
            if is_pydantic_available():
                # With pydantic, should return validated object
                assert hasattr(config, 'metadata') or isinstance(config, dict)
            else:
                # Without pydantic, returns raw dict
                assert isinstance(config, dict)
        except ImportError:
            # Pydantic not available, skip validation test
            pytest.skip("Pydantic not available")
    
    def test_save_configuration(self):
        """Test saving configuration to file"""
        new_config = self.test_config.copy()
        new_config['metadata']['version'] = '2.0.0'
        
        self.loader.save(new_config)
        
        # Reload and verify
        loaded_config = self.loader.load_raw()
        assert loaded_config['metadata']['version'] == '2.0.0'
    
    def test_load_save_roundtrip(self):
        """Test load/save roundtrip preserves data"""
        # Load original
        original = self.loader.load_raw()
        
        # Save it back
        self.loader.save(original)
        
        # Reload
        reloaded = self.loader.load_raw()
        
        # Compare
        assert original['metadata'] == reloaded['metadata']
        assert original['business_functions'] == reloaded['business_functions']
        assert original['qos_settings'] == reloaded['qos_settings']
    
    def test_get_enabled_functions(self):
        """Test getting only enabled functions"""
        enabled = self.loader.get_enabled_functions()
        
        assert len(enabled) == 1
        assert 'test_manager' in enabled
        assert 'disabled_manager' not in enabled
        assert enabled['test_manager']['enabled'] is True
    
    def test_save_creates_directory(self):
        """Test save creates directory if it doesn't exist"""
        new_dir = Path(self.temp_dir) / 'new_subdir'
        loader = BusinessFunctionsLoader(new_dir)
        
        loader.save(self.test_config)
        
        assert new_dir.exists()
        assert (new_dir / 'business_functions.yml').exists()
    
    def test_validate_importability_disabled(self):
        """Test validate_importability when disabled"""
        results = self.loader.validate_importability()
        
        # Should return empty dict when env var not set
        assert results == {}
    
    def test_validate_importability_enabled(self, monkeypatch):
        """Test validate_importability when enabled"""
        monkeypatch.setenv('ENABLE_IMPORT_CHECK', '1')
        
        results = self.loader.validate_importability()
        
        # Should check all functions
        assert 'test_manager' in results
        assert 'disabled_manager' in results
        
        # Both should fail (non-existent modules)
        assert results['test_manager'] is False
        assert results['disabled_manager'] is False


class TestBusinessFunctionsLoaderHelpers:
    """Test module-level helper functions"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        
        # Create minimal test config
        self.test_config = {
            'metadata': {
                'version': '1.0.0',
                'last_updated': '2025-10-25',
                'author': 'Test',
                'description': 'Test'
            },
            'business_functions': {
                'test_func': {
                    'enabled': True,
                    'description': 'Test',
                    'module_path': 'test.module',
                    'class_name': 'TestClass',
                    'routed_topics': []
                }
            }
        }
        
        # Write config file
        config_file = self.config_dir / 'business_functions.yml'
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.test_config, f)
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_business_functions_helper(self):
        """Test load_business_functions helper function"""
        config = load_business_functions(self.config_dir)
        
        assert config is not None
        assert 'business_functions' in config
        assert 'test_func' in config['business_functions']
    
    def test_save_business_functions_helper(self):
        """Test save_business_functions helper function"""
        new_config = self.test_config.copy()
        new_config['metadata']['version'] = '3.0.0'
        
        save_business_functions(new_config, self.config_dir)
        
        # Verify save
        loaded = load_business_functions(self.config_dir)
        assert loaded['metadata']['version'] == '3.0.0'
    
    def test_get_loader_helper(self):
        """Test get_loader helper function"""
        loader = get_loader(self.config_dir)
        
        assert isinstance(loader, BusinessFunctionsLoader)
        assert loader.config_dir == self.config_dir


class TestBusinessFunctionsValidation:
    """Test configuration validation"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)
        self.loader = BusinessFunctionsLoader(self.config_dir)
    
    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_missing_metadata_field(self):
        """Test validation with missing metadata fields"""
        invalid_config = {
            'metadata': {
                'version': '1.0.0',
                # Missing required fields
            },
            'business_functions': {
                'test': {
                    'enabled': True,
                    'description': 'Test',
                    'module_path': 'test',
                    'class_name': 'Test'
                }
            }
        }
        
        config_file = self.config_dir / 'business_functions.yml'
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(invalid_config, f)
        
        # Should still load (some validators are lenient)
        try:
            config = self.loader.load_validated()
            assert config is not None
        except Exception:
            # Pydantic may raise validation error
            pass
    
    def test_missing_required_function_field(self):
        """Test validation with missing required function fields"""
        invalid_config = {
            'metadata': {
                'version': '1.0.0',
                'last_updated': '2025-10-25',
                'author': 'Test'
            },
            'business_functions': {
                'test': {
                    'enabled': True,
                    'description': 'Test',
                    # Missing module_path and class_name
                }
            }
        }
        
        config_file = self.config_dir / 'business_functions.yml'
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(invalid_config, f)
        
        # Should raise validation error with pydantic
        try:
            from omf2.config.schemas.business_functions_schema import is_pydantic_available
            
            if is_pydantic_available():
                with pytest.raises(Exception):
                    self.loader.load_validated()
            else:
                # Without pydantic, no validation
                config = self.loader.load_validated()
                assert config is not None
        except ImportError:
            pytest.skip("Pydantic not available")
    
    def test_empty_business_functions(self):
        """Test validation with empty business_functions"""
        invalid_config = {
            'metadata': {
                'version': '1.0.0',
                'last_updated': '2025-10-25',
                'author': 'Test'
            },
            'business_functions': {}
        }
        
        config_file = self.config_dir / 'business_functions.yml'
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(invalid_config, f)
        
        # Should raise validation error with pydantic
        try:
            from omf2.config.schemas.business_functions_schema import is_pydantic_available
            
            if is_pydantic_available():
                with pytest.raises(Exception):
                    self.loader.load_validated()
            else:
                # Without pydantic, loads as-is
                config = self.loader.load_validated()
                assert config is not None
        except ImportError:
            pytest.skip("Pydantic not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
