# Testing MultiLevelRingBufferHandler Persistence

This directory contains tests for the MultiLevelRingBufferHandler persistence fix.

## Automated Tests

### test_multilevel_handler_persistence.py

Run automated unit tests:

```bash
# OMF2 Tests wurden entfernt (Legacy)
# Für OMF3 Tests: nx test ccu-ui
```

**Tests:**
1. `test_handler_attachment_after_setup` - Verifies handler is attached after setup
2. `test_handler_reuse_without_force_new` - Verifies handler reuse when force_new=False
3. `test_handler_replacement_with_force_new` - Verifies new handler with force_new=True
4. `test_handler_persistence_after_apply_logging_config` - Verifies handler survives config changes
5. `test_logging_actually_works` - Verifies logs are captured in buffers
6. `test_environment_switch_simulation` - Simulates environment switch scenario

**Expected Output:**
```
✅ test_handler_attachment_after_setup PASSED
✅ test_handler_reuse_without_force_new PASSED
✅ test_handler_replacement_with_force_new PASSED
✅ test_handler_persistence_after_apply_logging_config PASSED
✅ test_logging_actually_works PASSED
✅ test_environment_switch_simulation PASSED
✅ ALL TESTS PASSED
```

## Manual Verification

### manual_verify_handler_persistence.py

Run manual verification script:

```bash
python tests/manual_verify_handler_persistence.py
```

**Simulates:**
1. Initial dashboard setup (like omf.py)
2. Environment switch (mock → replay)
3. UI reading logs (like system_logs_tab.py)
4. Additional logging after switch

**Expected Output:**
```
📦 PHASE 1: Initial Dashboard Setup
✅ Initial logging setup complete
✅ Logging configuration applied
✅ Handler attachment verified

🔄 PHASE 2: Environment Switch (mock → replay)
✅ Handler verified: Exactly 1 MultiLevelRingBufferHandler attached

📺 PHASE 3: UI Reading Logs
✅ UI successfully read X total log entries from buffers

📝 PHASE 4: Additional Logging After Environment Switch
✅ Logs captured in buffers

✅ SUCCESS: All acceptance criteria met!
```

## Running All Tests

Run both automated and manual tests:

```bash
# Automated tests
python tests/test_omf2/test_multilevel_handler_persistence.py

# Manual verification
python tests/manual_verify_handler_persistence.py
```

## Test Coverage

### What is Tested

✅ Handler attachment to root logger
✅ Handler persistence across configuration changes
✅ Handler persistence across environment switches
✅ Prevention of duplicate handlers
✅ Actual log capture in buffers
✅ UI reading logs from buffers
✅ Session state handler identity

### What is NOT Tested (Requires Streamlit)

⚠️ Actual Streamlit UI rendering
⚠️ Real MQTT connections
⚠️ Real environment switches in production

## Integration Testing

To test with actual Streamlit dashboard:

1. Start the dashboard:
   ```bash
   streamlit run omf2/omf.py
   ```

2. Perform environment switch:
   - Change environment from "mock" to "replay" in sidebar
   - Observe logs in System Logs tab

3. Verify:
   - ✅ Logs appear in UI after environment switch
   - ✅ No duplicate handlers
   - ✅ All log levels captured (ERROR, WARNING, INFO, DEBUG)

## Troubleshooting

If tests fail:

1. Check Python version (requires >=3.8)
2. Ensure all dependencies are installed
3. Check for import errors
4. Review test output for specific failure points

For detailed debugging, check the log messages in test output.
