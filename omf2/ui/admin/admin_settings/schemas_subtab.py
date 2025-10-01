#!/usr/bin/env python3
"""
Schemas Subtab - Schema Verwaltung für Admin Settings
Zeigt alle Schemas aus der Registry mit Validierung und Test-Funktionen
"""

import streamlit as st
import json
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_schemas_subtab():
    """Render Schemas Subtab mit Registry-Daten"""
    try:
        st.subheader("📝 Schemas Konfiguration")
        st.markdown("Registry-basierte Schema-Verwaltung mit JSON Schema Validierung")

        # Load registry manager from session state (initialized in omf.py)
        if 'registry_manager' not in st.session_state:
            from omf2.registry.manager.registry_manager import get_registry_manager
            st.session_state['registry_manager'] = get_registry_manager("omf2/registry/")
        registry_manager = st.session_state['registry_manager']
        
        # Debug: Log registry manager info
        logger.debug(f"🔍 Registry Manager Debug:")
        logger.debug(f"  - Registry Path: {registry_manager.registry_path}")
        logger.debug(f"  - Schemas Path: {registry_manager.registry_path / 'schemas'}")
        logger.debug(f"  - Schemas Path exists: {(registry_manager.registry_path / 'schemas').exists()}")
        logger.debug(f"  - Schemas count: {len(registry_manager.get_schemas())}")
        
        # Show debug info in UI
        with st.expander("🔍 Debug Info", expanded=True):
            st.write(f"**Registry Path:** `{registry_manager.registry_path}`")
            st.write(f"**Schemas Path:** `{registry_manager.registry_path / 'schemas'}`")
            st.write(f"**Schemas Path exists:** `{(registry_manager.registry_path / 'schemas').exists()}`")
            st.write(f"**Schemas count:** `{len(registry_manager.get_schemas())}`")
            
            # List schema files
            schemas_path = registry_manager.registry_path / 'schemas'
            if schemas_path.exists():
                schema_files = list(schemas_path.glob("*.schema.json"))
                st.write(f"**Schema files found:** `{len(schema_files)}`")
                for i, schema_file in enumerate(schema_files[:5]):  # Show first 5
                    st.write(f"  - {schema_file.name}")
                if len(schema_files) > 5:
                    st.write(f"  - ... and {len(schema_files) - 5} more")
            else:
                st.write("**Schemas directory does not exist!**")
        
        # Get all schemas
        all_schemas = registry_manager.get_schemas()
        
        if not all_schemas:
            st.warning("⚠️ Keine Schemas in der Registry gefunden")
            return
        
        # Schema Overview
        with st.expander("📊 Schema Overview", expanded=True):
            schema_stats = _get_schema_statistics(registry_manager)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Schemas", schema_stats['total_schemas'])
            with col2:
                st.metric("Topics with Schema", schema_stats['topics_with_schema'])
            with col3:
                st.metric("Unique Schema Files", schema_stats['unique_schemas'])
        
        # Schema Files List
        with st.expander("📂 Schema Files", expanded=False):
            schema_files = _get_schema_files(registry_manager)
            
            for schema_file, topics in schema_files.items():
                with st.expander(f"📄 {schema_file} ({len(topics)} topics)", expanded=False):
                    # Show topics using this schema
                    topic_data = []
                    for topic in topics:
                        topic_info = registry_manager.topics.get(topic, {})
                        topic_data.append({
                            "Topic": topic,
                            "QoS": topic_info.get('qos', 'N/A'),
                            "Retain": topic_info.get('retain', 'N/A'),
                            "Description": topic_info.get('description', 'No description')
                        })
                    
                    if topic_data:
                        st.dataframe(
                            topic_data,
                            column_config={
                                "Topic": st.column_config.TextColumn("Topic", width="large"),
                                "QoS": st.column_config.NumberColumn("QoS", width="small"),
                                "Retain": st.column_config.NumberColumn("Retain", width="small"),
                                "Description": st.column_config.TextColumn("Description", width="large"),
                            },
                            hide_index=True,
                        )
        
        # Schema Validation Test
        with st.expander("🧪 Schema Validation Test", expanded=False):
            _render_schema_validation_test(registry_manager)
        
        # Schema Content Viewer
        with st.expander("🔍 Schema Content Viewer", expanded=False):
            _render_schema_content_viewer(registry_manager)
        
        # Test Payload Generator
        with st.expander("🧪 Test Payload Generator", expanded=False):
            _render_test_payload_generator()
        
    except Exception as e:
        logger.error(f"❌ Schemas Subtab rendering error: {e}")
        st.error(f"❌ Schemas Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _get_schema_statistics(registry_manager):
    """Gibt Schema-Statistiken zurück"""
    # Get actual schema files from registry
    all_schemas = registry_manager.get_schemas()
    all_topics = registry_manager.get_topics()
    
    # Count topics with schema field
    topics_with_schema = 0
    for topic, info in all_topics.items():
        if info.get('schema'):
            topics_with_schema += 1
    
    return {
        'total_schemas': len(all_schemas),  # Use actual schema count
        'topics_with_schema': topics_with_schema,
        'unique_schemas': len(all_schemas)  # Use actual schema count
    }


def _get_schema_files(registry_manager):
    """Gibt Schema-Dateien mit zugehörigen Topics zurück"""
    schema_files = {}
    all_topics = registry_manager.get_topics()
    
    for topic, info in all_topics.items():
        schema_file = info.get('schema')
        if schema_file:
            if schema_file not in schema_files:
                schema_files[schema_file] = []
            schema_files[schema_file].append(topic)
    
    return schema_files


def _render_schema_validation_test(registry_manager):
    """Rendert Schema-Validierungstest"""
    st.write("**Test Payload Validation:**")
    
    # Topic Selection
    all_topics = registry_manager.get_topics()
    topics_with_schema = [topic for topic, info in all_topics.items() if info.get('schema')]
    
    if not topics_with_schema:
        st.warning("Keine Topics mit Schema gefunden")
        return
    
    selected_topic = st.selectbox("Select Topic:", topics_with_schema, key="admin_settings_schemas_validation_topic")
    
    if selected_topic:
        topic_info = all_topics[selected_topic]
        st.write(f"**Schema:** {topic_info.get('schema')}")
        st.write(f"**Description:** {topic_info.get('description', 'No description')}")
        
        # Test Payload Input
        st.write("**Test Payload (JSON):**")
        default_payload = {
            "example": "payload",
            "timestamp": "2025-01-01T12:00:00Z"
        }
        
        payload_text = st.text_area(
            "JSON Payload:",
            value=json.dumps(default_payload, indent=2),
            height=200,
            key="admin_settings_schemas_validation_payload"
        )
        
        if st.button("🔍 Validate Payload", key="admin_settings_schemas_validation_validate"):
            try:
                payload = json.loads(payload_text)
                validation_result = registry_manager.validate_topic_payload(selected_topic, payload)
                
                if validation_result['valid']:
                    st.success("✅ Payload is valid!")
                else:
                    st.error(f"❌ Payload validation failed: {validation_result['error']}")
                    
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")
            except Exception as e:
                st.error(f"❌ Validation error: {e}")


def _render_schema_content_viewer(registry_manager):
    """Rendert Schema-Content-Viewer"""
    st.write("**Schema Content Viewer:**")
    
    # Schema File Selection
    schema_files = _get_schema_files(registry_manager)
    selected_schema = st.selectbox("Select Schema File:", list(schema_files.keys()), key="admin_settings_schemas_content_viewer")
    
    if selected_schema:
        try:
            # Load schema content
            schema_path = registry_manager.registry_path / "schemas" / selected_schema
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_content = json.load(f)
                
                st.write(f"**Schema File:** {selected_schema}")
                st.write(f"**Topics using this schema:** {len(schema_files[selected_schema])}")
                
                # Display schema content
                st.json(schema_content)
            else:
                st.error(f"Schema file not found: {schema_path}")
                
        except Exception as e:
            st.error(f"Error loading schema: {e}")


def _render_test_payload_generator():
    """Rendert Test-Payload-Generator"""
    st.write("**Generate Test Payloads from Recorded Data:**")
    
    try:
        from omf2.registry.tools.test_payload_generator import TestPayloadGenerator
        
        generator = TestPayloadGenerator()
        available_topics = generator.get_available_topics()
        
        if not available_topics:
            st.warning("No recorded topics found in aps-data")
            return
        
        st.write(f"**Available Topics:** {len(available_topics)}")
        
        # Topic Selection
        selected_topic = st.selectbox("Select Topic:", available_topics, key="admin_settings_schemas_test_payload_topic")
        
        if selected_topic:
            examples = generator.get_topic_examples(selected_topic)
            st.write(f"**Examples available:** {len(examples)}")
            
            # Variation Selection
            variation = st.selectbox(
                "Payload Variation:",
                ["random", "latest", "template"],
                key="admin_settings_schemas_test_payload_variation",
                help="random: random example, latest: newest example, template: generated template"
            )
            
            if st.button("🎲 Generate Test Payload", key="admin_settings_schemas_test_payload_generate"):
                payload = generator.generate_test_payload(selected_topic, variation)
                
                if payload:
                    st.success("✅ Test payload generated!")
                    st.json(payload)
                    
                    # Copy to clipboard button
                    if st.button("📋 Copy to Clipboard", key="admin_settings_schemas_test_payload_copy"):
                        st.code(json.dumps(payload, indent=2))
                else:
                    st.error("❌ Failed to generate test payload")
        
        # Generate Test Suite
        st.write("**Generate Complete Test Suite:**")
        if st.button("📦 Generate Test Suite", key="admin_settings_schemas_test_suite_generate"):
            with st.spinner("Generating test suite..."):
                output_file = generator.export_test_suite()
                st.success(f"✅ Test suite exported to: {output_file}")
                
                # Show preview
                try:
                    with open(output_file, 'r', encoding='utf-8') as f:
                        test_suite = json.load(f)
                    
                    st.write("**Test Suite Preview:**")
                    st.write(f"Topics: {len(test_suite)}")
                    
                    # Show first topic as example
                    if test_suite:
                        first_topic = list(test_suite.keys())[0]
                        st.write(f"**Example - {first_topic}:**")
                        st.json(test_suite[first_topic])
                        
                except Exception as e:
                    st.error(f"Error loading test suite: {e}")
                    
    except Exception as e:
        st.error(f"Error initializing test payload generator: {e}")
        st.info("Make sure aps-data/topics contains recorded JSON files")


def show_schemas_subtab():
    """Wrapper für Schemas Subtab"""
    render_schemas_subtab()
