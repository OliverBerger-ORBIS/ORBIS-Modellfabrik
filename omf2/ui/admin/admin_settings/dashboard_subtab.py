"""
Dashboard Subtab für Admin Settings
Zeigt Konfigurationsinformationen aus omf2/config/*.yml Dateien an
Nur Anzeige - keine Änderungsmöglichkeiten
"""

from pathlib import Path

import streamlit as st
import yaml

from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_dashboard_subtab():
    """Rendert das Dashboard Subtab mit Konfigurationsinformationen"""

    st.header(f"{UISymbols.get_functional_icon('dashboard')} Dashboard Konfiguration")
    st.info("ℹ️ **Nur Anzeige** - Konfigurationsänderungen sind zur Laufzeit nicht möglich")

    # Projekt-Root ermitteln
    project_root = Path(__file__).parent.parent.parent.parent.parent
    config_path = project_root / "omf2" / "config"

    if not config_path.exists():
        st.error(f"❌ Config-Pfad nicht gefunden: {config_path}")
        return

    # Expandable Boxes statt Tabs
    with st.expander("🌐 MQTT Settings", expanded=True):
        _render_mqtt_settings(config_path)

    with st.expander("👥 User Roles", expanded=False):
        _render_user_roles(config_path)

    with st.expander("📱 Apps Configuration", expanded=False):
        _render_apps_config(config_path)

    with st.expander("🔧 System Information", expanded=False):
        _render_system_info()

    with st.expander("🔄 Auto-Refresh Status", expanded=False):
        _render_refresh_status()


def _render_mqtt_settings(config_path: Path):
    """Zeigt MQTT Settings an"""
    st.subheader("🌐 MQTT Broker Konfiguration")

    mqtt_file = config_path / "mqtt_settings.yml"
    if not mqtt_file.exists():
        st.warning("⚠️ mqtt_settings.yml nicht gefunden")
        return

    try:
        with open(mqtt_file, encoding="utf-8") as f:
            mqtt_config = yaml.safe_load(f)

        # Default Environment
        default_env = mqtt_config.get("default_environment", "N/A")
        st.info(f"🎯 **Standard Environment:** `{default_env}`")

        # Default MQTT Settings
        if "mqtt" in mqtt_config:
            default_mqtt = mqtt_config["mqtt"]
            st.subheader("⚙️ Standard MQTT Einstellungen")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("🌐 Host", default_mqtt.get("host", "N/A"))
                st.metric("🔌 Port", default_mqtt.get("port", "N/A"))
                st.metric("👤 Username", default_mqtt.get("username", "N/A"))

            with col2:
                st.metric("⏱️ Keep Alive", f"{default_mqtt.get('keepalive', 'N/A')}s")
                st.metric("🔄 Clean Session", "✅ Ja" if default_mqtt.get("clean_session", True) else "❌ Nein")
                st.metric("⏱️ Connection Timeout", f"{default_mqtt.get('connection_timeout', 'N/A')}s")

            with col3:
                st.metric("💾 QoS Default", default_mqtt.get("qos_default", "N/A"))
                st.metric("📦 Buffer Size", default_mqtt.get("buffer_size", "N/A"))
                st.metric("📚 Message History", default_mqtt.get("message_history_size", "N/A"))

        # Environment-spezifische Konfigurationen
        if "environments" in mqtt_config:
            st.subheader("🌍 Environment Konfigurationen")

            environments = mqtt_config["environments"]

            for env_name, env_config in environments.items():
                with st.expander(f"🌍 {env_name.upper()} Environment", expanded=(env_name == default_env)):
                    st.write(f"**Beschreibung:** {env_config.get('description', 'N/A')}")

                    if "mqtt" in env_config:
                        env_mqtt = env_config["mqtt"]

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("🌐 Host", env_mqtt.get("host", "N/A"))
                            st.metric("🔌 Port", env_mqtt.get("port", "N/A"))
                            st.metric("👤 Username", env_mqtt.get("username", "N/A"))

                        with col2:
                            st.metric("🆔 Client ID Postfix", env_mqtt.get("client_id_postfix", "N/A"))
                            st.metric("✅ Enabled", "✅ Ja" if env_mqtt.get("enabled", True) else "❌ Nein")
                            st.metric("🔐 TLS", "✅ Ja" if env_mqtt.get("tls", False) else "❌ Nein")

                        with col3:
                            st.metric("⏱️ Keep Alive", f"{env_mqtt.get('keepalive', 'N/A')}s")
                            st.metric("🔄 Clean Session", "✅ Ja" if env_mqtt.get("clean_session", True) else "❌ Nein")
                            st.metric("🔑 Password", "***" if env_mqtt.get("password") else "N/A")

        # Logging Settings
        if "logging" in mqtt_config:
            logging_config = mqtt_config["logging"]
            st.subheader("📝 Logging Einstellungen")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("📊 Log Level", logging_config.get("level", "N/A"))
                st.metric("🔗 Log Connections", "✅ Ja" if logging_config.get("log_connections", True) else "❌ Nein")

            with col2:
                st.metric("💬 Log Messages", "✅ Ja" if logging_config.get("log_messages", False) else "❌ Nein")
                st.metric(
                    "📡 Log Subscriptions", "✅ Ja" if logging_config.get("log_subscriptions", True) else "❌ Nein"
                )

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der MQTT Settings: {e}")
        logger.error(f"Failed to load MQTT settings: {e}")


def _render_user_roles(config_path: Path):
    """Zeigt User Roles an"""
    st.subheader("👥 Benutzerrollen")

    roles_file = config_path / "user_roles.yml"
    if not roles_file.exists():
        st.warning("⚠️ user_roles.yml nicht gefunden")
        return

    try:
        with open(roles_file, encoding="utf-8") as f:
            roles_config = yaml.safe_load(f)

        if "roles" in roles_config:
            roles = roles_config["roles"]

            for role_name, role_info in roles.items():
                with st.expander(f"👤 {role_name}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Beschreibung:** {role_info.get('description', 'N/A')}")
                        st.write(f"**Level:** {role_info.get('level', 'N/A')}")

                    with col2:
                        permissions = role_info.get("permissions", [])
                        st.write(f"**Berechtigungen:** {len(permissions)}")
                        for perm in permissions:
                            st.write(f"• {perm}")

        # Default Role
        if "default_role" in roles_config:
            st.info(f"🔧 **Standard-Rolle:** {roles_config['default_role']}")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der User Roles: {e}")
        logger.error(f"Failed to load user roles: {e}")


def _render_apps_config(config_path: Path):
    """Zeigt Apps Konfiguration an"""
    st.subheader("📱 Apps Konfiguration")

    apps_file = config_path / "apps.yml"
    if not apps_file.exists():
        st.warning("⚠️ apps.yml nicht gefunden")
        return

    try:
        with open(apps_file, encoding="utf-8") as f:
            apps_config = yaml.safe_load(f)

        if "apps" in apps_config:
            apps = apps_config["apps"]

            for app_name, app_info in apps.items():
                with st.expander(f"📱 {app_name}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Name:** {app_info.get('name', 'N/A')}")
                        st.write(f"**Version:** {app_info.get('version', 'N/A')}")
                        st.write(f"**Status:** {'✅ Aktiv' if app_info.get('enabled', True) else '❌ Inaktiv'}")

                    with col2:
                        st.write(f"**Beschreibung:** {app_info.get('description', 'N/A')}")
                        st.write(f"**Kategorie:** {app_info.get('category', 'N/A')}")

                        # Dependencies
                        deps = app_info.get("dependencies", [])
                        if deps:
                            st.write(f"**Abhängigkeiten:** {', '.join(deps)}")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Apps Konfiguration: {e}")
        logger.error(f"Failed to load apps config: {e}")


def _render_system_info():
    """Zeigt System-Informationen an"""
    st.subheader("🔧 System Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🐍 Python Version", "3.x")
        st.metric("📦 Streamlit", "Latest")

    with col2:
        st.metric("📁 Config Path", "omf2/config/")
        st.metric("🗂️ Registry Path", "omf2/registry/")

    with col3:
        st.metric("🌐 MQTT Client", "paho-mqtt")
        st.metric("📊 YAML Parser", "PyYAML")

    # Registry Stats (falls verfügbar)
    try:
        registry_manager = st.session_state.get("registry_manager")
        if registry_manager:
            stats = registry_manager.get_registry_stats()

        st.subheader("📊 Registry Statistiken")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("📡 Topics", stats.get("topics_count", 0))
            st.metric("📝 Schemas", stats.get("schemas_count", 0))

        with col2:
            st.metric("🔗 Mappings", stats.get("mappings_count", 0))
            st.metric("🌐 MQTT Clients", stats.get("mqtt_clients_count", 0))

        with col3:
            st.metric("🔧 Workpieces", stats.get("workpieces_count", 0))
            st.metric("🏭 Modules", stats.get("modules_count", 0))

        with col4:
            st.metric("🏢 Stations", stats.get("stations_count", 0))
            st.metric("🎮 TXT Controllers", stats.get("txt_controllers_count", 0))

        st.caption(f"⏰ Letztes Update: {stats.get('load_timestamp', 'N/A')}")

    except Exception as e:
        st.warning(f"⚠️ Registry Statistiken nicht verfügbar: {e}")
        logger.warning(f"Registry stats not available: {e}")


def _render_refresh_status():
    """Zeigt Auto-Refresh Status an"""
    import os

    st.subheader("🔄 Auto-Refresh Configuration Status")
    st.markdown("**Feature status for Redis-backed UI refresh mechanism**")

    # Redis-backed refresh status
    st.markdown("---")
    st.markdown("### Redis-Backed Refresh")

    col1, col2 = st.columns(2)

    with col1:
        try:
            from omf2.backend.refresh import get_all_refresh_groups

            groups = get_all_refresh_groups()
            redis_available = True
            st.metric("Redis Backend", "✅ Available")
            st.caption(f"📋 Active groups: {len(groups)}")
            if groups:
                st.caption(f"Groups: {', '.join(groups)}")
        except Exception as e:
            redis_available = False
            st.metric("Redis Backend", "❌ Unavailable")
            st.caption(f"⚠️ Error: {str(e)[:50]}")

    with col2:
        try:
            redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            # Mask password for security
            from urllib.parse import urlparse, urlunparse

            parsed = urlparse(redis_url)
            if parsed.password:
                netloc = f"{parsed.username}:***@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"
                safe_url = urlunparse((parsed.scheme, netloc, parsed.path, "", "", ""))
            else:
                safe_url = redis_url

            st.metric("Redis URL", "Configured")
            st.caption(f"🔌 {safe_url}")
        except Exception as e:
            st.metric("Redis URL", "Error")
            st.caption(f"⚠️ {str(e)[:50]}")

    # Refresh mechanism summary
    st.markdown("---")
    if redis_available:
        st.success("✅ Redis-backed refresh mechanism is operational")
        st.info("💡 Gateway triggers refreshes via `request_refresh()` → Redis → UI polls backend")
    else:
        st.warning("⚠️ Redis is not available. In-memory fallback is active (not shared across processes)")
        st.info("💡 To enable full refresh: Start Redis and configure REDIS_URL")

    # Developer info
    st.markdown("---")
    st.markdown("### Developer Information")
    st.caption("📝 Refresh path: Gateway → `omf2.backend.refresh.request_refresh()` → Redis → UI polling")
    st.caption("🔍 Manual refresh: Always available via F5 or 'Refresh Dashboard' button")
    st.caption("📚 See: docs/operations/auto_refresh.md for details")
