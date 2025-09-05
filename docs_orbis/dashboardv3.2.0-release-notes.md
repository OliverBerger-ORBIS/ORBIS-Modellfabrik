# Dashboard v3.2.0 Release Notes

**Release Date:** 2025-09-05  
**Version:** dashboardv3.2.0  
**Status:** ✅ Released

## 🎯 Overview

Dashboard v3.2.0 introduces comprehensive FTS and CCU monitoring capabilities with robust template validation, enhanced message processing, and improved user experience.

## 🚛 New Features

### FTS (Fahrerloses Transportsystem) Tab
- **Complete FTS monitoring** with 5 sub-tabs:
  - `fts_order` - FTS navigation orders and commands
  - `fts_instantaction` - Instant actions (reset, clearLoadHandler, etc.)
  - `fts_state` - Current FTS state and position
  - `fts_connection` - Connection status and health
  - `fts_factsheet` - FTS configuration and specifications
- **Semantic analysis** for all FTS MQTT topics
- **Template validation** with error tracking
- **Real-time data display** with timestamps

### CCU (Central Control Unit) Tab
- **Complete CCU monitoring** with 5 sub-tabs:
  - `ccu_state` - CCU system state and inventory
  - `ccu_control` - Control commands and orders
  - `ccu_set` - Configuration and reset commands
  - `ccu_status` - System status and health
  - `ccu_pairing` - Module and transport pairing
- **Semantic analysis** for all CCU MQTT topics
- **Template validation** with error tracking
- **Real-time data display** with timestamps

## 🛡️ Template Validation System

### ValidationErrorTracker
- **Error history tracking** across multiple messages
- **Original payload display** for debugging
- **Persistent error storage** in session state
- **Error clearing functionality**

### Validation Types
- **Auto-analyzed template detection** - Identifies automatically generated templates
- **Missing field validation** - Checks for expected data structure
- **Template not found** - Handles unknown message formats
- **Field mismatch detection** - Validates against expected schemas

### Error Display
- **Real-time validation feedback** in UI
- **Error history with timestamps**
- **Original payload inspection**
- **Clear error categorization**

## 📋 Message Templates

### FTS Templates
- `fts/v1/ff/5iO4/state` - FTS state information
- `fts/v1/ff/5iO4/connection` - Connection status
- `fts/v1/ff/5iO4/factsheet` - Configuration data
- `fts/v1/ff/5iO4/instantAction` - Instant actions
- `fts/v1/ff/5iO4/order` - Navigation orders

### Template Categories
- **FTS category** added to categories.yml
- **Proper template organization** by system type
- **Validation rules** for each template type

## ⚙️ Settings Improvements

### Default Broker Connection
- **Replay/Live mode selection** in settings
- **Default to Replay mode** for testing
- **Scheduled switch** to Live mode documented
- **User-friendly configuration** interface

## 🔧 Technical Improvements

### Message Processing
- **MessageProcessor pattern** implemented across all components
- **Efficient message filtering** and processing
- **Reduced debug spam** in sidebar
- **Performance optimizations**

### Component Architecture
- **Fault-tolerant loading** for missing components
- **Dummy component fallback** system
- **Modular component structure**
- **Consistent error handling**

### Replay Station
- **Fixed speed steps** (1x, 2x, 3x, 5x, 10x, Maximal)
- **Better user experience** for speed control
- **Consistent speed selection** interface

## 🐛 Bug Fixes

### Import Issues
- **Relative import errors** resolved
- **Component loading** made fault-tolerant
- **Path resolution** improved

### Template Validation
- **Auto-analyzed template** false positives eliminated
- **Missing field detection** improved
- **Error message clarity** enhanced

### Performance
- **Message processing loops** eliminated
- **Debug output** optimized
- **Memory usage** reduced

## 📊 Testing

### Validation Testing
- **Unsinnige Nachrichten** correctly identified
- **Auto-analyzed templates** properly flagged
- **Missing fields** detected accurately
- **Error history** maintained correctly

### Component Testing
- **FTS components** fully functional
- **CCU components** fully functional
- **Template validation** working across all tabs
- **Error tracking** persistent and accurate

## 🚀 Migration Notes

### For Users
- **New FTS and CCU tabs** available immediately
- **Template validation** active by default
- **Error history** starts fresh on restart
- **Settings** may need reconfiguration

### For Developers
- **MessageProcessor pattern** should be used for new components
- **ValidationErrorTracker** available for error handling
- **Template validation** should be implemented in all message-processing components

## 📈 Performance Impact

### Positive
- **Reduced message processing** overhead
- **Optimized debug output**
- **Efficient error tracking**
- **Better memory management**

### Considerations
- **Error history storage** uses session state
- **Template validation** adds processing overhead
- **Component loading** has fallback mechanisms

## 🔮 Future Enhancements

### Planned
- **Overview tabs template validation** (pending)
- **Additional FTS navigation examples**
- **Enhanced CCU control capabilities**
- **Performance monitoring dashboard**

### Under Consideration
- **Template validation** for all dashboard components
- **Automated template generation**
- **Enhanced error reporting**
- **Real-time validation metrics**

## 📝 Technical Details

### Files Added
- `src_orbis/omf/dashboard/components/fts*.py` - FTS components
- `src_orbis/omf/dashboard/components/ccu*.py` - CCU components
- `src_orbis/omf/dashboard/components/validation_error_tracker.py` - Error tracking
- `src_orbis/omf/config/message_templates/templates/fts/*.yml` - FTS templates

### Files Modified
- `src_orbis/omf/dashboard/omf_dashboard.py` - Main dashboard
- `src_orbis/omf/dashboard/components/message_processor.py` - Message processing
- `src_orbis/omf/config/message_templates/categories.yml` - Template categories
- `src_orbis/omf/replay_station/*.py` - Replay station improvements

### Dependencies
- **No new dependencies** required
- **Existing MessageTemplate library** enhanced
- **Streamlit components** extended

## ✅ Quality Assurance

### Testing Completed
- ✅ **FTS component functionality**
- ✅ **CCU component functionality**
- ✅ **Template validation accuracy**
- ✅ **Error tracking persistence**
- ✅ **Performance optimization**
- ✅ **Import error resolution**

### Validation Results
- ✅ **All unsinnige Nachrichten** correctly identified
- ✅ **Auto-analyzed templates** properly flagged
- ✅ **Missing fields** detected accurately
- ✅ **Error history** maintained correctly
- ✅ **Original payload** displayed properly

## 🎉 Conclusion

Dashboard v3.2.0 represents a significant enhancement in monitoring capabilities with comprehensive FTS and CCU support, robust template validation, and improved user experience. The new validation system ensures data quality while the enhanced component architecture provides better reliability and maintainability.

---

**Next Release:** dashboardv3.3.0 (Overview tabs template validation)  
**Maintenance:** Ongoing support and bug fixes  
**Documentation:** Complete and up-to-date
