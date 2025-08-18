"""
UI Components for the APS Dashboard
"""
import streamlit as st
from datetime import datetime, timedelta

def create_filters(df):
    """Create filters for APS analysis"""
    st.subheader("🔍 Filter")

    # Initialize filter states
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = 'Alle'
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
        # Date range filter
        if not df.empty:
            min_date = df['date'].min()
            max_date = df['date'].max()
            default_date = st.session_state.selected_date if st.session_state.selected_date else max_date
            selected_date = st.date_input(
                "Datum",
                value=default_date,
                min_value=min_date,
                max_value=max_date
            )
            st.session_state.selected_date = selected_date
            df_filtered = df[df['date'] == selected_date]

        # Session filter
        sessions = ['Alle'] + list(df['session_label'].unique())
        selected_session = st.selectbox("Session", sessions, index=0 if st.session_state.selected_session == 'Alle' else sessions.index(st.session_state.selected_session) if st.session_state.selected_session in sessions else 0)
        st.session_state.selected_session = selected_session
        if selected_session != 'Alle':
            df_filtered = df_filtered[df_filtered['session_label'] == selected_session]

        # Process filter
        processes = ['Alle'] + list(df['process_label'].unique())
        selected_process = st.selectbox("Prozess", processes, index=0 if st.session_state.selected_process == 'Alle' else processes.index(st.session_state.selected_process) if st.session_state.selected_process in processes else 0)
        st.session_state.selected_process = selected_process
        if selected_process != 'Alle':
            df_filtered = df_filtered[df_filtered['process_label'] == selected_process]

    with col2:
        # Module filter
        modules = ['Alle'] + list(df['module_type'].unique())
        selected_module = st.selectbox("Modul", modules, index=0 if st.session_state.selected_module == 'Alle' else modules.index(st.session_state.selected_module) if st.session_state.selected_module in modules else 0)
        st.session_state.selected_module = selected_module
        if selected_module != 'Alle':
            df_filtered = df_filtered[df_filtered['module_type'] == selected_module]

        # Status filter
        statuses = ['Alle'] + list(df['status'].unique())
        selected_status = st.selectbox("Status", statuses, index=0 if st.session_state.selected_status == 'Alle' else statuses.index(st.session_state.selected_status) if st.session_state.selected_status in statuses else 0)
        st.session_state.selected_status = selected_status
        if selected_status != 'Alle':
            df_filtered = df_filtered[df_filtered['status'] == selected_status]

        # Topic filter
        topics = ['Alle'] + list(df['topic'].unique())
        selected_topic = st.selectbox("Topic", topics, index=0 if st.session_state.selected_topic == 'Alle' else topics.index(st.session_state.selected_topic) if st.session_state.selected_topic in topics else 0)
        st.session_state.selected_topic = selected_topic
        if selected_topic != 'Alle':
            df_filtered = df_filtered[df_filtered['topic'] == selected_topic]

    # Filter reset button
    if st.button("🔄 Filter zurücksetzen"):
        st.session_state.selected_date = None
        st.session_state.selected_session = 'Alle'
        st.session_state.selected_process = 'Alle'
        st.session_state.selected_module = 'Alle'
        st.session_state.selected_status = 'Alle'
        st.session_state.selected_topic = 'Alle'
        st.rerun()
    
    st.markdown(f"**Gefilterte Nachrichten:** {len(df_filtered):,}")
    if len(df_filtered) == 0:
        st.warning("⚠️ Keine Nachrichten mit den gewählten Filtern gefunden!")
        st.info("💡 Tipp: Versuche andere Filter-Kombinationen oder aktiviere den Verbose-Modus")
    
    return df_filtered
