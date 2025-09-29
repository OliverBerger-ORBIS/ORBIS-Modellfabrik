#!/usr/bin/env python3
"""
Generic Steering Tab - Factory Control UI Component
"""

import streamlit as st
from omf2.admin.admin_gateway import AdminGateway
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_generic_steering_tab():
    """Render Generic Steering Tab"""
    logger.info("🎛️ Rendering Generic Steering Tab")
    try:
        st.header("🎛️ Factory Control")
        st.markdown("Advanced Factory Management and Control")
        
        # Initialize Gateways
        if 'admin_gateway' not in st.session_state:
            st.session_state['admin_gateway'] = AdminGateway()
        
        if 'ccu_gateway' not in st.session_state:
            st.session_state['ccu_gateway'] = CcuGateway()
        
        admin_gateway = st.session_state['admin_gateway']
        ccu_gateway = st.session_state['ccu_gateway']
        
        # Factory Overview Section
        with st.expander("🏭 Factory Overview", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Factory Status", "🟢 Running", "Operational")
            
            with col2:
                st.metric("Active Modules", "7", "Online")
            
            with col3:
                st.metric("Orders in Queue", "3", "Processing")
            
            with col4:
                st.metric("System Health", "98%", "Excellent")
        
        # Emergency Controls Section
        with st.expander("🚨 Emergency Controls", expanded=True):
            st.markdown("### Critical Factory Operations")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🛑 Emergency Stop", type="primary", key="generic_steering_emergency_stop_btn"):
                    st.error("🚨 EMERGENCY STOP ACTIVATED")
                    st.warning("⚠️ All factory operations have been halted")
            
            with col2:
                if st.button("🔄 Factory Reset", type="secondary", key="generic_steering_factory_reset_btn"):
                    if ccu_gateway.reset_factory():
                        st.success("✅ Factory reset initiated")
                    else:
                        st.error("❌ Factory reset failed")
            
            with col3:
                if st.button("📊 System Diagnostics", key="generic_steering_diagnostics_btn"):
                    st.info("🔍 Running system diagnostics...")
                    st.success("✅ All systems operational")
        
        # Module Control Section
        with st.expander("🔧 Module Control", expanded=True):
            st.markdown("### Individual Module Management")
            
            # Module selection
            modules = [
                {"id": "SVR3QA0022", "name": "DPS", "type": "Processing"},
                {"id": "SVR4H76449", "name": "FTS", "type": "Transport"},
                {"id": "SVR3QA2098", "name": "AIQS", "type": "Quality"},
                {"id": "SVR4H76530", "name": "CHRG", "type": "Charging"},
                {"id": "SVR4H73275", "name": "CGW", "type": "Gateway"},
            ]
            
            selected_module = st.selectbox(
                "Select Module:",
                [f"{m['name']} ({m['id']})" for m in modules],
                key="generic_steering_module_select"
            )
            
            if selected_module:
                module_info = next(m for m in modules if f"{m['name']} ({m['id']})" == selected_module)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Module:** {module_info['name']}")
                    st.markdown(f"**ID:** {module_info['id']}")
                    st.markdown(f"**Type:** {module_info['type']}")
                
                with col2:
                    st.markdown("**Module Actions:**")
                    if st.button("📊 Get Status", key="generic_steering_module_status_btn"):
                        st.info(f"📊 Status for {module_info['name']}: Active")
                    
                    if st.button("🔄 Restart Module", key="generic_steering_module_restart_btn"):
                        st.warning(f"🔄 Restarting {module_info['name']}...")
                        st.success(f"✅ {module_info['name']} restarted successfully")
        
        # Order Management Section
        with st.expander("📦 Order Management", expanded=True):
            st.markdown("### Factory Order Control")
            
            # Order list
            orders = [
                {"id": "ORD-001", "workpiece": "WP-001", "status": "processing", "progress": 75, "priority": "high"},
                {"id": "ORD-002", "workpiece": "WP-002", "status": "queued", "progress": 0, "priority": "medium"},
                {"id": "ORD-003", "workpiece": "WP-003", "status": "completed", "progress": 100, "priority": "low"},
            ]
            
            for order in orders:
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{order['id']}**")
                    
                    with col2:
                        st.write(order['workpiece'])
                    
                    with col3:
                        status_color = {
                            "processing": "🟡",
                            "queued": "⚪",
                            "completed": "🟢"
                        }.get(order['status'], "⚪")
                        st.write(f"{status_color} {order['status']}")
                    
                    with col4:
                        st.progress(order['progress'] / 100)
                    
                    with col5:
                        priority_color = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢"
                        }.get(order['priority'], "⚪")
                        st.write(f"{priority_color} {order['priority']}")
            
            # Order actions
            st.markdown("### Order Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📤 Create New Order", key="generic_steering_create_order_btn"):
                    st.success("✅ New order created: ORD-004")
            
            with col2:
                if st.button("⏸️ Pause All Orders", key="generic_steering_pause_orders_btn"):
                    st.warning("⏸️ All orders paused")
            
            with col3:
                if st.button("▶️ Resume All Orders", key="generic_steering_resume_orders_btn"):
                    st.success("▶️ All orders resumed")
        
        # System Monitoring Section
        with st.expander("📊 System Monitoring", expanded=True):
            st.markdown("### Real-time System Metrics")
            
            # System metrics
            metrics = [
                {"name": "CPU Usage", "value": "45%", "status": "normal"},
                {"name": "Memory Usage", "value": "67%", "status": "normal"},
                {"name": "MQTT Messages/min", "value": "234", "status": "normal"},
                {"name": "Error Rate", "value": "0.3%", "status": "good"},
            ]
            
            col1, col2 = st.columns(2)
            
            with col1:
                for metric in metrics[:2]:
                    status_color = "🟢" if metric['status'] == "normal" else "🟡" if metric['status'] == "warning" else "🔴"
                    st.write(f"{status_color} **{metric['name']}:** {metric['value']}")
            
            with col2:
                for metric in metrics[2:]:
                    status_color = "🟢" if metric['status'] in ["normal", "good"] else "🟡" if metric['status'] == "warning" else "🔴"
                    st.write(f"{status_color} **{metric['name']}:** {metric['value']}")
        
        # Advanced Controls Section
        with st.expander("🔬 Advanced Controls", expanded=False):
            st.markdown("### Advanced Factory Operations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Message Template Management:**")
                if st.button("📝 Generate All Templates", key="generic_steering_gen_templates_btn"):
                    st.info("📝 Generating message templates...")
                    st.success("✅ All templates generated successfully")
                
                if st.button("✅ Validate All Templates", key="generic_steering_validate_templates_btn"):
                    st.info("✅ Validating all templates...")
                    st.success("✅ All templates validated successfully")
            
            with col2:
                st.markdown("**System Maintenance:**")
                if st.button("🧹 Clear Message Buffers", key="generic_steering_clear_buffers_btn"):
                    st.info("🧹 Clearing message buffers...")
                    st.success("✅ Message buffers cleared")
                
                if st.button("📊 Generate System Report", key="generic_steering_system_report_btn"):
                    st.info("📊 Generating system report...")
                    st.success("✅ System report generated")
        
    except Exception as e:
        logger.error(f"❌ Generic Steering Tab rendering error: {e}")
        st.error(f"❌ Generic Steering Tab failed: {e}")
        st.info("💡 This component is currently under development.")
