#!/usr/bin/env python3
"""
Test suite for MultiLevelRingBufferHandler persistence
Verifies that the handler stays attached after environment switches and config changes

Acceptance Criteria:
1. After every environment switch, logs appear in the UI
2. Never more than one handler at the logger
3. Session state always points to the active handler
"""

import logging
import sys
import pytest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from omf2.common.logger import (
    setup_multilevel_ringbuffer_logging, 
    MultiLevelRingBufferHandler,
    ensure_ringbufferhandler_attached
)


class MockSessionState:
    """Mock Streamlit session state for testing"""
    def __init__(self):
        self._state = {}
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __contains__(self, key):
        return key in self._state


class MockStreamlit:
    """Mock Streamlit module for testing"""
    session_state = MockSessionState()


@pytest.fixture(autouse=True)
def setup_mock_streamlit():
    """Setup mock streamlit module before each test"""
    # Save original module if it exists
    original_streamlit = sys.modules.get('streamlit')
    
    # Install mock
    mock_st = MockStreamlit()
    mock_st.session_state = MockSessionState()
    sys.modules['streamlit'] = mock_st
    
    yield mock_st
    
    # Restore original or remove mock
    if original_streamlit:
        sys.modules['streamlit'] = original_streamlit
    else:
        sys.modules.pop('streamlit', None)


@pytest.fixture(autouse=True)
def clean_logger():
    """Clean up logger handlers before and after each test"""
    root = logging.getLogger()
    # Remove all handlers before test
    for handler in root.handlers[:]:
        root.removeHandler(handler)
    
    yield
    
    # Clean up after test
    for handler in root.handlers[:]:
        root.removeHandler(handler)


def test_handler_persistence_after_environment_switch():
    """
    Test: Handler persists after environment switch
    Acceptance: After every environment switch, logs appear in UI
    """
    import streamlit as st
    
    # Initial setup (simulating omf.py initialization)
    handler1, buffers1 = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler1
    st.session_state['log_buffers'] = buffers1
    
    # Set root logger level to allow INFO logs
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    # Log a test message
    logger = logging.getLogger('test')
    logger.setLevel(logging.INFO)
    logger.info("Before environment switch")
    
    # Verify initial state
    assert handler1 in root.handlers, "Handler should be attached initially"
    assert len([h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]) == 1
    
    # Simulate environment switch (calls _reconnect_logging_system in main_dashboard.py)
    handler2, buffers2 = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler2
    st.session_state['log_buffers'] = buffers2
    
    # Set root logger level again (environment switch resets it)
    root.setLevel(logging.DEBUG)
    
    # Verify handler attachment
    success = ensure_ringbufferhandler_attached()
    assert success, "Handler attachment should succeed"
    
    # Verify only one handler exists
    multilevel_handlers = [h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 handler, got {len(multilevel_handlers)}"
    
    # Verify session state points to active handler
    assert st.session_state['log_handler'] in root.handlers, "Session state handler should be attached"
    
    # Verify logs are captured after environment switch
    logger.info("After environment switch")
    logs = handler2.get_buffer('INFO')
    assert len(logs) > 0, "Logs should be captured after environment switch"
    assert any("After environment switch" in log for log in logs), "New log should be in buffer"
    
    # Old logs from handler1 are not in handler2 (expected behavior with force_new)
    assert not any("Before environment switch" in log for log in logs), "Old logs should not be in new handler"


def test_no_duplicate_handlers():
    """
    Test: Never more than one handler at the logger
    Acceptance: Nie mehr als ein Handler am Logger
    """
    import streamlit as st
    
    root = logging.getLogger()
    
    # Setup initial handler
    handler1, buffers1 = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler1
    st.session_state['log_buffers'] = buffers1
    
    # Verify single handler
    assert len([h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]) == 1
    
    # Multiple environment switches
    for i in range(5):
        handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
        st.session_state['log_handler'] = handler
        st.session_state['log_buffers'] = buffers
        ensure_ringbufferhandler_attached()
        
        # Verify only one handler after each switch
        multilevel_handlers = [h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]
        assert len(multilevel_handlers) == 1, f"Iteration {i}: Should have exactly 1 handler, got {len(multilevel_handlers)}"


def test_session_state_consistency():
    """
    Test: Session state always points to active handler
    Acceptance: Session-State zeigt immer auf aktiven Handler
    """
    import streamlit as st
    
    root = logging.getLogger()
    
    # Setup initial handler
    handler1, buffers1 = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler1
    st.session_state['log_buffers'] = buffers1
    
    # Verify consistency
    assert st.session_state['log_handler'] in root.handlers
    assert st.session_state['log_buffers'] is handler1.buffers
    
    # Environment switch
    handler2, buffers2 = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler2
    st.session_state['log_buffers'] = buffers2
    ensure_ringbufferhandler_attached()
    
    # Verify session state updated
    assert st.session_state['log_handler'] is handler2
    assert st.session_state['log_handler'] in root.handlers
    assert st.session_state['log_buffers'] is handler2.buffers


def test_handler_reattachment_after_detachment():
    """
    Test: Handler gets re-attached if detached
    """
    import streamlit as st
    
    root = logging.getLogger()
    
    # Setup handler
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler
    st.session_state['log_buffers'] = buffers
    
    assert handler in root.handlers
    
    # Simulate accidental detachment (e.g., from external code)
    root.removeHandler(handler)
    assert handler not in root.handlers
    
    # Call ensure function
    success = ensure_ringbufferhandler_attached()
    assert success, "Re-attachment should succeed"
    
    # Verify re-attached
    assert handler in root.handlers, "Handler should be re-attached"
    assert len([h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]) == 1


def test_apply_logging_config_preserves_handler():
    """
    Test: Handler persists after apply_logging_config()
    Acceptance: Nach jeder Logging-Konfigurationsänderung erscheinen Logs in der UI
    """
    import streamlit as st
    from omf2.common.logging_config import apply_logging_config
    
    # Setup handler
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler
    st.session_state['log_buffers'] = buffers
    
    # Log before config change
    logger = logging.getLogger('test')
    logger.info("Before config change")
    
    # Apply config (includes ensure_ringbufferhandler_attached call)
    apply_logging_config()
    
    root = logging.getLogger()
    
    # Verify handler still attached
    assert handler in root.handlers, "Handler should remain attached after config change"
    
    # Verify only one handler
    multilevel_handlers = [h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 handler, got {len(multilevel_handlers)}"
    
    # Verify logs still captured
    logger.info("After config change")
    logs = handler.get_buffer('INFO')
    assert len(logs) > 0, "Logs should still be captured after config change"


def test_complete_workflow():
    """
    Integration test: Complete workflow with multiple switches and config changes
    """
    import streamlit as st
    from omf2.common.logging_config import apply_logging_config
    
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    logger = logging.getLogger('test.workflow')
    logger.setLevel(logging.INFO)
    
    # Initial setup
    handler1, buffers1 = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler1
    st.session_state['log_buffers'] = buffers1
    logger.info("Initial setup")
    
    # Environment switch 1
    handler2, buffers2 = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler2
    st.session_state['log_buffers'] = buffers2
    ensure_ringbufferhandler_attached()
    root.setLevel(logging.DEBUG)  # Ensure level after switch
    logger.info("After switch 1")
    
    # Config change
    apply_logging_config()
    logger.info("After config change")
    
    # Environment switch 2
    handler3, buffers3 = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler3
    st.session_state['log_buffers'] = buffers3
    ensure_ringbufferhandler_attached()
    root.setLevel(logging.DEBUG)  # Ensure level after switch
    logger.info("After switch 2")
    
    # Final verification
    multilevel_handlers = [h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 handler, got {len(multilevel_handlers)}"
    assert st.session_state['log_handler'] in root.handlers
    
    # Verify logs captured
    logs = handler3.get_buffer('INFO')
    assert len(logs) > 0, "Logs should be captured throughout workflow"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
