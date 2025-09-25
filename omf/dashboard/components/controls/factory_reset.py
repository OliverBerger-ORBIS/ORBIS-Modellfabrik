# omf/dashboard/components/controls/factory_reset.py

import streamlit as st
from datetime import datetime, timezone

from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.tools.mqtt_gateway import MqttGateway
from omf.dashboard.utils.ui_refresh import request_refresh

# Logger für Factory Reset
logger = get_logger("omf.dashboard.components.controls.factory_reset")


def render_factory_reset():
    """Zeigt nur das ⚙️-Icon + modalen Dialog für Factory Reset."""
    
    # MQTT-Client prüfen (stumm - keine UI-Fehler)
    mqtt_client = st.session_state.get("mqtt_client")
    if not mqtt_client or not hasattr(mqtt_client, 'client') or not mqtt_client.client:
        # Stumm zurückgeben - keine UI-Fehler anzeigen
        return

    if "show_controls_modal" not in st.session_state:
        st.session_state.show_controls_modal = False

    # ⚙️ Icon-Button
    if st.button("⚙️", help="Factory Reset", key="open_factory_reset"):
        st.session_state.show_controls_modal = True

    # Modaler Dialog
    if st.session_state.show_controls_modal:
        with st.container():
            st.markdown("### ⚙️ Factory Reset")
            st.info("Setzt alle Module in den Ausgangszustand zurück")

            with_storage = st.radio(
                "Reset-Option:",
                ["Nur Factory Reset", "Factory Reset + Storage"],
                index=0,
                key="reset_option",
            ).endswith("+ Storage")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Factory Reset ausführen", key="do_factory_reset", type="primary"):
                    try:
                        # MqttGateway verwenden (wie in steering_factory.py)
                        gateway = MqttGateway(mqtt_client)
                        
                        payload = {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "withStorage": with_storage
                        }
                        
                        logger.info("🏭 Factory Reset angefordert")
                        success = gateway.send(
                            topic="ccu/set/reset",
                            builder=lambda: payload,
                            ensure_order_id=True,
                        )
                        
                        if success:
                            logger.info("✅ Factory Reset erfolgreich gesendet")
                            st.success("✅ Factory Reset gesendet")
                            # Modal automatisch schließen
                            st.session_state.show_controls_modal = False
                            # UI-Refresh Pattern verwenden (nicht st.rerun!)
                            request_refresh()
                        else:
                            logger.error("❌ Fehler beim Senden des Factory Reset")
                            st.error("❌ Fehler beim Senden des Factory Reset")
                        
                    except Exception as e:
                        logger.error(f"❌ Fehler beim Factory Reset: {e}")
                        st.error("❌ Fehler beim Factory Reset")

            with col2:
                if st.button("❌ Schließen", key="close_factory_reset"):
                    st.session_state.show_controls_modal = False
