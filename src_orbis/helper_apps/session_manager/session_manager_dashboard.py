#!/usr/bin/env python3
"""
OMF Session Manager
Streamlit App für Session-Management mit konfigurierbarem Logging
"""

import logging
import os
from pathlib import Path
from datetime import datetime

import streamlit as st


def setup_logging():
    """Logging-Setup mit dynamischer Level-Anpassung"""
    # Logging-Verzeichnis erstellen falls nicht vorhanden
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Log-Datei Pfad
    log_file = log_dir / "session_manager.log"
    
    # Aktuelles Logging-Level aus Session State holen, Default: INFO
    current_level = st.session_state.get("logging_level", "INFO")
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    
    # Logger konfigurieren
    logger = logging.getLogger("session_manager")
    logger.handlers.clear()  # Bestehende Handler entfernen
    
    # File Handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console Handler für Streamlit
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Handler hinzufügen
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Level setzen
    logger.setLevel(level_mapping.get(current_level, logging.INFO))
    
    return logger


def show_settings():
    """Settings-Tab mit Logging-Konfiguration"""
    st.subheader("⚙️ Einstellungen")
    
    # Logging-Einstellungen
    st.markdown("### 📝 Logging-Konfiguration")
    
    # Aktuelles Level anzeigen
    current_level = st.session_state.get("logging_level", "INFO")
    st.info(f"🔍 Aktuelles Logging-Level: **{current_level}**")
    
    # Level-Auswahl
    level_options = ["DEBUG", "INFO", "WARNING", "ERROR"]
    selected_level = st.selectbox(
        "Logging-Level auswählen:",
        level_options,
        index=level_options.index(current_level),
        help="DEBUG: Detaillierte Debug-Informationen\nINFO: Allgemeine Informationen\nWARNING: Warnungen\nERROR: Nur Fehler"
    )
    
    # Level-Änderung verarbeiten
    if selected_level != current_level:
        st.session_state["logging_level"] = selected_level
        st.success(f"✅ Logging-Level auf **{selected_level}** geändert")
        st.rerun()
    
    # Log-Datei Info
    log_file = Path("data/logs/session_manager.log")
    if log_file.exists():
        file_size = log_file.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        st.markdown(f"📄 **Log-Datei:** `{log_file}`")
        st.markdown(f"📊 **Dateigröße:** {file_size_mb:.2f} MB")
        
        # Log-Datei löschen Option
        if st.button("🗑️ Log-Datei löschen", help="Löscht die aktuelle Log-Datei"):
            try:
                log_file.unlink()
                st.success("✅ Log-Datei gelöscht")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Fehler beim Löschen: {e}")
    else:
        st.info("📄 Log-Datei wird beim ersten Logging-Ereignis erstellt")


def show_demo():
    """Demo-Tab zum Testen der Logging-Funktionalität"""
    st.subheader("🧪 Logging-Demo")
    
    logger = setup_logging()
    
    st.markdown("### Test-Nachrichten senden")
    st.markdown("Klicken Sie auf die Buttons um verschiedene Log-Level zu testen:")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🐛 DEBUG", help="DEBUG-Nachricht senden"):
            logger.debug("Debug-Nachricht vom Session Manager")
            st.success("DEBUG-Nachricht gesendet")
    
    with col2:
        if st.button("ℹ️ INFO", help="INFO-Nachricht senden"):
            logger.info("Info-Nachricht vom Session Manager")
            st.success("INFO-Nachricht gesendet")
    
    with col3:
        if st.button("⚠️ WARNING", help="WARNING-Nachricht senden"):
            logger.warning("Warning-Nachricht vom Session Manager")
            st.success("WARNING-Nachricht gesendet")
    
    with col4:
        if st.button("❌ ERROR", help="ERROR-Nachricht senden"):
            logger.error("Error-Nachricht vom Session Manager")
            st.success("ERROR-Nachricht gesendet")
    
    # Aktuelles Logging-Level Info
    current_level = st.session_state.get("logging_level", "INFO")
    st.info(f"💡 **Aktuelles Level:** {current_level} - Nur Nachrichten mit diesem Level oder höher werden geloggt")
    
    # Log-Datei Inhalt anzeigen
    log_file = Path("data/logs/session_manager.log")
    if log_file.exists() and st.button("📖 Letzte Log-Einträge anzeigen"):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-10:]  # Letzte 10 Zeilen
                if last_lines:
                    st.markdown("### 📋 Letzte Log-Einträge:")
                    for line in last_lines:
                        st.code(line.strip())
                else:
                    st.info("📄 Log-Datei ist leer")
        except Exception as e:
            st.error(f"❌ Fehler beim Lesen der Log-Datei: {e}")


def main():
    """Hauptfunktion der Session Manager App"""
    st.set_page_config(
        page_title="OMF Session Manager",
        page_icon="🎛️",
        layout="wide"
    )
    
    st.title("🎛️ OMF Session Manager")
    st.markdown("Session-Management mit konfigurierbarem Logging")
    
    # Initialize logging level if not set
    if "logging_level" not in st.session_state:
        st.session_state["logging_level"] = "INFO"
    
    # Setup logging
    logger = setup_logging()
    logger.info("Session Manager gestartet")
    
    # Tabs erstellen
    tab1, tab2 = st.tabs(["⚙️ Einstellungen", "🧪 Logging-Demo"])
    
    with tab1:
        show_settings()
    
    with tab2:
        show_demo()


if __name__ == "__main__":
    main()