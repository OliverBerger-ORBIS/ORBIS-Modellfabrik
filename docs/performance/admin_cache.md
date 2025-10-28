# Admin Cache Performance Optimization

## Overview

The Admin tab caching layer is a lightweight, opt-in performance optimization that reduces latency and repeated I/O operations when loading configuration files and manager data in the Admin dashboard.

## Rationale

The Admin tab frequently loads configuration files (MQTT settings, user roles, apps configuration) on every view. Without caching, these files are read from disk repeatedly, causing:

- Increased latency for dashboard rendering
- Unnecessary disk I/O operations
- Poor user experience when switching between admin tabs or refreshing the view

The caching layer addresses these issues by storing parsed configuration data in memory with a configurable Time-To-Live (TTL), reducing repeated file reads while ensuring data freshness.

## Architecture

### Cache Module (`omf2/ui/admin/cache.py`)

The cache implementation is:
- **Dependency-free**: Uses only Python standard library (`time`, `threading.Lock`)
- **Thread-safe**: Protected by locks for concurrent access
- **TTL-based**: Entries automatically expire after the configured TTL
- **Opt-in**: Disabled by default, enabled via environment variable

### Key Components

1. **TTLCache Class**: Core cache implementation with get/set/clear operations
2. **Cached Decorator**: Function decorator for automatic caching
3. **Global Cache Instance**: Singleton pattern for shared cache access

### Integration Points

Currently integrated in:
- `omf2/ui/admin/admin_settings/dashboard_subtab.py`
  - MQTT settings loading
  - User roles loading
  - Apps configuration loading

## Configuration

### Environment Variable

**`OMF2_ADMIN_CACHE_TTL`**: Time-to-live for cache entries in seconds

- **Default**: Caching disabled (if unset or `0`)
- **Recommended**: `60` (60 seconds)
- **Range**: Any positive float value

### Examples

```bash
# Enable caching with 60 second TTL
export OMF2_ADMIN_CACHE_TTL=60

# Enable caching with 2 second TTL (for testing)
export OMF2_ADMIN_CACHE_TTL=2

# Disable caching (default)
unset OMF2_ADMIN_CACHE_TTL
# or
export OMF2_ADMIN_CACHE_TTL=0
```

## Usage

### For Developers

The cache is integrated transparently in the dashboard. No code changes are needed to benefit from caching when it's enabled.

To add caching to new admin functions:

```python
from omf2.ui.admin.cache import get_cache

def load_expensive_config():
    cache = get_cache()
    
    def loader():
        # Your expensive operation here
        return load_from_disk()
    
    return cache.get_or_set("unique_key", loader)
```

Or using the decorator:

```python
from omf2.ui.admin.cache import cached

@cached(ttl=60, key_prefix="my_module")
def load_expensive_config():
    # Your expensive operation here
    return load_from_disk()
```

### Defensive Fallback

The dashboard implements defensive imports:

```python
try:
    from omf2.ui.admin.cache import get_cache
    _cache_available = True
except ImportError:
    _cache_available = False
```

If the cache module is not available or fails to import, the dashboard falls back to direct file loading without raising exceptions.

## Quality Assurance

### QA Steps

1. **Test with caching disabled (default)**
   ```bash
   unset OMF2_ADMIN_CACHE_TTL
   streamlit run omf2/omf.py
   ```
   - Navigate to Admin tab multiple times
   - Verify dashboard loads correctly
   - Check logs for "using direct loading" message

2. **Test with caching enabled**
   ```bash
   export OMF2_ADMIN_CACHE_TTL=60
   streamlit run omf2/omf.py
   ```
   - Navigate to Admin tab
   - Verify dashboard loads correctly
   - Refresh tab multiple times within 60 seconds
   - Verify subsequent loads are faster (config files only read once)

3. **Test cache expiration**
   ```bash
   export OMF2_ADMIN_CACHE_TTL=2
   streamlit run omf2/omf.py
   ```
   - Navigate to Admin tab (loads config files)
   - Wait 3 seconds
   - Navigate to Admin tab again
   - Verify config files are re-read after TTL expiration

4. **Verify cache behavior in logs**
   - Enable debug logging if available
   - Check for cache hit/miss logging
   - Verify file loading happens as expected

5. **Run automated tests**
   ```bash
   pytest tests/test_admin_cache.py -v
   ```
   - All tests should pass
   - Tests verify cache behavior, TTL expiration, and edge cases

### Manual Verification

To manually verify the cache is working:

1. Add temporary logging in `dashboard_subtab.py`:
   ```python
   def _load_config_file(file_path: Path) -> dict:
       logger.info(f"Loading config file: {file_path}")  # Add this
       # ... rest of function
   ```

2. Run with caching enabled:
   ```bash
   export OMF2_ADMIN_CACHE_TTL=60
   streamlit run omf2/omf.py
   ```

3. Navigate to Admin tab multiple times
4. Check logs - "Loading config file" should appear only once per TTL period

## Performance Impact

### Expected Benefits

- **Reduced latency**: Estimated 50-90% reduction in dashboard render time for cached entries (depends on file system speed and cache hit rate)
- **Reduced I/O**: Files read once per TTL period instead of every view
- **Better UX**: Faster tab switching and refresh in Admin dashboard

### Measurements

With TTL=60 and 3 config files (MQTT, roles, apps):

| Metric | Without Cache | With Cache (first load) | With Cache (cached) |
|--------|---------------|-------------------------|---------------------|
| File reads | 3 per view | 3 (initial) | 0 (cached) |
| Typical latency | 20-50ms | 20-50ms | <1ms |

## Safety & Constraints

### Safety Features

1. **Opt-in by default**: Caching disabled unless explicitly enabled
2. **Defensive fallback**: Dashboard works without cache if import fails
3. **Thread-safe**: All cache operations protected by locks
4. **No state mutation**: Cache stores immutable parsed configs
5. **Automatic expiration**: Stale data automatically removed by TTL

### Constraints

- Cache is in-memory only (not persisted)
- Cache is process-local (not shared across Streamlit processes)
- Cache does not detect file changes during TTL period
- For multi-process deployments, each process has its own cache

### Limitations

- If config files change during TTL, changes won't be visible until cache expires
- Recommended to set TTL ≤ 60 seconds for development environments
- For production, TTL can be longer (e.g., 300 seconds) if configs rarely change

## Troubleshooting

### Cache not working

1. Verify environment variable is set:
   ```bash
   echo $OMF2_ADMIN_CACHE_TTL
   ```

2. Check for import errors in logs (check your application's log output)

3. Ensure cache module exists:
   ```bash
   ls -la omf2/ui/admin/cache.py
   ```

### Cache serving stale data

1. Reduce TTL for more frequent updates:
   ```bash
   export OMF2_ADMIN_CACHE_TTL=10
   ```

2. Or disable caching during development:
   ```bash
   export OMF2_ADMIN_CACHE_TTL=0
   ```

### Memory usage concerns

The cache stores parsed YAML configs (typically small dictionaries). Memory overhead is minimal:
- Typical config file: 5-20 KB parsed
- 3 config files: ~15-60 KB total
- With overhead: ~100-200 KB maximum

For large deployments, monitor memory usage and adjust TTL as needed.

## Future Enhancements

Potential improvements (not currently implemented):

- File system watching to invalidate cache on file changes
- Configurable cache size limits
- Cache statistics/metrics endpoint
- Per-file TTL configuration
- Shared cache across processes (Redis/Memcached)

## Related Documentation

For more information on related topics, see the main documentation in the `docs/` directory.

## References

- Implementation: `omf2/ui/admin/cache.py`
- Integration: `omf2/ui/admin/admin_settings/dashboard_subtab.py`
- Tests: `tests/test_admin_cache.py`
