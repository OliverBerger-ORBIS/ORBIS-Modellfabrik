"""
Session Analyse Komponente
Analyse einer ausgewählten Session (aps_persistent_traffic)
"""

import streamlit as st

def show_session_analysis():
    """Session Analyse Tab"""
    
    st.header("📊 Session Analyse")
    st.markdown("Analyse einer ausgewählten Session")
    
    st.info("🚧 **In Entwicklung** - Diese Funktion wird in Phase 2 implementiert")
    
    # Placeholder content
    st.subheader("Geplante Features:")
    st.markdown("""
    - Session-Auswahl aus Database
    - Timeline-Visualisierung
    - Message-Statistiken
    - Topic-Filterung
    - Export-Funktionen
    """)
    
    # Mock data for demonstration
    if st.button("📊 Demo-Daten anzeigen"):
        st.subheader("Demo Session Data")
        
        # Mock session data
        session_data = {
            "session_id": "demo_session_001",
            "start_time": "2024-01-15 10:30:00",
            "end_time": "2024-01-15 11:45:00",
            "duration": "1h 15m",
            "message_count": 156,
            "topics": [
                "ccu/state/status",
                "module/v1/ff/SVR3QA0022/state",
                "module/v1/ff/SVR3QA0022/order"
            ]
        }
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Session ID", session_data["session_id"])
            st.metric("Dauer", session_data["duration"])
        
        with col2:
            st.metric("Start", session_data["start_time"])
            st.metric("Nachrichten", session_data["message_count"])
        
        with col3:
            st.metric("Ende", session_data["end_time"])
            st.metric("Topics", len(session_data["topics"]))
        
        st.subheader("Topics in dieser Session:")
        for topic in session_data["topics"]:
            st.code(topic)
