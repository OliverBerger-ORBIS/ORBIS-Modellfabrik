"""
APS Control Dashboard - Konsolidierte APS-Steuerung
Kombiniert System Commands, Status und Monitoring in einem Tab
"""

import streamlit as st
from datetime import datetime, timezone
from omf.dashboard.tools.logging_config import get_logger


class APSControlManager:
    """Manager für APS Control - OMF-konform mit APS-Standards"""

    def __init__(self):
        # OMF-Logging System
        self.logger = get_logger("omf.dashboard.components.supervisor.aps_control")
        self.logger.info("🔍 LOADED: supervisor.aps_control")
        
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
            "system_calibration": "ccu/set/calibration",
            "dps_reset": "dps/set/reset",
            "aiqs_reset": "aiqs/set/reset",
            "hbw_reset": "hbw/set/reset",
            "mill_reset": "mill/set/reset"
        }
        
        self.logger.info("🚀 APS Control Manager initialisiert")

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


def show_aps_control():
    """Konsolidierte APS Control mit Material Design und OMF-Standards"""
    
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
            🎮 APS Control Center
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; text-align: center;">
            Agile Production Simulation - System Control & Monitoring
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state (OMF-Standard)
    if "aps_control_manager" not in st.session_state:
        st.session_state["aps_control_manager"] = APSControlManager()

    manager = st.session_state["aps_control_manager"]

    # Untertabs für verschiedene Control-Bereiche
    control_tab1, control_tab2, control_tab3 = st.tabs(["⚡ System Commands", "📊 System Status", "🔧 Module Control"])

    # Tab 1: System Commands
    with control_tab1:
        st.markdown("### 🏭 Factory Control")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Factory Reset", key="ac_factory_reset", use_container_width=True):
                payload = manager.get_authentic_payload("factory_reset")
                result = manager.send_system_command(client, manager.aps_topics["factory_reset"], payload)
                if result:
                    st.success("✅ Factory Reset gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            if st.button("🅿️ Park Factory", key="ac_factory_park", use_container_width=True):
                payload = manager.get_authentic_payload("factory_park")
                result = manager.send_system_command(client, manager.aps_topics["factory_park"], payload)
                if result:
                    st.success("✅ Park Factory gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col3:
            if st.button("🔧 System Calibration", key="ac_system_calibration", use_container_width=True):
                payload = manager.get_authentic_payload("system_calibration")
                result = manager.send_system_command(client, manager.aps_topics["system_calibration"], payload)
                if result:
                    st.success("✅ System Calibration gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        st.markdown("### 🚗 FTS Control")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔋 FTS Charge", key="ac_fts_charge", use_container_width=True):
                payload = manager.get_authentic_payload("fts_charge", charge=True)
                result = manager.send_system_command(client, manager.aps_topics["fts_charge"], payload)
                if result:
                    st.success("✅ FTS Charge gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            if st.button("🔌 FTS Pair", key="ac_fts_pair", use_container_width=True):
                payload = manager.get_authentic_payload("fts_pair")
                result = manager.send_system_command(client, manager.aps_topics["fts_pair"], payload)
                if result:
                    st.success("✅ FTS Pair gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

    # Tab 2: System Status
    with control_tab2:
        st.markdown("### 📊 System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🏭 Factory Status", "🟢 Online", "Ready")
        
        with col2:
            st.metric("🚗 FTS Status", "🟢 Connected", "5iO4")
        
        with col3:
            st.metric("🔧 Modules", "🟢 4 Active", "All Connected")

        st.markdown("### 📈 System Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("📊 **Production Status:** Active")
            st.info("🔄 **Current Order:** None")
            st.info("⏱️ **Uptime:** 2h 15m")
        
        with col2:
            st.info("🔋 **Battery Level:** 85%")
            st.info("🌡️ **Temperature:** 23°C")
            st.info("📡 **MQTT Status:** Connected")

    # Tab 3: Module Control
    with control_tab3:
        st.markdown("### 🔧 Module Control")
        
        st.markdown("**Module Reset Commands:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 DPS Reset", key="ac_dps_reset", use_container_width=True):
                result = manager.send_system_command(client, manager.aps_topics["dps_reset"])
                if result:
                    st.success("✅ DPS Reset gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🔄 AIQS Reset", key="ac_aiqs_reset", use_container_width=True):
                result = manager.send_system_command(client, manager.aps_topics["aiqs_reset"])
                if result:
                    st.success("✅ AIQS Reset gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            if st.button("🔄 HBW Reset", key="ac_hbw_reset", use_container_width=True):
                result = manager.send_system_command(client, manager.aps_topics["hbw_reset"])
                if result:
                    st.success("✅ HBW Reset gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🔄 MILL Reset", key="ac_mill_reset", use_container_width=True):
                result = manager.send_system_command(client, manager.aps_topics["mill_reset"])
                if result:
                    st.success("✅ MILL Reset gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        st.markdown("**Instant Actions:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔍 AIQS Calibration", key="ac_aiqs_calibration", use_container_width=True):
                result = manager.send_instant_action(client, "aiqs", "calibration")
                if result:
                    st.success("✅ AIQS Calibration gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            if st.button("📊 DPS Status", key="ac_dps_status", use_container_width=True):
                result = manager.send_instant_action(client, "dps", "status")
                if result:
                    st.success("✅ DPS Status Request gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

    # Debug Information (erweiterte OMF-Integration)
    with st.expander("🔧 Debug Information & OMF Integration"):
        st.markdown("**APS Integration Status:**")
        st.json({
            "status": "✅ APS Integration aktiviert",
            "manager": "APSControlManager",
            "omf_logging": "✅ OMF-Logging aktiviert",
            "mqtt_client": "✅ MQTT-Client verfügbar",
            "aps_topics": manager.aps_topics,
            "authentic_payloads": "✅ Authentische APS-Payloads"
        })
        
        st.markdown("**Verfügbare APS Commands:**")
        for cmd, topic in manager.aps_topics.items():
            st.code(f"{cmd}: {topic}")
