"""
Interactive Factory Grid - Streamlit Application
=================================================

This Streamlit app demonstrates an interactive factory/shopfloor grid with
click and double-click event handling using streamlit-bokeh-events.

Features:
- 3x4 grid layout with special cells at positions (0,0) and (0,3)
- Interactive hover, click, and double-click events
- Single-click: Select and highlight a module
- Double-click: Show detail panel and navigation
- Event data: {type: 'module-click'|'module-dblclick', id: '<module-id>'}

Usage:
    streamlit run streamlit_factory_app.py
"""

import streamlit as st
from streamlit_bokeh_events import streamlit_bokeh_events
from bokeh.models import CustomJS
from bokeh.plotting import figure
from pathlib import Path
import json

# Page configuration
st.set_page_config(
    page_title="Factory Grid - Interactive Shopfloor",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    
    .stAlert {
        border-radius: 8px;
    }
    
    .module-detail {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    .event-info {
        font-family: 'Courier New', monospace;
        background: #f9f9f9;
        padding: 10px;
        border-radius: 4px;
        border-left: 4px solid #0066cc;
    }
    
    .selected-module {
        background: #4CAF50;
        color: white;
        padding: 10px 15px;
        border-radius: 4px;
        font-weight: bold;
        display: inline-block;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_module' not in st.session_state:
    st.session_state.selected_module = None
if 'show_detail' not in st.session_state:
    st.session_state.show_detail = False
if 'event_history' not in st.session_state:
    st.session_state.event_history = []
if 'detail_module' not in st.session_state:
    st.session_state.detail_module = None

# Title and description
st.title("🏭 Interactive Factory Grid")
st.markdown("""
This demo shows an interactive factory/shopfloor grid with event handling:
- **Single-click**: Select and highlight a module
- **Double-click**: Show detailed information panel
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    show_debug = st.checkbox("Show Debug Info", value=False)
    show_event_log = st.checkbox("Show Event Log", value=True)
    
    st.markdown("---")
    st.header("📊 Current State")
    
    if st.session_state.selected_module:
        st.success(f"Selected: **{st.session_state.selected_module}**")
    else:
        st.info("No module selected")
    
    if st.session_state.show_detail:
        st.warning(f"Detail view: **{st.session_state.detail_module}**")
    
    st.markdown("---")
    if st.button("🔄 Reset State"):
        st.session_state.selected_module = None
        st.session_state.show_detail = False
        st.session_state.event_history = []
        st.session_state.detail_module = None
        st.rerun()

# Load and display the HTML grid
html_file_path = Path(__file__).parent / "factory_grid.html"

if not html_file_path.exists():
    st.error(f"Error: factory_grid.html not found at {html_file_path}")
    st.info("Please ensure factory_grid.html is in the same directory as this script.")
    st.stop()

# Read the HTML content
with open(html_file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Create a minimal Bokeh figure (needed for streamlit-bokeh-events)
# This is just a placeholder - the actual interaction happens in the HTML
plot = figure(width=1, height=1, toolbar_location=None)

# JavaScript to listen for custom events from the iframe
js_code = """
// Listen for messages from the HTML content
let eventData = null;

// Set up message listener for postMessage events
window.addEventListener('message', function(event) {
    if (event.data && (event.data.type === 'module-click' || event.data.type === 'module-dblclick')) {
        eventData = event.data;
        // Trigger Bokeh event
        document.dispatchEvent(new CustomEvent("GET_FACTORY_EVENT", {detail: eventData}));
    }
});

// Also listen for direct custom events
window.addEventListener('factoryEvent', function(event) {
    if (event.detail) {
        eventData = event.detail;
        // Trigger Bokeh event
        document.dispatchEvent(new CustomEvent("GET_FACTORY_EVENT", {detail: eventData}));
    }
});
"""

# Create a CustomJS callback that will capture the events
callback = CustomJS(code=js_code)

# Display the factory grid in columns
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Factory Grid Layout")
    
    # Display the HTML with iframe
    st.components.v1.html(html_content, height=700, scrolling=False)

with col2:
    st.markdown("### Control Panel")
    
    # Listen for events from the Bokeh component
    try:
        event_result = streamlit_bokeh_events(
            bokeh_plot=plot,
            events="GET_FACTORY_EVENT",
            key="factory_events",
            refresh_on_update=True,
            debounce_time=100
        )
        
        if event_result and "GET_FACTORY_EVENT" in event_result:
            event_data = event_result["GET_FACTORY_EVENT"]
            
            if event_data:
                event_type = event_data.get('type', '')
                module_id = event_data.get('id', '')
                timestamp = event_data.get('timestamp', '')
                
                # Handle single-click events
                if event_type == 'module-click':
                    st.session_state.selected_module = module_id
                    st.session_state.event_history.append({
                        'type': 'click',
                        'module': module_id,
                        'timestamp': timestamp
                    })
                    st.rerun()
                
                # Handle double-click events
                elif event_type == 'module-dblclick':
                    st.session_state.detail_module = module_id
                    st.session_state.show_detail = True
                    st.session_state.event_history.append({
                        'type': 'dblclick',
                        'module': module_id,
                        'timestamp': timestamp
                    })
                    st.rerun()
    except Exception as e:
        st.warning(f"Note: streamlit-bokeh-events integration pending. Error: {str(e)}")
        st.info("The grid is interactive, but event capture requires streamlit-bokeh-events to be properly installed.")

    # Display selected module info
    if st.session_state.selected_module:
        st.markdown(f"""
        <div class="selected-module">
            📦 Selected: {st.session_state.selected_module}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Actions:**")
        if st.button("📋 View Details"):
            st.session_state.detail_module = st.session_state.selected_module
            st.session_state.show_detail = True
            st.rerun()
        
        if st.button("🗑️ Clear Selection"):
            st.session_state.selected_module = None
            st.rerun()

# Detail panel (shown when double-click or detail button is pressed)
if st.session_state.show_detail and st.session_state.detail_module:
    st.markdown("---")
    st.markdown("### 📊 Module Detail Panel")
    
    with st.container():
        st.markdown(f"""
        <div class="module-detail">
            <h3>Module: {st.session_state.detail_module}</h3>
            <p><strong>Type:</strong> Production Module</p>
            <p><strong>Status:</strong> Active</p>
            <p><strong>Location:</strong> Grid Position {st.session_state.detail_module}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Example: Navigation to different views
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 Performance View"):
                st.info(f"Navigate to performance metrics for {st.session_state.detail_module}")
        
        with col2:
            if st.button("🔧 Maintenance View"):
                st.info(f"Navigate to maintenance schedule for {st.session_state.detail_module}")
        
        with col3:
            if st.button("📦 Inventory View"):
                st.info(f"Navigate to inventory status for {st.session_state.detail_module}")
        
        # Example: Drill-down data
        with st.expander("🔍 Detailed Information", expanded=True):
            st.markdown("""
            **Module Configuration:**
            - Capacity: 100 units/hour
            - Efficiency: 95%
            - Uptime: 99.2%
            - Last Maintenance: 2025-10-10
            
            **Current Operation:**
            - Task: Assembly
            - Progress: 75%
            - ETA: 15 minutes
            """)
        
        if st.button("❌ Close Detail Panel"):
            st.session_state.show_detail = False
            st.session_state.detail_module = None
            st.rerun()

# Event log section
if show_event_log and st.session_state.event_history:
    st.markdown("---")
    st.markdown("### 📝 Event History")
    
    # Show last 10 events
    recent_events = st.session_state.event_history[-10:]
    
    for i, event in enumerate(reversed(recent_events)):
        event_type = event['type']
        module_id = event['module']
        timestamp = event['timestamp']
        
        icon = "🖱️" if event_type == "click" else "🖱️🖱️"
        color = "#0066cc" if event_type == "click" else "#cc6600"
        
        st.markdown(f"""
        <div class="event-info" style="border-left-color: {color};">
            {icon} <strong>{event_type.upper()}</strong>: Module {module_id}<br>
            <small>Time: {timestamp}</small>
        </div>
        """, unsafe_allow_html=True)

# Debug information
if show_debug:
    st.markdown("---")
    st.markdown("### 🐛 Debug Information")
    
    debug_info = {
        "Selected Module": st.session_state.selected_module,
        "Show Detail": st.session_state.show_detail,
        "Detail Module": st.session_state.detail_module,
        "Event Count": len(st.session_state.event_history),
        "Session State Keys": list(st.session_state.keys())
    }
    
    st.json(debug_info)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>Interactive Factory Grid Demo | Built with Streamlit & Bokeh Events</p>
    <p>Single-click to select | Double-click for details</p>
</div>
""", unsafe_allow_html=True)
