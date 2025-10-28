#!/usr/bin/env python3
"""
Unit tests for Dashboard Business Functions UI

Tests cover:
- Loader integration with simulated save/load
- File I/O operations using tmp_path
- Helper functions for UI operations

Note: Does not require running a browser - tests save/load helpers only
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from omf2.config.business_functions_loader import BusinessFunctionsLoader


class TestBusinessFunctionsUIHelpers:
    """Test UI helper functions for business functions configuration"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir)

        # Create test configuration
        self.test_config = {
            "metadata": {
                "version": "1.0.0",
                "last_updated": "2025-10-25",
                "author": "Test Author",
                "description": "Test UI configuration",
            },
            "business_functions": {
                "order_manager": {
                    "enabled": True,
                    "description": "Order management",
                    "module_path": "omf2.ccu.business.order_manager",
                    "class_name": "OrderManager",
                    "routed_topics": ["ccu/order/request", "ccu/order/response"],
                    "priority": 10,
                    "metadata": {"category": "orchestration", "requires_mqtt": True},
                },
                "stock_manager": {
                    "enabled": False,
                    "description": "Stock management",
                    "module_path": "omf2.ccu.business.stock_manager",
                    "class_name": "StockManager",
                    "routed_topics": ["ccu/state/stock"],
                    "priority": 8,
                },
            },
        }

        # Create loader
        self.loader = BusinessFunctionsLoader(self.config_dir)

        # Save initial config
        self.loader.save(self.test_config)

    def teardown_method(self):
        """Cleanup test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_for_ui_display(self):
        """Test loading configuration for UI display"""
        config = self.loader.load_raw()

        # Verify config structure for UI
        assert "metadata" in config
        assert "business_functions" in config

        # Verify functions can be iterated for UI display
        functions = config["business_functions"]
        assert len(functions) == 2
        assert "order_manager" in functions
        assert "stock_manager" in functions

    def test_simulate_ui_enable_disable(self):
        """Test simulating UI enable/disable toggle"""
        config = self.loader.load_raw()

        # Simulate UI disabling order_manager
        config["business_functions"]["order_manager"]["enabled"] = False

        # Save changes
        self.loader.save(config)

        # Reload and verify
        reloaded = self.loader.load_raw()
        assert reloaded["business_functions"]["order_manager"]["enabled"] is False

    def test_simulate_ui_edit_topics(self):
        """Test simulating UI editing routed topics"""
        config = self.loader.load_raw()

        # Simulate UI adding new topic
        original_topics = config["business_functions"]["order_manager"]["routed_topics"]
        new_topics = original_topics + ["ccu/order/completed"]
        config["business_functions"]["order_manager"]["routed_topics"] = new_topics

        # Save changes
        self.loader.save(config)

        # Reload and verify
        reloaded = self.loader.load_raw()
        assert "ccu/order/completed" in reloaded["business_functions"]["order_manager"]["routed_topics"]
        assert len(reloaded["business_functions"]["order_manager"]["routed_topics"]) == 3

    def test_simulate_ui_priority_change(self):
        """Test simulating UI priority slider change"""
        config = self.loader.load_raw()

        # Simulate UI changing priority
        config["business_functions"]["stock_manager"]["priority"] = 5

        # Save changes
        self.loader.save(config)

        # Reload and verify
        reloaded = self.loader.load_raw()
        assert reloaded["business_functions"]["stock_manager"]["priority"] == 5

    def test_simulate_yaml_editor_save(self):
        """Test simulating YAML editor save operation"""
        # User edits YAML in UI
        yaml_text = """
metadata:
  version: "2.0.0"
  last_updated: "2025-10-26"
  author: "Updated Author"
  description: "Updated via YAML editor"

business_functions:
  order_manager:
    enabled: true
    description: "Order management - edited"
    module_path: "omf2.ccu.business.order_manager"
    class_name: "OrderManager"
    routed_topics:
      - "ccu/order/request"
      - "ccu/order/response"
      - "ccu/order/new_topic"
    priority: 9
"""

        # Parse YAML (simulates UI parsing)
        edited_config = yaml.safe_load(yaml_text)

        # Save (simulates UI save button)
        self.loader.save(edited_config)

        # Reload and verify
        reloaded = self.loader.load_raw()
        assert reloaded["metadata"]["version"] == "2.0.0"
        assert reloaded["metadata"]["author"] == "Updated Author"
        assert "ccu/order/new_topic" in reloaded["business_functions"]["order_manager"]["routed_topics"]
        assert reloaded["business_functions"]["order_manager"]["priority"] == 9

    def test_simulate_ui_reload(self):
        """Test simulating UI reload button"""
        config = self.loader.load_raw()

        # Make changes in memory (not saved)
        config["business_functions"]["order_manager"]["enabled"] = False

        # Simulate reload - should get original values
        reloaded = self.loader.load_raw()
        assert reloaded["business_functions"]["order_manager"]["enabled"] is True

    def test_ui_validation_helper(self):
        """Test validation helper for UI"""
        config = self.loader.load_raw()

        # Check required fields
        errors = []
        for func_name, func_config in config["business_functions"].items():
            if not func_config.get("module_path"):
                errors.append(f"{func_name}: Missing module_path")
            if not func_config.get("class_name"):
                errors.append(f"{func_name}: Missing class_name")

        # Should have no errors
        assert len(errors) == 0

    def test_ui_validation_with_errors(self):
        """Test validation helper detects errors"""
        config = self.loader.load_raw()

        # Introduce validation error
        del config["business_functions"]["order_manager"]["module_path"]

        # Check validation
        errors = []
        for func_name, func_config in config["business_functions"].items():
            if not func_config.get("module_path"):
                errors.append(f"{func_name}: Missing module_path")
            if not func_config.get("class_name"):
                errors.append(f"{func_name}: Missing class_name")

        # Should have 1 error
        assert len(errors) == 1
        assert "order_manager" in errors[0]

    def test_get_enabled_functions_for_ui(self):
        """Test getting enabled functions for UI display"""
        enabled = self.loader.get_enabled_functions()

        # Should only get enabled functions
        assert len(enabled) == 1
        assert "order_manager" in enabled
        assert "stock_manager" not in enabled

    def test_ui_statistics_calculation(self):
        """Test calculating statistics for UI info display"""
        config = self.loader.load_raw()
        functions = config["business_functions"]

        total = len(functions)
        enabled = sum(1 for f in functions.values() if f.get("enabled", False))
        disabled = total - enabled

        assert total == 2
        assert enabled == 1
        assert disabled == 1


class TestBusinessFunctionsUIFileOperations:
    """Test file I/O operations for UI using tmp_path"""

    def test_save_load_with_tmp_path(self, tmp_path):
        """Test save/load operations using pytest tmp_path"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        loader = BusinessFunctionsLoader(config_dir)

        # Create test config
        test_config = {
            "metadata": {"version": "1.0.0", "last_updated": "2025-10-25", "author": "Test"},
            "business_functions": {
                "test_func": {
                    "enabled": True,
                    "description": "Test",
                    "module_path": "test.module",
                    "class_name": "TestClass",
                    "routed_topics": [],
                }
            },
        }

        # Save
        loader.save(test_config)

        # Verify file exists
        config_file = config_dir / "business_functions.yml"
        assert config_file.exists()

        # Load and verify
        loaded = loader.load_raw()
        assert loaded["metadata"]["version"] == "1.0.0"
        assert "test_func" in loaded["business_functions"]

    def test_multiple_save_operations(self, tmp_path):
        """Test multiple sequential save operations"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        loader = BusinessFunctionsLoader(config_dir)

        # Save version 1
        config_v1 = {
            "metadata": {"version": "1.0.0", "last_updated": "2025-10-25", "author": "Test"},
            "business_functions": {
                "func1": {"enabled": True, "description": "V1", "module_path": "m", "class_name": "C"}
            },
        }
        loader.save(config_v1)

        # Save version 2
        config_v2 = {
            "metadata": {"version": "2.0.0", "last_updated": "2025-10-26", "author": "Test"},
            "business_functions": {
                "func1": {"enabled": False, "description": "V2", "module_path": "m", "class_name": "C"}
            },
        }
        loader.save(config_v2)

        # Load and verify latest
        loaded = loader.load_raw()
        assert loaded["metadata"]["version"] == "2.0.0"
        assert loaded["business_functions"]["func1"]["enabled"] is False
        assert loaded["business_functions"]["func1"]["description"] == "V2"

    def test_concurrent_read_operations(self, tmp_path):
        """Test multiple concurrent read operations"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        loader = BusinessFunctionsLoader(config_dir)

        # Create and save config
        test_config = {
            "metadata": {"version": "1.0.0", "last_updated": "2025-10-25", "author": "Test"},
            "business_functions": {
                "func": {"enabled": True, "description": "Test", "module_path": "m", "class_name": "C"}
            },
        }
        loader.save(test_config)

        # Multiple reads
        config1 = loader.load_raw()
        config2 = loader.load_raw()
        config3 = loader.load_raw()

        # All should be equal
        assert config1 == config2 == config3

    def test_file_encoding(self, tmp_path):
        """Test file operations preserve UTF-8 encoding"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        loader = BusinessFunctionsLoader(config_dir)

        # Config with unicode characters
        test_config = {
            "metadata": {
                "version": "1.0.0",
                "last_updated": "2025-10-25",
                "author": "Test Author 测试",
                "description": "Configuration with unicode: äöü 中文",
            },
            "business_functions": {
                "func": {
                    "enabled": True,
                    "description": "Function with unicode: привет",
                    "module_path": "test.module",
                    "class_name": "TestClass",
                }
            },
        }

        # Save and reload
        loader.save(test_config)
        loaded = loader.load_raw()

        # Verify unicode preserved
        assert "测试" in loaded["metadata"]["author"]
        assert "中文" in loaded["metadata"]["description"]
        assert "привет" in loaded["business_functions"]["func"]["description"]


class TestBusinessFunctionsUIEdgeCases:
    """Test edge cases in UI operations"""

    def test_empty_topics_list(self, tmp_path):
        """Test handling empty routed_topics list"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        loader = BusinessFunctionsLoader(config_dir)

        config = {
            "metadata": {"version": "1.0.0", "last_updated": "2025-10-25", "author": "Test"},
            "business_functions": {
                "func": {
                    "enabled": True,
                    "description": "Test",
                    "module_path": "test",
                    "class_name": "Test",
                    "routed_topics": [],  # Empty list
                }
            },
        }

        loader.save(config)
        loaded = loader.load_raw()

        assert loaded["business_functions"]["func"]["routed_topics"] == []

    def test_large_topics_list(self, tmp_path):
        """Test handling large routed_topics list"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        loader = BusinessFunctionsLoader(config_dir)

        # Create large topic list
        large_topics = [f"topic/{i}/subtopic" for i in range(100)]

        config = {
            "metadata": {"version": "1.0.0", "last_updated": "2025-10-25", "author": "Test"},
            "business_functions": {
                "func": {
                    "enabled": True,
                    "description": "Test",
                    "module_path": "test",
                    "class_name": "Test",
                    "routed_topics": large_topics,
                }
            },
        }

        loader.save(config)
        loaded = loader.load_raw()

        assert len(loaded["business_functions"]["func"]["routed_topics"]) == 100
        assert loaded["business_functions"]["func"]["routed_topics"] == large_topics

    def test_special_characters_in_topics(self, tmp_path):
        """Test handling special characters in topic names"""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        loader = BusinessFunctionsLoader(config_dir)

        special_topics = [
            "topic/with/+/wildcard",
            "topic/with/#/multilevel",
            "topic-with-dashes",
            "topic_with_underscores",
            "topic.with.dots",
        ]

        config = {
            "metadata": {"version": "1.0.0", "last_updated": "2025-10-25", "author": "Test"},
            "business_functions": {
                "func": {
                    "enabled": True,
                    "description": "Test",
                    "module_path": "test",
                    "class_name": "Test",
                    "routed_topics": special_topics,
                }
            },
        }

        loader.save(config)
        loaded = loader.load_raw()

        assert loaded["business_functions"]["func"]["routed_topics"] == special_topics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
