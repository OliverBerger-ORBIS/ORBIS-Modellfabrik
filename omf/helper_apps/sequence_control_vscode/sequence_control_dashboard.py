import streamlit as st

from .python_sequences import python_sequence
from .workflow_sequence_manager import get_workflow_sequence_manager

RECIPES_DIR = "omf/helper_apps/sequence_control_vscode/recipes"
sequence_manager = get_workflow_sequence_manager(RECIPES_DIR)

st.title("Sequenzielle Steuerung")

sequences = sequence_manager.loader.list_sequences() + [python_sequence.name]
selected_sequence = st.selectbox("Sequenz auswählen", sequences)
module = st.text_input("Modul-ID", "MILL-01")

if st.button("Sequenz starten"):
    if selected_sequence == python_sequence.name:
        st.session_state["active_order_id"] = f"py_{python_sequence.name}"
        st.session_state["py_sequence_idx"] = 0
        st.session_state["py_sequence_status"] = "active"
        st.session_state["show_step_details"] = False
    else:
        order_id = sequence_manager.start_sequence(selected_sequence, module)
        st.session_state["active_order_id"] = order_id
        st.session_state["show_step_details"] = False

order_id = st.session_state.get("active_order_id")
if order_id:
    if order_id.startswith("py_"):
        # Python-basierte Sequenz
        steps = python_sequence.steps
        idx = st.session_state.get("py_sequence_idx", 0)
        status = {
            "status": st.session_state.get("py_sequence_status", "active"),
            "context": {"orderId": "PY-ORDER", "module": module},
        }
    else:
        status = sequence_manager.get_sequence_status(order_id)
        steps = status["sequence"]["steps"]
        idx = status["current_step"]

    # Statusanzeige oben
    if status["status"] == "active":
        st.info("Sequenz gestartet")
    elif status["status"] == "completed":
        st.success("Sequenz beendet")
    elif status["status"] == "aborted":
        st.warning("Sequenz abgebrochen")

    # Vertikale Linie und eingerückte Schritte

    st.markdown("<div style='border-left: 3px solid #888; padding-left: 60px;'>", unsafe_allow_html=True)
    show_details = st.checkbox(
        "Step Context & Payload anzeigen", value=st.session_state.get("show_step_details", False)
    )
    st.session_state["show_step_details"] = show_details
    for i, step in enumerate(steps):
        style = "font-weight:bold;" if i == idx else ""
        num_icon = f"{i+1}."
        icon = "✅" if i < idx else ("➡️" if i == idx else "🔲")
        st.markdown(
            f"<div style='margin-bottom:8px;{style}'>{num_icon} {icon} {step['name']}</div>", unsafe_allow_html=True
        )
        # Context/Payload direkt unter dem Schritt anzeigen
        if show_details:
            with st.expander(f"Details zu Schritt: {step['name']}", expanded=False):
                st.json({"Step": step, "Context": status["context"]})
    st.markdown("</div>", unsafe_allow_html=True)

    # Senden-Button für aktuellen Schritt
    if status["status"] == "active" and idx < len(steps):
        if st.button(f"Senden: {steps[idx]['name']}"):
            if order_id.startswith("py_"):
                python_sequence.run_step(idx, status["context"])
                st.session_state["py_sequence_idx"] += 1
                if st.session_state["py_sequence_idx"] >= len(steps):
                    st.session_state["py_sequence_status"] = "completed"
            else:
                sequence_manager.next_step(order_id)

    # Sequenz abbrechen immer aktiv
    if status["status"] == "active":
        if st.button("Sequenz abbrechen"):
            if order_id.startswith("py_"):
                st.session_state["py_sequence_status"] = "aborted"
                st.session_state["active_order_id"] = None
            else:
                sequence_manager.abort_sequence(order_id)
                st.session_state["active_order_id"] = None

    # Abschlussanzeige auf Höhe von Sequenz starten
    if status["status"] == "completed":
        st.success("Sequenz beendet!")
        st.session_state["active_order_id"] = None
    elif status["status"] == "aborted":
        st.warning("Sequenz abgebrochen!")
        st.session_state["active_order_id"] = None
