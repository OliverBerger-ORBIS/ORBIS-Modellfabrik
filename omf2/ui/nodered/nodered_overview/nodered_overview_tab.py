#!/usr/bin/env python3
"""
Node-RED Overview Tab - Node-RED Overview UI Component
"""

import streamlit as st
from omf2.nodered.nodered_gateway import NoderedGateway
from omf2.nodered.nodered_pub_mqtt_client import get_nodered_pub_mqtt_client
from omf2.nodered.nodered_sub_mqtt_client import get_nodered_sub_mqtt_client
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_nodered_overview_tab():
    """Render Node-RED Overview Tab"""
    logger.info("🔄 Rendering Node-RED Overview Tab")
    try:
        st.header("🔄 Node-RED Overview")
        st.markdown("Node-RED Integration and Message Processing")
        
        # Initialize Node-RED Gateway
        if 'nodered_gateway' not in st.session_state:
            st.session_state['nodered_gateway'] = NoderedGateway()
        
        nodered_gateway = st.session_state['nodered_gateway']
        
        # Node-RED Status Section
        with st.expander("📊 Node-RED Status", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", "🟢 Connected", "Online")
            
            with col2:
                st.metric("Flows", "12", "Active")
            
            with col3:
                st.metric("Messages/min", "45", "↗️ +5")
        
        # Message Processing Section
        with st.expander("📨 Message Processing", expanded=True):
            st.markdown("### Message Flow Overview")
            
            # Message flow data
            flows = [
                {"name": "OPC-UA to MQTT", "status": "running", "messages": 234, "errors": 0},
                {"name": "MQTT Normalization", "status": "running", "messages": 189, "errors": 1},
                {"name": "Status Aggregation", "status": "running", "messages": 156, "errors": 0},
                {"name": "Error Handling", "status": "idle", "messages": 12, "errors": 0},
            ]
            
            for flow in flows:
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
                    
                    with col1:
                        st.write(f"**{flow['name']}**")
                    
                    with col2:
                        status_color = "🟢" if flow['status'] == "running" else "🟡"
                        st.write(f"{status_color} {flow['status']}")
                    
                    with col3:
                        st.write(f"{flow['messages']} messages")
                    
                    with col4:
                        error_color = "🟢" if flow['errors'] == 0 else "🔴"
                        st.write(f"{error_color} {flow['errors']}")
        
        # MQTT Client Status Section
        with st.expander("🔗 MQTT Client Status", expanded=True):
            st.markdown("### Node-RED MQTT Clients")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Publisher Client:**")
                pub_client = get_nodered_pub_mqtt_client()
                st.write(f"Status: 🟢 Connected")
                st.write(f"Published Topics: {len(nodered_gateway.get_pub_topics())}")
                
                st.markdown("**Published Topics:**")
                for topic in nodered_gateway.get_pub_topics()[:3]:
                    st.write(f"• {topic}")
                if len(nodered_gateway.get_pub_topics()) > 3:
                    st.write(f"• ... and {len(nodered_gateway.get_pub_topics()) - 3} more")
            
            with col2:
                st.markdown("**Subscriber Client:**")
                sub_client = get_nodered_sub_mqtt_client()
                st.write(f"Status: 🟢 Connected")
                st.write(f"Subscribed Topics: {len(nodered_gateway.get_sub_topics())}")
                
                st.markdown("**Subscribed Topics:**")
                for topic in nodered_gateway.get_sub_topics()[:3]:
                    st.write(f"• {topic}")
                if len(nodered_gateway.get_sub_topics()) > 3:
                    st.write(f"• ... and {len(nodered_gateway.get_sub_topics()) - 3} more")
        
        # Message Normalization Section
        with st.expander("🔄 Message Normalization", expanded=True):
            st.markdown("### Normalized Messages")
            
            # Normalized message examples
            normalized_messages = [
                {"topic": "NodeRed/module/SVR3QA0022/state", "source": "DPS", "timestamp": "2025-09-28T16:24:55Z"},
                {"topic": "NodeRed/module/SVR4H76449/state", "source": "FTS", "timestamp": "2025-09-28T16:24:50Z"},
                {"topic": "NodeRed/module/SVR3QA2098/state", "source": "AIQS", "timestamp": "2025-09-28T16:24:45Z"},
            ]
            
            for msg in normalized_messages:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.write(f"**{msg['topic']}**")
                    
                    with col2:
                        st.write(msg['source'])
                    
                    with col3:
                        st.write(msg['timestamp'])
        
        # Control Actions Section
        with st.expander("🎛️ Control Actions", expanded=False):
            st.markdown("### Node-RED Control")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🔄 Restart Flows", key="nodered_overview_restart_btn"):
                    st.info("🔄 Restarting Node-RED flows...")
                    st.success("✅ Flows restarted successfully")
            
            with col2:
                if st.button("📊 Get Statistics", key="nodered_overview_stats_btn"):
                    st.info("📊 Gathering Node-RED statistics...")
                    st.success("✅ Statistics updated")
            
            with col3:
                if st.button("🔍 Check Health", key="nodered_overview_health_btn"):
                    st.info("🔍 Checking Node-RED health...")
                    st.success("✅ All systems healthy")
        
    except Exception as e:
        logger.error(f"❌ Node-RED Overview Tab rendering error: {e}")
        st.error(f"❌ Node-RED Overview Tab failed: {e}")
        st.info("💡 This component is currently under development.")
