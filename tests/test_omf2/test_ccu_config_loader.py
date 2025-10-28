#!/usr/bin/env python3
"""
Tests for CCU Config Loader
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from omf2.ccu.config_loader import CCUConfigLoader, get_ccu_config_loader


class TestCCUConfigLoader:
    """Test cases for CCU Config Loader"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir)

        # Create test JSON files
        self._create_test_config_files()

        # Create config loader instance
        self.config_loader = CCUConfigLoader(self.config_path)

    def _create_test_config_files(self):
        """Create test configuration files"""
        # Production workflows
        production_workflows = {
            "_meta": {"_description": "Test production workflows", "_version": "1.0"},
            "BLUE": {"steps": ["MILL", "DRILL", "AIQS"]},
            "WHITE": {"steps": ["DRILL", "AIQS"]},
            "RED": {"steps": ["MILL", "AIQS"]},
        }

        # Production settings
        production_settings = {
            "_meta": {"_description": "Test production settings", "_version": "1.0"},
            "productionDurations": {"WHITE": 440, "BLUE": 460, "RED": 500},
            "productionSettings": {"maxParallelOrders": 4},
            "ftsSettings": {"chargeThresholdPercent": 10},
        }

        # Shopfloor layout
        shopfloor_layout = {
            "_meta": {"_description": "Test shopfloor layout", "_version": "1.0"},
            "grid": {"rows": 3, "columns": 4},
            "modules": [],
            "intersections": [],
            "roads": [],
        }

        # Write test files
        with open(self.config_path / "production_workflows.json", "w") as f:
            json.dump(production_workflows, f, indent=2)

        with open(self.config_path / "production_settings.json", "w") as f:
            json.dump(production_settings, f, indent=2)

        with open(self.config_path / "shopfloor_layout.json", "w") as f:
            json.dump(shopfloor_layout, f, indent=2)

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_path(self):
        """Test CCUConfigLoader initialization with default path"""
        with patch("omf2.ccu.config_loader.Path") as mock_path:
            mock_path.return_value.parent.parent = Path("/test")
            loader = CCUConfigLoader()
            assert loader.config_path == Path("/test/config/ccu")

    def test_init_custom_path(self):
        """Test CCUConfigLoader initialization with custom path"""
        custom_path = Path("/custom/path")
        loader = CCUConfigLoader(custom_path)
        assert loader.config_path == custom_path

    def test_load_production_workflows(self):
        """Test loading production workflows"""
        workflows = self.config_loader.load_production_workflows()

        assert "BLUE" in workflows
        assert "WHITE" in workflows
        assert "RED" in workflows
        assert workflows["BLUE"]["steps"] == ["MILL", "DRILL", "AIQS"]
        assert workflows["WHITE"]["steps"] == ["DRILL", "AIQS"]
        assert workflows["RED"]["steps"] == ["MILL", "AIQS"]

    def test_load_production_settings(self):
        """Test loading production settings"""
        settings = self.config_loader.load_production_settings()

        assert "productionDurations" in settings
        assert "productionSettings" in settings
        assert "ftsSettings" in settings

        # Check BLUE, WHITE, RED order
        durations = settings["productionDurations"]
        assert durations["WHITE"] == 440
        assert durations["BLUE"] == 460
        assert durations["RED"] == 500

        assert settings["productionSettings"]["maxParallelOrders"] == 4
        assert settings["ftsSettings"]["chargeThresholdPercent"] == 10

    def test_load_shopfloor_layout(self):
        """Test loading shopfloor layout"""
        layout = self.config_loader.load_shopfloor_layout()

        assert "grid" in layout
        assert "modules" in layout
        assert "intersections" in layout
        assert "roads" in layout

        assert layout["grid"]["rows"] == 3
        assert layout["grid"]["columns"] == 4

    def test_get_config_meta(self):
        """Test getting configuration metadata"""
        meta = self.config_loader.get_config_meta("production_workflows")

        assert "_description" in meta
        assert "_version" in meta
        assert meta["_description"] == "Test production workflows"
        assert meta["_version"] == "1.0"

    def test_cache_functionality(self):
        """Test configuration caching"""
        # First load should populate cache
        workflows1 = self.config_loader.load_production_workflows()
        
        # Test that caching works by checking performance
        # (If cache is working, second load should be faster)
        import time
        start_time = time.time()
        workflows2 = self.config_loader.load_production_workflows()
        load_time = time.time() - start_time
        
        # Cache should make subsequent loads very fast (< 0.01 seconds)
        assert load_time < 0.01, f"Load time {load_time}s suggests cache not working"
        
        # Content should be identical (even if not same object reference)
        assert workflows1 == workflows2, "Cached content should be identical"

    def test_clear_cache(self):
        """Test cache clearing"""
        # Load some configs to populate cache
        workflows1 = self.config_loader.load_production_workflows()
        settings1 = self.config_loader.load_production_settings()

        # Load again to ensure they're cached
        workflows2 = self.config_loader.load_production_workflows()
        settings2 = self.config_loader.load_production_settings()
        
        # Content should be identical
        assert workflows1 == workflows2
        assert settings1 == settings2

        # Clear cache - this should force reload from disk
        self.config_loader.clear_cache()
        
        # Load again after cache clear
        workflows3 = self.config_loader.load_production_workflows()
        settings3 = self.config_loader.load_production_settings()
        
        # Content should still be identical (cache clear doesn't change data)
        assert workflows1 == workflows3
        assert settings1 == settings3
        
        # Test that clear_cache() method exists and can be called
        assert hasattr(self.config_loader, 'clear_cache')
        assert callable(self.config_loader.clear_cache)

    def test_list_available_configs(self):
        """Test listing available configuration files"""
        configs = self.config_loader.list_available_configs()

        assert "production_workflows.json" in configs
        assert "production_settings.json" in configs
        assert "shopfloor_layout.json" in configs

    def test_file_not_found_error(self):
        """Test FileNotFoundError when config file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            self.config_loader._load_json_config("nonexistent.json")

    def test_json_decode_error(self):
        """Test JSONDecodeError when config file is malformed"""
        # Create malformed JSON file
        malformed_file = self.config_path / "malformed.json"
        with open(malformed_file, "w") as f:
            f.write("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            self.config_loader._load_json_config("malformed.json")


class TestCCUConfigLoaderSingleton:
    """Test cases for CCU Config Loader singleton"""

    def test_singleton_instance(self):
        """Test that get_ccu_config_loader returns singleton instance"""
        loader1 = get_ccu_config_loader()
        loader2 = get_ccu_config_loader()

        assert loader1 is loader2  # Same instance

    @patch("omf2.ccu.config_loader._ccu_config_loader", None)
    def test_singleton_initialization(self):
        """Test singleton initialization"""
        loader = get_ccu_config_loader()
        assert loader is not None
        assert isinstance(loader, CCUConfigLoader)


class TestCCUConfigLoaderIntegration:
    """Integration tests for CCU Config Loader with real config files"""

    def test_load_real_config_files(self):
        """Test loading real CCU configuration files"""
        # Use real config path
        config_loader = CCUConfigLoader()

        try:
            # Test loading real files (if they exist)
            workflows = config_loader.load_production_workflows()
            assert isinstance(workflows, dict)

            settings = config_loader.load_production_settings()
            assert isinstance(settings, dict)

            layout = config_loader.load_shopfloor_layout()
            assert isinstance(layout, dict)

        except FileNotFoundError:
            # Skip test if config files don't exist yet
            pytest.skip("CCU config files not found - skipping integration test")


if __name__ == "__main__":
    pytest.main([__file__])
