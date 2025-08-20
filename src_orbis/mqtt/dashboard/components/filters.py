"""
UI Components for the APS Dashboard
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from ..config.topic_mapping import get_friendly_topic_name
from ..config.icon_config import get_module_icon

def create_filters(df, single_session_mode=False):
    """
    Create filters for APS analysis
    
    Args:
        df: DataFrame with MQTT data
        single_session_mode: If True, session filter is hidden and time slider is used
    """
    st.subheader("🔍 Filter")

    # Initialize filter states
    if 'selected_time_range' not in st.session_state:
        st.session_state.selected_time_range = None
    if 'selected_process' not in st.session_state:
        st.session_state.selected_process = 'Alle'
    if 'selected_module' not in st.session_state:
        st.session_state.selected_module = 'Alle'
    if 'selected_status' not in st.session_state:
        st.session_state.selected_status = 'Alle'
    if 'selected_topic' not in st.session_state:
        st.session_state.selected_topic = 'Alle'

    col1, col2 = st.columns(2)
    df_filtered = df

    with col1:
        # Time range filter (replaces date picker)
        if not df.empty and single_session_mode:
            # Convert timestamp to datetime if needed
            if 'timestamp' in df.columns:
                # More robust timestamp parsing - treat as local time without timezone conversion
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                
                # Remove any invalid timestamps
                df_valid = df.dropna(subset=['timestamp'])
                
                if len(df_valid) > 0:
                    min_time = df_valid['timestamp'].min()
                    max_time = df_valid['timestamp'].max()
                else:
                    st.error("❌ Keine gültigen Zeitstempel in den Daten gefunden")
                    return df
                
                # Ensure we have valid timestamps and min < max
                if (pd.notna(min_time) and pd.notna(max_time) and 
                    min_time < max_time and 
                    min_time.year > 2000 and max_time.year > 2000):  # Basic sanity check
                    # Check if time range is too small (less than 1 second)
                    time_diff = max_time - min_time
                    if time_diff.total_seconds() < 1:
                        st.info(f"ℹ️ Zeitbereich zu klein für Slider ({time_diff.total_seconds():.3f}s). Verwende gesamten Bereich.")
                        df_filtered = df
                        return df_filtered
                    else:
                        # Convert pandas timestamps to Python datetime objects for Streamlit slider
                        # Create clean datetime objects without microseconds to avoid Streamlit interpretation issues
                        min_time_dt = datetime(
                            min_time.year, min_time.month, min_time.day,
                            min_time.hour, min_time.minute, min_time.second
                        )
                        max_time_dt = datetime(
                            max_time.year, max_time.month, max_time.day,
                            max_time.hour, max_time.minute, max_time.second
                        )
                        
                        # Ensure we have valid datetime objects and reasonable time range
                        if (min_time_dt and max_time_dt and 
                            min_time_dt < max_time_dt and 
                            min_time_dt.year > 2000 and max_time_dt.year > 2000):
                            
                            # Calculate time range in seconds for numeric slider
                            min_seconds = min_time_dt.hour * 3600 + min_time_dt.minute * 60 + min_time_dt.second
                            max_seconds = max_time_dt.hour * 3600 + max_time_dt.minute * 60 + max_time_dt.second
                            
                            # Calculate relative seconds (starting from 0)
                            total_duration = max_seconds - min_seconds
                            
                            # Create numeric time slider with relative seconds
                            time_range_relative = st.slider(
                                "⏰ Zeitbereich",
                                min_value=0,
                                max_value=total_duration,
                                value=(0, total_duration)
                            )
                            
                            # Convert relative seconds back to absolute seconds
                            start_relative, end_relative = time_range_relative
                            time_range_seconds = (min_seconds + start_relative, min_seconds + end_relative)
                            
                            # Convert back to datetime objects
                            start_seconds, end_seconds = time_range_seconds
                            start_hour = start_seconds // 3600
                            start_minute = (start_seconds % 3600) // 60
                            start_second = start_seconds % 60
                            end_hour = end_seconds // 3600
                            end_minute = (end_seconds % 3600) // 60
                            end_second = end_seconds % 60
                            
                            time_range = (
                                datetime(min_time_dt.year, min_time_dt.month, min_time_dt.day, start_hour, start_minute, start_second),
                                datetime(max_time_dt.year, max_time_dt.month, max_time_dt.day, end_hour, end_minute, end_second)
                            )
                            
                            # Show the actual time range as text
                            st.write(f"**Zeitbereich:** {time_range[0].strftime('%H:%M:%S')} - {time_range[1].strftime('%H:%M:%S')}")
                            
                            # Store the time range in session state for debugging
                            st.session_state.debug_time_range = {
                                'min': min_time_dt.strftime('%H:%M:%S'),
                                'max': max_time_dt.strftime('%H:%M:%S'),
                                'selected': (time_range[0].strftime('%H:%M:%S'), time_range[1].strftime('%H:%M:%S'))
                            }
                        else:
                            st.error("❌ Ungültige Zeitstempel für Slider")
                            df_filtered = df
                            return df_filtered
                        
                        st.session_state.selected_time_range = time_range
                        
                        # Filter by time range
                        df_filtered = df[
                            (df['timestamp'] >= time_range[0]) & 
                            (df['timestamp'] <= time_range[1])
                        ]
                else:
                    st.warning("⚠️ Ungültige Zeitstempel in den Daten gefunden")
                    df_filtered = df
        
        # Session filter (only show if not in single session mode)
        if not single_session_mode:
            sessions = ['Alle'] + sorted(list(df['session_label'].unique()))
            selected_session = st.selectbox(
                "📁 Session", 
                sessions, 
                index=0 if st.session_state.get('selected_session', 'Alle') == 'Alle' 
                else sessions.index(st.session_state.get('selected_session', 'Alle')) 
                if st.session_state.get('selected_session', 'Alle') in sessions else 0
            )
            st.session_state.selected_session = selected_session
            if selected_session != 'Alle':
                df_filtered = df_filtered[df_filtered['session_label'] == selected_session]

        # Process filter (alphabetically sorted)
        processes = ['Alle'] + sorted(list(df['process_label'].unique()))
        selected_process = st.selectbox(
            "🔄 Prozess", 
            processes, 
            index=0 if st.session_state.selected_process == 'Alle' 
            else processes.index(st.session_state.selected_process) 
            if st.session_state.selected_process in processes else 0
        )
        st.session_state.selected_process = selected_process
        if selected_process != 'Alle':
            df_filtered = df_filtered[df_filtered['process_label'] == selected_process]

    with col2:
        # Module filter with icons (alphabetically sorted)
        modules = ['Alle'] + sorted(list(df['module_type'].unique()))
        
        # Create module options with icons
        module_options = ['Alle']
        for module in sorted(df['module_type'].unique()):
            icon = get_module_icon(module)
            module_options.append(f"{icon} {module}")
        
        selected_module_index = st.selectbox(
            "🏭 Modul", 
            module_options, 
            index=0 if st.session_state.selected_module == 'Alle' 
            else module_options.index(f"{get_module_icon(st.session_state.selected_module)} {st.session_state.selected_module}") 
            if st.session_state.selected_module in modules else 0
        )
        
        # Extract module name from selection
        if selected_module_index == 'Alle':
            selected_module = 'Alle'
        else:
            selected_module = selected_module_index.split(' ', 1)[1]  # Remove icon
        
        st.session_state.selected_module = selected_module
        if selected_module != 'Alle':
            df_filtered = df_filtered[df_filtered['module_type'] == selected_module]

        # Status filter (alphabetically sorted)
        statuses = ['Alle'] + sorted(list(df['status'].unique()))
        selected_status = st.selectbox(
            "📊 Status", 
            statuses, 
            index=0 if st.session_state.selected_status == 'Alle' 
            else statuses.index(st.session_state.selected_status) 
            if st.session_state.selected_status in statuses else 0
        )
        st.session_state.selected_status = selected_status
        if selected_status != 'Alle':
            df_filtered = df_filtered[df_filtered['status'] == selected_status]

        # Topic filter with friendly names (alphabetically sorted)
        topics = list(df['topic'].unique())
        friendly_topics = {}
        
        # Create friendly topic mappings
        for topic in topics:
            friendly_name = get_friendly_topic_name(topic)
            friendly_topics[friendly_name] = topic
        
        # Sort friendly names alphabetically
        sorted_friendly_names = ['Alle'] + sorted(friendly_topics.keys())
        
        selected_friendly_topic = st.selectbox(
            "📡 Topic", 
            sorted_friendly_names, 
            index=0 if st.session_state.selected_topic == 'Alle' 
            else sorted_friendly_names.index(get_friendly_topic_name(st.session_state.selected_topic)) 
            if st.session_state.selected_topic in topics else 0
        )
        
        # Map back to original topic
        if selected_friendly_topic == 'Alle':
            selected_topic = 'Alle'
        else:
            selected_topic = friendly_topics[selected_friendly_topic]
        
        st.session_state.selected_topic = selected_topic
        if selected_topic != 'Alle':
            df_filtered = df_filtered[df_filtered['topic'] == selected_topic]

    # Filter reset button
    if st.button("🔄 Filter zurücksetzen"):
        st.session_state.selected_time_range = None
        if not single_session_mode:
            st.session_state.selected_session = 'Alle'
        st.session_state.selected_process = 'Alle'
        st.session_state.selected_module = 'Alle'
        st.session_state.selected_status = 'Alle'
        st.session_state.selected_topic = 'Alle'
        st.rerun()
    
    # Show filter summary
    st.markdown(f"**Gefilterte Nachrichten:** {len(df_filtered):,}")
    
    if len(df_filtered) == 0:
        st.warning("⚠️ Keine Nachrichten mit den gewählten Filtern gefunden!")
        st.info("💡 Tipp: Versuche andere Filter-Kombinationen oder aktiviere den Verbose-Modus")
    
    return df_filtered
