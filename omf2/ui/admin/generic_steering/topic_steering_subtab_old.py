#!/usr/bin/env python3
"""
Topic Steering Subtab - Commands from omf/dashboard/components/admin/steering_generic.py
Gateway-Pattern konform: Nutzt AdminGateway statt direkten MQTT-Client
"""

import streamlit as st
import json
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def _run_schema_test(registry_manager, admin_gateway):
    """Run systematic test for all topics with schema validation"""
    st.markdown("### 🧪 Schema Test Results")
    
    # Get all topics
    topics = registry_manager.get_topics()
    test_results = []
    
    # Progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_topics = len(topics)
    valid_count = 0
    invalid_count = 0
    no_schema_count = 0
    
    for i, (topic, topic_info) in enumerate(topics.items()):
        status_text.text(f"Testing topic {i+1}/{total_topics}: {topic}")
        progress_bar.progress((i + 1) / total_topics)
        
        try:
            # Get schema for topic
            topic_schema = registry_manager.get_topic_schema(topic)
            
            if not topic_schema:
                test_results.append({
                    'topic': topic,
                    'status': 'NO_SCHEMA',
                    'error': 'No schema found',
                    'payload': None
                })
                no_schema_count += 1
                continue
            
            # Generate payload
            payload = _generate_example_payload(topic, registry_manager)
            
            # Validate payload
            validation_result = registry_manager.validate_topic_payload(topic, payload)
            
            if validation_result.get('valid', False):
                test_results.append({
                    'topic': topic,
                    'status': 'VALID',
                    'error': None,
                    'payload': payload
                })
                valid_count += 1
            else:
                test_results.append({
                    'topic': topic,
                    'status': 'INVALID',
                    'error': validation_result.get('error', 'Unknown validation error'),
                    'payload': payload
                })
                invalid_count += 1
                
        except Exception as e:
            test_results.append({
                'topic': topic,
                'status': 'ERROR',
                'error': str(e),
                'payload': None
            })
            invalid_count += 1
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Display results
    st.markdown("#### 📊 Test Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Topics", total_topics)
    with col2:
        st.metric("✅ Valid", valid_count, delta=f"{valid_count/total_topics*100:.1f}%")
    with col3:
        st.metric("❌ Invalid", invalid_count, delta=f"{invalid_count/total_topics*100:.1f}%")
    with col4:
        st.metric("⚠️ No Schema", no_schema_count, delta=f"{no_schema_count/total_topics*100:.1f}%")
    
    # Show detailed results
    st.markdown("#### 📋 Detailed Results")
    
    # Filter options - use session state to persist selection
    if "test_filter_option" not in st.session_state:
        st.session_state.test_filter_option = "All"
    
    # Use radio buttons instead of selectbox to avoid UI jumping
    filter_option = st.radio(
        "Filter Results:",
        ["All", "Valid Only", "Invalid Only", "No Schema", "Errors Only"],
        key="test_filter_radio",
        horizontal=True
    )
    
    # Update session state
    st.session_state.test_filter_option = filter_option
    
    filtered_results = test_results
    if filter_option == "Valid Only":
        filtered_results = [r for r in test_results if r['status'] == 'VALID']
    elif filter_option == "Invalid Only":
        filtered_results = [r for r in test_results if r['status'] == 'INVALID']
    elif filter_option == "No Schema":
        filtered_results = [r for r in test_results if r['status'] == 'NO_SCHEMA']
    elif filter_option == "Errors Only":
        filtered_results = [r for r in test_results if r['status'] == 'ERROR']
    
    # Display results in expandable sections
    for result in filtered_results[:20]:  # Show first 20 results
        status_icon = "✅" if result['status'] == 'VALID' else "❌" if result['status'] == 'INVALID' else "⚠️" if result['status'] == 'NO_SCHEMA' else "🚨"
        
        with st.expander(f"{status_icon} {result['topic']}", expanded=False):
            st.markdown(f"**Status:** {result['status']}")
            if result['error']:
                st.error(f"**Error:** {result['error']}")
            if result['payload']:
                st.json(result['payload'])
    
    if len(filtered_results) > 20:
        st.info(f"... and {len(filtered_results) - 20} more results")
    
    # Save results option
    if st.button("💾 Export Test Results", key="export_test_results_btn"):
        import csv
        from io import StringIO
        
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(['Topic', 'Status', 'Error', 'Payload'])
        
        for result in test_results:
            payload_str = json.dumps(result['payload']) if result['payload'] else ''
            writer.writerow([result['topic'], result['status'], result['error'] or '', payload_str])
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_buffer.getvalue(),
            file_name="schema_test_results.csv",
            mime="text/csv"
        )


def _generate_example_payload(topic, registry_manager):
    """Generate example payload based on topic and schema"""
    try:
        # Get schema for topic
        schema = registry_manager.get_topic_schema(topic)
        if not schema:
            return {"message": "No schema available", "timestamp": "2024-01-01T00:00:00Z"}
        
        # Check if schema is already a dict (from get_topic_schema)
        if isinstance(schema, dict):
            schema_data = schema
        else:
            # Load schema file if it's a string path
            schema_path = registry_manager.registry_path / "schemas" / schema
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_data = json.load(f)
            else:
                return {"message": "Schema file not found", "timestamp": "2024-01-01T00:00:00Z"}
        
        # Generate example based on schema properties
        example = {}
        if 'properties' in schema_data:
            for prop, prop_info in schema_data['properties'].items():
                    if prop == 'timestamp':
                        example[prop] = "2024-01-01T00:00:00Z"
                    elif prop == 'id':
                        example[prop] = "example_id"
                    elif prop == 'status':
                        example[prop] = "idle"
                    elif prop == 'command':
                        example[prop] = "status"
                    elif prop == 'type':
                        example[prop] = "WHITE"
                    elif prop == 'orderType':
                        example[prop] = "STORAGE"
                    elif prop == 'workpieceId':
                        example[prop] = "047c8bca341291"
                    elif prop == 'serialNumber':
                        example[prop] = "SVR3QA0022"
                    elif prop == 'clientId':
                        example[prop] = "example_client"
                    elif prop == 'ipAddress':
                        example[prop] = "192.168.1.100"
                    elif prop == 'connected':
                        example[prop] = True
                    elif prop == 'version':
                        example[prop] = "1.0.0"
                    elif prop == 'systemStatus':
                        example[prop] = "RUNNING"
                    elif prop == 'activeOrders':
                        example[prop] = 0
                    elif prop == 'completedOrders':
                        example[prop] = 0
                    elif prop == 'errorCount':
                        example[prop] = 0
                    elif prop == 'uptime':
                        example[prop] = 3600
                    elif prop == 't':
                        example[prop] = 25.4
                    elif prop == 'h':
                        example[prop] = 31.6
                    elif prop == 'p':
                        example[prop] = 1003.8
                    elif prop == 'iaq':
                        example[prop] = 48
                    elif prop == 'aq':
                        example[prop] = 3
                    elif prop == 'gr':
                        example[prop] = 0
                    elif prop == 'ts':
                        example[prop] = "2024-01-01T00:00:00Z"
                    elif prop == 'rt':
                        example[prop] = 0.0
                    elif prop == 'rh':
                        example[prop] = 0.0
                    elif prop == 'orderUpdateId':
                        example[prop] = 0  # Integer, not null
                    elif prop == 'orderId':
                        example[prop] = "example_order_id"  # String, not null
                    elif prop == 'operatingMode':
                        example[prop] = "AUTOMATIC"  # Valid operating mode
                    elif prop == 'paused':
                        example[prop] = False  # Boolean, not null
                    elif prop == 'loads':
                        example[prop] = []  # Empty array
                    elif prop == 'errors':
                        example[prop] = []  # Empty array
                    elif prop == 'information':
                        example[prop] = []  # Empty array
                    elif prop == 'actionStates':
                        example[prop] = []  # Empty array
                    elif prop == 'actionState':
                        example[prop] = {}  # Empty object, not null
                    elif prop == 'metadata':
                        example[prop] = {"opcuaState": "connected"}  # Required nested property
                    elif prop == 'batteryState':
                        example[prop] = {
                            "charging": True,
                            "currentVoltage": 12.0,
                            "maxVolt": 14.4,
                            "minVolt": 10.0,
                            "percentage": 85
                        }
                    elif prop == 'loads':
                        example[prop] = [
                            {
                                "loadType": "WHITE",
                                "loadId": "047c8bca341291",
                                "loadPosition": "A1",
                                "loadTimestamp": 1759220483909
                            }
                        ]
                    elif prop == 'load':
                        example[prop] = [
                            {
                                "loadType": "WHITE",
                                "loadId": "047c8bca341291",
                                "loadPosition": "A1",
                                "loadTimestamp": 1759220483909
                            }
                        ]
                    elif prop == 'actionStates':
                        example[prop] = [
                            {
                                "id": "example_action_id",
                                "state": "FINISHED",
                                "command": "example_command",
                                "metadata": {}
                            }
                        ]
                    elif prop == 'edgeStates':
                        example[prop] = [
                            {
                                "edgeId": "example_edge_id",
                                "state": "ACTIVE",
                                "timestamp": "2024-01-01T00:00:00Z"
                            }
                        ]
                    elif prop == 'nodeStates':
                        example[prop] = [
                            {
                                "nodeId": "example_node_id",
                                "state": "ACTIVE",
                                "timestamp": "2024-01-01T00:00:00Z"
                            }
                        ]
                    elif prop == 'lastNodeSequenceId':
                        example[prop] = 1
                    elif prop == 'lastNodeId':
                        example[prop] = "example_node_id"
                    elif prop == 'lastCode':
                        example[prop] = "example_code"
                    elif prop == 'waitingForLoadHandling':
                        example[prop] = False
                    elif prop == 'driving':
                        example[prop] = False
                    else:
                        # Default values based on type
                        prop_type = prop_info.get('type')
                        
                        # Handle union types (e.g., ['integer', 'string'])
                        if isinstance(prop_type, list):
                            # Use first type from union
                            prop_type = prop_type[0]
                        
                        if prop_type == 'string':
                            example[prop] = f"example_{prop}"
                        elif prop_type == 'number':
                            example[prop] = 0
                        elif prop_type == 'integer':
                            example[prop] = 0
                        elif prop_type == 'boolean':
                            example[prop] = True
                        elif prop_type == 'array':
                            # Handle array with specific items
                            if 'items' in prop_info and prop_info['items'].get('type') == 'string':
                                example[prop] = ["example_item1", "example_item2"]
                            else:
                                example[prop] = []
                        elif prop_type == 'object':
                            # Handle nested object with required properties
                            nested_obj = {}
                            if 'properties' in prop_info:
                                # Get required properties for this object
                                required_props = prop_info.get('required', [])
                                
                                for nested_prop, nested_info in prop_info['properties'].items():
                                    nested_type = nested_info.get('type')
                                    
                                    # Handle union types
                                    if isinstance(nested_type, list):
                                        nested_type = nested_type[0]
                                    
                                    if nested_prop == 'opcuaState':
                                        nested_obj[nested_prop] = "connected"
                                    elif nested_prop == 'charging':
                                        nested_obj[nested_prop] = True
                                    elif nested_prop == 'currentVoltage':
                                        nested_obj[nested_prop] = 12.0
                                    elif nested_prop == 'maxVolt':
                                        nested_obj[nested_prop] = 14.4
                                    elif nested_prop == 'minVolt':
                                        nested_obj[nested_prop] = 10.0
                                    elif nested_prop == 'percentage':
                                        nested_obj[nested_prop] = 85
                                    elif nested_type == 'string':
                                        nested_obj[nested_prop] = f"example_{nested_prop}"
                                    elif nested_type == 'integer':
                                        nested_obj[nested_prop] = 0
                                    elif nested_type == 'number':
                                        nested_obj[nested_prop] = 0.0
                                    elif nested_type == 'boolean':
                                        nested_obj[nested_prop] = True
                                    elif nested_type == 'array':
                                        if 'items' in nested_info and nested_info['items'].get('type') == 'string':
                                            nested_obj[nested_prop] = ["example_item1", "example_item2"]
                                        else:
                                            nested_obj[nested_prop] = []
                                    else:
                                        nested_obj[nested_prop] = f"example_{nested_prop}"
                                
                                # Ensure all required properties are present
                                for req_prop in required_props:
                                    if req_prop not in nested_obj:
                                        nested_obj[req_prop] = f"required_{req_prop}"
                            
                            example[prop] = nested_obj
                        elif prop_type == 'null':
                            example[prop] = None
                        else:
                            # For unknown types, try to use a safe default
                            if 'required' in schema_data and prop in schema_data['required']:
                                # Required field - use string as fallback
                                example[prop] = f"example_{prop}"
                            else:
                                # Optional field - can be null
                                example[prop] = None
            
            return example
        else:
            return {"message": "No properties in schema", "timestamp": "2024-01-01T00:00:00Z"}
            
    except Exception as e:
        logger.error(f"❌ Error generating example payload: {e}")
        return {"error": str(e), "timestamp": "2024-01-01T00:00:00Z"}


def render_topic_steering_subtab(admin_gateway, registry_manager):
    """Render Topic Steering Subtab with commands from steering_generic.py
    
    Args:
        admin_gateway: AdminGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz
    """
    logger.info("🔧 Rendering Topic Steering Subtab")
    
    try:
        st.subheader("🔧 Generic Steuerung")
        st.markdown("**Erweiterte Steuerungsmöglichkeiten für direkte MQTT-Nachrichten:**")
        
        # Free Mode Section
        st.markdown("### 📝 Freier Modus")
        st.markdown("**Direkte Eingabe von Topic und Message-Payload:**")
        
        with st.expander("📝 Free Mode Commands", expanded=True):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**Topic:**")
                topic_input = st.text_input(
                    "MQTT Topic:",
                    value="ccu/command",
                    key="free_mode_topic",
                    help="Enter MQTT topic for the message"
                )
                
                st.markdown("**QoS Level:**")
                qos_level = st.selectbox(
                    "QoS:",
                    options=[0, 1, 2],
                    index=0,
                    key="free_mode_qos",
                    help="Quality of Service level"
                )
                
                retain_message = st.checkbox(
                    "Retain Message",
                    value=False,
                    key="free_mode_retain",
                    help="Retain message on broker"
                )
            
            with col2:
                st.markdown("**Message Payload (JSON):**")
                default_payload = {
                    "command": "status",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "source": "omf2_admin"
                }
                
                payload_input = st.text_area(
                    "JSON Payload:",
                    value=json.dumps(default_payload, indent=2),
                    height=150,
                    key="free_mode_payload",
                    help="Enter JSON payload for the message"
                )
            
            # Send button
            if st.button("🚀 Send Message", key="free_mode_send_btn", type="primary"):
                try:
                    # Parse JSON payload
                    payload = json.loads(payload_input)
                    
                    # Gateway-Pattern: Nutze AdminGateway publish_message
                    success = admin_gateway.publish_message(
                        topic=topic_input,
                        message=payload,
                        qos=qos_level,
                        retain=retain_message
                    )
                    
                    if success:
                        st.success(f"✅ Message sent to topic: {topic_input}")
                        st.json(payload)
                        logger.info(f"📤 Free mode message sent: {topic_input} (QoS: {qos_level}, Retain: {retain_message})")
                    else:
                        st.error(f"❌ Failed to send message to {topic_input}")
                    
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON: {e}")
                except Exception as e:
                    st.error(f"❌ Send failed: {e}")
                    logger.error(f"❌ Free mode send error: {e}")
        
        # Topic-driven Mode Section
        st.markdown("---")
        st.markdown("### 📡 Topic-getriebener Ansatz")
        st.markdown("**Topic auswählen und Schema-basierte Payload-Generierung:**")
        
        with st.expander("📡 Topic-driven Commands", expanded=True):
            # Topic Selection from Registry
            if registry_manager:
                topics = registry_manager.get_topics()
                topic_options = list(topics.keys())[:20]  # Show more topics
                st.info(f"📚 Available topics from Registry: {len(topics)} total")
            else:
                topic_options = ["ccu/command", "module/status", "txt/control"]
                st.warning("⚠️ Registry Manager not available, using default topics")
            
            selected_topic = st.selectbox(
                "Select Topic:",
                options=topic_options,
                key="topic_driven_topic",
                help="Select topic from available options"
            )
            
            # Schema-based Payload Generation
            if selected_topic and registry_manager:
                # Get schema for selected topic
                topic_schema = registry_manager.get_topic_schema(selected_topic)
                topic_description = registry_manager.get_topic_description(selected_topic)
                
                if topic_schema:
                    if isinstance(topic_schema, dict):
                        st.success(f"✅ Schema found: {topic_schema.get('title', 'Unknown Schema')}")
                        if topic_description:
                            st.info(f"📝 Description: {topic_description}")
                    else:
                        st.success(f"✅ Schema found: {topic_schema}")
                        if topic_description:
                            st.info(f"📝 Description: {topic_description}")
                    
                    # Generate example payload based on schema
                    example_payload = _generate_example_payload(selected_topic, registry_manager)
                    
                    col1, col2 = st.columns([1, 1])
                    
            with col1:
                        st.markdown("**Generated Payload:**")
                        payload_editor = st.text_area(
                            "Edit Payload:",
                            value=json.dumps(example_payload, indent=2),
                            height=200,
                            key="topic_driven_payload",
                            help="Edit the generated payload"
                        )
                    
            with col2:
                        st.markdown("**Message Options:**")
                        qos_level = st.selectbox(
                            "QoS:",
                            options=[0, 1, 2],
                            index=0,
                            key="topic_driven_qos",
                            help="Quality of Service level"
                        )
                        
                        retain_message = st.checkbox(
                            "Retain Message",
                            value=False,
                            key="topic_driven_retain",
                            help="Retain message on broker"
                        )
                        
                        # Send button
                        if st.button("🚀 Send Message", key="topic_driven_send_btn", type="primary"):
                            try:
                                # Parse and validate payload
                                payload = json.loads(payload_editor)
                                
                                # Validate against schema
                                validation_result = registry_manager.validate_topic_payload(selected_topic, payload)
                                
                                if validation_result.get('valid', False):
                                    # Send via Gateway
                                    success = admin_gateway.publish_message(
                                        topic=selected_topic,
                                        message=payload,
                                        qos=qos_level,
                                        retain=retain_message
                                    )
                                    
                                    if success:
                                        st.success(f"✅ Message sent to topic: {selected_topic}")
                                        st.json(payload)
                                        logger.info(f"📤 Topic-driven message sent: {selected_topic} (QoS: {qos_level}, Retain: {retain_message})")
                                    else:
                                        st.error(f"❌ Failed to send message to {selected_topic}")
                                else:
                                    st.error(f"❌ Payload validation failed: {validation_result.get('error', 'Unknown error')}")
                                    
                            except json.JSONDecodeError as e:
                                st.error(f"❌ Invalid JSON: {e}")
                            except Exception as e:
                                st.error(f"❌ Send failed: {e}")
                                logger.error(f"❌ Topic-driven send error: {e}")
                else:
                    st.warning(f"⚠️ No schema found for topic: {selected_topic}")
                    st.info("💡 You can still send messages, but without schema validation")
        
        # Schema-driven Mode Section
        st.markdown("---")
        st.markdown("### 📋 Schema-getriebener Ansatz")
        st.markdown("**Schema auswählen und zugehörige Topics anzeigen:**")
        
        with st.expander("📋 Schema-driven Commands", expanded=True):
            if registry_manager:
                # Get available schemas
                schemas = registry_manager.get_schemas()
                schema_options = list(schemas.keys())[:20]  # Show more schemas
                st.info(f"📚 Available schemas from Registry: {len(schemas)} total")
                
                selected_schema = st.selectbox(
                    "Select Schema:",
                    options=schema_options,
                    key="schema_driven_schema",
                    help="Select schema from available options"
                )
                
                if selected_schema:
                    # Find topics that use this schema
                    topics = registry_manager.get_topics()
                    related_topics = []
                    
                    # Debug: Show what we're looking for
                    st.info(f"🔍 Looking for topics using schema: {selected_schema}")
                    
                    # Check each topic's schema
                    for topic, topic_info in topics.items():
                        topic_schema = registry_manager.get_topic_schema(topic)
                        if topic_schema:
                            # Handle both dict and string schema responses
                            if isinstance(topic_schema, dict):
                                schema_title = topic_schema.get('title', '')
                                schema_file = topic_schema.get('$id', '')
                                
                                # Multiple matching strategies
                                if (selected_schema in schema_title or 
                                    selected_schema.replace('.schema', '') in schema_title or
                                    selected_schema in schema_file or
                                    selected_schema.replace('.schema', '') in schema_file):
                                    related_topics.append(topic)
                                    st.write(f"✅ Found match: {topic} -> {schema_title}")
                            elif isinstance(topic_schema, str):
                                if selected_schema in topic_schema or selected_schema.replace('.schema', '') in topic_schema:
                                    related_topics.append(topic)
                                    st.write(f"✅ Found match: {topic} -> {topic_schema}")
                    
                    # If no matches found, show debug info
                    if not related_topics:
                        st.warning("🔍 Debug: No topics found. Checking schema mappings...")
                        
                        # Try alternative approach - check topic schema mappings
                        try:
                            topic_schema_mappings = registry_manager.get_topic_schema_mappings()
                            st.write(f"📊 Topic-Schema mappings available: {len(topic_schema_mappings)}")
                            
                            for topic, schema_file in topic_schema_mappings.items():
                                # Handle both string and dict schema_file
                                schema_file_str = schema_file
                                if isinstance(schema_file, dict):
                                    schema_file_str = schema_file.get('title', '') or schema_file.get('$id', '') or str(schema_file)
                                
                                # Try different matching strategies
                                if (selected_schema in schema_file_str or 
                                    selected_schema.replace('.schema', '') in schema_file_str or
                                    selected_schema.replace('.schema.json', '') in schema_file_str or
                                    schema_file_str.replace('.schema.json', '') in selected_schema):
                                    related_topics.append(topic)
                                    st.write(f"✅ Found via mapping: {topic} -> {schema_file_str}")
                                    
                            # If still no matches, show some example mappings
                            if not related_topics:
                                st.info("🔍 Example schema mappings:")
                                for i, (topic, schema_file) in enumerate(list(topic_schema_mappings.items())[:5]):
                                    schema_file_str = schema_file
                                    if isinstance(schema_file, dict):
                                        schema_file_str = schema_file.get('title', '') or schema_file.get('$id', '') or str(schema_file)
                                    st.text(f"  {topic} -> {schema_file_str}")
                                st.text(f"... and {len(topic_schema_mappings) - 5} more mappings")
                        except Exception as e:
                            st.error(f"❌ Error getting topic schema mappings: {e}")
                    
                    if related_topics:
                        st.success(f"✅ Found {len(related_topics)} topics using schema: {selected_schema}")
                        
                        # Display related topics with editable messages
                        st.markdown("**Related Topics:**")
                        for i, topic in enumerate(related_topics[:5]):  # Show first 5 for better UI
                            with st.expander(f"📤 {topic}", expanded=False):
                                # Generate payload for this topic
                                example_payload = _generate_example_payload(topic, registry_manager)
                                
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.markdown("**Editable Payload:**")
                                    editable_payload = st.text_area(
                                        f"Payload for {topic}:",
                                        value=json.dumps(example_payload, indent=2),
                                        height=150,
                                        key=f"schema_payload_{i}",
                                        help="Edit the payload before sending"
                                    )
                                    
                                    # Message options
                                    col_qos, col_retain = st.columns(2)
                                    with col_qos:
                                        qos_level = st.selectbox(
                                            "QoS:",
                                            options=[0, 1, 2],
                                            index=0,
                                            key=f"schema_qos_{i}",
                                            help="Quality of Service level"
                                        )
                                    with col_retain:
                                        retain_message = st.checkbox(
                                            "Retain",
                                            value=False,
                                            key=f"schema_retain_{i}",
                                            help="Retain message on broker"
                                        )
                                
                                with col2:
                                    st.markdown("**Actions:**")
                                    if st.button(f"🚀 Send Message", key=f"schema_send_{i}", type="primary"):
                                        try:
                                            # Parse edited payload
                                            payload = json.loads(editable_payload)
                                            
                                            # Validate against schema
                                            validation_result = registry_manager.validate_topic_payload(topic, payload)
                                            
                                            if validation_result.get('valid', False):
                                                # Send via Gateway
                                                success = admin_gateway.publish_message(
                                                    topic=topic,
                                                    message=payload,
                                                    qos=qos_level,
                                                    retain=retain_message
                                                )
                                                
                                                if success:
                                                    st.success(f"✅ Message sent to: {topic}")
                                                    st.json(payload)
                                                    logger.info(f"📤 Schema-driven message sent: {topic} using schema {selected_schema} (QoS: {qos_level}, Retain: {retain_message})")
                                                else:
                                                    st.error(f"❌ Failed to send to: {topic}")
                                            else:
                                                st.error(f"❌ Payload validation failed: {validation_result.get('error', 'Unknown error')}")
                                                
                                        except json.JSONDecodeError as e:
                                            st.error(f"❌ Invalid JSON: {e}")
                                        except Exception as e:
                                            st.error(f"❌ Send error: {e}")
                                            logger.error(f"❌ Schema-driven send error: {e}")
                                    
                                    # Quick actions
                                    if st.button(f"🔄 Reset", key=f"schema_reset_{i}"):
                                        st.rerun()
                                    
                                    if st.button(f"📋 Copy", key=f"schema_copy_{i}"):
                                        st.code(editable_payload, language="json")
                        
                        if len(related_topics) > 5:
                            st.info(f"... and {len(related_topics) - 5} more topics")
                    else:
                        st.warning(f"⚠️ No topics found using schema: {selected_schema}")
                        
                        # Show schema content - try different file extensions
                        st.markdown("**Schema Content:**")
                        schema_found = False
                        
                        # Try different file extensions
                        for ext in ['.schema.json', '.json', '.schema']:
                            schema_path = registry_manager.registry_path / "schemas" / f"{selected_schema}{ext}"
                            if schema_path.exists():
                                with open(schema_path, 'r', encoding='utf-8') as f:
                                    schema_content = json.load(f)
                                st.json(schema_content)
                                schema_found = True
                                break
                        
                        if not schema_found:
                            st.error(f"❌ Schema file not found: {selected_schema}")
                            st.info("💡 Available schema files:")
                            
                            # List available schema files
                            schemas_dir = registry_manager.registry_path / "schemas"
                            if schemas_dir.exists():
                                schema_files = list(schemas_dir.glob("*.json"))
                                for schema_file in schema_files[:10]:  # Show first 10
                                    st.text(f"📄 {schema_file.name}")
                                if len(schema_files) > 10:
                                    st.text(f"... and {len(schema_files) - 10} more files")
                            else:
                                st.error("❌ Schemas directory not found")
            else:
                st.warning("⚠️ Registry Manager not available")
                st.info("💡 Schema-driven mode requires Registry Manager")
        
        # Schema Test Mode Section
        st.markdown("---")
        st.markdown("### 🧪 Schema Test Mode")
        st.markdown("**Systematischer Test aller Topics mit Schema-Validation:**")
        
        with st.expander("🧪 Schema Test Commands", expanded=False):
            if registry_manager:
                if st.button("🚀 Test All Topics", key="test_all_topics_btn", type="primary"):
                    _run_schema_test(registry_manager, admin_gateway)
            else:
                st.warning("⚠️ Registry Manager not available for testing")
        
        # Connection Info via Gateway
        conn_info = admin_gateway.get_connection_info()
        if conn_info.get('connected', False):
            st.info(f"🔗 MQTT Client: {conn_info.get('client_id', 'Unknown')} | Connected: {conn_info.get('connected', False)}")
        else:
            st.warning("⚠️ MQTT Client not connected")
            
    except Exception as e:
        logger.error(f"❌ Topic Steering Subtab error: {e}")
        st.error(f"❌ Topic Steering failed: {e}")
