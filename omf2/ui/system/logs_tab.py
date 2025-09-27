"""
Logs Tab Component
Displays system logs with filtering and real-time updates
"""

import streamlit as st
import logging
from datetime import datetime
from omf2.common.i18n import translate, get_current_language


def show_logs_tab(logger: logging.Logger):
    """
    Zeigt den Logs Tab mit Live-Log-Anzeige
    
    Args:
        logger: Logger instance für diese Komponente
    """
    logger.info("Logs Tab geöffnet")
    
    current_lang = get_current_language()
    
    st.header(f"📋 {translate('logs_title', current_lang)}")
    
    # Log-Controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        log_level = st.selectbox(
            translate('log_level', current_lang),
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1
        )
        
    with col2:
        auto_refresh = st.checkbox("Auto-Refresh", value=True)
        
    with col3:
        if st.button(f"🔄 {translate('refresh_logs', current_lang)}"):
            logger.info("Logs manuell aktualisiert")
            st.rerun()
            
    with col4:
        if st.button(f"🗑️ {translate('clear_logs', current_lang)}"):
            logger.info("Logs gelöscht")
            if "log_messages" in st.session_state:
                st.session_state.log_messages = []
            st.success("✅ Logs gelöscht")
    
    # Log-Container
    log_container = st.container()
    
    with log_container:
        # Simulierte Log-Nachrichten (in echter Implementierung würde hier der RingBuffer verwendet)
        if "log_messages" not in st.session_state:
            st.session_state.log_messages = _generate_sample_logs()
        
        # Filter anwenden
        filtered_logs = [
            log for log in st.session_state.log_messages 
            if _should_show_log(log, log_level)
        ]
        
        # Logs anzeigen
        st.write(f"### {translate('logs', current_lang)} ({len(filtered_logs)} Einträge)")
        
        # Log-Ausgabe in scrollbarem Container
        with st.container():
            if filtered_logs:
                log_text = "\n".join(filtered_logs[-50:])  # Nur letzte 50 Logs anzeigen
                st.code(log_text, language="text")
            else:
                st.info("📋 Keine Logs verfügbar")
    
    # Live-Logs hinzufügen (Simulation)
    if auto_refresh:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_log = f"[{current_time}] [INFO] omf_dashboard: Live-Update - Tab aktiv"
        
        if "log_messages" in st.session_state:
            if new_log not in st.session_state.log_messages:
                st.session_state.log_messages.append(new_log)
                
        # Auto-refresh nach 5 Sekunden
        st.rerun()


def _generate_sample_logs():
    """Generiert Beispiel-Log-Nachrichten"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return [
        f"[{current_time}] [INFO] omf_dashboard: 🚀 OMF Dashboard gestartet",
        f"[{current_time}] [INFO] omf_dashboard: Settings Tab geöffnet",
        f"[{current_time}] [INFO] omf_dashboard: Workpiece Subtab geöffnet", 
        f"[{current_time}] [INFO] omf_dashboard: Logs Tab geöffnet",
        f"[{current_time}] [DEBUG] omf.dashboard.tools.logging_config: Logging-System initialisiert",
        f"[{current_time}] [WARNING] omf.dashboard: Beispiel-Warnung für Demo",
        f"[{current_time}] [INFO] omf_dashboard: Message Center Tab geöffnet",
        f"[{current_time}] [DEBUG] omf.dashboard.tools.mqtt_gateway: MQTT-Verbindung hergestellt",
        f"[{current_time}] [INFO] omf.dashboard.components: Komponenten erfolgreich geladen",
        f"[{current_time}] [ERROR] omf.dashboard: Beispiel-Fehler für Demo (ungefährlich)"
    ]


def _should_show_log(log_message: str, min_level: str):
    """Prüft, ob eine Log-Nachricht angezeigt werden soll basierend auf Level"""
    level_order = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
    min_level_num = level_order.get(min_level, 1)
    
    # Extrahiere Log-Level aus der Nachricht
    for level in level_order.keys():
        if f"[{level}]" in log_message:
            log_level_num = level_order[level]
            return log_level_num >= min_level_num
    
    return True  # Falls kein Level erkannt wird, zeige Log an