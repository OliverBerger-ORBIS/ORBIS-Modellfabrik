# Central Logging Refactoring - Implementation Summary

## Overview
This document summarizes the refactoring of the central logging and log buffering system in omf2/.

## Changes Made

### 1. Enhanced `omf2/common/logger.py`
**Purpose**: Central logging infrastructure

**Added Components**:
- `RingBufferHandler`: Logging handler that writes to a ring buffer (thread-safe)
- `create_log_buffer()`: Creates a deque-based log buffer with size limit
- `setup_central_log_buffer()`: Initializes central log buffer and attaches handlers to root and omf2 loggers
- `get_log_buffer_entries()`: Retrieves formatted log entries from buffer

**Modified Components**:
- `get_logger()`: Now detects if central buffer is active and allows propagation accordingly
  - When central buffer exists: logs propagate to root logger
  - When no central buffer: creates local handler (backward compatible)

### 2. Refactored `omf2/admin/log_manager.py`
**Purpose**: Business logic layer for log management

**Key Changes**:
- `LogManager` now accepts and uses the central log buffer (Deque[str])
- `LogEntry.from_log_line()`: Parses log lines from central buffer (supports millisecond timestamps)
- All analysis methods (`get_logs`, `search_logs`, `get_statistics`, etc.) read from central buffer
- Business logic separated from buffer management
- Removed old `LogBuffer` class (now uses central buffer from logger.py)

**API**:
- `get_log_manager(log_buffer=...)`: Creates/returns singleton with central buffer
- `set_log_buffer(buffer)`: Late initialization of buffer
- `get_logs(limit, level, component, since)`: Get filtered logs
- `search_logs(query, limit)`: Search logs by content
- `get_log_statistics()`: Get statistics from buffer
- `export_logs(filepath, ...)`: Export logs to JSON
- `clear_logs()`: Clear central buffer

### 3. Updated `omf2/ui/admin/system_logs/system_logs_tab.py`
**Purpose**: System Logs UI component

**Implementation**:
- Renders System Logs tab with 4 sub-tabs:
  1. **Recent Logs**: Filterable log viewer (by level, component, limit)
  2. **Search Logs**: Search functionality with keyword matching
  3. **Statistics**: Log statistics dashboard (level/component distribution)
  4. **Management**: Clear logs and export functionality

**Features**:
- Uses `LogManager` to access central buffer
- Color-coded log levels with icons
- Expandable log entries with full details
- Real-time filtering and search
- Log export to JSON with filters
- Clear logs functionality

### 4. Updated `omf2/omf.py`
**Purpose**: Application startup

**Changes**:
- Replaced manual log buffer initialization with `setup_central_log_buffer()`
- Simplified initialization code
- Central buffer stored in `st.session_state['log_buffer']`
- All omf2 loggers automatically configured to propagate

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Startup                      │
│                      (omf2/omf.py)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ setup_central_log_buffer()
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Central Logging Infrastructure                  │
│                 (omf2/common/logger.py)                     │
│                                                             │
│  ┌──────────────┐    ┌─────────────────┐                  │
│  │ RingBuffer   │◄───│ RingBuffer      │                  │
│  │ Handler      │    │ Handler         │                  │
│  └──────┬───────┘    └────────┬────────┘                  │
│         │                     │                            │
│         │ attached to         │ attached to                │
│         ▼                     ▼                            │
│  ┌──────────────┐    ┌─────────────────┐                  │
│  │ Root Logger  │    │ omf2.* Loggers  │                  │
│  │              │    │ (propagate=True)│                  │
│  └──────┬───────┘    └────────┬────────┘                  │
│         │                     │                            │
│         └──────────┬──────────┘                            │
│                    │                                        │
│                    ▼                                        │
│         ┌─────────────────────┐                           │
│         │  Central Log Buffer │                           │
│         │  (Deque[str])       │                           │
│         └──────────┬──────────┘                           │
└────────────────────┼───────────────────────────────────────┘
                     │
                     │ read access
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Business Logic Layer                            │
│              (omf2/admin/log_manager.py)                    │
│                                                             │
│  ┌────────────────────────────────────────────┐            │
│  │ LogManager                                 │            │
│  │  - parse logs from buffer                  │            │
│  │  - filter by level/component/time          │            │
│  │  - search logs                             │            │
│  │  - get statistics                          │            │
│  │  - export logs                             │            │
│  └────────────────┬───────────────────────────┘            │
└───────────────────┼─────────────────────────────────────────┘
                    │
                    │ uses
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                      UI Layer                                │
│        (omf2/ui/admin/system_logs/system_logs_tab.py)       │
│                                                             │
│  ┌────────────────────────────────────────────┐            │
│  │ System Logs Tab                            │            │
│  │  - Recent Logs (filtered viewer)           │            │
│  │  - Search Logs (keyword search)            │            │
│  │  - Statistics (dashboard)                  │            │
│  │  - Management (clear/export)               │            │
│  └────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Testing

### Test Coverage
- **27 tests** for omf2 logging functionality
- **3 test suites**:
  1. `test_central_logging.py`: Tests for central logging infrastructure (6 tests)
  2. `test_log_manager.py`: Tests for LogManager business logic (15 tests)
  3. `test_logging_integration.py`: Integration tests (6 tests)

### Test Results
```
Ran 27 tests in 0.009s - OK
```

### Key Test Scenarios
- ✅ Central log buffer creation and initialization
- ✅ RingBufferHandler functionality
- ✅ Logger propagation to central buffer
- ✅ LogManager filtering (level, component, time)
- ✅ LogManager search functionality
- ✅ LogManager statistics generation
- ✅ Log export to JSON
- ✅ Log parsing from buffer
- ✅ Integration with get_logger()

## Benefits

1. **Centralized**: All logging components in one place (`omf2/common/logger.py`)
2. **Separation of Concerns**: 
   - Infrastructure in `common/logger.py`
   - Business logic in `admin/log_manager.py`
   - UI in `ui/admin/system_logs/`
3. **Thread-Safe**: RingBufferHandler is thread-safe for MQTT callbacks
4. **Backward Compatible**: Old code still works
5. **Testable**: Comprehensive test coverage
6. **Configurable**: Log level and buffer size configurable
7. **Propagation**: All omf2 loggers automatically captured

## Usage Examples

### Setup Central Buffer (Application Startup)
```python
from omf2.common.logger import setup_central_log_buffer

# Initialize at app startup
log_buffer, ring_handler = setup_central_log_buffer(
    buffer_size=1000,
    log_level=logging.INFO
)
st.session_state['log_buffer'] = log_buffer
```

### Using LogManager (Business Logic)
```python
from omf2.admin.log_manager import get_log_manager, LogLevel

# Get LogManager with central buffer
log_manager = get_log_manager(log_buffer=st.session_state['log_buffer'])

# Get filtered logs
logs = log_manager.get_logs(limit=100, level=LogLevel.ERROR)

# Search logs
results = log_manager.search_logs("MQTT", limit=50)

# Get statistics
stats = log_manager.get_log_statistics()

# Export logs
log_manager.export_logs(Path("logs/export.json"))
```

### Using get_logger (Application Code)
```python
from omf2.common.logger import get_logger

# Get logger (automatically propagates to central buffer)
logger = get_logger("omf2.mymodule")

# Log messages (appear in System Logs tab)
logger.info("Application started")
logger.warning("Warning message")
logger.error("Error message")
```

## Migration Notes

### Old Dashboard Components
The following old components still exist but are no longer used:
- `omf/dashboard/tools/streamlit_log_buffer.py`
- `omf2/common/streamlit_log_buffer.py`

These can be deleted after PR approval as specified in the requirements.

### Breaking Changes
None - the implementation is backward compatible.

## Future Enhancements

Possible improvements for future iterations:
1. Persistent log storage (already has file export)
2. Real-time log streaming in UI
3. Log visualization (charts, graphs)
4. Advanced filtering (regex, date ranges)
5. Log rotation policies
6. Performance metrics logging
7. Integration with external logging services

## Conclusion

The central logging refactoring successfully:
- ✅ Consolidates all logging infrastructure in `omf2/common/logger.py`
- ✅ Separates business logic into `omf2/admin/log_manager.py`
- ✅ Provides a comprehensive System Logs UI
- ✅ Ensures all logger.info() calls appear in System Logs
- ✅ Maintains backward compatibility
- ✅ Has comprehensive test coverage (27 tests passing)
