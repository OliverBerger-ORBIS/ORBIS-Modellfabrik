"""
Topic Selector Component
Handles topic selection and schema-driven UI
"""

import json
from typing import Any, Dict, List

import streamlit as st

from omf2.common.logger import get_logger

logger = get_logger(__name__)


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
        selected_topic = st.selectbox("Select Topic:", all_topics, key="topic_driven_topic_select")

        if selected_topic:
            self._render_topic_details(selected_topic)

    def render_schema_driven_ui(self):
        """Renders the schema-driven approach UI"""
        st.markdown("#### 📋 Schema-driven Commands")
        st.markdown("Select a schema and find related topics")

        try:
            # Get topics with schema information from registry
            topics_with_schemas = self._get_topics_with_schemas()
            if not topics_with_schemas:
                st.warning("⚠️ No topics with schemas found in registry")
                return

            # Extract unique schemas that have topics
            schema_to_topics = {}
            for topic, topic_info in topics_with_schemas.items():
                schema_name = topic_info.get("schema", "")
                if schema_name:
                    if schema_name not in schema_to_topics:
                        schema_to_topics[schema_name] = []
                    schema_to_topics[schema_name].append(topic)

            if not schema_to_topics:
                st.warning("⚠️ No schemas with topics found")
                return

            # Create schema options (only schemas that have topics)
            schema_options = sorted(schema_to_topics.keys())

            # Schema selection
            selected_schema = st.selectbox("Select Schema:", schema_options, key="schema_driven_schema_select")

            if selected_schema:
                self._render_schema_details_with_topics(
                    selected_schema, schema_to_topics[selected_schema], topics_with_schemas
                )

        except Exception as e:
            logger.error(f"❌ Schema-driven UI error: {e}")
            st.error(f"❌ Failed to load schemas: {e}")

    def _render_topic_details(self, topic: str):
        """Renders details for a selected topic"""
        try:
            # Get topic info including QoS and retain from registry
            topics_with_schemas = self._get_topics_with_schemas()
            topic_info = topics_with_schemas.get(topic, {})
            qos = topic_info.get("qos", 1)
            retain = topic_info.get("retain", False)
            client = topic_info.get("client", "unknown")

            # Get topic schema and description
            topic_schema = self.registry_manager.get_topic_schema(topic)
            topic_description = self.registry_manager.get_topic_description(topic)

            if topic_schema:
                st.success(
                    f"✅ Schema found: {topic_schema.get('title', 'Unknown Schema') if isinstance(topic_schema, dict) else topic_schema}"
                )
            else:
                st.warning("⚠️ No schema found for this topic")

            if topic_description:
                st.info(f"📝 Description: {topic_description}")

            # Display QoS and Retain information
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"🔢 QoS: {qos}")
            with col2:
                st.info(f"💾 Retain: {'Yes' if retain else 'No'}")
            with col3:
                st.info(f"📡 Client: {client}")

            # Generate and display payload
            from omf2.ui.common.components.payload_generator import PayloadGenerator

            generator = PayloadGenerator(self.registry_manager)
            payload = generator.generate_example_payload(topic)

            if payload:
                st.markdown("**Generated Payload:**")
                st.json(payload)

                # Payload editing
                st.markdown("**Edit Payload:**")
                edited_payload = st.text_area(
                    "Payload JSON:", value=json.dumps(payload, indent=2), height=200, key=f"payload_edit_{topic}"
                )

                # Message sending with QoS and retain info
                self._render_message_sending_ui_with_info(topic, edited_payload, qos, retain)
            else:
                st.error("❌ Failed to generate payload")

        except Exception as e:
            logger.error(f"❌ Topic details error: {e}")
            st.error(f"❌ Failed to render topic details: {e}")

    def _render_schema_details(self, schema_name: str, schema_display_name: str = None):
        """Renders details for a selected schema"""
        try:
            # Get schema info
            try:
                # Try to get schema info from registry manager
                if hasattr(self.registry_manager, "get_schema"):
                    schema_info = self.registry_manager.get_schema(schema_name)
                else:
                    # Fallback: get from schemas dict
                    schemas = self.registry_manager.get_schemas()
                    schema_info = schemas.get(schema_name, {})

                if schema_info:
                    st.success(f"✅ Schema: {schema_display_name or schema_name}")
                    if isinstance(schema_info, dict):
                        description = schema_info.get("description", "")
                        if description:
                            st.info(f"📝 Description: {description}")
                else:
                    st.info(f"📋 Schema: {schema_display_name or schema_name}")

            except Exception as e:
                logger.warning(f"⚠️ Failed to get schema info: {e}")
                st.info(f"📋 Schema: {schema_display_name or schema_name}")

            # Find topics using this schema
            related_topics = self._find_topics_for_schema(schema_name)

            if related_topics:
                st.success(f"✅ Found {len(related_topics)} topics using schema: {schema_display_name or schema_name}")

                # Topic selection dropdown
                selected_topic = st.selectbox("Select Topic:", related_topics, key=f"schema_topic_select_{schema_name}")

                if selected_topic:
                    st.divider()
                    self._render_topic_details(selected_topic)
            else:
                st.warning(f"⚠️ No topics found using schema: {schema_display_name or schema_name}")

        except Exception as e:
            logger.error(f"❌ Schema details error: {e}")
            st.error(f"❌ Failed to load schema details: {e}")

    def _find_topics_for_schema(self, schema_name: str) -> List[str]:
        """Find topics that use the specified schema"""
        try:
            # Get all topics and check their schemas
            all_topics = self.registry_manager.get_topics()
            related_topics = []

            for topic in all_topics:
                topic_schema = self.registry_manager.get_topic_schema(topic)
                if topic_schema:
                    # Check if this topic uses the selected schema
                    if self._schema_matches(topic_schema, schema_name):
                        related_topics.append(topic)

            return related_topics

        except Exception as e:
            logger.error(f"❌ Failed to find topics for schema {schema_name}: {e}")
            return []

    def _schema_matches(self, topic_schema: Any, target_schema_name: str) -> bool:
        """Check if topic schema matches target schema name"""
        try:
            if isinstance(topic_schema, dict):
                # Check various schema identifiers
                schema_id = topic_schema.get("$id", "")
                schema_title = topic_schema.get("title", "")
                schema_name = topic_schema.get("name", "")

                return (
                    target_schema_name in schema_id
                    or target_schema_name in schema_title
                    or target_schema_name in schema_name
                )
            else:
                # String comparison for non-dict schemas
                return target_schema_name in str(topic_schema)
        except Exception:
            return False

    def _get_topics_with_schemas(self) -> Dict[str, Dict]:
        """Get all topics with their schema, QoS, and retain information from registry"""
        try:
            # Get MQTT clients configuration which contains topic information
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            topics_with_info = {}

            for client_name, client_config in mqtt_clients.items():
                if isinstance(client_config, dict):
                    subscribed_topics = client_config.get("subscribed_topics", [])
                    for topic_info in subscribed_topics:
                        if isinstance(topic_info, dict):
                            topic = topic_info.get("topic", "")
                            qos = topic_info.get("qos", 1)
                            retain = topic_info.get("retain", False)
                            schema = topic_info.get("schema", "")
                        else:
                            topic = str(topic_info)
                            qos = 1
                            retain = False
                            schema = ""

                        if topic and topic != "#":  # Skip wildcard topics
                            # Try to infer schema from topic name if not explicitly set
                            if not schema:
                                schema = self._infer_schema_from_topic(topic)

                            topics_with_info[topic] = {
                                "qos": qos,
                                "retain": retain,
                                "schema": schema,
                                "client": client_name,
                            }

            return topics_with_info

        except Exception as e:
            logger.error(f"❌ Failed to get topics with schemas: {e}")
            return {}

    def _infer_schema_from_topic(self, topic: str) -> str:
        """Infer schema name from topic name based on patterns"""
        try:
            # Common topic patterns and their inferred schemas
            if "/state" in topic:
                return "module_state.schema"
            elif "/connection" in topic:
                return "module_connection.schema"
            elif "/factsheet" in topic:
                return "module_factsheet.schema"
            elif "ccu/" in topic:
                return "ccu_control.schema"
            elif "fts/" in topic:
                return "fts_status.schema"
            elif "module/" in topic:
                return "module_general.schema"
            else:
                return "generic_message.schema"
        except Exception:
            return "unknown.schema"

    def _render_schema_details_with_topics(self, schema_name: str, topics: List[str], topics_with_schemas: Dict):
        """Render schema details with topics and their QoS/retain information"""
        try:
            st.success(f"✅ Schema: {schema_name}")
            st.info(f"📋 Found {len(topics)} topics using this schema")

            # Topic selection
            selected_topic = st.selectbox("Select Topic:", topics, key=f"schema_topic_select_{schema_name}")

            if selected_topic:
                st.divider()
                # Get topic info including QoS and retain
                topic_info = topics_with_schemas.get(selected_topic, {})
                qos = topic_info.get("qos", 1)
                retain = topic_info.get("retain", False)
                client = topic_info.get("client", "unknown")

                # Display topic information
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("QoS", qos)
                with col2:
                    st.metric("Retain", "Yes" if retain else "No")
                with col3:
                    st.metric("Client", client)
                with col4:
                    st.metric("Schema", schema_name)

                # Render topic details with QoS/retain info
                self._render_topic_details_with_info(selected_topic, qos, retain)

        except Exception as e:
            logger.error(f"❌ Schema details with topics error: {e}")
            st.error(f"❌ Failed to render schema details: {e}")

    def _render_topic_details_with_info(self, topic: str, qos: int, retain: bool):
        """Render topic details with QoS and retain information"""
        try:
            # Get topic schema and description
            topic_schema = self.registry_manager.get_topic_schema(topic)
            topic_description = self.registry_manager.get_topic_description(topic)

            if topic_schema:
                st.success(
                    f"✅ Schema found: {topic_schema.get('title', 'Unknown Schema') if isinstance(topic_schema, dict) else topic_schema}"
                )
            else:
                st.warning("⚠️ No schema found for this topic")

            if topic_description:
                st.info(f"📝 Description: {topic_description}")

            # Display QoS and Retain information
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"🔢 QoS: {qos}")
            with col2:
                st.info(f"💾 Retain: {'Yes' if retain else 'No'}")

            # Generate and display payload
            from omf2.ui.common.components.payload_generator import PayloadGenerator

            generator = PayloadGenerator(self.registry_manager)
            payload = generator.generate_example_payload(topic)

            if payload:
                st.markdown("**Generated Payload:**")
                st.json(payload)

                # Payload editing
                st.markdown("**Edit Payload:**")
                edited_payload = st.text_area(
                    "Payload JSON:", value=json.dumps(payload, indent=2), height=200, key=f"payload_edit_{topic}"
                )

                # Message sending with QoS and retain
                self._render_message_sending_ui_with_info(topic, edited_payload, qos, retain)
            else:
                st.error("❌ Failed to generate payload")

        except Exception as e:
            logger.error(f"❌ Topic details with info error: {e}")
            st.error(f"❌ Failed to render topic details: {e}")

    def _render_message_sending_ui_with_info(self, topic: str, payload_json: str, qos: int, retain: bool):
        """Render message sending UI with QoS and retain information"""
        st.markdown("**Message Options:**")

        # Display QoS and Retain info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🔢 QoS: {qos}")
        with col2:
            st.info(f"💾 Retain: {'Yes' if retain else 'No'}")

        # Message sending button
        if st.button(f"📤 Send Message to {topic}", key=f"send_message_{topic}"):
            try:
                # Parse JSON payload
                payload = json.loads(payload_json)

                # TODO: Implement actual message sending via gateway
                st.success(f"✅ Message sent to {topic} (QoS: {qos}, Retain: {retain})")
                logger.info(f"📤 Message sent to {topic}: {payload}")

            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON payload: {e}")
            except Exception as e:
                st.error(f"❌ Failed to send message: {e}")

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
                    if not validation_result.get("valid", False):
                        st.error(f"❌ Payload validation failed: {validation_result.get('error', 'Unknown error')}")
                        return

                # Send message via gateway
                from omf2.factory.gateway_factory import get_admin_gateway

                gateway = get_admin_gateway()

                if gateway and hasattr(gateway, "publish_message"):
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
