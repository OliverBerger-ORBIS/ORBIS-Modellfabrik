#!/usr/bin/env python3
"""
Tests für Registry v1 Manager
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from src_orbis.omf.tools.registry_manager import (
    MessageTemplateManager,
    Registry,
    TemplateMissingError,
    TopicManager,
    TopicResolver,
    UnknownTopicError,
    ValidationError,
)


@pytest.fixture
def temp_registry():
    """Create temporary registry for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "registry" / "model" / "v1"
        registry_path.mkdir(parents=True)

        # Create manifest
        manifest = {
            "version": "1.0.0",
            "sources": ["modules.yml", "enums.yml", "workpieces.yml"],
            "notes": "Test registry",
        }
        with open(registry_path / "manifest.yml", "w") as f:
            yaml.dump(manifest, f)

        # Create modules
        modules = {"modules": [{"serial": "SVR3QA0022", "id": "SVR3QA0022", "name": "HBW", "type": "Storage"}]}
        with open(registry_path / "modules.yml", "w") as f:
            yaml.dump(modules, f)

        # Create mappings directory
        mappings_dir = registry_path / "mappings"
        mappings_dir.mkdir()

        # Create mapping
        mapping = {
            "defaults": {"direction": "inbound"},
            "mappings": [
                {"pattern": "module/v1/ff/{module_id}/state", "template": "module.state"},
                {"topic": "module/v1/ff/SVR3QA0022/state", "template": "module.state.hbw_inventory"},
            ],
        }
        with open(mappings_dir / "topic_template.yml", "w") as f:
            yaml.dump(mapping, f)

        # Create templates
        templates_dir = registry_path / "templates"
        templates_dir.mkdir()

        # Module order template
        order_template = {
            "version": "1.0.0",
            "extends": "module/order",
            "module": "DRILL",
            "match": {"required_fields": ["orderId", "actionId", "command"], "command_enum": ["PICK", "DRILL", "DROP"]},
        }
        with open(templates_dir / "module.order.drill.yml", "w") as f:
            yaml.dump(order_template, f)

        # Also create module.order.yml for hierarchical lookup
        with open(templates_dir / "module.order.yml", "w") as f:
            yaml.dump(order_template, f)

        yield str(registry_path)


def test_version_pinning_violation():
    """Test version pinning: should fail for v2.x.x"""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "registry" / "model" / "v1"
        registry_path.mkdir(parents=True)

        # Create manifest with v2.0.0
        manifest = {"version": "2.0.0"}
        with open(registry_path / "manifest.yml", "w") as f:
            yaml.dump(manifest, f)

        with pytest.raises(Exception, match="Version pinning violation"):
            Registry(str(registry_path))


def test_exact_overrides_pattern(temp_registry):
    """Test exact match overrides pattern match"""
    registry = Registry(temp_registry)
    topic_mgr = TopicManager(registry)

    # HBW exact match should override pattern
    hbw_result = topic_mgr.route("module/v1/ff/SVR3QA0022/state")
    assert hbw_result["template"] == "module.state.hbw_inventory"

    # Other module should use pattern
    mill_result = topic_mgr.route("module/v1/ff/SVR4H76449/state")
    assert mill_result["template"] == "module.state"


def test_unknown_topic_handling(temp_registry):
    """Test unknown topic handling"""
    registry = Registry(temp_registry)
    topic_mgr = TopicManager(registry)

    # Unknown topic should return None
    result = topic_mgr.route("unknown/topic")
    assert result is None

    # Should be tracked in telemetry
    unknown_topics = topic_mgr.get_unknown_topics()
    assert "unknown/topic" in unknown_topics


def test_template_missing_handling(temp_registry):
    """Test template missing handling"""
    registry = Registry(temp_registry)
    template_mgr = MessageTemplateManager(registry)

    # Missing template should return None
    result = template_mgr.get("missing/template")
    assert result is None

    # Should be tracked in telemetry
    missing_templates = template_mgr.get_missing_templates()
    assert "missing/template" in missing_templates


def test_hierarchical_template_keys(temp_registry):
    """Test hierarchical template key resolution"""
    registry = Registry(temp_registry)
    template_mgr = MessageTemplateManager(registry)

    # "module/order" should resolve to "module.order.drill.yml"
    result = template_mgr.get("module/order")
    assert result is not None
    assert result["module"] == "DRILL"


def test_validation_errors_non_blocking(temp_registry):
    """Test validation errors are non-blocking"""
    registry = Registry(temp_registry)
    template_mgr = MessageTemplateManager(registry)

    # Missing required field should return errors but not raise exception
    errors = template_mgr.validate_payload("module/order", {"command": "PICK"})
    assert "missing field: orderId" in errors
    assert "missing field: actionId" in errors


def test_command_enum_validation(temp_registry):
    """Test command enum validation"""
    registry = Registry(temp_registry)
    template_mgr = MessageTemplateManager(registry)

    # Invalid command should return error
    errors = template_mgr.validate_payload(
        "module/order", {"orderId": "test", "actionId": "test", "command": "INVALID"}
    )
    assert "command not in enum" in str(errors)


def test_empty_workpieces_handling(temp_registry):
    """Test empty workpieces.yml handling"""
    registry = Registry(temp_registry)

    # Should return empty mapping instead of exception
    workpieces = registry.workpieces()
    assert workpieces == {"nfc_codes": {}}


def test_hot_reload_watch_mode(temp_registry):
    """Test hot-reload in watch mode"""
    registry = Registry(temp_registry, watch_mode=True)

    # Load initial data
    modules1 = registry.modules()
    assert len(modules1["modules"]) == 1

    # Modify modules file
    modules_path = Path(temp_registry) / "modules.yml"
    new_modules = {
        "modules": [
            {"serial": "SVR3QA0022", "id": "SVR3QA0022", "name": "HBW", "type": "Storage"},
            {"serial": "SVR4H76449", "id": "SVR4H76449", "name": "DRILL", "type": "Processing"},
        ]
    }
    with open(modules_path, "w") as f:
        yaml.dump(new_modules, f)

    # Touch file to update mtime
    modules_path.touch()

    # Should reload and see new data
    modules2 = registry.modules()
    assert len(modules2["modules"]) == 2
