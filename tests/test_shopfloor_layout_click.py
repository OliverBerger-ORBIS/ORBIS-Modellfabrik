import importlib
import types

def _make_dummy_columns(n):
    class DummyCol:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def markdown(self, *args, **kwargs): pass
        def components(self, *args, **kwargs): pass
    return [DummyCol() for _ in range(n)]

def _mock_streamlit():
    """Mock Streamlit für Tests"""
    st_mock = types.ModuleType('streamlit')
    st_mock.subheader = lambda x: None
    st_mock.markdown = lambda x, **kwargs: None
    st_mock.components = types.ModuleType('components')
    st_mock.components.v1 = types.ModuleType('v1')
    st_mock.components.v1.html = lambda x, height: None
    st_mock.session_state = {}
    st_mock.columns = _make_dummy_columns
    return st_mock

def test_click_interaction_modes():
    """Test dass verschiedene Modi korrekt funktionieren"""
    # Mock Streamlit
    import sys
    sys.modules['streamlit'] = _mock_streamlit()
    
    # Mock Dependencies
    sys.modules['omf2.assets'] = types.ModuleType('assets')
    sys.modules['omf2.config'] = types.ModuleType('config')
    sys.modules['omf2.common.logger'] = types.ModuleType('logger')
    
    class MockAssetManager:
        def get_module_icon_path(self, name): return None
    
    sys.modules['omf2.assets'].get_asset_manager = lambda: MockAssetManager()
    
    class MockConfigLoader:
        def load_shopfloor_layout(self):
            return {
                "modules": [
                    {"id": "MILL", "name": "MILL", "position": [0, 1]},
                    {"id": "DRILL", "name": "DRILL", "position": [1, 1]}
                ],
                "empty_positions": [],
                "intersections": []
            }
    
    sys.modules['omf2.config'].get_ccu_config_loader = lambda: MockConfigLoader()
    
    class MockLogger:
        def error(self, msg): pass
        def warning(self, msg): pass
    
    sys.modules['omf2.common.logger'].get_logger = lambda name: MockLogger()
    
    # Test verschiedene Modi
    try:
        from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout
        
        # Test view_mode
        show_shopfloor_layout(mode="view_mode")
        
        # Test ccu_configuration
        show_shopfloor_layout(mode="ccu_configuration")
        
        # Test interactive
        show_shopfloor_layout(mode="interactive")
        
        print("✅ All interaction modes work")
        return True
    except Exception as e:
        print(f"❌ Interaction modes test failed: {e}")
        return False

def test_active_module_highlighting():
    """Test dass aktive Module korrekt hervorgehoben werden"""
    # Mock Streamlit
    import sys
    sys.modules['streamlit'] = _mock_streamlit()
    
    # Mock Dependencies
    sys.modules['omf2.assets'] = types.ModuleType('assets')
    sys.modules['omf2.config'] = types.ModuleType('config')
    sys.modules['omf2.common.logger'] = types.ModuleType('logger')
    
    class MockAssetManager:
        def get_module_icon_path(self, name): return None
    
    sys.modules['omf2.assets'].get_asset_manager = lambda: MockAssetManager()
    
    class MockConfigLoader:
        def load_shopfloor_layout(self):
            return {
                "modules": [
                    {"id": "MILL", "name": "MILL", "position": [0, 1]},
                    {"id": "DRILL", "name": "DRILL", "position": [1, 1]}
                ],
                "empty_positions": [],
                "intersections": []
            }
    
    sys.modules['omf2.config'].get_ccu_config_loader = lambda: MockConfigLoader()
    
    class MockLogger:
        def error(self, msg): pass
        def warning(self, msg): pass
    
    sys.modules['omf2.common.logger'].get_logger = lambda name: MockLogger()
    
    # Test active module highlighting
    try:
        from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout
        
        # Test mit aktivem Modul
        show_shopfloor_layout(
            active_module_id="MILL",
            mode="view_mode"
        )
        
        # Test mit aktiven Intersections
        show_shopfloor_layout(
            active_intersections=[{"position": [0, 1]}],
            mode="view_mode"
        )
        
        print("✅ Active module highlighting works")
        return True
    except Exception as e:
        print(f"❌ Active module highlighting test failed: {e}")
        return False

def test_deprecated_functions():
    """Test dass deprecated functions noch funktionieren (mit Warnings)"""
    # Mock Streamlit
    import sys
    sys.modules['streamlit'] = _mock_streamlit()
    
    # Mock Dependencies
    sys.modules['omf2.assets'] = types.ModuleType('assets')
    sys.modules['omf2.config'] = types.ModuleType('config')
    sys.modules['omf2.common.logger'] = types.ModuleType('logger')
    
    class MockLogger:
        def error(self, msg): pass
        def warning(self, msg): pass
    
    sys.modules['omf2.common.logger'].get_logger = lambda name: MockLogger()
    
    # Test deprecated functions
    try:
        from omf2.ui.ccu.common.shopfloor_layout import (
            _generate_omf2_svg_grid_with_roads,
            _process_grid_events,
            _handle_grid_event
        )
        
        # Diese sollten nicht crashen, aber Warnings loggen
        result1 = _generate_omf2_svg_grid_with_roads()
        assert result1 == ""
        
        _process_grid_events()
        _handle_grid_event()
        
        print("✅ Deprecated functions work (with warnings)")
        return True
    except Exception as e:
        print(f"❌ Deprecated functions test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running shopfloor_layout click tests...")
    
    test1 = test_click_interaction_modes()
    test2 = test_active_module_highlighting()
    test3 = test_deprecated_functions()
    
    if test1 and test2 and test3:
        print("✅ All click tests passed!")
    else:
        print("❌ Some click tests failed!")
        exit(1)
