# Handler Persistence - Quick Reference

## When to Call `ensure_ringbufferhandler_attached()`

### ✅ MUST Call After
1. **Environment Switch** - After changing from live/replay/mock
2. **Logging Config Change** - After calling `apply_logging_config()`
3. **Handler Recreation** - After calling `setup_multilevel_ringbuffer_logging(force_new=True)`

### ❌ DO NOT Call
- On every log message (performance impact)
- Inside loops or hot code paths
- During normal logging operations

## Code Patterns

### Environment Switch Pattern
```python
# In main_dashboard.py
def _reconnect_logging_system(self):
    # 1. Force new handler creation
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
    
    # 2. Update session state
    st.session_state['log_handler'] = handler
    st.session_state['log_buffers'] = buffers
    
    # 3. Verify attachment
    ensure_ringbufferhandler_attached()
```

### Config Change Pattern
```python
# In logging_config.py
def apply_logging_config():
    # 1. Apply log levels
    logging.getLogger().setLevel(level)
    
    # 2. Ensure handler survives config changes
    ensure_ringbufferhandler_attached()
```

### UI Access Pattern
```python
# In system_logs_tab.py
def _render_log_history(admin_gateway):
    # CORRECT: Read from session state
    log_handler = st.session_state.get('log_handler')
    logs = log_handler.get_buffer('INFO')
    
    # WRONG: Direct access to root logger
    # root = logging.getLogger()
    # handler = [h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)][0]
```

## Debugging

### Check Handler Status
```python
import logging
from omf2.common.logger import MultiLevelRingBufferHandler

root = logging.getLogger()
multilevel_handlers = [h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]

print(f"Handler count: {len(multilevel_handlers)}")  # Should be 1
print(f"Handler attached: {st.session_state['log_handler'] in root.handlers}")  # Should be True
```

### Verify Logs Flow
```python
# 1. Log a test message
logger = logging.getLogger('test')
logger.info("Test message")

# 2. Check if captured
handler = st.session_state.get('log_handler')
logs = handler.get_buffer('INFO')
print(f"Captured logs: {len(logs)}")  # Should be > 0
print(f"Test message in logs: {'Test message' in str(logs)}")  # Should be True
```

### Common Issues

#### Issue: No logs in UI
```python
# Check 1: Handler exists in session state?
if 'log_handler' not in st.session_state:
    print("❌ No log_handler in session state")
    # Solution: Call setup_multilevel_ringbuffer_logging()

# Check 2: Handler attached to root logger?
handler = st.session_state['log_handler']
if handler not in logging.getLogger().handlers:
    print("❌ Handler not attached to root logger")
    # Solution: Call ensure_ringbufferhandler_attached()

# Check 3: Log level allows messages?
if logging.getLogger().level > logging.INFO:
    print("❌ Root logger level too high")
    # Solution: logging.getLogger().setLevel(logging.DEBUG)
```

#### Issue: Duplicate logs
```python
# Check: Multiple handlers?
root = logging.getLogger()
multilevel_handlers = [h for h in root.handlers if isinstance(h, MultiLevelRingBufferHandler)]
if len(multilevel_handlers) > 1:
    print(f"❌ Found {len(multilevel_handlers)} handlers (should be 1)")
    # Solution: Call ensure_ringbufferhandler_attached() to remove duplicates
```

## Testing

### Unit Test Template
```python
def test_my_handler_change():
    import streamlit as st
    from omf2.common.logger import setup_multilevel_ringbuffer_logging, ensure_ringbufferhandler_attached
    
    # Setup
    handler, buffers = setup_multilevel_ringbuffer_logging(force_new=True)
    st.session_state['log_handler'] = handler
    st.session_state['log_buffers'] = buffers
    
    # Your code that modifies logging
    # ...
    
    # Verify
    ensure_ringbufferhandler_attached()
    assert st.session_state['log_handler'] in logging.getLogger().handlers
    
    # Verify single handler
    multilevel_handlers = [h for h in logging.getLogger().handlers 
                          if isinstance(h, MultiLevelRingBufferHandler)]
    assert len(multilevel_handlers) == 1
```

### Run Handler Tests
```bash
# Run all handler persistence tests
pytest tests/test_omf2/test_handler_persistence.py -v

# Run all logging tests
pytest tests/test_omf2/ -k "logging or handler" -v
```

## Performance Notes

### Good Practices
- ✅ Call `ensure_ringbufferhandler_attached()` only after config changes
- ✅ Use `force_new=True` only when necessary (environment switches)
- ✅ Read from session state in UI, not root logger

### Bad Practices
- ❌ Calling `ensure_ringbufferhandler_attached()` on every log message
- ❌ Creating new handlers without `force_new=True` cleanup
- ❌ Accessing root logger handlers directly in UI

## Summary

**Key Principle**: Handler should be created once per environment, stored in session state, and verified after any config changes.

**Flow**:
1. Create handler: `setup_multilevel_ringbuffer_logging(force_new=True)`
2. Store in session: `st.session_state['log_handler'] = handler`
3. Verify after changes: `ensure_ringbufferhandler_attached()`
4. UI reads from session: `st.session_state.get('log_handler')`

**Result**: Logs always appear in System Logs UI, no matter how many environment switches or config changes.
