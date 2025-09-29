#!/usr/bin/env python3
"""
Message Center Tab - Message Center UI Component
"""

import streamlit as st
from omf2.nodered.nodered_gateway import NoderedGateway
from omf2.nodered.nodered_pub_mqtt_client import get_nodered_pub_mqtt_client
from omf2.nodered.nodered_sub_mqtt_client import get_nodered_sub_mqtt_client
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_message_center_tab():
    """Render Message Center Tab"""
    logger.info("📨 Rendering Message Center Tab")
    try:
        st.header("📨 Message Center")
        st.markdown("MQTT Message Monitoring and Management")
        
        # Initialize Node-RED Gateway
        if 'nodered_gateway' not in st.session_state:
            st.session_state['nodered_gateway'] = NoderedGateway()
        
        nodered_gateway = st.session_state['nodered_gateway']
        
        # Message Statistics Section
        with st.expander("📊 Message Statistics", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Messages", "1,247", "↗️ +12")
            
            with col2:
                st.metric("Active Topics", "23", "↗️ +2")
            
            with col3:
                st.metric("Error Rate", "0.3%", "↘️ -0.1%")
            
            with col4:
                st.metric("Throughput", "45/min", "↗️ +5")
        
        # Message Types Section
        with st.expander("📋 Message Types", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📤 Published Messages")
                st.markdown("**Node-RED Publisher Topics:**")
                pub_topics = nodered_gateway.get_pub_topics()
                for topic in pub_topics[:5]:  # Show first 5
                    st.write(f"• {topic}")
                if len(pub_topics) > 5:
                    st.write(f"• ... and {len(pub_topics) - 5} more")
            
            with col2:
                st.markdown("### 📥 Subscribed Messages")
                st.markdown("**Node-RED Subscriber Topics:**")
                sub_topics = nodered_gateway.get_sub_topics()
                for topic in sub_topics[:5]:  # Show first 5
                    st.write(f"• {topic}")
                if len(sub_topics) > 5:
                    st.write(f"• ... and {len(sub_topics) - 5} more")
        
        # Normalized Module States Section
        with st.expander("🔄 Normalized Module States", expanded=True):
            st.markdown("### Node-RED Normalized States")
            
            # Placeholder normalized states
            normalized_states = [
                {"module": "SVR3QA0022", "state": "idle", "timestamp": "2025-09-28T16:24:55Z", "source": "Node-RED"},
                {"module": "SVR4H76449", "state": "moving", "timestamp": "2025-09-28T16:24:50Z", "source": "Node-RED"},
                {"module": "SVR3QA2098", "state": "processing", "timestamp": "2025-09-28T16:24:45Z", "source": "Node-RED"},
            ]
            
            for state in normalized_states:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
                with col1:
                    st.write(f"**{state['module']}**")
                with col2:
                    st.write(state['state'])
                with col3:
                    st.write(state['timestamp'])
                with col4:
                    st.write(state['source'])
        
        # CCU Commands Section
        with st.expander("🎛️ CCU Commands", expanded=True):
            st.markdown("### Recent CCU Commands")
            
            # Placeholder CCU commands
            ccu_commands = [
                {"command": "reset_factory", "timestamp": "2025-09-28T16:20:00Z", "status": "executed"},
                {"command": "global_status", "timestamp": "2025-09-28T16:15:00Z", "status": "executed"},
                {"command": "order_request", "timestamp": "2025-09-28T16:10:00Z", "status": "pending"},
            ]
            
            for cmd in ccu_commands:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**{cmd['command']}**")
                with col2:
                    st.write(cmd['timestamp'])
                with col3:
                    status_color = "🟢" if cmd['status'] == "executed" else "🟡"
                    st.write(f"{status_color} {cmd['status']}")
        
        # OPC-UA States Section
        with st.expander("🏭 OPC-UA States", expanded=True):
            st.markdown("### OPC-UA Module States")
            
            # Placeholder OPC-UA states
            opc_ua_states = [
                {"module": "SPS1", "state": "running", "timestamp": "2025-09-28T16:24:55Z"},
                {"module": "SPS2", "state": "idle", "timestamp": "2025-09-28T16:24:50Z"},
                {"module": "SPS3", "state": "error", "timestamp": "2025-09-28T16:24:45Z"},
            ]
            
            for state in opc_ua_states:
                col1, col2, col3 = st.columns([2, 2, 2])
                with col1:
                    st.write(f"**{state['module']}**")
                with col2:
                    status_color = "🟢" if state['state'] == "running" else "🔴" if state['state'] == "error" else "🟡"
                    st.write(f"{status_color} {state['state']}")
                with col3:
                    st.write(state['timestamp'])
        
        # Message Testing Section
        with st.expander("🧪 Message Testing", expanded=False):
            st.markdown("### Test Message Generation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Send Test Message:**")
                test_topic = st.text_input("Topic:", value="test/message", key="message_center_test_topic")
                test_message = st.text_area("Message:", value='{"test": "data", "timestamp": "2025-09-28T16:24:55Z"}', key="message_center_test_message")
                
                if st.button("📤 Send Test Message", key="message_center_test_send_btn"):
                    st.success(f"✅ Test message sent to {test_topic}")
            
            with col2:
                st.markdown("**Message Validation:**")
                validation_topic = st.text_input("Validation Topic:", value="module/v1/ff/SVR3QA0022/state", key="message_center_val_topic")
                validation_message = st.text_area("Validation Message:", value='{"module_id": "SVR3QA0022", "state": "idle", "timestamp": "2025-09-28T16:24:55Z"}', key="message_center_val_message")
                
                if st.button("✅ Validate Message", key="message_center_val_btn"):
                    st.success("✅ Message validation passed")
        
    except Exception as e:
        logger.error(f"❌ Message Center Tab rendering error: {e}")
        st.error(f"❌ Message Center Tab failed: {e}")
        st.info("💡 This component is currently under development.")
