"""
APS Overview - Commands
Authentisches APS-Dashboard mit Material Design und OMF-Standards
"""

import streamlit as st
from datetime import datetime, timezone
from omf.dashboard.tools.logging_config import get_logger


class APSCommandsManager:
    """Manager für APS System Commands - OMF-konform mit APS-Standards"""

    def __init__(self):
        # OMF-Logging System
        self.logger = get_logger("omf.dashboard.components.aps_overview_commands")
        
        # APS-Standard Commands (basierend auf Original APS-Analyse)
        self.commands = []
        self.last_update = None
        
        # Authentische APS-Topics (aus Original APS-Dashboard)
        self.aps_topics = {
            "factory_reset": "ccu/set/reset",
            "factory_park": "ccu/set/park", 
            "fts_charge": "ccu/set/charge",
            "fts_pair": "ccu/set/pairFts",
            "module_delete": "ccu/set/deleteModule",
            "system_calibration": "ccu/set/calibration"
        }
        
        self.logger.info("🚀 APS Commands Manager initialisiert")

    def send_system_command(self, mqtt_client, command, payload=None):
        """Sendet einen Command nach APS-Standard mit OMF-Logging"""
        try:
            if payload is None:
                payload = {}
            
            # OMF-Logging für Analyse
            self.logger.info(f"🔍 APS System Command: Topic='{command}', Payload={payload}")
            
            # APS-Standard: Direkter MQTT Publish (QoS=2, retain=True)
            # Wie in Original APS-Dashboard: this.mqtt.publish(topic, payload, {qos:2})
            result = mqtt_client.publish(command, payload, qos=2, retain=True)
            
            self.logger.info(f"📤 APS System Command gesendet: Result={result}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Senden des Commands: {e}")
            st.error(f"❌ Fehler beim Senden des Commands: {e}")
            return False

    def send_instant_action(self, mqtt_client, module, action):
        """Sendet eine Instant Action nach APS-Standard"""
        try:
            topic = f"{module.lower()}/instantAction"
            payload = {"action": action}
            
            self.logger.info(f"🔍 APS Instant Action: Module='{module}', Action='{action}'")
            result = mqtt_client.publish(topic, payload, qos=2, retain=True)
            
            self.logger.info(f"📤 APS Instant Action gesendet: Result={result}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Senden der Instant Action: {e}")
            st.error(f"❌ Fehler beim Senden der Instant Action: {e}")
            return False

    def get_authentic_payload(self, command_type, **kwargs):
        """Generiert authentische APS-Payloads basierend auf Original APS-Dashboard"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        payloads = {
            "factory_reset": {"timestamp": timestamp, "withStorage": False},
            "factory_park": {"timestamp": timestamp},
            "fts_charge": {
                "serialNumber": kwargs.get("serialNumber", "5iO4"),
                "charge": kwargs.get("charge", True),
                "timestamp": timestamp
            },
            "fts_pair": {
                "serialNumber": kwargs.get("serialNumber", "5iO4")
            },
            "module_delete": {
                "serialNumber": kwargs.get("serialNumber", "5iO4")
            }
        }
        
        return payloads.get(command_type, {"timestamp": timestamp})


def show_aps_commands():
    """Authentisches APS-Dashboard mit Material Design und OMF-Standards"""
    
    # Header mit authentischem APS-Design
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="color: white; margin: 0; text-align: center; font-size: 2rem;">
            🏭 APS System Commands
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; text-align: center;">
            Agile Production Simulation - Authentisches Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state (OMF-Standard)
    if "aps_commands_manager" not in st.session_state:
        st.session_state["aps_commands_manager"] = APSCommandsManager()

    manager = st.session_state["aps_commands_manager"]

    # Floating Action Button für Factory Park (wie im Original APS-Dashboard)
    st.markdown("""
    <div style="
        position: fixed;
        top: 45px;
        right: 65px;
        z-index: 2001;
    ">
        <button style="
            background: #ff6b6b;
            color: white;
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 8px;
        " onclick="document.getElementById('park-factory-btn').click()">
            🅿️ Fabrik parken
        </button>
    </div>
    """, unsafe_allow_html=True)

    # System Commands Grid (Material Design)
    st.markdown("### 🎛️ System Commands")
    
    # Grid Layout für authentisches APS-Design
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #4CAF50;
            margin-bottom: 1rem;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #333;">🏭 Factory Control</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Factory Reset", key="aoc_factory_reset", use_container_width=True):
            payload = manager.get_authentic_payload("factory_reset")
            result = manager.send_system_command(client, manager.aps_topics["factory_reset"], payload)
            if result:
                st.success("✅ Factory Reset gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔧 System Calibration", key="aoc_system_calibration", use_container_width=True):
            payload = manager.get_authentic_payload("system_calibration")
            result = manager.send_system_command(client, manager.aps_topics["system_calibration"], payload)
            if result:
                st.success("✅ System Calibration gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col2:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #2196F3;
            margin-bottom: 1rem;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #333;">🚗 FTS Control</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔋 FTS Charge", key="aoc_fts_charge", use_container_width=True):
            payload = manager.get_authentic_payload("fts_charge", charge=True)
            result = manager.send_system_command(client, manager.aps_topics["fts_charge"], payload)
            if result:
                st.success("✅ FTS Charge gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔌 FTS Pair", key="aoc_fts_pair", use_container_width=True):
            payload = manager.get_authentic_payload("fts_pair")
            result = manager.send_system_command(client, manager.aps_topics["fts_pair"], payload)
            if result:
                st.success("✅ FTS Pair gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    with col3:
        st.markdown("""
        <div style="
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #FF9800;
            margin-bottom: 1rem;
        ">
            <h4 style="margin: 0 0 1rem 0; color: #333;">🔧 Module Control</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Delete Module", key="aoc_module_delete", use_container_width=True):
            payload = manager.get_authentic_payload("module_delete")
            result = manager.send_system_command(client, manager.aps_topics["module_delete"], payload)
            if result:
                st.success("✅ Module Delete gesendet")
            else:
                st.error("❌ Fehler beim Senden")

        if st.button("🔍 AIQS Calibration", key="aoc_aiqs_calibration", use_container_width=True):
            result = manager.send_instant_action(client, "aiqs", "calibration")
            if result:
                st.success("✅ AIQS Calibration gesendet")
            else:
                st.error("❌ Fehler beim Senden")

    # Hidden button für Floating Action Button
    if st.button("🅿️ Park Factory", key="park-factory-btn", help="Floating Action Button"):
        payload = manager.get_authentic_payload("factory_park")
        result = manager.send_system_command(client, manager.aps_topics["factory_park"], payload)
        if result:
            st.success("✅ Park Factory gesendet")
        else:
            st.error("❌ Fehler beim Senden")

    # Status Information (authentisches APS-Design)
    st.markdown("### 📊 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏭 Factory Status", "🟢 Online", "Ready")
    
    with col2:
        st.metric("🚗 FTS Status", "🟢 Connected", "5iO4")
    
    with col3:
        st.metric("🔧 Modules", "🟢 4 Active", "All Connected")

    # Debug Information (erweiterte OMF-Integration)
    with st.expander("🔧 Debug Information & OMF Integration"):
        st.markdown("**APS Integration Status:**")
        st.json({
            "status": "✅ APS Integration aktiviert",
            "manager": "APSCommandsManager",
            "omf_logging": "✅ OMF-Logging aktiviert",
            "mqtt_client": "✅ MQTT-Client verfügbar",
            "aps_topics": manager.aps_topics,
            "authentic_payloads": "✅ Authentische APS-Payloads"
        })
        
        st.markdown("**Verfügbare APS Commands:**")
        for cmd, topic in manager.aps_topics.items():
            st.code(f"{cmd}: {topic}")
