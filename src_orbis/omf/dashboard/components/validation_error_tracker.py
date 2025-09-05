#!/usr/bin/env python3
"""
OMF Dashboard - Template-Validierungsfehler Tracker
Sammelt und verwaltet Template-Validierungsfehler über mehrere Messages hinweg
"""

from datetime import datetime
from typing import Dict, List

import streamlit as st


class ValidationErrorTracker:
    """Verfolgt Template-Validierungsfehler über mehrere Messages hinweg"""

    def __init__(self, component_name: str):
        self.component_name = component_name
        self.errors_key = f"{component_name}_validation_errors"

    def add_error(self, topic: str, error: str, message_data: Dict):
        """Fügt einen Validierungsfehler zur Historie hinzu"""
        if self.errors_key not in st.session_state:
            st.session_state[self.errors_key] = []

        error_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "topic": topic,
            "error": error,
            "message_data": message_data,
        }

        # Fehler zur Historie hinzufügen (max. 10 Einträge)
        st.session_state[self.errors_key].append(error_entry)
        if len(st.session_state[self.errors_key]) > 10:
            st.session_state[self.errors_key] = st.session_state[self.errors_key][-10:]

    def get_errors(self) -> List[Dict]:
        """Gibt alle Validierungsfehler zurück"""
        return st.session_state.get(self.errors_key, [])

    def clear_errors(self):
        """Löscht alle Validierungsfehler"""
        if self.errors_key in st.session_state:
            del st.session_state[self.errors_key]

    def has_errors(self) -> bool:
        """Prüft, ob Validierungsfehler vorhanden sind"""
        return len(self.get_errors()) > 0

    def display_errors(self):
        """Zeigt die Validierungsfehler-Historie in der UI an"""
        errors = self.get_errors()

        if errors:
            st.markdown("### 🚨 Template-Validierungsfehler Historie")
            st.warning(f"⚠️ **{len(errors)} Validierungsfehler** in der Historie")

            with st.expander("🔍 Fehler-Details anzeigen"):
                for i, error_entry in enumerate(errors[-5:]):  # Letzte 5 Fehler
                    st.write(f"**Fehler {i+1}:**")
                    st.write(f"- **Zeit:** {error_entry.get('timestamp', 'N/A')}")
                    st.write(f"- **Topic:** {error_entry.get('topic', 'N/A')}")
                    st.write(f"- **Fehler:** {error_entry.get('error', 'N/A')}")

                    # Original Payload anzeigen
                    message_data = error_entry.get("message_data", {})
                    if message_data:
                        st.write("- **Original Payload:**")
                        st.json(message_data)

                    st.write("---")

            if st.button("🗑️ Fehler-Historie löschen", key=f"clear_{self.component_name}_errors"):
                self.clear_errors()
                st.rerun()
        else:
            st.success("✅ **Keine Template-Validierungsfehler** in der Historie")


def get_validation_tracker(component_name: str) -> ValidationErrorTracker:
    """Factory-Funktion für ValidationErrorTracker"""
    return ValidationErrorTracker(component_name)
