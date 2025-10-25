# Business Functions Configuration

## Overview

The `business_functions.yml` configuration file defines metadata and wiring for business functions (managers) in the OMF2 system. This is a declarative configuration file that contains **NO executable code** - only metadata, class references, and topic routing information.

## Location

```
omf2/registry/business_functions.yml
```

## Purpose

Business functions are domain-specific components that handle:
- MQTT message routing and processing
- Business logic orchestration
- Domain-specific state management
- Inter-component coordination

The configuration file serves as:
1. **Documentation** - Clear overview of all business functions and their responsibilities
2. **Routing Configuration** - Defines which MQTT topics each function handles
3. **Enablement Control** - Easy enable/disable of functions without code changes
4. **Metadata Store** - Priority, categorization, and other metadata

## File Format

### Structure

```yaml
metadata:
  version: "1.0.0"
  last_updated: "YYYY-MM-DD"
  author: "Author Name"
  description: |
    Multi-line description of the configuration

business_functions:
  <function_name>:
    enabled: true/false
    description: "Human-readable description"
    module_path: "python.module.path"
    class_name: "ClassName"
    routed_topics:
      - "mqtt/topic/pattern"
      - "mqtt/topic/+/wildcard"
    priority: 1-10
    metadata:
      category: "category_name"
      requires_mqtt: true/false

qos_settings:
  default_qos: 1
  critical_topics:
    - "topic/pattern"
  qos: 2

routing:
  enable_wildcard_matching: true
  topic_separator: "/"

validation:
  require_module_path: true
  require_class_name: true
  allow_disabled_functions: true
```

### Field Descriptions

#### Metadata Section
- `version`: Configuration format version (semantic versioning)
- `last_updated`: Date of last update (ISO 8601)
- `author`: Configuration author/maintainer
- `description`: Multi-line description of the configuration

#### Business Functions Section

Each function requires:

- `enabled` (required): Whether the function is active
- `description` (required): Human-readable description
- `module_path` (required): Python module path (e.g., `omf2.ccu.business.order_manager`)
- `class_name` (required): Class name implementing the function
- `routed_topics` (optional): List of MQTT topics this function handles
  - Supports MQTT wildcards: `+` (single level), `#` (multi-level)
- `priority` (optional): Priority level 1-10 (default: 5, higher = more important)
- `metadata` (optional): Additional custom metadata
  - `category`: Function category (e.g., "orchestration", "inventory")
  - `requires_mqtt`: Whether MQTT connection is required

#### QoS Settings Section (Optional)
- `default_qos`: Default QoS level for topics (0, 1, or 2)
- `critical_topics`: List of topics requiring higher QoS
- `qos`: QoS level for critical topics

#### Routing Section (Optional)
- `enable_wildcard_matching`: Enable/disable wildcard support in topics
- `topic_separator`: Character used to separate topic levels (default: "/")

#### Validation Section (Optional)
- `require_module_path`: Enforce module_path presence
- `require_class_name`: Enforce class_name presence
- `allow_disabled_functions`: Allow disabled functions in config

## Example Configuration

```yaml
metadata:
  version: "1.0.0"
  last_updated: "2025-10-25"
  author: "OMF Development Team"
  description: "Production business functions configuration"

business_functions:
  order_manager:
    enabled: true
    description: "Manages order lifecycle and orchestration"
    module_path: "omf2.ccu.business.order_manager"
    class_name: "OrderManager"
    routed_topics:
      - "ccu/order/request"
      - "ccu/order/response"
      - "module/v1/ff/+/order"
    priority: 10
    metadata:
      category: "orchestration"
      requires_mqtt: true

  stock_manager:
    enabled: true
    description: "Manages inventory state"
    module_path: "omf2.ccu.business.stock_manager"
    class_name: "StockManager"
    routed_topics:
      - "ccu/state/stock"
      - "/j1/txt/1/f/i/stock"
    priority: 8
    metadata:
      category: "inventory"
      requires_mqtt: true
```

## Usage

### Loading Configuration

```python
from omf2.config.business_functions_loader import load_business_functions

# Load configuration
config = load_business_functions()

# Access business functions
functions = config['business_functions']
for name, func in functions.items():
    if func['enabled']:
        print(f"{name}: {func['description']}")
```

### Saving Configuration

```python
from omf2.config.business_functions_loader import save_business_functions

# Modify configuration
config['business_functions']['order_manager']['enabled'] = False

# Save back to file
save_business_functions(config)
```

### Using the Loader Class

```python
from omf2.config.business_functions_loader import BusinessFunctionsLoader

loader = BusinessFunctionsLoader()

# Load and validate (with Pydantic if available)
config = loader.load_validated()

# Get only enabled functions
enabled = loader.get_enabled_functions()

# Optional: Validate importability (requires ENABLE_IMPORT_CHECK=1)
import os
os.environ['ENABLE_IMPORT_CHECK'] = '1'
results = loader.validate_importability()
```

## Dashboard UI

The configuration can be viewed and edited through the Dashboard UI:

1. Navigate to **CCU Configuration** tab
2. Select **Business Functions** subtab
3. Use the interface to:
   - **Quick Edit**: Enable/disable functions, edit topics, change priorities
   - **YAML View**: Edit the complete configuration as YAML
   - **Info**: View statistics and metadata

### UI Features

- **Enable/Disable Toggle**: Quickly enable or disable functions
- **Topic Editor**: Edit routed topics (one per line, supports wildcards)
- **Priority Slider**: Adjust function priority (1-10)
- **YAML Editor**: Direct YAML editing with syntax validation
- **Save/Reload**: Save changes to file or reload from disk
- **Validation**: Check configuration for errors

## Migration Guide

### From Code to Configuration

If business function routing was previously hardcoded:

**Before (Code):**
```python
class OrderManager:
    def get_subscribed_topics(self):
        return ["ccu/order/request", "ccu/order/response"]
```

**After (Configuration):**
```yaml
business_functions:
  order_manager:
    enabled: true
    description: "Order management"
    module_path: "omf2.ccu.business.order_manager"
    class_name: "OrderManager"
    routed_topics:
      - "ccu/order/request"
      - "ccu/order/response"
```

### Adding New Business Functions

1. Create the business function class:
   ```python
   # omf2/ccu/business/my_manager.py
   class MyManager:
       def __init__(self, gateway):
           self.gateway = gateway
   ```

2. Add to configuration:
   ```yaml
   business_functions:
     my_manager:
       enabled: true
       description: "My new manager"
       module_path: "omf2.ccu.business.my_manager"
       class_name: "MyManager"
       routed_topics:
         - "my/topic/+"
       priority: 5
   ```

3. Restart the application to load the new configuration

## Validation

### Schema Validation

The configuration uses Pydantic models for validation (when available):

```python
from omf2.config.schemas.business_functions_schema import BusinessFunctionsConfig

# Validate configuration
config_obj = BusinessFunctionsConfig(**config_dict)
```

### Required Fields

Per function:
- `enabled` (bool)
- `description` (string)
- `module_path` (string, valid Python module path)
- `class_name` (string, valid Python identifier)

### Optional Import Check

Set `ENABLE_IMPORT_CHECK=1` to validate that all referenced modules/classes can be imported:

```bash
ENABLE_IMPORT_CHECK=1 python -m omf2.config.business_functions_loader
```

## Best Practices

1. **Keep It Declarative**: Only metadata and references - no executable code
2. **Use Descriptive Names**: Function names should clearly indicate their purpose
3. **Document Changes**: Update `last_updated` and use version control
4. **Test After Changes**: Validate configuration after modifications
5. **Use Wildcards Wisely**: MQTT wildcards (`+`, `#`) can simplify routing
6. **Set Appropriate Priorities**: Higher priority for critical functions
7. **Enable Selectively**: Disable unused functions to reduce overhead

## Troubleshooting

### Configuration Not Loading

Check:
1. File exists at `omf2/registry/business_functions.yml`
2. YAML syntax is valid
3. File encoding is UTF-8
4. File permissions allow reading

### Validation Errors

Common issues:
- Missing required fields (`enabled`, `description`, `module_path`, `class_name`)
- Invalid module path (not a valid Python module path)
- Invalid class name (not a valid Python identifier)
- Empty `business_functions` dictionary

### Import Errors

If using `ENABLE_IMPORT_CHECK=1`:
- Ensure all referenced modules exist
- Check that classes are properly defined
- Verify module paths are correct

## Security Considerations

1. **No Code Execution**: Configuration file should never execute code
2. **Safe YAML Loading**: Always use `yaml.safe_load()` / `yaml.safe_dump()`
3. **Validation**: Validate configuration before using it
4. **Access Control**: Restrict write access to configuration file
5. **Audit Trail**: Use version control to track changes

## See Also

- [MQTT Clients Configuration](../omf2/registry/mqtt_clients.yml) - Related MQTT configuration
- [Gateway Architecture](../02-architecture/omf2-architecture.md) - System architecture overview
- [Registry System](../02-architecture/omf2-registry-system.md) - Registry system documentation
