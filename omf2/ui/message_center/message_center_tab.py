"""
Message Center Tab Component
Provides messaging interface and communication center
"""

import streamlit as st
import logging
from datetime import datetime
from omf2.common.i18n import translate, get_current_language


def show_message_center_tab(logger: logging.Logger):
    """
    Zeigt den Message Center Tab
    
    Args:
        logger: Logger instance für diese Komponente
    """
    logger.info("Message Center Tab geöffnet")
    
    current_lang = get_current_language()
    
    st.header(f"💬 {translate('message_center_title', current_lang)}")
    
    # Message Center Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📨 {translate('messages', current_lang)}")
        
        # Message-Liste
        if "messages" not in st.session_state:
            st.session_state.messages = _get_sample_messages()
        
        # Messages anzeigen
        message_container = st.container()
        
        with message_container:
            if st.session_state.messages:
                for i, message in enumerate(reversed(st.session_state.messages[-10:])):  # Letzte 10 Messages
                    with st.expander(f"{message['icon']} {message['title']} - {message['timestamp']}"):
                        st.write(f"**Von:** {message['sender']}")
                        st.write(f"**Typ:** {message['type']}")
                        st.write(f"**Nachricht:** {message['content']}")
                        
                        # Aktionsbuttons für Nachrichten
                        col_reply, col_archive = st.columns(2)
                        with col_reply:
                            if st.button(f"↩️ Antworten", key=f"reply_{i}"):
                                logger.info(f"Antwort auf Nachricht: {message['title']}")
                                st.info("📧 Antwort wird vorbereitet...")
                        with col_archive:
                            if st.button(f"🗃️ Archivieren", key=f"archive_{i}"):
                                logger.info(f"Nachricht archiviert: {message['title']}")
                                st.success("✅ Nachricht archiviert!")
            else:
                st.info("📭 Keine Nachrichten vorhanden")
    
    with col2:
        st.subheader("✉️ Neue Nachricht")
        
        # Nachricht senden Interface
        with st.form("send_message_form", clear_on_submit=True):
            recipient = st.selectbox(
                "Empfänger:",
                ["Operator", "Supervisor", "Admin", "System"]
            )
            
            message_type = st.selectbox(
                "Typ:",
                ["Info", "Warnung", "Fehler", "Anfrage"]
            )
            
            subject = st.text_input("Betreff:")
            message_content = st.text_area("Nachricht:", height=100)
            
            priority = st.selectbox(
                "Priorität:",
                ["Niedrig", "Normal", "Hoch", "Kritisch"]
            )
            
            if st.form_submit_button(f"📤 {translate('send_message', current_lang)}"):
                if subject and message_content:
                    new_message = {
                        "title": subject,
                        "content": message_content,
                        "sender": "Dashboard User",
                        "recipient": recipient,
                        "type": message_type,
                        "priority": priority,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "icon": _get_message_icon(message_type)
                    }
                    
                    st.session_state.messages.append(new_message)
                    logger.info(f"Neue Nachricht gesendet: {subject}")
                    st.success("✅ Nachricht erfolgreich gesendet!")
                    st.rerun()
                else:
                    st.error("❌ Bitte füllen Sie alle Felder aus")
        
        # Message Statistics
        st.subheader("📊 Statistiken")
        
        total_messages = len(st.session_state.messages)
        unread_messages = sum(1 for msg in st.session_state.messages if msg.get("unread", True))
        
        col_total, col_unread = st.columns(2)
        with col_total:
            st.metric("Gesamt", total_messages)
        with col_unread:
            st.metric("Ungelesen", unread_messages)
        
        # Quick Actions
        st.subheader("⚡ Schnell-Aktionen")
        
        if st.button("🗑️ Alle Nachrichten löschen"):
            st.session_state.messages = []
            logger.info("Alle Nachrichten gelöscht")
            st.success("✅ Alle Nachrichten gelöscht!")
            st.rerun()
        
        if st.button("📨 Testnachricht senden"):
            test_message = {
                "title": "Testnachricht",
                "content": "Dies ist eine automatisch generierte Testnachricht.",
                "sender": "System",
                "recipient": "Dashboard User", 
                "type": "Info",
                "priority": "Normal",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "icon": "ℹ️"
            }
            st.session_state.messages.append(test_message)
            logger.info("Testnachricht erstellt")
            st.success("✅ Testnachricht gesendet!")
            st.rerun()


def _get_sample_messages():
    """Generiert Beispiel-Nachrichten"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return [
        {
            "title": "System-Start",
            "content": "Das OMF Dashboard wurde erfolgreich gestartet.",
            "sender": "System",
            "recipient": "All Users",
            "type": "Info",
            "priority": "Normal",
            "timestamp": current_time,
            "icon": "ℹ️",
            "unread": True
        },
        {
            "title": "Konfiguration aktualisiert",
            "content": "Die Werkstück-Konfiguration wurde erfolgreich gespeichert.",
            "sender": "Supervisor",
            "recipient": "Operator",
            "type": "Info", 
            "priority": "Normal",
            "timestamp": current_time,
            "icon": "ℹ️",
            "unread": True
        },
        {
            "title": "Wartungshinweis",
            "content": "Das System sollte in den nächsten 24 Stunden gewartet werden.",
            "sender": "System",
            "recipient": "Admin",
            "type": "Warnung",
            "priority": "Hoch",
            "timestamp": current_time,
            "icon": "⚠️",
            "unread": True
        }
    ]


def _get_message_icon(message_type: str) -> str:
    """Gibt das passende Icon für einen Nachrichtentyp zurück"""
    icons = {
        "Info": "ℹ️",
        "Warnung": "⚠️", 
        "Fehler": "❌",
        "Anfrage": "❓"
    }
    return icons.get(message_type, "📝")