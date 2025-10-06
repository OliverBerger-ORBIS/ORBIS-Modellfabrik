#!/usr/bin/env python3
"""
Integration test for logging handler persistence across operations.

Tests the complete workflow:
1. Setup handler
2. Apply logging config
3. Simulate environment switch
4. Verify logs are still captured
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from omf2.common.logger import (
    setup_multilevel_ringbuffer_logging,
    MultiLevelRingBufferHandler,
    ensure_ringbufferhandler_attached
)
from omf2.common.logging_config import apply_logging_config


def test_complete_workflow():
    """Test: Complete workflow from setup to environment switch"""
    print("\n🧪 Testing complete logging workflow...")
    
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
    
    # Setup mock streamlit
    mock_st = type('MockStreamlit', (), {})()
    mock_st.session_state = MockSessionState()
    sys.modules['streamlit'] = mock_st
    
    try:
        # Setup
        root_logger = logging.getLogger()
        
        # Clear all handlers
        for h in list(root_logger.handlers):
            root_logger.removeHandler(h)
        
        # Step 1: Initial setup (simulate app startup)
        print("  Step 1: Initial setup...")
        handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
        mock_st.session_state['log_handler'] = handler
        mock_st.session_state['log_buffers'] = buffers
        root_logger.setLevel(logging.DEBUG)
        
        # Verify
        assert handler in root_logger.handlers, "Handler should be attached after setup"
        print("  ✅ Handler attached after setup")
        
        # Write test log
        test_logger = logging.getLogger("test.integration")
        test_logger.setLevel(logging.DEBUG)
        test_logger.info("LOG AFTER INITIAL SETUP")
        
        # Verify log captured
        info_logs = handler.get_buffer('INFO')
        assert any("LOG AFTER INITIAL SETUP" in log for log in info_logs), "Initial log should be captured"
        print("  ✅ Initial log captured")
        
        # Step 2: Apply logging config (simulate config change)
        print("  Step 2: Applying logging config...")
        apply_logging_config()
        
        # Verify handler still attached
        assert handler in root_logger.handlers, "Handler should still be attached after apply_logging_config"
        print("  ✅ Handler still attached after config apply")
        
        # Write test log
        test_logger.info("LOG AFTER APPLY_LOGGING_CONFIG")
        
        # Verify log captured
        info_logs = handler.get_buffer('INFO')
        assert any("LOG AFTER APPLY_LOGGING_CONFIG" in log for log in info_logs), "Log after config should be captured"
        print("  ✅ Log captured after apply_logging_config")
        
        # Step 3: Simulate environment switch (mock -> replay)
        print("  Step 3: Simulating environment switch...")
        handler2, buffers2 = setup_multilevel_ringbuffer_logging(force_new=True)
        mock_st.session_state['log_handler'] = handler2
        mock_st.session_state['log_buffers'] = buffers2
        
        # Verify new handler is attached and old one removed
        assert handler2 in root_logger.handlers, "New handler should be attached after environment switch"
        assert handler not in root_logger.handlers, "Old handler should be removed after environment switch"
        print("  ✅ New handler attached after environment switch")
        
        # Verify only ONE handler
        multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
        assert len(multilevel_handlers) == 1, f"Should have exactly 1 handler, got {len(multilevel_handlers)}"
        print("  ✅ Only one handler exists")
        
        # Write test log
        test_logger.info("LOG AFTER ENVIRONMENT SWITCH")
        
        # Verify log captured by new handler
        info_logs = handler2.get_buffer('INFO')
        assert any("LOG AFTER ENVIRONMENT SWITCH" in log for log in info_logs), "Log after env switch should be captured"
        print("  ✅ Log captured after environment switch")
        
        # Step 4: Call ensure_ringbufferhandler_attached (simulate manual check)
        print("  Step 4: Testing ensure_ringbufferhandler_attached...")
        result = ensure_ringbufferhandler_attached()
        
        assert result == True, "ensure_ringbufferhandler_attached should return True"
        assert handler2 in root_logger.handlers, "Handler should still be attached after ensure call"
        print("  ✅ ensure_ringbufferhandler_attached works correctly")
        
        # Final verification: Write more logs and ensure they are captured
        print("  Step 5: Final verification...")
        test_logger.error("FINAL ERROR LOG")
        test_logger.warning("FINAL WARNING LOG")
        test_logger.info("FINAL INFO LOG")
        test_logger.debug("FINAL DEBUG LOG")
        
        error_logs = handler2.get_buffer('ERROR')
        warning_logs = handler2.get_buffer('WARNING')
        info_logs = handler2.get_buffer('INFO')
        debug_logs = handler2.get_buffer('DEBUG')
        
        assert any("FINAL ERROR LOG" in log for log in error_logs), "Final ERROR log should be captured"
        assert any("FINAL WARNING LOG" in log for log in warning_logs), "Final WARNING log should be captured"
        assert any("FINAL INFO LOG" in log for log in info_logs), "Final INFO log should be captured"
        assert any("FINAL DEBUG LOG" in log for log in debug_logs), "Final DEBUG log should be captured"
        print("  ✅ All log levels captured correctly")
        
        print("✅ test_complete_workflow PASSED")
        return True
        
    finally:
        # Cleanup
        if 'streamlit' in sys.modules:
            del sys.modules['streamlit']


def test_handler_persistence_across_multiple_config_changes():
    """Test: Handler persists across multiple apply_logging_config calls"""
    print("\n🧪 Testing handler persistence across multiple config changes...")
    
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
    
    # Setup mock streamlit
    mock_st = type('MockStreamlit', (), {})()
    mock_st.session_state = MockSessionState()
    sys.modules['streamlit'] = mock_st
    
    try:
        # Setup
        root_logger = logging.getLogger()
        
        # Clear all handlers
        for h in list(root_logger.handlers):
            root_logger.removeHandler(h)
        
        # Initial setup
        handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
        mock_st.session_state['log_handler'] = handler
        mock_st.session_state['log_buffers'] = buffers
        root_logger.setLevel(logging.DEBUG)
        
        test_logger = logging.getLogger("test.multiconfig")
        test_logger.setLevel(logging.DEBUG)
        
        # Apply config multiple times
        for i in range(5):
            print(f"  Config change #{i+1}...")
            apply_logging_config()
            
            # Verify handler still attached
            assert handler in root_logger.handlers, f"Handler should be attached after config change #{i+1}"
            
            # Verify only ONE handler
            multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
            assert len(multilevel_handlers) == 1, f"Should have exactly 1 handler after config #{i+1}, got {len(multilevel_handlers)}"
            
            # Write test log
            test_logger.info(f"LOG AFTER CONFIG CHANGE #{i+1}")
            
            # Verify log captured
            info_logs = handler.get_buffer('INFO')
            assert any(f"LOG AFTER CONFIG CHANGE #{i+1}" in log for log in info_logs), f"Log after config #{i+1} should be captured"
        
        print("  ✅ Handler persisted across 5 config changes")
        print("✅ test_handler_persistence_across_multiple_config_changes PASSED")
        return True
        
    finally:
        # Cleanup
        if 'streamlit' in sys.modules:
            del sys.modules['streamlit']


if __name__ == "__main__":
    print("🧪 Running Logging Integration Tests")
    print("=" * 70)
    
    try:
        test_complete_workflow()
        test_handler_persistence_across_multiple_config_changes()
        
        print("=" * 70)
        print("✅ ALL INTEGRATION TESTS PASSED")
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
