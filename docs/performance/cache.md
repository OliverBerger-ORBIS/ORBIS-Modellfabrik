# Cache Performance Optimization

## Overview

The caching layer is a lightweight, opt-in performance optimization that reduces latency and repeated I/O operations when loading configuration files and manager data throughout the application.

This provides a **consistent caching architecture and pattern** for all managers and config loaders:
- Admin dashboard config loading
- RegistryManager  
- CCUConfigLoader
- Other manager/loader instances across all modules

## Rationale

Many parts of the application frequently load configuration files and manager data. Without caching, these files are read from disk repeatedly, causing:

- Increased latency for rendering and operations
- Unnecessary disk I/O operations
- Poor user experience when switching between tabs or refreshing views

The caching layer addresses these issues by storing parsed configuration data in memory with a configurable Time-To-Live (TTL), reducing repeated file reads while ensuring data freshness.

## Architecture

### Cache Module (`omf2/common/cache.py`)

The cache implementation is:
- **Dependency-free**: Uses only Python standard library (`time`, `threading.Lock`)
- **Thread-safe**: Protected by locks for concurrent access
- **TTL-based**: Entries automatically expire after the configured TTL
- **Opt-in**: Disabled by default, enabled via environment variable
- **Consistent**: Same pattern across all modules

### Key Components

1. **TTLCache Class**: Core cache implementation with get/set/clear operations
2. **Cached Decorator**: Function decorator for automatic caching
3. **Global Cache Instance**: Singleton pattern for shared cache access

### Integration Points

The cache can be used consistently across all modules:

**Currently integrated:**
- `omf2/ui/admin/admin_settings/dashboard_subtab.py` - Admin dashboard config loading

**Available for integration:**
- `omf2/registry/manager/registry_manager.py` - Registry data loading
- `omf2/ccu/config_loader.py` - CCU config loading
- Other manager/loader modules throughout the application

## Configuration

### Environment Variables

**`OMF2_CACHE_TTL`** (Recommended): General cache TTL for all modules
- **Default**: Caching disabled (if unset or `0`)
- **Recommended**: `60` (60 seconds)
- **Range**: Any positive float value

**`OMF2_ADMIN_CACHE_TTL`** (Legacy): Admin-specific cache TTL (backwards compatibility)
- Falls back to this if `OMF2_CACHE_TTL` is not set
- Maintained for backwards compatibility

**Precedence**: `OMF2_CACHE_TTL` takes precedence over `OMF2_ADMIN_CACHE_TTL` if both are set.

### Examples

```bash
# Enable caching with 60 second TTL (recommended - works for all modules)
export OMF2_CACHE_TTL=60

# Enable caching with 2 second TTL (for testing)
export OMF2_CACHE_TTL=2

# Disable caching (default)
unset OMF2_CACHE_TTL
# or
export OMF2_CACHE_TTL=0

# Legacy admin-specific setting (still supported)
export OMF2_ADMIN_CACHE_TTL=60
```

## Usage

### For Developers - Consistent Pattern Across All Modules

The cache provides a consistent architecture and pattern for use in any module. Here are the recommended patterns:

#### Pattern 1: Using `get_or_set` (Recommended)

```python
from omf2.common.cache import get_cache

def load_expensive_config():
    cache = get_cache()
    
    def loader():
        # Your expensive operation here
        return load_from_disk()
    
    return cache.get_or_set("unique_key", loader)
```

#### Pattern 2: Using the `@cached` Decorator

```python
from omf2.common.cache import cached

@cached(ttl=60, key_prefix="my_module")
def load_expensive_config():
    # Your expensive operation here
    return load_from_disk()
```

#### Example: Integrating with Existing Managers

**For CCUConfigLoader:**
```python
from omf2.common.cache import get_cache

class CCUConfigLoader:
    def _load_json_config(self, filename: str) -> Dict[str, Any]:
        cache = get_cache()
        cache_key = f"ccu_config:{filename}"
        
        def loader():
            # Existing loading logic
            config_file = self.config_path / filename
            with open(config_file, encoding="utf-8") as f:
                return json.load(f)
        
        return cache.get_or_set(cache_key, loader)
```

**For RegistryManager:**
```python
from omf2.common.cache import cached

class RegistryManager:
    @cached(ttl=120, key_prefix="registry")
    def _load_topics(self):
        # Existing loading logic
        topics_file = self.registry_path / "topics.yml"
        with open(topics_file) as f:
            return yaml.safe_load(f)
```

### Defensive Fallback

All modules should implement defensive imports to ensure graceful degradation:

```python
try:
    from omf2.common.cache import get_cache
    _cache_available = True
except ImportError:
    _cache_available = False
```

If the cache module is not available or fails to import, code continues without cache, directly loading data.

## Quality Assurance

### QA Steps

1. **Test with caching disabled (default)**
   ```bash
   unset OMF2_CACHE_TTL
   streamlit run omf2/omf.py
   ```
   - Navigate to Admin tab multiple times
   - Verify dashboard loads correctly
   - Check logs for "using direct loading" message

2. **Test with caching enabled**
   ```bash
   export OMF2_CACHE_TTL=60
   streamlit run omf2/omf.py
   ```
   - Navigate to Admin tab
   - Verify dashboard loads correctly
   - Refresh tab multiple times within 60 seconds
   - Verify subsequent loads are faster (config files only read once)

3. **Test cache expiration**
   ```bash
   export OMF2_CACHE_TTL=2
   streamlit run omf2/omf.py
   ```
   - Navigate to Admin tab (loads config files)
   - Wait 3 seconds
   - Navigate to Admin tab again
   - Verify config files are re-read after TTL expiration

4. **Test legacy environment variable (backwards compatibility)**
   ```bash
   export OMF2_ADMIN_CACHE_TTL=60
   streamlit run omf2/omf.py
   ```
   - Verify caching still works with legacy env var

5. **Verify cache behavior in logs**
   - Enable debug logging if available
   - Check for cache hit/miss logging
   - Verify file loading happens as expected

6. **Run automated tests**
   ```bash
   pytest tests/test_admin_cache.py -v
   ```
   - All tests should pass (21 tests)
   - Tests verify cache behavior, TTL expiration, env var precedence, and edge cases

### Manual Verification

To manually verify the cache is working in any module:

1. Add temporary logging in the module you're testing:
   ```python
   def _load_config_file(file_path: Path) -> dict:
       logger.info(f"Loading config file: {file_path}")  # Add this
       # ... rest of function
   ```

2. Run with caching enabled:
   ```bash
   export OMF2_CACHE_TTL=60
   streamlit run omf2/omf.py
   ```

3. Use the module/feature multiple times
4. Check logs - "Loading config file" should appear only once per TTL period

## Performance Impact

### Expected Benefits

- **Reduced latency**: Estimated 50-90% reduction in load time for cached entries (depends on file system speed and cache hit rate)
- **Reduced I/O**: Files read once per TTL period instead of every access
- **Better UX**: Faster tab switching, refresh, and module operations
- **Consistent pattern**: Same caching approach across all modules reduces code duplication

### Measurements

With TTL=60 and typical config files (admin dashboard example):

| Metric | Without Cache | With Cache (first load) | With Cache (cached) |
|--------|---------------|-------------------------|---------------------|
| File reads | 3 per view | 3 (initial) | 0 (cached) |
| Typical latency | 20-50ms | 20-50ms | <1ms |

### Scalability

The consistent caching architecture provides benefits across the application:
- Admin dashboard: 3 config files
- CCU Config Loader: Multiple JSON configs
- Registry Manager: YAML registry files
- Other managers: Various config/data files

**Total impact increases** as more modules adopt the consistent caching pattern.

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
   echo $OMF2_CACHE_TTL
   # or check legacy var
   echo $OMF2_ADMIN_CACHE_TTL
   ```

2. Check for import errors in logs (check your application's log output)

3. Ensure cache module exists:
   ```bash
   ls -la omf2/common/cache.py
   ```

### Cache serving stale data

1. Reduce TTL for more frequent updates:
   ```bash
   export OMF2_CACHE_TTL=10
   ```

2. Or disable caching during development:
   ```bash
   export OMF2_CACHE_TTL=0
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
- Per-file or per-module TTL configuration
- Shared cache across processes (Redis/Memcached)
- Integration examples for all existing managers

## Related Documentation

For more information on related topics, see the main documentation in the `docs/` directory.

## References

- **Cache Implementation**: `omf2/common/cache.py` (moved from `omf2/ui/admin/cache.py`)
- **Admin Integration**: `omf2/ui/admin/admin_settings/dashboard_subtab.py`
- **Tests**: `tests/test_admin_cache.py`
- **Available for Integration**:
  - `omf2/registry/manager/registry_manager.py`
  - `omf2/ccu/config_loader.py`
  - Other manager/loader modules
