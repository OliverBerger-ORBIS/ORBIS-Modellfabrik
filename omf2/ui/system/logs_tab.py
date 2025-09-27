#!/usr/bin/env python3
"""
Logs Tab - UI component for system log management
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from omf2.system import LogManager
from omf2.system.logs import LogLevel, get_log_manager

logger = logging.getLogger(__name__)


class LogsTab:
    """
    Logs Tab - System log viewer and management interface
    """
    
    def __init__(self):
        self.log_manager = get_log_manager()
        logger.info("📝 Logs Tab initialized")
    
    def render(self):
        """Render the logs tab"""
        if not STREAMLIT_AVAILABLE:
            logger.error("Streamlit not available for UI rendering")
            return
        
        st.header("📝 System Logs")
        st.markdown("System log viewer and analysis")
        
        # Log management tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Recent Logs",
            "🔍 Search & Filter", 
            "📊 Statistics",
            "⚙️ Management"
        ])
        
        with tab1:
            self._render_recent_logs()
        
        with tab2:
            self._render_search_filter()
        
        with tab3:
            self._render_statistics()
        
        with tab4:
            self._render_management()
    
    def _render_recent_logs(self):
        """Render recent logs view"""
        st.subheader("📋 Recent System Logs")
        
        # Time range selector
        time_options = {
            "Last 15 minutes": 15,
            "Last 30 minutes": 30, 
            "Last 1 hour": 60,
            "Last 2 hours": 120,
            "Last 4 hours": 240,
            "Last 8 hours": 480
        }
        
        selected_time = st.selectbox(
            "Time Range",
            list(time_options.keys()),
            index=2  # Default to 1 hour
        )
        
        minutes = time_options[selected_time]
        
        # Level filter
        level_filter = st.multiselect(
            "Log Levels",
            [level.value for level in LogLevel],
            default=["INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        
        # Get logs
        recent_logs = self.log_manager.get_recent_logs(minutes=minutes, limit=200)
        
        # Filter by level
        if level_filter:
            filtered_logs = [log for log in recent_logs if log.level.value in level_filter]
        else:
            filtered_logs = recent_logs
        
        # Display logs
        if filtered_logs:
            st.write(f"**Found {len(filtered_logs)} log entries**")
            
            # Log entries
            for log_entry in reversed(filtered_logs[-50:]):  # Show last 50, newest first
                self._render_log_entry(log_entry)
        else:
            st.info("No logs found for the selected criteria")
    
    def _render_search_filter(self):
        """Render search and filter interface"""
        st.subheader("🔍 Search & Filter Logs")
        
        # Search form
        with st.form("log_search_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                search_query = st.text_input("Search Query", placeholder="Enter search terms...")
                component_filter = st.text_input("Component Filter", placeholder="e.g., ccu, nodered...")
            
            with col2:
                level_filter = st.selectbox(
                    "Log Level",
                    ["All"] + [level.value for level in LogLevel]
                )
                limit = st.number_input("Max Results", min_value=10, max_value=1000, value=100)
            
            search_submitted = st.form_submit_button("🔍 Search")
        
        if search_submitted:
            # Perform search
            if search_query:
                search_results = self.log_manager.search_logs(search_query, limit=limit)
            else:
                # Get logs with filters
                level_obj = None if level_filter == "All" else LogLevel(level_filter)
                search_results = self.log_manager.get_logs(
                    limit=limit,
                    level=level_obj,
                    component=component_filter if component_filter else None
                )
            
            # Display results
            if search_results:
                st.write(f"**Found {len(search_results)} matching entries**")
                
                # Export button
                if st.button("📄 Export Results"):
                    self._export_search_results(search_results)
                
                # Display log entries
                for log_entry in reversed(search_results):  # Newest first
                    self._render_log_entry(log_entry)
            else:
                st.info("No logs found matching your search criteria")
    
    def _render_statistics(self):
        """Render log statistics"""
        st.subheader("📊 Log Statistics")
        
        # Get statistics
        stats = self.log_manager.get_log_statistics()
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Entries", stats.get("total_entries", 0))
        
        with col2:
            error_count = stats.get("level_distribution", {}).get("ERROR", 0)
            critical_count = stats.get("level_distribution", {}).get("CRITICAL", 0)
            st.metric("Errors", error_count + critical_count)
        
        with col3:
            st.metric("Buffer Usage", stats.get("buffer_usage", "0/0"))
        
        with col4:
            component_count = len(stats.get("component_distribution", {}))
            st.metric("Components", component_count)
        
        # Level distribution chart
        level_dist = stats.get("level_distribution", {})
        if level_dist:
            st.write("**Log Level Distribution:**")
            
            # Create color mapping for levels
            level_colors = {
                "DEBUG": "#808080",
                "INFO": "#0066CC", 
                "WARNING": "#FF8C00",
                "ERROR": "#FF4444",
                "CRITICAL": "#CC0000"
            }
            
            for level, count in level_dist.items():
                color = level_colors.get(level, "#808080")
                percentage = (count / stats["total_entries"] * 100) if stats["total_entries"] > 0 else 0
                st.write(f"• **{level}**: {count} ({percentage:.1f}%)")
        
        # Component distribution
        component_dist = stats.get("component_distribution", {})
        if component_dist:
            st.write("**Component Distribution:**")
            
            # Sort by count, show top 10
            sorted_components = sorted(component_dist.items(), key=lambda x: x[1], reverse=True)[:10]
            
            for component, count in sorted_components:
                percentage = (count / stats["total_entries"] * 100) if stats["total_entries"] > 0 else 0
                st.write(f"• **{component}**: {count} ({percentage:.1f}%)")
        
        # Recent error summary
        st.write("**Recent Errors:**")
        error_logs = self.log_manager.get_error_logs(limit=10)
        
        if error_logs:
            for log_entry in error_logs:
                with st.expander(f"🔴 {log_entry.component} - {log_entry.timestamp.strftime('%H:%M:%S')}"):
                    st.write(f"**Level:** {log_entry.level.value}")
                    st.write(f"**Message:** {log_entry.message}")
                    if log_entry.context:
                        st.write(f"**Context:** {log_entry.context}")
        else:
            st.info("No recent errors")
    
    def _render_management(self):
        """Render log management interface"""
        st.subheader("⚙️ Log Management")
        
        # Log generation (for testing)
        st.write("**Generate Test Logs:**")
        col1, col2 = st.columns(2)
        
        with col1:
            test_component = st.text_input("Component", value="test_component")
            test_level = st.selectbox("Level", [level.value for level in LogLevel])
        
        with col2:
            test_message = st.text_input("Message", value="Test log message")
            
            if st.button("➕ Generate Log"):
                level_obj = LogLevel(test_level)
                self.log_manager.add_log_entry(level_obj, test_component, test_message)
                st.success("✅ Test log generated")
        
        st.divider()
        
        # Clear logs
        st.write("**Clear Logs:**")
        st.warning("⚠️ This action cannot be undone!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            clear_component = st.text_input("Component (optional)", placeholder="Leave empty to clear all")
        
        with col2:
            if st.button("🗑️ Clear Logs", type="secondary"):
                if clear_component:
                    self.log_manager.clear_logs(component=clear_component)
                    st.success(f"✅ Logs cleared for component: {clear_component}")
                else:
                    self.log_manager.clear_logs()
                    st.success("✅ All logs cleared")
        
        st.divider()
        
        # Export logs
        st.write("**Export Logs:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_level = st.selectbox(
                "Export Level",
                ["All"] + [level.value for level in LogLevel],
                key="export_level"
            )
            export_component = st.text_input("Export Component (optional)", key="export_component")
        
        with col2:
            export_hours = st.number_input("Hours back", min_value=1, max_value=168, value=24)
            
            if st.button("📄 Export Logs"):
                self._export_logs(export_level, export_component, export_hours)
    
    def _render_log_entry(self, log_entry):
        """Render a single log entry"""
        # Color coding for levels
        level_colors = {
            "DEBUG": "🔍",
            "INFO": "ℹ️",
            "WARNING": "⚠️", 
            "ERROR": "❌",
            "CRITICAL": "🚨"
        }
        
        level_icon = level_colors.get(log_entry.level.value, "📝")
        time_str = log_entry.timestamp.strftime("%H:%M:%S")
        
        # Create expandable log entry
        summary = f"{level_icon} `{time_str}` **{log_entry.component}** - {log_entry.message[:100]}..."
        
        with st.expander(summary):
            st.write(f"**Timestamp:** {log_entry.timestamp.isoformat()}")
            st.write(f"**Level:** {log_entry.level.value}")
            st.write(f"**Component:** {log_entry.component}")
            st.write(f"**Message:** {log_entry.message}")
            
            if log_entry.context:
                st.write("**Context:**")
                st.json(log_entry.context)
    
    def _export_search_results(self, results):
        """Export search results"""
        try:
            from pathlib import Path
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                export_path = Path(f.name)
            
            # Create export data
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "search_results": True,
                "entries": [entry.to_dict() for entry in results]
            }
            
            import json
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            st.success(f"✅ Search results exported to: {export_path}")
            
        except Exception as e:
            st.error(f"❌ Export failed: {e}")
            logger.error(f"Log export error: {e}")
    
    def _export_logs(self, level_filter: str, component_filter: str, hours_back: int):
        """Export logs with filters"""
        try:
            from pathlib import Path
            import tempfile
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                export_path = Path(f.name)
            
            # Apply filters
            level_obj = None if level_filter == "All" else LogLevel(level_filter)
            component = component_filter if component_filter else None
            since = datetime.now() - timedelta(hours=hours_back)
            
            # Export
            if self.log_manager.export_logs(export_path, level=level_obj, component=component, since=since):
                st.success(f"✅ Logs exported to: {export_path}")
            else:
                st.error("❌ Export failed")
            
        except Exception as e:
            st.error(f"❌ Export failed: {e}")
            logger.error(f"Log export error: {e}")


def render_logs_tab():
    """Convenience function to render logs tab"""
    tab = LogsTab()
    tab.render()