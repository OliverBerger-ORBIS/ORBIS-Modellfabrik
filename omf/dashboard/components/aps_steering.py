"""
APS Steering Dashboard - Konsolidierte APS-Steuerung
Funktionale Steuerung für Factory, FTS, Modules und Orders
"""

import streamlit as st
from datetime import datetime, timezone
from omf.dashboard.tools.logging_config import get_logger


class APSSteeringManager:
    """Manager für APS Steering - OMF-konform mit APS-Standards"""

    def __init__(self):
        # OMF-Logging System
        self.logger = get_logger("omf.dashboard.components.aps_steering")
        
        # APS-Standard Commands (basierend auf Original APS-Analyse)
        self.commands = []
        self.last_update = None
        
        # Authentische APS-Topics (aus Original APS-Dashboard)
        self.aps_topics = {
            # Factory Commands
            "factory_status": "ccu/get/status",
            "factory_clean": "ccu/set/clean",
            "factory_settings": "ccu/get/settings",
            "factory_config": "ccu/get/config",
            "factory_info": "ccu/get/info",
            "factory_debug": "ccu/debug/info",
            
            # FTS Commands
            "fts_status": "ccu/get/ftsStatus",
            "fts_debug": "ccu/debug/fts",
            "fts_go_to": "ccu/set/ftsGoTo",
            "fts_battery": "ccu/get/ftsBattery",
            "fts_charge": "ccu/set/charge",
            "fts_battery_info": "ccu/get/ftsBatteryInfo",
            
            # Module Commands
            "module_status": "ccu/get/moduleStatus",
            "module_reset": "ccu/set/moduleReset",
            "module_calibration": "ccu/set/moduleCalibration",
            
            # Order Commands
            "order_status": "ccu/get/orderStatus",
            "order_start": "ccu/set/orderStart",
            "order_stop": "ccu/set/orderStop",
            "order_pause": "ccu/set/orderPause"
        }
        
        self.logger.info("🚀 APS Steering Manager initialisiert")

    def send_steering_command(self, mqtt_client, command, payload=None):
        """Sendet einen Steering Command nach APS-Standard mit OMF-Logging"""
        try:
            if payload is None:
                payload = {}
            
            # OMF-Logging für Analyse
            self.logger.info(f"🔍 APS Steering Command: Topic='{command}', Payload={payload}")
            
            # APS-Standard: Direkter MQTT Publish (QoS=2, retain=True)
            result = mqtt_client.publish(command, payload, qos=2, retain=True)
            
            self.logger.info(f"📤 APS Steering Command gesendet: Result={result}")
            return result

        except Exception as e:
            self.logger.error(f"❌ Fehler beim Senden des Steering Commands: {e}")
            st.error(f"❌ Fehler beim Senden des Steering Commands: {e}")
            return False


def show_aps_steering():
    """Konsolidierte APS Steering mit funktionaler Steuerung"""
    
    # Header mit authentischem APS-Design
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h1 style="color: white; margin: 0; text-align: center; font-size: 2rem;">
            🎮 APS Steering Center
        </h1>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; text-align: center;">
            Agile Production Simulation - Functional Control & Navigation
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Get MQTT client from session state
    client = st.session_state.get("mqtt_client")
    if not client:
        st.error("❌ MQTT Client nicht verfügbar")
        return

    # Initialize manager in session state (OMF-Standard)
    if "aps_steering_manager" not in st.session_state:
        st.session_state["aps_steering_manager"] = APSSteeringManager()

    manager = st.session_state["aps_steering_manager"]

    # Untertabs für verschiedene Steering-Bereiche
    steering_tab1, steering_tab2, steering_tab3, steering_tab4 = st.tabs(
        ["🏭 Factory Control", "🚗 FTS Navigation", "🔧 Module Control", "📋 Order Management"]
    )

    # Tab 1: Factory Control
    with steering_tab1:
        st.markdown("### 🏭 Factory Control")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Factory Status & Info:**")
            
            if st.button("📊 Factory Status", key="as_factory_status", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["factory_status"])
                if result:
                    st.success("✅ Factory Status gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("⚙️ Factory Settings", key="as_factory_settings", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["factory_settings"])
                if result:
                    st.success("✅ Factory Settings gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("📋 Factory Info", key="as_factory_info", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["factory_info"])
                if result:
                    st.success("✅ Factory Info gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            st.markdown("**Factory Actions:**")
            
            if st.button("🧹 Factory Clean", key="as_factory_clean", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["factory_clean"])
                if result:
                    st.success("✅ Factory Clean gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🔧 Factory Config", key="as_factory_config", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["factory_config"])
                if result:
                    st.success("✅ Factory Config gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🔍 Factory Debug", key="as_factory_debug", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["factory_debug"])
                if result:
                    st.success("✅ Factory Debug gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

    # Tab 2: FTS Navigation
    with steering_tab2:
        st.markdown("### 🚗 FTS Navigation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**FTS Status & Battery:**")
            
            if st.button("📊 FTS Status", key="as_fts_status", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["fts_status"])
                if result:
                    st.success("✅ FTS Status gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🔋 FTS Battery Status", key="as_fts_battery", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["fts_battery"])
                if result:
                    st.success("✅ FTS Battery Status gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🔋 FTS Battery Info", key="as_fts_battery_info", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["fts_battery_info"])
                if result:
                    st.success("✅ FTS Battery Info gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            st.markdown("**FTS Navigation:**")
            
            if st.button("🎯 FTS Go to DPS", key="as_fts_go_to_dps", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["fts_go_to"], {"target": "DPS"})
                if result:
                    st.success("✅ FTS Go to DPS gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🎯 FTS Go to HBW", key="as_fts_go_to_hbw", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["fts_go_to"], {"target": "HBW"})
                if result:
                    st.success("✅ FTS Go to HBW gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🎯 FTS Go to AIQS", key="as_fts_go_to_aiqs", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["fts_go_to"], {"target": "AIQS"})
                if result:
                    st.success("✅ FTS Go to AIQS gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        st.markdown("**FTS Charging Control:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("⚡ FTS Start Charging", key="as_fts_start_charging", use_container_width=True):
                payload = {"serialNumber": "5iO4", "charge": True, "timestamp": datetime.now(timezone.utc).isoformat()}
                result = manager.send_steering_command(client, manager.aps_topics["fts_charge"], payload)
                if result:
                    st.success("✅ FTS Start Charging gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            if st.button("⏹️ FTS Stop Charging", key="as_fts_stop_charging", use_container_width=True):
                payload = {"serialNumber": "5iO4", "charge": False, "timestamp": datetime.now(timezone.utc).isoformat()}
                result = manager.send_steering_command(client, manager.aps_topics["fts_charge"], payload)
                if result:
                    st.success("✅ FTS Stop Charging gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

    # Tab 3: Module Control
    with steering_tab3:
        st.markdown("### 🔧 Module Control")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Module Status:**")
            
            if st.button("📊 Module Status", key="as_module_status", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["module_status"])
                if result:
                    st.success("✅ Module Status gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            st.markdown("**Module Actions:**")
            
            if st.button("🔄 Module Reset", key="as_module_reset", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["module_reset"])
                if result:
                    st.success("✅ Module Reset gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("🔧 Module Calibration", key="as_module_calibration", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["module_calibration"])
                if result:
                    st.success("✅ Module Calibration gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

    # Tab 4: Order Management
    with steering_tab4:
        st.markdown("### 📋 Order Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Order Status:**")
            
            if st.button("📊 Order Status", key="as_order_status", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["order_status"])
                if result:
                    st.success("✅ Order Status gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

        with col2:
            st.markdown("**Order Control:**")
            
            if st.button("▶️ Order Start", key="as_order_start", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["order_start"])
                if result:
                    st.success("✅ Order Start gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("⏸️ Order Pause", key="as_order_pause", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["order_pause"])
                if result:
                    st.success("✅ Order Pause gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

            if st.button("⏹️ Order Stop", key="as_order_stop", use_container_width=True):
                result = manager.send_steering_command(client, manager.aps_topics["order_stop"])
                if result:
                    st.success("✅ Order Stop gesendet")
                else:
                    st.error("❌ Fehler beim Senden")

    # Debug Information (erweiterte OMF-Integration)
    with st.expander("🔧 Debug Information & OMF Integration"):
        st.markdown("**APS Steering Status:**")
        st.json({
            "status": "✅ APS Steering aktiviert",
            "manager": "APSSteeringManager",
            "omf_logging": "✅ OMF-Logging aktiviert",
            "mqtt_client": "✅ MQTT-Client verfügbar",
            "aps_topics": manager.aps_topics,
            "functional_control": "✅ Funktionale Steuerung aktiviert"
        })
        
        st.markdown("**Verfügbare APS Steering Commands:**")
        for cmd, topic in manager.aps_topics.items():
            st.code(f"{cmd}: {topic}")
