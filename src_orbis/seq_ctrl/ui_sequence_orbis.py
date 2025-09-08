import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import streamlit as st
from sequence_control_orbis import WorkflowOrderManager

from src_orbis.seq_ctrl.recipes_orbis import get_recipe_names, load_sequence_recipe


def show_sequence_window(order_id: str):
    manager = WorkflowOrderManager.get_instance()
    seq = manager.sequences.get(order_id)
    if not seq:
        st.sidebar.warning("Sequenz nicht gefunden.")
        return

    st.sidebar.header(f"Sequenz {order_id}")
    for i, step in enumerate(seq["steps"]):
        if i == seq["current_step"]:
            st.sidebar.write(f"➡️ **{step['name']}** (Aktuell)")
            if st.sidebar.button(f"Send: {step['name']}"):
                manager.next_step(order_id)
        elif i < seq["current_step"]:
            st.sidebar.write(f"✅ {step['name']} (Abgeschlossen)")
        else:
            st.sidebar.write(f"{step['name']} (Ausstehend)")
    if st.sidebar.button("Sequenz abbrechen"):
        manager.abort_sequence(order_id)
        st.sidebar.write("Sequenz abgebrochen!")


st.title("ORBIS Sequenzsteuerung")

# Dropdown für Rezeptauswahl
rezepte = get_recipe_names()
auswahl = st.selectbox("Sequenz wählen", rezepte)
manager = WorkflowOrderManager.get_instance()

if st.button("Sequenz starten"):
    sequence = load_sequence_recipe(auswahl)
    manager.start_sequence(auswahl, sequence)
    st.success(f"Sequenz '{auswahl}' gestartet.")

if auswahl in manager.sequences:
    show_sequence_window(auswahl)
else:
    st.info("Bitte Sequenz starten, um die Schritte zu sehen.")
