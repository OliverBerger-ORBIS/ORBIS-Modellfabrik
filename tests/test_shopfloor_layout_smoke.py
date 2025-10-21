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

def test_shopfloor_layout_imports():
    """Test dass shopfloor_layout ohne Fehler importiert werden kann"""
    # Mock Streamlit
    import sys
    sys.modules['streamlit'] = _mock_streamlit()
    
    # Mock andere Dependencies
    sys.modules['omf2.assets'] = types.ModuleType('assets')
    sys.modules['omf2.config'] = types.ModuleType('config')
    sys.modules['omf2.common.logger'] = types.ModuleType('logger')
    
    # Mock Asset Manager
    class MockAssetManager:
        def get_module_icon_path(self, name): return None
    
    sys.modules['omf2.assets'].get_asset_manager = lambda: MockAssetManager()
    
    # Mock Config Loader
    class MockConfigLoader:
        def load_shopfloor_layout(self):
            return {
                "modules": [],
                "empty_positions": [],
                "intersections": []
            }
    
    sys.modules['omf2.config'].get_ccu_config_loader = lambda: MockConfigLoader()
    
    # Mock Logger
    class MockLogger:
        def error(self, msg): pass
        def warning(self, msg): pass
    
    sys.modules['omf2.common.logger'].get_logger = lambda name: MockLogger()
    
    # Import testen
    try:
        from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout
        assert callable(show_shopfloor_layout)
        print("✅ shopfloor_layout import successful")
        return True
    except Exception as e:
        print(f"❌ shopfloor_layout import failed: {e}")
        return False

def test_shopfloor_layout_basic_call():
    """Test dass show_shopfloor_layout ohne Fehler aufgerufen werden kann"""
    # Mock Streamlit
    import sys
    sys.modules['streamlit'] = _mock_streamlit()
    
    # Mock Dependencies (wie oben)
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
                "empty_positions": [[0, 0], [2, 2]],
                "intersections": []
            }
    
    sys.modules['omf2.config'].get_ccu_config_loader = lambda: MockConfigLoader()
    
    class MockLogger:
        def error(self, msg): pass
        def warning(self, msg): pass
    
    sys.modules['omf2.common.logger'].get_logger = lambda name: MockLogger()
    
    # Test call
    try:
        from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout
        show_shopfloor_layout(
            active_module_id="MILL",
            title="Test Layout",
            mode="view_mode"
        )
        print("✅ shopfloor_layout call successful")
        return True
    except Exception as e:
        print(f"❌ shopfloor_layout call failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running shopfloor_layout smoke tests...")
    
    test1 = test_shopfloor_layout_imports()
    test2 = test_shopfloor_layout_basic_call()
    
    if test1 and test2:
        print("✅ All smoke tests passed!")
    else:
        print("❌ Some smoke tests failed!")
        exit(1)
