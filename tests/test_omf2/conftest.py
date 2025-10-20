"""
Pytest configuration for OMF2 tests with Streamlit mocking.

This conftest.py provides fixtures to mock Streamlit components for UI tests
that would otherwise conflict with the DeltaGeneratorSingleton.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys


@pytest.fixture(autouse=True)
def mock_streamlit():
    """
    Automatically mock Streamlit for all tests to prevent DeltaGeneratorSingleton conflicts.
    
    This fixture runs for every test and provides a complete Streamlit mock
    that allows UI components to be imported and tested without conflicts.
    """
    # Create a comprehensive Streamlit mock
    streamlit_mock = MagicMock()
    
    # Mock common Streamlit components
    streamlit_mock.columns = MagicMock(return_value=[MagicMock() for _ in range(3)])
    streamlit_mock.container = MagicMock()
    streamlit_mock.expander = MagicMock()
    streamlit_mock.tabs = MagicMock(return_value=[MagicMock() for _ in range(3)])
    streamlit_mock.sidebar = MagicMock()
    streamlit_mock.markdown = MagicMock()
    streamlit_mock.write = MagicMock()
    streamlit_mock.button = MagicMock(return_value=False)
    streamlit_mock.selectbox = MagicMock(return_value="test")
    streamlit_mock.text_input = MagicMock(return_value="test")
    streamlit_mock.number_input = MagicMock(return_value=1)
    streamlit_mock.checkbox = MagicMock(return_value=False)
    streamlit_mock.radio = MagicMock(return_value="test")
    streamlit_mock.slider = MagicMock(return_value=1)
    streamlit_mock.select_slider = MagicMock(return_value="test")
    streamlit_mock.multiselect = MagicMock(return_value=[])
    streamlit_mock.file_uploader = MagicMock(return_value=None)
    streamlit_mock.download_button = MagicMock(return_value=False)
    streamlit_mock.dataframe = MagicMock()
    streamlit_mock.table = MagicMock()
    streamlit_mock.json = MagicMock()
    streamlit_mock.metric = MagicMock()
    streamlit_mock.progress = MagicMock()
    streamlit_mock.spinner = MagicMock()
    streamlit_mock.balloons = MagicMock()
    streamlit_mock.snow = MagicMock()
    streamlit_mock.error = MagicMock()
    streamlit_mock.warning = MagicMock()
    streamlit_mock.info = MagicMock()
    streamlit_mock.success = MagicMock()
    streamlit_mock.exception = MagicMock()
    streamlit_mock.empty = MagicMock()
    streamlit_mock.rerun = MagicMock()
    
    # Mock session state
    streamlit_mock.session_state = MagicMock()
    streamlit_mock.session_state.get = MagicMock(return_value=None)
    streamlit_mock.session_state.__setitem__ = MagicMock()
    streamlit_mock.session_state.__getitem__ = MagicMock(return_value=None)
    streamlit_mock.session_state.__contains__ = MagicMock(return_value=False)
    
    # Mock cache
    streamlit_mock.cache_data = MagicMock()
    streamlit_mock.cache_resource = MagicMock()
    
    # Mock experimental components
    streamlit_mock.experimental_rerun = MagicMock()
    
    # Mock the main streamlit module
    with patch.dict('sys.modules', {'streamlit': streamlit_mock}):
        yield streamlit_mock


@pytest.fixture
def mock_streamlit_ui():
    """
    Specific fixture for UI component tests that need more detailed Streamlit mocking.
    
    Use this fixture for tests that specifically test UI component behavior.
    """
    streamlit_mock = MagicMock()
    
    # Enhanced UI-specific mocks
    streamlit_mock.columns = MagicMock(return_value=[MagicMock() for _ in range(5)])
    streamlit_mock.tabs = MagicMock(return_value=[MagicMock() for _ in range(4)])
    streamlit_mock.expander = MagicMock()
    streamlit_mock.container = MagicMock()
    
    # Mock session state with realistic behavior
    session_state = {}
    streamlit_mock.session_state = session_state
    streamlit_mock.session_state.get = lambda key, default=None: session_state.get(key, default)
    streamlit_mock.session_state.__setitem__ = lambda key, value: session_state.update({key: value})
    streamlit_mock.session_state.__getitem__ = lambda key: session_state[key]
    streamlit_mock.session_state.__contains__ = lambda key: key in session_state
    
    with patch.dict('sys.modules', {'streamlit': streamlit_mock}):
        yield streamlit_mock


@pytest.fixture
def mock_i18n():
    """
    Mock the i18n translation system for tests.
    """
    i18n_mock = MagicMock()
    i18n_mock.t = MagicMock(side_effect=lambda key: f"translated_{key}")
    
    with patch.dict('sys.modules', {'omf2.common.i18n': i18n_mock}):
        with patch('omf2.common.i18n', i18n_mock):
            yield i18n_mock


@pytest.fixture
def mock_ui_symbols():
    """
    Mock the UISymbols class for tests.
    """
    ui_symbols_mock = MagicMock()
    ui_symbols_mock.get_status_icon = MagicMock(return_value="✅")
    ui_symbols_mock.get_module_icon = MagicMock(return_value="🏭")
    ui_symbols_mock.get_order_icon = MagicMock(return_value="📋")
    
    with patch.dict('sys.modules', {'omf2.ui.common.ui_symbols': ui_symbols_mock}):
        with patch('omf2.ui.common.ui_symbols', ui_symbols_mock):
            yield ui_symbols_mock


@pytest.fixture
def mock_gateway():
    """
    Mock a generic gateway for UI component tests.
    """
    gateway_mock = MagicMock()
    gateway_mock.get_data = MagicMock(return_value=[])
    gateway_mock.publish_message = MagicMock(return_value=True)
    gateway_mock.get_status = MagicMock(return_value="connected")
    
    return gateway_mock


@pytest.fixture
def mock_registry_manager():
    """
    Mock the RegistryManager for UI component tests.
    """
    registry_mock = MagicMock()
    registry_mock.get_topics = MagicMock(return_value=[])
    registry_mock.get_schemas = MagicMock(return_value={})
    registry_mock.get_topic_info = MagicMock(return_value={})
    
    return registry_mock


@pytest.fixture
def mock_asset_manager():
    """
    Mock the AssetManager for UI component tests.
    """
    asset_mock = MagicMock()
    asset_mock.get_workpiece_svg = MagicMock(return_value="<svg>mock</svg>")
    asset_mock.get_workpiece_palett = MagicMock(return_value="<svg>palett</svg>")
    asset_mock.get_module_icon = MagicMock(return_value="<svg>module</svg>")
    
    return asset_mock


# Mark UI tests for selective execution
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "ui: mark test as UI test")
    config.addinivalue_line("markers", "streamlit: mark test as Streamlit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle UI tests."""
    for item in items:
        # Mark tests that import streamlit as UI tests
        if "streamlit" in str(item.fspath) or "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
            item.add_marker(pytest.mark.streamlit)
