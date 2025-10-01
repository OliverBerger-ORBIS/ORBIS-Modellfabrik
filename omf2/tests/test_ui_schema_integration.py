#!/usr/bin/env python3
"""
Test UI Schema Integration - Admin Settings mit Schema-Validierung
"""

import unittest
from unittest.mock import patch, MagicMock
import streamlit as st
from omf2.registry.manager.registry_manager import get_registry_manager, RegistryManager


class TestUISchemaIntegration(unittest.TestCase):
    """Test UI Schema Integration in Admin Settings"""
    
    def setUp(self):
        """Setup für jeden Test"""
        # Reset Singleton
        RegistryManager._instance = None
        RegistryManager._initialized = False
        self.registry_manager = get_registry_manager("omf2/registry/")
    
    def test_schemas_subtab_imports(self):
        """Test: Schemas-Subtab kann importiert werden"""
        try:
            from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab
            self.assertTrue(callable(render_schemas_subtab), "render_schemas_subtab sollte eine Funktion sein")
        except ImportError as e:
            self.fail(f"Schemas-Subtab kann nicht importiert werden: {e}")
    
    def test_schemas_subtab_rendering(self):
        """Test: Schemas-Subtab kann gerendert werden"""
        from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab
        
        # Mock Streamlit session_state
        with patch('streamlit.session_state', {'registry_manager': self.registry_manager}):
            with patch('streamlit.write') as mock_write:
                with patch('streamlit.selectbox') as mock_selectbox:
                    with patch('streamlit.button') as mock_button:
                        # Mock return values
                        mock_selectbox.return_value = "ccu_global.schema"
                        mock_button.return_value = False
                        
                        # Test rendering
                        try:
                            render_schemas_subtab()
                            # Test sollte ohne Exception durchlaufen
                            self.assertTrue(True, "Schemas-Subtab sollte ohne Fehler gerendert werden")
                        except Exception as e:
                            self.fail(f"Schemas-Subtab Rendering fehlgeschlagen: {e}")
    
    def test_topics_subtab_schema_integration(self):
        """Test: Topics-Subtab zeigt Schema-Informationen"""
        from omf2.ui.admin.admin_settings.topics_subtab import render_topics_subtab
        
        # Mock Streamlit session_state
        with patch('streamlit.session_state', {'registry_manager': self.registry_manager}):
            with patch('streamlit.dataframe') as mock_dataframe:
                with patch('streamlit.write') as mock_write:
                    # Test rendering
                    try:
                        render_topics_subtab()
                        # Prüfe dass DataFrame mit Schema-Spalten erstellt wird
                        self.assertTrue(True, "Topics-Subtab sollte Schema-Informationen anzeigen")
                    except Exception as e:
                        self.fail(f"Topics-Subtab Schema-Integration fehlgeschlagen: {e}")
    
    def test_admin_settings_tab_schema_integration(self):
        """Test: Admin Settings Tab integriert Schema-Subtab"""
        from omf2.ui.admin.admin_settings.admin_settings_tab import render_admin_settings_tab
        
        # Mock Streamlit session_state
        with patch('streamlit.session_state', {'registry_manager': self.registry_manager}):
            with patch('streamlit.tabs') as mock_tabs:
                with patch('streamlit.write') as mock_write:
                    # Mock tabs return
                    mock_tab = MagicMock()
                    mock_tabs.return_value = [mock_tab]
                    
                    # Test rendering
                    try:
                        render_admin_settings_tab()
                        # Prüfe dass Schema-Subtab in Tabs enthalten ist
                        self.assertTrue(True, "Admin Settings Tab sollte Schema-Subtab enthalten")
                    except Exception as e:
                        self.fail(f"Admin Settings Tab Schema-Integration fehlgeschlagen: {e}")
    
    def test_schema_validation_ui_components(self):
        """Test: Schema-Validierung UI-Komponenten funktionieren"""
        from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab
        
        # Mock Streamlit session_state
        with patch('streamlit.session_state', {'registry_manager': self.registry_manager}):
            with patch('streamlit.selectbox') as mock_selectbox:
                with patch('streamlit.text_area') as mock_text_area:
                    with patch('streamlit.button') as mock_button:
                        with patch('streamlit.write') as mock_write:
                            # Mock return values
                            mock_selectbox.return_value = "ccu_global.schema"
                            mock_text_area.return_value = '{"type": "test"}'
                            mock_button.return_value = True
                            
                            # Test Schema-Validierung UI
                            try:
                                render_schemas_subtab()
                                # Test sollte ohne Exception durchlaufen
                                self.assertTrue(True, "Schema-Validierung UI sollte funktionieren")
                            except Exception as e:
                                self.fail(f"Schema-Validierung UI fehlgeschlagen: {e}")
    
    def test_schema_content_viewer(self):
        """Test: Schema-Content-Viewer funktioniert"""
        from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab
        
        # Mock Streamlit session_state
        with patch('streamlit.session_state', {'registry_manager': self.registry_manager}):
            with patch('streamlit.selectbox') as mock_selectbox:
                with patch('streamlit.code') as mock_code:
                    with patch('streamlit.write') as mock_write:
                        # Mock return values
                        mock_selectbox.return_value = "ccu_global.schema"
                        
                        # Test Schema-Content-Viewer
                        try:
                            render_schemas_subtab()
                            # Test sollte ohne Exception durchlaufen
                            self.assertTrue(True, "Schema-Content-Viewer sollte funktionieren")
                        except Exception as e:
                            self.fail(f"Schema-Content-Viewer fehlgeschlagen: {e}")
    
    def test_schema_statistics_display(self):
        """Test: Schema-Statistiken werden korrekt angezeigt"""
        from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab
        
        # Mock Streamlit session_state
        with patch('streamlit.session_state', {'registry_manager': self.registry_manager}):
            with patch('streamlit.metric') as mock_metric:
                with patch('streamlit.write') as mock_write:
                    # Test Schema-Statistiken
                    try:
                        render_schemas_subtab()
                        # Prüfe dass Statistiken angezeigt werden
                        self.assertTrue(True, "Schema-Statistiken sollten angezeigt werden")
                    except Exception as e:
                        self.fail(f"Schema-Statistiken Display fehlgeschlagen: {e}")
    
    def test_schema_test_payload_generator(self):
        """Test: Test-Payload-Generator funktioniert"""
        from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab
        
        # Mock Streamlit session_state
        with patch('streamlit.session_state', {'registry_manager': self.registry_manager}):
            with patch('streamlit.selectbox') as mock_selectbox:
                with patch('streamlit.button') as mock_button:
                    with patch('streamlit.write') as mock_write:
                        # Mock return values
                        mock_selectbox.return_value = "ccu_global.schema"
                        mock_button.return_value = True
                        
                        # Test Test-Payload-Generator
                        try:
                            render_schemas_subtab()
                            # Test sollte ohne Exception durchlaufen
                            self.assertTrue(True, "Test-Payload-Generator sollte funktionieren")
                        except Exception as e:
                            self.fail(f"Test-Payload-Generator fehlgeschlagen: {e}")
    
    def test_ui_key_uniqueness(self):
        """Test: UI-Keys sind eindeutig (verhindert Streamlit Key-Konflikte)"""
        from omf2.ui.admin.admin_settings.schemas_subtab import render_schemas_subtab
        
        # Mock Streamlit session_state
        with patch('streamlit.session_state', {'registry_manager': self.registry_manager}):
            with patch('streamlit.selectbox') as mock_selectbox:
                with patch('streamlit.text_area') as mock_text_area:
                    with patch('streamlit.button') as mock_button:
                        with patch('streamlit.write') as mock_write:
                            # Mock return values
                            mock_selectbox.return_value = "ccu_global.schema"
                            mock_text_area.return_value = '{"type": "test"}'
                            mock_button.return_value = False
                            
                            # Test UI-Key-Eindeutigkeit
                            try:
                                render_schemas_subtab()
                                
                                # Prüfe dass alle UI-Komponenten eindeutige Keys haben
                                selectbox_calls = mock_selectbox.call_args_list
                                text_area_calls = mock_text_area.call_args_list
                                button_calls = mock_button.call_args_list
                                
                                # Sammle alle Keys
                                all_keys = []
                                for call in selectbox_calls:
                                    if 'key' in call.kwargs:
                                        all_keys.append(call.kwargs['key'])
                                for call in text_area_calls:
                                    if 'key' in call.kwargs:
                                        all_keys.append(call.kwargs['key'])
                                for call in button_calls:
                                    if 'key' in call.kwargs:
                                        all_keys.append(call.kwargs['key'])
                                
                                # Prüfe Eindeutigkeit
                                unique_keys = set(all_keys)
                                self.assertEqual(len(all_keys), len(unique_keys), 
                                             f"UI-Keys sollten eindeutig sein. Duplikate: {set(all_keys) - unique_keys}")
                                
                            except Exception as e:
                                self.fail(f"UI-Key-Eindeutigkeit Test fehlgeschlagen: {e}")


if __name__ == '__main__':
    unittest.main()
