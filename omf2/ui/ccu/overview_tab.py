#!/usr/bin/env python3
"""
CCU Overview Tab - UI component for CCU dashboard
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from omf2.ccu import CCUGateway, ccu_mqtt_client
from omf2.ccu.workpiece_manager import get_workpiece_manager

logger = logging.getLogger(__name__)


class CCUOverviewTab:
    """
    CCU Overview Tab - Main dashboard for Central Control Unit
    """
    
    def __init__(self):
        self.workpiece_manager = get_workpiece_manager()
        self.ccu_gateway = CCUGateway(ccu_mqtt_client)
        logger.info("🏭 CCU Overview Tab initialized")
    
    def render(self):
        """Render the CCU overview tab"""
        if not STREAMLIT_AVAILABLE:
            logger.error("Streamlit not available for UI rendering")
            return
        
        st.header("🏭 CCU Dashboard")
        st.markdown("Central Control Unit monitoring and control")
        
        # Connection status
        self._render_connection_status()
        
        # Main dashboard layout
        col1, col2 = st.columns(2)
        
        with col1:
            self._render_system_status()
            self._render_workpiece_info()
        
        with col2:
            self._render_workflow_status()
            self._render_recent_activity()
    
    def _render_connection_status(self):
        """Render connection status indicator"""
        is_connected = self.ccu_gateway.is_connected()
        
        if is_connected:
            st.success("🟢 CCU MQTT Connected")
        else:
            st.error("🔴 CCU MQTT Disconnected")
            if st.button("🔄 Reconnect CCU"):
                self._reconnect_ccu()
    
    def _render_system_status(self):
        """Render system status section"""
        st.subheader("📊 System Status")
        
        # Get latest state
        latest_state = self.ccu_gateway.get_latest_state()
        
        if latest_state:
            status = latest_state.get("status", "unknown")
            timestamp = latest_state.get("timestamp", "")
            
            # Status indicator
            status_colors = {
                "running": "🟢",
                "idle": "🟡", 
                "error": "🔴",
                "maintenance": "🟠"
            }
            
            status_icon = status_colors.get(status, "❓")
            st.metric("Current Status", f"{status_icon} {status.title()}")
            
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    st.caption(f"Last updated: {dt.strftime('%H:%M:%S')}")
                except ValueError:
                    st.caption(f"Last updated: {timestamp}")
        else:
            st.info("No system status data available")
            if st.button("🔄 Request Status Update"):
                self._request_status_update()
    
    def _render_workpiece_info(self):
        """Render workpiece information section"""
        st.subheader("🔧 Workpiece Information")
        
        # Workpiece statistics
        stats = self.workpiece_manager.get_statistics()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Workpieces", stats.get("total_workpieces", 0))
        with col2:
            st.metric("NFC Codes", stats.get("total_nfc_codes", 0))
        with col3:
            st.metric("Colors", len(stats.get("colors", {})))
        
        # Color distribution
        colors = stats.get("colors", {})
        if colors:
            st.write("**Color Distribution:**")
            for color, count in colors.items():
                st.write(f"• {color.title()}: {count}")
    
    def _render_workflow_status(self):
        """Render workflow status section"""
        st.subheader("🔄 Workflow Status")
        
        # Sample workflow data (in real implementation, get from gateway)
        workflows = [
            {"id": "WF001", "status": "running", "progress": 75},
            {"id": "WF002", "status": "completed", "progress": 100},
            {"id": "WF003", "status": "pending", "progress": 0}
        ]
        
        for workflow in workflows:
            with st.expander(f"Workflow {workflow['id']} - {workflow['status'].title()}"):
                st.progress(workflow['progress'] / 100)
                st.write(f"Progress: {workflow['progress']}%")
                
                if workflow['status'] == 'running':
                    if st.button(f"⏸️ Pause {workflow['id']}", key=f"pause_{workflow['id']}"):
                        self._control_workflow(workflow['id'], "pause")
                elif workflow['status'] == 'pending':
                    if st.button(f"▶️ Start {workflow['id']}", key=f"start_{workflow['id']}"):
                        self._control_workflow(workflow['id'], "start")
    
    def _render_recent_activity(self):
        """Render recent activity section"""
        st.subheader("📋 Recent Activity")
        
        # Get recent status history
        status_history = self.ccu_gateway.get_status_history(limit=10)
        
        if status_history:
            for entry in status_history[-5:]:  # Show last 5 entries
                payload = entry.get("payload", {})
                timestamp = payload.get("timestamp", "")
                message = f"{payload.get('module', 'System')}: {payload.get('state', 'Unknown')}"
                
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime('%H:%M:%S')
                except (ValueError, AttributeError):
                    time_str = "Unknown"
                
                st.write(f"• `{time_str}` {message}")
        else:
            st.info("No recent activity")
    
    def _reconnect_ccu(self):
        """Reconnect CCU MQTT client"""
        try:
            ccu_mqtt_client.disconnect()
            if ccu_mqtt_client.connect():
                st.success("✅ CCU reconnected successfully")
            else:
                st.error("❌ Failed to reconnect CCU")
        except Exception as e:
            st.error(f"❌ Reconnection error: {e}")
            logger.error(f"CCU reconnection error: {e}")
    
    def _request_status_update(self):
        """Request system status update"""
        try:
            success = self.ccu_gateway.send_control_command(
                command="status_request",
                target="system",
                parameters={"type": "full_status"}
            )
            
            if success:
                st.success("✅ Status update requested")
            else:
                st.error("❌ Failed to request status update")
        except Exception as e:
            st.error(f"❌ Status request error: {e}")
            logger.error(f"Status request error: {e}")
    
    def _control_workflow(self, workflow_id: str, command: str):
        """Control workflow execution"""
        try:
            success = self.ccu_gateway.send_workflow_update(
                workflow_id=workflow_id,
                step="control",
                status=command,
                data={"command": command, "timestamp": datetime.now().isoformat()}
            )
            
            if success:
                st.success(f"✅ Workflow {workflow_id} {command} command sent")
            else:
                st.error(f"❌ Failed to {command} workflow {workflow_id}")
        except Exception as e:
            st.error(f"❌ Workflow control error: {e}")
            logger.error(f"Workflow control error: {e}")


def render_ccu_overview_tab():
    """Convenience function to render CCU overview tab"""
    tab = CCUOverviewTab()
    tab.render()