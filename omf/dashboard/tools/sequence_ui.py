"""
SequenceUI - Streamlit UI-Komponenten für Sequenz-Steuerung
Implementiert die UI-Anforderungen aus requirements_sequence_control.md
"""

from typing import Any, Dict

import streamlit as st

try:
    from .sequence_definition import SequenceDefinitionLoader
    from .sequence_executor import SequenceExecutor, WaitHandler
    from .workflow_order_manager import workflow_order_manager
except ImportError:
    from sequence_definition import SequenceDefinitionLoader
    from sequence_executor import SequenceExecutor, WaitHandler
    from workflow_order_manager import workflow_order_manager

# Import für UI-Refresh Pattern
try:
    from ..dashboard.utils.ui_refresh import request_refresh
except ImportError:
    # Fallback für direkte Ausführung
    def request_refresh():
        st.rerun()


class SequenceUI:
    """UI-Komponenten für Sequenz-Steuerung"""

    def __init__(self, sequence_executor: SequenceExecutor):
        self.executor = sequence_executor
        self.loader = SequenceDefinitionLoader()
        self.mqtt_client = None  # Wird vom Dashboard gesetzt

        # Session State initialisieren
        if "active_sequence" not in st.session_state:
            st.session_state.active_sequence = None
        if "show_step_details" not in st.session_state:
            st.session_state.show_step_details = {}

    def show_sequence_selector(self):
        """Zeigt Sequenz-Auswahl"""
        st.subheader("🎯 Sequenz-Auswahl")

        # Verfügbare Sequenzen laden
        sequences = self.loader.get_all_sequences()

        if not sequences:
            st.warning("⚠️ Keine Sequenz-Definitionen gefunden")
            st.info("💡 Erstelle YML oder Python-Dateien in `config/sequence_definitions/`")
            return None

        # Sequenz-Auswahl
        sequence_names = list(sequences.keys())
        selected_sequence_name = st.selectbox(
            "Wähle eine Sequenz:", sequence_names, help="Wähle eine Sequenz-Definition aus"
        )

        if selected_sequence_name:
            sequence = sequences[selected_sequence_name]
            self._show_sequence_info(sequence)

            # Sequenz starten
            if st.button("🚀 Sequenz starten", key="start_sequence"):
                if self.mqtt_client and self.mqtt_client.connected:
                    # MQTT-Client an Executor übergeben falls noch nicht gesetzt
                    if not self.executor.mqtt_client:
                        self.executor.mqtt_client = self.mqtt_client
                        self.executor.wait_handler = WaitHandler(self.mqtt_client)

                    order_id = self.executor.execute_sequence(sequence)
                    st.session_state.active_sequence = order_id
                    st.success(f"✅ Sequenz '{sequence.name}' gestartet!")
                    request_refresh()
                else:
                    st.error("❌ MQTT-Client nicht verfügbar oder nicht verbunden")
                    st.info("ℹ️ Bitte verbinden Sie sich zuerst mit MQTT in den Einstellungen")

        return selected_sequence_name

    def _show_sequence_info(self, sequence):
        """Zeigt Sequenz-Informationen"""
        with st.expander(f"📋 Sequenz-Details: {sequence.name}", expanded=False):
            st.write(f"**Beschreibung:** {sequence.description}")
            st.write(f"**Anzahl Schritte:** {len(sequence.steps)}")

            # Kontext-Variablen
            if sequence.context:
                st.write("**Kontext-Variablen:**")
                st.json(sequence.context)

            # Schritte anzeigen
            st.write("**Schritte:**")
            for i, step in enumerate(sequence.steps):
                st.write(f"{i+1}. **{step.name}** → `{step.topic}`")

    def show_active_sequence(self):
        """Zeigt aktive Sequenz mit UI"""
        if not st.session_state.active_sequence:
            return

        order_id = st.session_state.active_sequence
        status = self.executor.get_sequence_status(order_id)

        if not status:
            st.error("❌ Sequenz-Status nicht verfügbar")
            st.session_state.active_sequence = None
            return

        order = status["order"]
        sequence = status["sequence"]

        # Sequenz-Header
        st.subheader(f"🔄 Aktive Sequenz: {sequence.name}")

        # Status-Anzeige
        status_color = {"running": "🟢", "completed": "✅", "cancelled": "❌", "error": "🔴"}.get(order.status, "⚪")

        st.write(f"**Status:** {status_color} {order.status.upper()}")
        st.write(f"**Schritt:** {order.current_step} / {order.total_steps}")

        # Fortschrittsanzeige
        if order.total_steps > 0:
            progress = order.current_step / order.total_steps
            st.progress(progress)

        # Sequenz-Schritte anzeigen
        self._show_sequence_steps(status)

        # Abbruch-Button
        if order.status == "running":
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🛑 Sequenz abbrechen", key="cancel_sequence"):
                    self.executor.cancel_sequence(order_id)
                    st.session_state.active_sequence = None
                    st.warning("⚠️ Sequenz abgebrochen!")
                    request_refresh()

    def _show_sequence_steps(self, status: Dict[str, Any]):
        """Zeigt Sequenz-Schritte mit UI"""
        steps = status["steps"]
        order = status["order"]

        st.markdown("### 📋 Sequenz-Schritte")

        for i, step_info in enumerate(steps):
            step_status = step_info["status"]
            step_name = step_info["name"]

            # Status-Symbol
            status_symbol = {
                "pending": "⏳",
                "ready": "🟡",
                "sent": "📤",
                "waiting": "⏳",
                "completed": "✅",
                "error": "❌",
            }.get(step_status, "⚪")

            # Schritt-Container
            with st.container():
                # Schritt-Header mit Einrückung (60px)
                col1, col2, col3 = st.columns([1, 8, 2])

                with col1:
                    st.markdown(f"**{i+1}.**")

                with col2:
                    # Schritt-Name und Status
                    st.markdown(f"{status_symbol} **{step_name}** ({step_status})")

                    # Topic anzeigen
                    st.markdown(f"`{step_info['topic']}`")

                with col3:
                    # Send-Button für bereite Schritte
                    if step_status == "ready" and order.status == "running":
                        if st.button("📤 Senden", key=f"send_step_{i}"):
                            success = self.executor.execute_step(order.order_id, i)
                            if success:
                                st.success("✅ Gesendet!")
                            else:
                                st.error("❌ Fehler beim Senden!")
                            request_refresh()
                    elif step_status == "waiting":
                        st.info("⏳ Warte...")
                    elif step_status == "completed":
                        st.success("✅ Fertig")
                    elif step_status == "error":
                        st.error("❌ Fehler")

                # Step-Details (optional)
                step_key = f"step_details_{i}"
                if step_key not in st.session_state.show_step_details:
                    st.session_state.show_step_details[step_key] = False

                if st.checkbox("Details", key=f"details_{i}", value=st.session_state.show_step_details[step_key]):
                    st.session_state.show_step_details[step_key] = True
                    with st.expander("📄 Schritt-Details", expanded=True):
                        st.write("**Payload:**")
                        st.json(step_info["payload"])

                        # Kontext-Variablen falls vorhanden
                        if "context_vars" in step_info and step_info["context_vars"]:
                            st.write("**Kontext-Variablen:**")
                            st.json(step_info["context_vars"])
                else:
                    st.session_state.show_step_details[step_key] = False

                # Trennlinie zwischen Schritten (außer letzter)
                if i < len(steps) - 1:
                    st.markdown("---")

        # Abschluss-Anzeige
        if order.status == "completed":
            st.success("🎉 **Sequenz erfolgreich abgeschlossen!**")
            if st.button("🔄 Neue Sequenz starten", key="new_sequence"):
                st.session_state.active_sequence = None
                request_refresh()
        elif order.status == "cancelled":
            st.warning("⚠️ **Sequenz abgebrochen**")
            if st.button("🔄 Neue Sequenz starten", key="new_sequence_cancelled"):
                st.session_state.active_sequence = None
                request_refresh()
        elif order.status == "error":
            st.error("❌ **Sequenz mit Fehler beendet**")
            if st.button("🔄 Neue Sequenz starten", key="new_sequence_error"):
                st.session_state.active_sequence = None
                request_refresh()

    def show_sequence_history(self):
        """Zeigt Sequenz-Historie"""
        st.subheader("📚 Sequenz-Historie")

        all_orders = workflow_order_manager.get_all_orders()

        if not all_orders:
            st.info("ℹ️ Noch keine Sequenzen ausgeführt")
            return

        # Tabelle mit Historie
        for order_id, order in all_orders.items():
            with st.expander(f"{order.sequence_name} - {order.status}", expanded=False):
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.write(f"**Order ID:** {order_id[:8]}...")
                    st.write(f"**Status:** {order.status}")

                with col2:
                    st.write(f"**Schritte:** {order.current_step}/{order.total_steps}")
                    st.write(f"**Update ID:** {order.order_update_id}")

                with col3:
                    if order.context:
                        st.write("**Kontext:**")
                        st.json(order.context)

    def show_debug_info(self):
        """Zeigt Debug-Informationen"""
        st.subheader("🔍 Debug-Informationen")

        # WorkflowOrderManager Status
        st.write("**WorkflowOrderManager:**")
        all_orders = workflow_order_manager.get_all_orders()
        st.write(f"- Aktive Orders: {len(all_orders)}")

        # SequenceExecutor Status
        st.write("**SequenceExecutor:**")
        st.write(f"- Laufende Sequenzen: {len(self.executor.running_sequences)}")

        # Verfügbare Sequenzen
        st.write("**Verfügbare Sequenzen:**")
        sequences = self.loader.get_all_sequences()
        for name, sequence in sequences.items():
            st.write(f"- {name}: {len(sequence.steps)} Schritte")

        # Session State
        st.write("**Session State:**")
        st.json(
            {
                "active_sequence": st.session_state.active_sequence,
                "show_step_details": st.session_state.show_step_details,
            }
        )

    def show_sequence_status(self):
        """Zeigt den aktuellen Sequenz-Status"""
        st.subheader("📊 Sequenz-Status")

        # Workflow Manager Status
        all_orders = workflow_order_manager.get_all_orders()

        if all_orders:
            st.success(f"✅ {len(all_orders)} aktive Sequenz-Orders")

            # Status-Tabelle
            for order_id, order in all_orders.items():
                with st.expander(f"Order {order_id[:8]}... - Status: {order.status}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Status:** {order.status}")
                        st.write(f"**Schritt:** {order.current_step}/{order.total_steps}")
                        st.write(f"**Update ID:** {order.order_update_id}")

                    with col2:
                        st.write(f"**Sequenz:** {order.sequence_name}")
                        st.write(f"**Order ID:** {order_id}")

                        # Order-Details als JSON
                        st.json(
                            {
                                "order_id": order_id,
                                "status": order.status,
                                "current_step": order.current_step,
                                "total_steps": order.total_steps,
                                "sequence_name": order.sequence_name,
                                "context": order.context,
                            }
                        )
        else:
            st.info("ℹ️ Keine aktiven Sequenz-Orders")

    def show_active_sequences(self):
        """Zeigt aktive Sequenzen und deren Fortschritt"""
        st.subheader("🔄 Aktive Sequenzen")

        # Sequenz-Executor Status
        if hasattr(self.executor, "running_sequences") and self.executor.running_sequences:
            st.success(f"✅ {len(self.executor.running_sequences)} laufende Sequenzen")

            for order_id, sequence_info in self.executor.running_sequences.items():
                # sequence_info ist ein SequenceDefinition Objekt, nicht ein Dictionary
                sequence_name = getattr(sequence_info, "name", "Unbekannt")
                with st.expander(f"Sequenz: {sequence_name} - Order: {order_id[:8]}...", expanded=True):
                    # Status aus WorkflowOrderManager holen
                    order = workflow_order_manager.get_order(order_id)
                    if order:
                        st.write(f"**Status:** {order.status}")
                        st.write(f"**Aktueller Schritt:** {order.current_step}")
                        st.write(f"**Gesamte Schritte:** {order.total_steps}")

                        # Fortschrittsbalken für die gesamte Sequenz
                        completed_steps = 0
                        for step in sequence_info.steps:
                            step_status = getattr(step, "status", "")
                            # Status normalisieren (falls es ein Enum ist)
                            if hasattr(step_status, "name"):
                                step_status_str = step_status.name
                            else:
                                step_status_str = str(step_status)

                            if step_status_str == "COMPLETED":
                                completed_steps += 1

                        total_steps = len(sequence_info.steps)
                        progress = completed_steps / total_steps if total_steps > 0 else 0
                        st.progress(
                            progress,
                            text=f"Sequenz-Fortschritt: {completed_steps}/{total_steps} Schritte abgeschlossen",
                        )

                        # Detaillierte Schritt-Status anzeigen
                        st.write("**Schritt-Details:**")
                        for i, step in enumerate(sequence_info.steps):
                            step_name = getattr(step, "name", f"Schritt {i+1}")
                            step_status = getattr(step, "status", "UNKNOWN")

                            # Status-String normalisieren (falls es ein Enum ist)
                            if hasattr(step_status, "name"):
                                step_status_str = step_status.name
                            else:
                                step_status_str = str(step_status)

                            # Status-Icons
                            status_icon = {
                                "PENDING": "⏳",
                                "READY": "🟡",
                                "SENT": "📤",
                                "WAITING": "⏰",
                                "COMPLETED": "✅",
                                "ERROR": "❌",
                            }.get(step_status_str, "❓")

                            # Erweiterte Anzeige für WAITING-Schritte
                            if step_status == "WAITING":
                                st.write(f"{status_icon} **{step_name}:** {step_status}")

                                # Verbleibende Wartezeit anzeigen
                                if hasattr(self.executor, "wait_handler") and self.executor.wait_handler:
                                    remaining_time = self.executor.wait_handler.get_remaining_wait_time(order_id)
                                    if remaining_time > 0:
                                        st.write(
                                            f"   ⏰ **Warte noch {remaining_time:.1f}s bis zum nächsten Schritt...**"
                                        )
                                        # Progress Bar für Wartezeit
                                        progress = 1.0 - (remaining_time / 5.0)  # 5 Sekunden Standard
                                        st.progress(
                                            progress, text=f"Wartezeit läuft... ({remaining_time:.1f}s verbleibend)"
                                        )
                                    else:
                                        st.write("   ⏰ **Wartezeit abgeschlossen - nächster Schritt startet...**")
                                else:
                                    st.write("   ⏰ **Warte 5 Sekunden bis zum nächsten Schritt...**")
                            else:
                                st.write(f"{status_icon} **{step_name}:** {step_status}")

                            # Zusätzliche Info für verschiedene Status
                            if step_status == "SENT":
                                st.write("   📤 Nachricht wurde versendet")
                            elif step_status == "COMPLETED":
                                st.write("   ✅ Schritt erfolgreich abgeschlossen")
                            elif step_status == "ERROR":
                                st.write("   ❌ Fehler beim Ausführen des Schritts")
                    else:
                        st.write("**Status:** Unbekannt")
                        st.write("**Aktueller Schritt:** 0")
                        st.write("**Gesamte Schritte:** 0")
        else:
            st.info("ℹ️ Keine aktiven Sequenzen")


def create_sequence_ui_app():
    """Erstellt die komplette Sequence UI App"""
    st.set_page_config(page_title="Workflow Sequence Control", page_icon="🔄", layout="wide")

    st.title("🔄 Workflow Sequence Control")
    st.markdown("Sequenzielle Steuerungsbefehle in logischer Klammer mit UI-Unterstützung")

    # Mock MQTT Client für Tests
    class MockMqttClient:
        def publish(self, topic, payload, qos=1):
            st.info(f"📤 Mock MQTT: {topic} → {payload}")
            return True

        def get_recent_messages(self):
            return []

    # SequenceExecutor mit Mock MQTT Client
    mock_mqtt = MockMqttClient()
    executor = SequenceExecutor(mock_mqtt)

    # UI erstellen
    ui = SequenceUI(executor)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Sequenz-Steuerung", "📚 Historie", "🔍 Debug"])

    with tab1:
        # Sequenz-Auswahl
        ui.show_sequence_selector()

        # Aktive Sequenz
        ui.show_active_sequence()

    with tab2:
        ui.show_sequence_history()

    with tab3:
        ui.show_debug_info()


if __name__ == "__main__":
    create_sequence_ui_app()
