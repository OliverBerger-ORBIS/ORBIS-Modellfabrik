#!/usr/bin/env python3
"""
OMF Dashboard - Zentrales Message-Processing-System
Belastbares Pattern für alle Komponenten, die MQTT-Nachrichten verarbeiten
"""

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Union

import streamlit as st


@dataclass
class MessageProcessor:
    """Zentraler Message-Processor für alle Dashboard-Komponenten"""

    component_name: str
    message_filter: Optional[Callable[[Dict], bool]] = None
    processor_function: Optional[Callable[[List[Dict]], None]] = None

    def __post_init__(self):
        """Initialisiert Session-State Keys für diese Komponente"""
        self.last_processed_key = f"{self.component_name}_last_processed_count"
        self.last_count_key = f"{self.component_name}_last_count"
        self.store_key = f"{self.component_name}_store"
        self.validation_errors_key = f"{self.component_name}_validation_errors"

    def process_messages(self, mqtt_client) -> List[Dict]:
        """
        Verarbeitet nur neue MQTT-Nachrichten für diese Komponente

        Args:
            mqtt_client: MQTT-Client mit drain() Methode

        Returns:
            List[Dict]: Alle verfügbaren Nachrichten (für weitere Verarbeitung)
        """
        if not mqtt_client:
            return []

        try:
            # Alle Nachrichten holen
            all_messages = mqtt_client.drain()
            last_processed_count = st.session_state.get(self.last_processed_key, 0)

            # Nur neue Nachrichten verarbeiten
            if len(all_messages) > last_processed_count:
                new_messages = all_messages[last_processed_count:]

                # Nachrichten filtern (falls Filter definiert)
                if self.message_filter:
                    filtered_messages = [msg for msg in new_messages if self.message_filter(msg)]
                else:
                    filtered_messages = new_messages

                # Nachrichten verarbeiten (falls Processor definiert)
                if filtered_messages and self.processor_function:
                    self.processor_function(filtered_messages)

                # Session-State aktualisieren
                st.session_state[self.last_processed_key] = len(all_messages)
                st.session_state[self.last_count_key] = len(all_messages)

                # Debug-Info (optional) - PERFORMANCE-FIX: Debug-Spam reduziert
                if filtered_messages:
                    # Nur bei vielen Nachrichten anzeigen, um Sidebar-Spam zu vermeiden
                    if len(filtered_messages) > 5:
                        st.sidebar.info(
                            f"📊 {self.component_name}: {len(filtered_messages)} neue Nachrichten verarbeitet"
                        )

            else:
                # Keine neuen Nachrichten
                st.session_state[self.last_count_key] = len(all_messages)

            return all_messages

        except Exception as e:
            st.warning(f"⚠️ {self.component_name}: Fehler beim Verarbeiten der MQTT-Nachrichten: {e}")
            return []

    def add_validation_error(self, topic: str, error: str, message_data: Dict):
        """Fügt einen Template-Validierungsfehler zur Historie hinzu"""
        if self.validation_errors_key not in st.session_state:
            st.session_state[self.validation_errors_key] = []

        error_entry = {
            "timestamp": message_data.get("timestamp", "N/A"),
            "topic": topic,
            "error": error,
            "message_data": message_data,
        }

        # Fehler zur Historie hinzufügen (max. 10 Einträge)
        st.session_state[self.validation_errors_key].append(error_entry)
        if len(st.session_state[self.validation_errors_key]) > 10:
            st.session_state[self.validation_errors_key] = st.session_state[self.validation_errors_key][-10:]

    def get_validation_errors(self) -> List[Dict]:
        """Gibt alle Template-Validierungsfehler zurück"""
        return st.session_state.get(self.validation_errors_key, [])

    def clear_validation_errors(self):
        """Löscht alle Template-Validierungsfehler"""
        if self.validation_errors_key in st.session_state:
            del st.session_state[self.validation_errors_key]

    def get_message_count(self) -> int:
        """Gibt die Anzahl der verarbeiteten Nachrichten zurück"""
        return st.session_state.get(self.last_count_key, 0)

    def reset_processing(self):
        """Setzt die Verarbeitung zurück (für Tests oder Reset)"""
        st.session_state[self.last_processed_key] = 0
        st.session_state[self.last_count_key] = 0


# Globale Message-Processor Instanzen
_message_processors: Dict[str, MessageProcessor] = {}


def create_topic_filter(topics: Union[str, List[str]]) -> Callable[[Dict], bool]:
    """
    Erstellt einen Filter für Topics

    Args:
        topics: Einzelner Topic oder Liste von Topics

    Returns:
        Callable: Filter-Funktion
    """
    if isinstance(topics, str):
        topics = [topics]

    def filter_func(msg):
        topic = msg.get("topic", "")
        return any(topic.startswith(t) for t in topics)

    return filter_func


def create_regex_filter(pattern: str) -> Callable[[Dict], bool]:
    """
    Erstellt einen Regex-basierten Filter

    Args:
        pattern: Regex-Pattern für Topics

    Returns:
        Callable: Filter-Funktion
    """
    regex = re.compile(pattern)

    def filter_func(msg):
        topic = msg.get("topic", "")
        return regex.search(topic) is not None

    return filter_func


def get_message_processor(
    component_name: str,
    message_filter: Optional[Callable[[Dict], bool]] = None,
    processor_function: Optional[Callable[[List[Dict]], None]] = None,
) -> MessageProcessor:
    """
    Factory-Funktion für Message-Processor

    Args:
        component_name: Eindeutiger Name der Komponente
        message_filter: Optional: Filter-Funktion für Nachrichten
        processor_function: Optional: Verarbeitungs-Funktion für neue Nachrichten

    Returns:
        MessageProcessor: Konfigurierter Message-Processor
    """
    if component_name not in _message_processors:
        _message_processors[component_name] = MessageProcessor(
            component_name=component_name, message_filter=message_filter, processor_function=processor_function
        )

    return _message_processors[component_name]


def reset_all_processors():
    """Setzt alle Message-Processor zurück (für Tests oder Reset)"""
    for processor in _message_processors.values():
        processor.reset_processing()


def get_all_processor_stats() -> Dict[str, int]:
    """Gibt Statistiken aller Message-Processor zurück"""
    return {name: processor.get_message_count() for name, processor in _message_processors.items()}
