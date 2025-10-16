#!/usr/bin/env python3
"""
Tests für MultiLevelRingBufferHandler Persistence nach Environment-Switch

Verifiziert, dass der Handler korrekt am Root-Logger bleibt nach:
- setup_multilevel_ringbuffer_logging(force_new=True)
- apply_logging_config()
- Environment switches
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from omf2.common.logger import MultiLevelRingBufferHandler, setup_multilevel_ringbuffer_logging
from omf2.common.logging_config import apply_logging_config


def test_handler_attachment_after_setup():
    """Test: Handler ist nach setup_multilevel_ringbuffer_logging am Root-Logger"""
    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # Run setup
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)

    # Verify
    assert handler in root_logger.handlers, "Handler should be attached to root logger"

    # Verify only ONE handler
    multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 MultiLevelRingBufferHandler, got {len(multilevel_handlers)}"

    print("✅ test_handler_attachment_after_setup PASSED")


def test_handler_reuse_without_force_new():
    """Test: Handler wird wiederverwendet wenn bereits vorhanden (force_new=False)"""
    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # First setup
    handler1, buffers1 = setup_multilevel_ringbuffer_logging(force_new=False)

    # Second setup without force_new
    handler2, buffers2 = setup_multilevel_ringbuffer_logging(force_new=False)

    # Verify same handler instance
    assert handler1 is handler2, "Should reuse same handler instance"

    # Verify only ONE handler
    multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 MultiLevelRingBufferHandler, got {len(multilevel_handlers)}"

    print("✅ test_handler_reuse_without_force_new PASSED")


def test_handler_replacement_with_force_new():
    """Test: Handler wird ersetzt bei force_new=True"""
    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # First setup
    handler1, buffers1 = setup_multilevel_ringbuffer_logging(force_new=False)

    # Second setup WITH force_new
    handler2, buffers2 = setup_multilevel_ringbuffer_logging(force_new=True)

    # Verify different handler instance
    assert handler1 is not handler2, "Should create new handler instance with force_new=True"

    # Verify only ONE handler (old one should be removed)
    multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 MultiLevelRingBufferHandler, got {len(multilevel_handlers)}"

    # Verify the new handler is attached
    assert handler2 in root_logger.handlers, "New handler should be attached to root logger"
    assert handler1 not in root_logger.handlers, "Old handler should NOT be attached to root logger"

    print("✅ test_handler_replacement_with_force_new PASSED")


def test_handler_persistence_after_apply_logging_config():
    """Test: Handler bleibt attached nach apply_logging_config()"""
    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # Setup handler
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)

    # Verify handler is attached before
    assert handler in root_logger.handlers, "Handler should be attached before apply_logging_config"

    # Apply logging config (this might remove handlers in some implementations)
    apply_logging_config()

    # Verify handler is STILL attached after
    assert handler in root_logger.handlers, "Handler should STILL be attached after apply_logging_config"

    # Verify only ONE handler
    multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 MultiLevelRingBufferHandler after config, got {len(multilevel_handlers)}"

    print("✅ test_handler_persistence_after_apply_logging_config PASSED")


def test_logging_actually_works():
    """Test: Logs werden tatsächlich in den Buffer geschrieben"""
    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # Setup handler
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)

    # WICHTIG: Set root logger to DEBUG to capture DEBUG logs
    root_logger.setLevel(logging.DEBUG)

    # Clear buffers
    for level in buffers:
        buffers[level].clear()

    # Create test logger and set to DEBUG
    test_logger = logging.getLogger("test.multilevel")
    test_logger.setLevel(logging.DEBUG)

    # Write test logs
    test_logger.error("TEST ERROR MESSAGE")
    test_logger.warning("TEST WARNING MESSAGE")
    test_logger.info("TEST INFO MESSAGE")
    test_logger.debug("TEST DEBUG MESSAGE")

    # Verify logs are in buffers
    error_logs = handler.get_buffer('ERROR')
    warning_logs = handler.get_buffer('WARNING')
    info_logs = handler.get_buffer('INFO')
    debug_logs = handler.get_buffer('DEBUG')

    assert len(error_logs) > 0, "Should have ERROR logs in buffer"
    assert len(warning_logs) > 0, "Should have WARNING logs in buffer"
    assert len(info_logs) > 0, "Should have INFO logs in buffer"
    assert len(debug_logs) > 0, "Should have DEBUG logs in buffer"

    # Verify message content
    assert any("TEST ERROR MESSAGE" in log for log in error_logs), "ERROR buffer should contain test message"
    assert any("TEST WARNING MESSAGE" in log for log in warning_logs), "WARNING buffer should contain test message"
    assert any("TEST INFO MESSAGE" in log for log in info_logs), "INFO buffer should contain test message"
    assert any("TEST DEBUG MESSAGE" in log for log in debug_logs), "DEBUG buffer should contain test message"

    print("✅ test_logging_actually_works PASSED")


def test_environment_switch_simulation():
    """Test: Simuliert Environment-Switch und verifiziert Handler-Persistenz"""
    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # Initial setup (mock environment)
    handler1, buffers1 = setup_multilevel_ringbuffer_logging(force_new=True)

    # Write some logs
    test_logger = logging.getLogger("test.env_switch")
    test_logger.info("LOG IN MOCK ENVIRONMENT")

    # Simulate environment switch (mock -> replay)
    # This should force_new=True to clean up
    handler2, buffers2 = setup_multilevel_ringbuffer_logging(force_new=True)

    # Verify new handler is attached
    assert handler2 in root_logger.handlers, "New handler should be attached after environment switch"

    # Verify only ONE handler
    multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 MultiLevelRingBufferHandler after env switch, got {len(multilevel_handlers)}"

    # Write logs after switch
    test_logger.info("LOG IN REPLAY ENVIRONMENT")

    # Verify new logs are captured
    info_logs = handler2.get_buffer('INFO')
    assert any("LOG IN REPLAY ENVIRONMENT" in log for log in info_logs), "New logs should be captured after environment switch"

    print("✅ test_environment_switch_simulation PASSED")


def test_ensure_ringbufferhandler_attached_without_streamlit():
    """Test: ensure_ringbufferhandler_attached() works gracefully without streamlit"""
    from omf2.common.logger import ensure_ringbufferhandler_attached

    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # Call without streamlit session state (should return False gracefully)
    result = ensure_ringbufferhandler_attached()

    # Should return False when streamlit is not available or no handler in session
    assert result == False, "Should return False when streamlit context not available"

    print("✅ test_ensure_ringbufferhandler_attached_without_streamlit PASSED")


def test_ensure_ringbufferhandler_reattaches_detached_handler():
    """Test: ensure_ringbufferhandler_attached() re-attaches a detached handler"""
    from omf2.common.logger import ensure_ringbufferhandler_attached

    # Mock streamlit session state
    class MockSessionState:
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

    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # Setup handler
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)

    # Create mock session state
    mock_st = type('MockStreamlit', (), {})()
    mock_st.session_state = MockSessionState()
    mock_st.session_state['log_handler'] = handler
    mock_st.session_state['log_buffers'] = buffers

    # Import and monkey-patch streamlit module
    import sys
    sys.modules['streamlit'] = mock_st

    # Detach handler manually (simulate the bug)
    root_logger.removeHandler(handler)

    # Verify handler is detached
    assert handler not in root_logger.handlers, "Handler should be detached before test"

    # Call ensure_ringbufferhandler_attached
    result = ensure_ringbufferhandler_attached()

    # Verify handler is re-attached
    assert result == True, "Should return True when handler successfully attached"
    assert handler in root_logger.handlers, "Handler should be re-attached after call"

    # Verify only ONE handler
    multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1, f"Should have exactly 1 MultiLevelRingBufferHandler, got {len(multilevel_handlers)}"

    # Cleanup: remove mock streamlit
    del sys.modules['streamlit']

    print("✅ test_ensure_ringbufferhandler_reattaches_detached_handler PASSED")


def test_ensure_ringbufferhandler_removes_duplicates():
    """Test: ensure_ringbufferhandler_attached() removes duplicate handlers"""
    from omf2.common.logger import ensure_ringbufferhandler_attached

    # Mock streamlit session state
    class MockSessionState:
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

    # Setup
    root_logger = logging.getLogger()

    # Clear all handlers
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    # Setup two handlers (simulate duplicate bug)
    handler1, buffers1 = setup_multilevel_ringbuffer_logging(force_new=True)
    handler2 = MultiLevelRingBufferHandler()
    root_logger.addHandler(handler2)

    # Create mock session state with first handler
    mock_st = type('MockStreamlit', (), {})()
    mock_st.session_state = MockSessionState()
    mock_st.session_state['log_handler'] = handler1
    mock_st.session_state['log_buffers'] = buffers1

    # Import and monkey-patch streamlit module
    import sys
    sys.modules['streamlit'] = mock_st

    # Verify we have 2 handlers before
    multilevel_handlers_before = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers_before) == 2, "Should have 2 handlers before test"

    # Call ensure_ringbufferhandler_attached
    result = ensure_ringbufferhandler_attached()

    # Verify only ONE handler remains (the one from session state)
    assert result == True, "Should return True when duplicates removed"
    multilevel_handlers_after = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers_after) == 1, f"Should have exactly 1 MultiLevelRingBufferHandler after, got {len(multilevel_handlers_after)}"

    # Verify correct handler is kept
    assert handler1 in root_logger.handlers, "Handler from session state should be kept"
    assert handler2 not in root_logger.handlers, "Duplicate handler should be removed"

    # Cleanup: remove mock streamlit
    del sys.modules['streamlit']

    print("✅ test_ensure_ringbufferhandler_removes_duplicates PASSED")


if __name__ == "__main__":
    print("🧪 Running MultiLevelRingBufferHandler Persistence Tests")
    print("=" * 70)

    try:
        test_handler_attachment_after_setup()
        test_handler_reuse_without_force_new()
        test_handler_replacement_with_force_new()
        test_handler_persistence_after_apply_logging_config()
        test_logging_actually_works()
        test_environment_switch_simulation()
        test_ensure_ringbufferhandler_attached_without_streamlit()
        test_ensure_ringbufferhandler_reattaches_detached_handler()
        test_ensure_ringbufferhandler_removes_duplicates()

        print("=" * 70)
        print("✅ ALL TESTS PASSED")
        sys.exit(0)

    except AssertionError as e:
        print("=" * 70)
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print("=" * 70)
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
