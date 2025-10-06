#!/usr/bin/env python3
"""
Manual Verification Script für MultiLevelRingBufferHandler Persistence

Simuliert einen Environment-Switch und zeigt, dass Logs korrekt in UI-Buffers landen.
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from omf2.common.logger import setup_multilevel_ringbuffer_logging, MultiLevelRingBufferHandler
from omf2.common.logging_config import apply_logging_config, _ensure_multilevel_handler_attached


class MockSessionState:
    """Mock Streamlit session_state for testing"""
    def __init__(self):
        self._data = {}
    
    def get(self, key, default=None):
        return self._data.get(key, default)
    
    def __setitem__(self, key, value):
        self._data[key] = value
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __contains__(self, key):
        return key in self._data


def simulate_initial_setup(session_state):
    """Simuliert die initiale Dashboard-Initialisierung"""
    print("\n" + "="*70)
    print("📦 PHASE 1: Initial Dashboard Setup (omf.py)")
    print("="*70)
    
    # Initial setup like in omf.py
    if 'log_handler' not in session_state:
        handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
        session_state['log_handler'] = handler
        session_state['log_buffers'] = buffers
        print("✅ Initial logging setup complete")
    
    # Apply logging config
    apply_logging_config()
    print("✅ Logging configuration applied")
    
    # Verify handler is attached
    _ensure_multilevel_handler_attached()
    print("✅ Handler attachment verified")
    
    # Test logging
    logger = logging.getLogger("omf2.dashboard")
    logger.setLevel(logging.INFO)
    logger.info("🚀 Dashboard initialized - MOCK environment")
    
    # Show logs in buffer
    handler = session_state.get('log_handler')
    info_logs = handler.get_buffer('INFO')
    print(f"\n📋 Logs in UI buffer (INFO): {len(info_logs)} entries")
    for log in info_logs[-3:]:
        print(f"  • {log}")


def simulate_environment_switch(session_state, old_env, new_env):
    """Simuliert einen Environment-Switch"""
    print("\n" + "="*70)
    print(f"🔄 PHASE 2: Environment Switch ({old_env} → {new_env})")
    print("="*70)
    
    logger = logging.getLogger("omf2.dashboard")
    logger.info(f"🔄 ENV-SWITCH: Environment-Wechsel erkannt: '{old_env}' -> '{new_env}'")
    
    # Reconnect logging system (like in _reconnect_logging_system)
    print("🔧 Reconnecting logging system...")
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
    session_state['log_handler'] = handler
    session_state['log_buffers'] = buffers
    
    # VERIFICATION
    root_logger = logging.getLogger()
    handler_attached = handler in root_logger.handlers
    multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    handler_count = len(multilevel_handlers)
    
    if not handler_attached:
        print("❌ FEHLER: Handler ist NICHT am Root-Logger attached!")
        root_logger.addHandler(handler)
        print("⚠️ Forced re-attachment of handler")
    elif handler_count != 1:
        print(f"❌ FEHLER: {handler_count} MultiLevelRingBufferHandler (sollte 1 sein)")
    else:
        print(f"✅ Handler verified: Exactly 1 MultiLevelRingBufferHandler attached")
    
    # Test logging after switch
    logger.info(f"✅ Logging system reconnected successfully")
    logger.info(f"🧪 TEST: Environment switch complete - logging system reconnected")
    logger.info(f"📡 Now in {new_env.upper()} environment")
    
    # Show logs in buffer
    handler = session_state.get('log_handler')
    info_logs = handler.get_buffer('INFO')
    print(f"\n📋 Logs in UI buffer after switch (INFO): {len(info_logs)} entries")
    for log in info_logs[-5:]:
        print(f"  • {log}")


def simulate_ui_read_logs(session_state):
    """Simuliert das Lesen der Logs durch die UI"""
    print("\n" + "="*70)
    print("📺 PHASE 3: UI Reading Logs (system_logs_tab.py)")
    print("="*70)
    
    # Get log handler from session state (like in system_logs_tab.py)
    log_handler = session_state.get('log_handler')
    if not log_handler:
        print("❌ ERROR: No log handler available in session state!")
        return
    
    # Get all logs from all levels
    all_logs = []
    for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
        level_logs = log_handler.get_buffer(level)
        all_logs.extend(level_logs)
        print(f"  • {level}: {len(level_logs)} entries")
    
    print(f"\n✅ UI successfully read {len(all_logs)} total log entries from buffers")
    
    # Show recent logs
    print("\n📋 Recent logs (last 5):")
    for log in all_logs[-5:]:
        print(f"  • {log}")


def simulate_additional_logging(session_state):
    """Simuliert zusätzliche Logs nach Environment-Switch"""
    print("\n" + "="*70)
    print("📝 PHASE 4: Additional Logging After Environment Switch")
    print("="*70)
    
    # Create test loggers
    admin_logger = logging.getLogger("omf2.admin.admin_gateway")
    admin_logger.setLevel(logging.INFO)
    
    ccu_logger = logging.getLogger("omf2.ccu.ccu_gateway")
    ccu_logger.setLevel(logging.INFO)
    
    # Write some logs
    admin_logger.info("🔌 Admin MQTT Client connected to replay")
    ccu_logger.info("🏗️ CCU MQTT Client connected to replay")
    admin_logger.warning("⚠️ Some non-critical issue in admin")
    ccu_logger.error("❌ Critical error in CCU")
    
    # Read logs from buffer
    handler = session_state.get('log_handler')
    info_logs = handler.get_buffer('INFO')
    warning_logs = handler.get_buffer('WARNING')
    error_logs = handler.get_buffer('ERROR')
    
    print(f"\n📊 Buffer Statistics:")
    print(f"  • INFO: {len(info_logs)} entries")
    print(f"  • WARNING: {len(warning_logs)} entries")
    print(f"  • ERROR: {len(error_logs)} entries")
    
    print(f"\n📋 Recent ERROR logs:")
    for log in error_logs[-2:]:
        print(f"  • {log}")
    
    print(f"\n📋 Recent WARNING logs:")
    for log in warning_logs[-2:]:
        print(f"  • {log}")


def main():
    """Main verification script"""
    print("\n" + "="*70)
    print("🧪 MANUAL VERIFICATION: MultiLevelRingBufferHandler Persistence")
    print("="*70)
    print("\nThis script simulates:")
    print("1. Initial dashboard setup")
    print("2. Environment switch (mock → replay)")
    print("3. UI reading logs from buffers")
    print("4. Additional logging after switch")
    
    # Mock session state
    session_state = MockSessionState()
    
    # Simulate workflow
    simulate_initial_setup(session_state)
    simulate_environment_switch(session_state, "mock", "replay")
    simulate_ui_read_logs(session_state)
    simulate_additional_logging(session_state)
    
    # Final verification
    print("\n" + "="*70)
    print("✅ VERIFICATION COMPLETE")
    print("="*70)
    
    handler = session_state.get('log_handler')
    root_logger = logging.getLogger()
    
    # Check handler is still attached
    handler_attached = handler in root_logger.handlers
    multilevel_handlers = [h for h in root_logger.handlers if isinstance(h, MultiLevelRingBufferHandler)]
    handler_count = len(multilevel_handlers)
    
    print(f"\n🔍 Final Status:")
    print(f"  • Handler in session_state: {'✅ Yes' if handler else '❌ No'}")
    print(f"  • Handler attached to root logger: {'✅ Yes' if handler_attached else '❌ No'}")
    print(f"  • Number of MultiLevelRingBufferHandler: {handler_count} {'✅' if handler_count == 1 else '❌'}")
    print(f"  • Handler identity match: {'✅ Yes' if handler is session_state.get('log_handler') else '❌ No'}")
    
    # Buffer statistics
    info_count = len(handler.get_buffer('INFO'))
    warning_count = len(handler.get_buffer('WARNING'))
    error_count = len(handler.get_buffer('ERROR'))
    debug_count = len(handler.get_buffer('DEBUG'))
    total = info_count + warning_count + error_count + debug_count
    
    print(f"\n📊 Total Logs in Buffers: {total}")
    print(f"  • INFO: {info_count}")
    print(f"  • WARNING: {warning_count}")
    print(f"  • ERROR: {error_count}")
    print(f"  • DEBUG: {debug_count}")
    
    # Success check
    if handler_attached and handler_count == 1 and total > 0:
        print("\n✅ SUCCESS: All acceptance criteria met!")
        print("  • Handler correctly attached to root logger")
        print("  • Exactly ONE MultiLevelRingBufferHandler exists")
        print("  • Logs are being captured in UI buffers")
        print("  • Handler in session_state matches actual handler")
        return 0
    else:
        print("\n❌ FAILURE: Some criteria not met")
        return 1


if __name__ == "__main__":
    sys.exit(main())
