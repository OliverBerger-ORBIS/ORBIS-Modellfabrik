#!/usr/bin/env python3
"""
Sequence Test App - Isolierte Test-Anwendung für Workflow-Sequenzen
Kann unabhängig vom OMF Dashboard getestet werden
"""

import os

import streamlit as st

from .sequence_definition import create_example_python_sequence, create_example_sequences
from .sequence_ui import create_sequence_ui_app

# Pfad für Imports hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

def main():
    """Hauptfunktion der Test-App"""

    # Beispiel-Sequenzen erstellen falls nicht vorhanden
    try:
        create_example_sequences()
        create_example_python_sequence()
    except Exception as e:
        st.error(f"Fehler beim Erstellen der Beispiel-Sequenzen: {e}")

    # UI-App starten
    create_sequence_ui_app()

if __name__ == "__main__":
    main()
