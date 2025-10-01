"""
Topic Selector Component
Handles topic selection and schema-driven UI
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from omf2.registry.manager.registry_manager import get_registry_manager


class TopicSelector:
    def __init__(self, registry_manager):
        self.registry_manager = registry_manager
    
    def render_topic_driven_ui(self):
        """Renders the topic-driven approach UI"""
        st.markdown("#### 📡 Topic-driven Commands")
        st.markdown("Select a topic and generate schema-compliant payload")
        
        # Get all topics
        all_topics = self.registry_manager.get_topics()
        if not all_topics:
            st.warning("⚠️ No topics found in registry")
            return
        
        # Topic selection
        selected_topic = st.selectbox(
            "Select Topic:",
            all_topics,
            key="topic_driven_topic_select"
        )
        
        if selected_topic:
            self._render_topic_details(selected_topic)
    
    def render_schema_driven_ui(self):
        """Renders the schema-driven approach UI"""
        st.markdown("#### 📋 Schema-driven Commands")
        st.markdown("Select a schema and find related topics")
        
        # Get all schemas
        all_schemas = self.registry_manager.get_schemas()
        if not all_schemas:
            st.warning("⚠️ No schemas found in registry")
            return
        
        # Schema selection
        schema_options = list(all_schemas.keys())
        selected_schema = st.selectbox(
            "Select Schema:",
            schema_options,
            key="schema_driven_schema_select"
        )
        
        if selected_schema:
            self._render_schema_details(selected_schema)
    
    def _render_topic_details(self, topic: str):
        """Renders details for a selected topic"""
        # Get topic schema and description
        topic_schema = self.registry_manager.get_topic_schema(topic)
        topic_description = self.registry_manager.get_topic_description(topic)
        
        if topic_schema:
            st.success(f"✅ Schema found: {topic_schema.get('title', 'Unknown Schema') if isinstance(topic_schema, dict) else topic_schema}")
        else:
            st.warning("⚠️ No schema found for this topic")
        
        if topic_description:
            st.info(f"📝 Description: {topic_description}")
        
        # Generate and display payload
        from .payload_generator import PayloadGenerator
        generator = PayloadGenerator(self.registry_manager)
        payload = generator.generate_example_payload(topic)
        
        if payload:
            st.markdown("**Generated Payload:**")
            st.json(payload)
            
            # Payload editing
            st.markdown("**Edit Payload:**")
            edited_payload = st.text_area(
                "Payload JSON:",
                value=json.dumps(payload, indent=2),
                height=200,
                key=f"payload_edit_{topic}"
            )
            
            # Message sending
            self._render_message_sending_ui(topic, edited_payload)
        else:
            st.error("❌ Failed to generate payload")
    
    def _render_schema_details(self, schema_name: str):
        """Renders details for a selected schema"""
        # Find topics using this schema
        topic_schema_mappings = self.registry_manager.get_topic_schema_mappings()
        related_topics = []
        
        for topic, schema_file in topic_schema_mappings.items():
            schema_file_str = schema_file
            if isinstance(schema_file, dict):
                schema_file_str = schema_file.get('title', '') or schema_file.get('$id', '') or str(schema_file)
            
            # Try different matching strategies
            if (schema_name in schema_file_str or 
                schema_name.replace('.schema', '') in schema_file_str or
                schema_name.replace('.schema.json', '') in schema_file_str or
                schema_file_str.replace('.schema.json', '') in schema_name):
                related_topics.append(topic)
        
        if related_topics:
            st.success(f"✅ Found {len(related_topics)} topics using schema: {schema_name}")
            
            st.markdown("**Related Topics:**")
            for topic in related_topics:
                with st.expander(f"📤 {topic}"):
                    self._render_topic_details(topic)
        else:
            st.warning(f"⚠️ No topics found using schema: {schema_name}")
    
    def _render_message_sending_ui(self, topic: str, payload_json: str):
        """Renders the message sending UI"""
        st.markdown("**Message Options:**")
        
        col1, col2 = st.columns(2)
        with col1:
            qos = st.selectbox("QoS:", [0, 1, 2], key=f"qos_{topic}")
        with col2:
            retain = st.checkbox("Retain", key=f"retain_{topic}")
        
        if st.button(f"📤 Send Message to {topic}", key=f"send_{topic}"):
            try:
                # Parse JSON payload
                import json
                payload = json.loads(payload_json)
                
                # Validate payload if schema exists
                topic_schema = self.registry_manager.get_topic_schema(topic)
                if topic_schema:
                    validation_result = self.registry_manager.validate_topic_payload(topic, payload)
                    if not validation_result.get('valid', False):
                        st.error(f"❌ Payload validation failed: {validation_result.get('error', 'Unknown error')}")
                        return
                
                # Send message via gateway
                from omf2.admin.admin_gateway import get_admin_gateway
                gateway = get_admin_gateway()
                
                if gateway and hasattr(gateway, 'publish_message'):
                    success = gateway.publish_message(topic, payload, qos, retain)
                    if success:
                        st.success(f"✅ Message sent successfully to {topic}")
                    else:
                        st.error(f"❌ Failed to send message to {topic}")
                else:
                    st.error("❌ Gateway not available")
                    
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")
            except Exception as e:
                st.error(f"❌ Send failed: {e}")
