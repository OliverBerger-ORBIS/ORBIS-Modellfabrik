#!/usr/bin/env python3
"""
CCU Module Manager - Business-Logik für Module-Status-Verarbeitung
Entspricht der overview_module_status.py Funktionalität, aber für CCU
"""

from typing import Any, Dict, List, Optional

from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


class CcuModuleManager:
    """
    CCU Module Manager - Business-Logik für Module-Status-Verarbeitung

    Verantwortlichkeiten:
    - Real-time Status-Verarbeitung
    - Module-Status-Caching (Session State)
    - Business-Logik für Connection/Availability
    - Integration mit CCU Gateway
    """

    def __init__(self, registry_manager=None):
        """
        Initialize CCU Module Manager

        Args:
            registry_manager: Registry Manager instance
        """
        self.registry_manager = registry_manager or get_registry_manager()
        self._initialized = False

        # Module configuration and icons (NO HARDCODED STRINGS - loaded from Registry)
        self.MODULE_ICONS = None  # Lazy Loading - wird beim ersten Zugriff geladen

        # NEU: State-Holder für Module-Status
        self.module_status = {}  # {module_id: module_status_data}

        # Performance: Shopfloor layout cache
        self._factory_config_cache = None

        # NEU: State-Holder für Factsheet-Status
        self.factsheet_status = {}  # {module_id: factsheet_data}

        logger.info("🏗️ CCU Module Manager initialized with State-Holder")

    def process_module_message(self, topic: str, payload: Dict[str, Any], meta: Optional[Dict] = None):
        """
        NEU: Verarbeitet eingehende Module-Message und updated State
        Wird vom Gateway über Topic-Routing aufgerufen

        Args:
            topic: MQTT Topic (String)
            payload: Payload-Daten (Dict ohne MQTT-Metadaten)
            meta: Metadaten (timestamp, raw, qos, retain)
        """
        try:
            # Extract module ID from topic
            module_id = self._extract_module_id_from_topic(topic)
            if not module_id:
                return

            # Check if this is a factsheet message
            if "/factsheet" in topic:
                self.process_factsheet_message(module_id, payload, topic, meta)
            else:
                # Update module status in State-Holder (mit Topic-Kontext)
                self.update_module_status(module_id, payload, self.module_status, topic)

        except Exception as e:
            logger.error(f"❌ Failed to process module message for topic {topic}: {e}")

    def process_factsheet_message(
        self, module_id: str, payload: Dict[str, Any], topic: str, meta: Optional[Dict] = None
    ):
        """
        NEU: Verarbeitet Factsheet-Message für Configured Status

        Args:
            module_id: Module identifier
            payload: Factsheet payload
            topic: MQTT topic
            meta: Optional metadata
        """
        try:
            logger.debug(f"📋 Processing factsheet for module {module_id}")
            logger.debug(f"📋 Topic: {topic}")
            logger.debug(f"📋 Payload keys: {list(payload.keys()) if payload else 'None'}")
            logger.debug(f"📋 Meta: {meta}")

            # Store factsheet data in State-Holder
            self.factsheet_status[module_id] = {
                "factsheet_data": payload,
                "topic": topic,
                "last_update": meta.get("timestamp") if meta else "Unknown",
                "configured": True,  # If factsheet exists, module is configured
            }

            logger.info(f"✅ Module {module_id} factsheet received - configured: True")
            logger.debug(f"📋 Factsheet status updated for {module_id}: {len(self.factsheet_status)} total factsheets")

        except Exception as e:
            logger.error(f"❌ Failed to process factsheet for module {module_id}: {e}")

    def _get_module_icons(self) -> Dict[str, str]:
        """Lazy Loading für Module Icons - wird beim ersten Zugriff geladen"""
        if self.MODULE_ICONS is None:
            self.MODULE_ICONS = self._load_module_icons_from_registry()
        return self.MODULE_ICONS

    def _load_module_icons_from_registry(self) -> Dict[str, str]:
        """Loads module icons from registry (NO HARDCODED STRINGS)."""
        try:
            logger.debug("🔍 Loading module icons from registry...")

            # Get all modules from Registry
            modules = self.registry_manager.get_modules()
            logger.debug(f"🔍 Found {len(modules)} modules in registry")

            module_icons = {}

            for module_id, module_info in modules.items():
                # Get icon from Registry module info
                icon = module_info.get("icon", "❓")
                module_icons[module_id] = icon
                logger.debug(f"🔍 Module {module_id}: {icon}")

                # NO duplicate mapping by name - only use Module IDs

            logger.info(f"✅ Loaded {len(module_icons)} module icons from registry")
            return module_icons

        except Exception as e:
            logger.error(f"❌ Failed to load module icons from Registry: {e}")
            import traceback

            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            # Fallback to default icons
            return {"default": "❓"}

    def get_all_modules(self) -> Dict[str, Dict]:
        """
        Get all configured modules from registry

        Returns:
            Dict with module information
        """
        try:
            # Get modules from registry
            modules = self.registry_manager.get_modules()
            if not modules:
                logger.warning("⚠️ No modules found in registry")
                return {}

            return modules

        except Exception as e:
            logger.error(f"❌ Failed to get modules: {e}")
            return {}

    def get_module_status(self, module_id: str, status_store: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get real-time status for a specific module

        Args:
            module_id: Module identifier
            status_store: Module status store from session state

        Returns:
            Module status information
        """
        if module_id not in status_store:
            return {"connected": False, "available": "Unknown", "message_count": 0, "last_update": "Never"}

        return status_store[module_id]

    def update_module_status(
        self, module_id: str, payload: Dict[str, Any], status_store: Dict[str, Any], topic: str = ""
    ) -> None:
        """
        Update module status from payload data (Business-Manager Pattern)

        Args:
            module_id: Module identifier
            payload: Payload-Daten (Dict ohne MQTT-Metadaten)
            status_store: Module status store to update
        """
        try:
            # Initialize module status if not exists
            if module_id not in status_store:
                status_store[module_id] = {
                    "connected": False,
                    "available": "Unknown",
                    "message_count": 0,
                    "last_update": "Never",
                }

            # Payload ist bereits ein Dict - keine JSON-Parsing nötig!
            # (Business-Manager Pattern: direkte Payload-Verarbeitung)

            # Extract module status from payload (Business-Manager Pattern)
            # Based on analysis of real MQTT data from ai-not-ok-rot_1.log
            if "/connection" in topic:
                # Connection Messages: connectionState → connected
                if "connectionState" in payload:
                    connection_state = payload.get("connectionState", "OFFLINE")
                    connected = connection_state == "ONLINE"
                    status_store[module_id]["connected"] = connected

            elif "/state" in topic:
                # State Messages: actionState.state + paused → available
                action_state_obj = payload.get("actionState")
                paused = payload.get("paused", False)

                if action_state_obj is None:
                    # Fallback: Wenn actionState null ist, aber Modul connected → READY
                    if status_store[module_id].get("connected", False):
                        available = "READY"
                    else:
                        available = "Unknown"
                else:
                    # Normale Verarbeitung mit actionState
                    action_state = action_state_obj.get("state", "Unknown")

                    if paused:
                        available = "BLOCKED"
                    elif action_state == "RUNNING":
                        available = "BUSY"
                    elif action_state == "FINISHED":
                        available = "READY"
                    else:
                        available = action_state  # Fallback

                status_store[module_id]["available"] = available

            elif "/factsheet" in topic:
                # Factsheet Messages: factsheet vorhanden → configured = true
                status_store[module_id]["configured"] = True
                status_store[module_id]["factsheet_data"] = payload

            elif "ccu/pairing/state" in topic:
                # Pairing Messages: modules array → connected + available
                if "modules" in payload:
                    modules = payload.get("modules", [])
                    for module_info in modules:
                        if module_info.get("serialNumber") == module_id:
                            if "connected" in module_info:
                                connected = module_info.get("connected", False)
                                status_store[module_id]["connected"] = connected

                            if "available" in module_info:
                                available = module_info.get("available", "Unknown")
                                status_store[module_id]["available"] = available
                            break

            # Update message count and timestamp
            status_store[module_id]["message_count"] += 1
            # Always use string format for last_update to avoid Arrow conversion issues
            from datetime import datetime

            status_store[module_id]["last_update"] = datetime.now().strftime("%H:%M:%S")

        except Exception as e:
            logger.error(f"❌ Failed to update module status for {module_id}: {e}")

    def process_module_messages(self, ccu_gateway) -> Dict[str, Any]:
        """
        Process all module messages from CCU Gateway buffers

        Args:
            ccu_gateway: CCU Gateway instance

        Returns:
            Updated module status store
        """
        try:
            # Initialize status store
            status_store = {}

            # Get all buffers via CCU Gateway (Gateway-Pattern)
            if not ccu_gateway:
                logger.warning("⚠️ No CCU Gateway available")
                return {}

            # Get buffers via Gateway (Gateway-Pattern)
            all_buffers = ccu_gateway.get_all_message_buffers()
            for topic, messages in all_buffers.items():
                if not messages:
                    continue

                # Extract module ID from topic
                module_id = self._extract_module_id_from_topic(topic)
                if not module_id:
                    continue

                # Process latest message for status
                latest_message = messages[-1] if messages else None
                if latest_message:
                    # Add topic information to message for processing
                    latest_message["topic"] = topic
                    self.update_module_status(module_id, latest_message, status_store)

            return status_store

        except Exception as e:
            logger.error(f"❌ Failed to process module messages: {e}")
            return {}

    def _extract_module_id_from_topic(self, topic: str) -> Optional[str]:
        """
        Extract module ID from MQTT topic using Registry Module IDs (NO HARDCODED STRINGS)

        Args:
            topic: MQTT topic string

        Returns:
            Module ID or None
        """
        try:
            # Get all module IDs from Registry (NO HARDCODED STRINGS)
            modules = self.registry_manager.get_modules()
            module_ids = list(modules.keys())

            # Get topic patterns from Registry (NO HARDCODED STRINGS)
            topic_patterns = self._get_topic_patterns_from_registry()

            # Check each topic pattern from Registry
            for pattern_info in topic_patterns:
                pattern = pattern_info["pattern"]
                module_id_position = pattern_info["module_id_position"]

                if topic.startswith(pattern):
                    parts = topic.split("/")
                    if len(parts) >= module_id_position + 1:
                        potential_module_id = parts[module_id_position]
                        # Check if this module ID exists in Registry
                        if potential_module_id in module_ids:
                            return potential_module_id

            return None

        except Exception as e:
            logger.error(f"❌ Failed to extract module ID from topic {topic}: {e}")
            return None

    def _get_topic_patterns_from_registry(self) -> List[Dict[str, Any]]:
        """
        Get topic patterns from Registry (NO HARDCODED STRINGS)

        Returns:
            List of topic pattern info
        """
        try:
            # Get topic patterns from Registry configuration
            mqtt_clients = self.registry_manager.get_mqtt_clients()
            ccu_client = mqtt_clients.get("ccu_mqtt_client", {})
            subscribed_topics = ccu_client.get("subscribed_topics", [])

            # Extract patterns from subscribed topics
            patterns = set()
            for topic_info in subscribed_topics:
                if isinstance(topic_info, dict):
                    topic = topic_info.get("topic", "")
                else:
                    topic = str(topic_info)

                # Extract pattern from topic (e.g., "module/v1/ff/+/state" -> "module/v1/ff/")
                if topic.startswith("module/v1/ff/"):
                    patterns.add("module/v1/ff/")
                elif topic.startswith("fts/v1/ff/"):
                    patterns.add("fts/v1/ff/")

            # Convert to pattern info list
            topic_patterns = []
            for pattern in patterns:
                if pattern == "module/v1/ff/":
                    # Direkte Module Topics: module/v1/ff/SVR4H73275/state
                    topic_patterns.append({"pattern": pattern, "module_id_position": 3, "type": "module"})
                    # NodeRed Module Topics: module/v1/ff/NodeRed/SVR4H73275/state
                    topic_patterns.append(
                        {"pattern": "module/v1/ff/NodeRed/", "module_id_position": 4, "type": "module_nodered"}
                    )
                elif pattern == "fts/v1/ff/":
                    topic_patterns.append({"pattern": pattern, "module_id_position": 3, "type": "fts"})

            return topic_patterns

        except Exception as e:
            logger.error(f"❌ Failed to get topic patterns from Registry: {e}")
            return []

    def get_module_icon(self, module_id: str) -> str:
        """
        Get module icon from module ID (Registry-based)

        Args:
            module_id: Module identifier

        Returns:
            Icon string from Registry
        """
        # Direct lookup in Registry-based MODULE_ICONS
        return self._get_module_icons().get(module_id, "❓")  # Unknown module

    def get_module_icon_html(self, module_id: str, size_px: int = 24) -> str:
        """
        Get module icon as SVG HTML from module ID.

        Maps module serial ID → module type name → SVG icon via get_icon_html().
        Falls back to emoji icon if SVG not available.

        Args:
            module_id: Module serial ID (e.g., "SVR3QA0022")
            size_px: Size in pixels for the icon (default: 24)

        Returns:
            HTML string with inline SVG or emoji in span

        Example:
            >>> manager.get_module_icon_html("SVR3QA0022", size_px=20)
            '<svg width="20">...</svg>'  # HBW SVG icon
        """
        try:
            # Import here to avoid circular dependencies
            from omf2.ui.common.symbols import get_icon_html

            # Get module info from registry to find the type/name
            modules = self.get_all_modules()
            module_info = modules.get(module_id)

            if module_info:
                # Get the module name/type (e.g., "HBW", "DRILL")
                module_name = module_info.get("name", module_id)

                # Try to get SVG icon using the module type name
                icon_html = get_icon_html(module_name, size_px=size_px)

                # Check if we got SVG or just emoji fallback
                if "<svg" in icon_html:
                    logger.debug(f"✅ Got SVG icon for {module_id} ({module_name})")
                    return icon_html
                else:
                    logger.debug(f"⚠️ No SVG for {module_id} ({module_name}), using emoji")
                    return icon_html
            else:
                logger.warning(f"⚠️ Module {module_id} not found in registry")
                # Fallback to emoji icon
                emoji_icon = self.get_module_icon(module_id)
                return f'<span style="font-size: {size_px}px;">{emoji_icon}</span>'

        except Exception as e:
            logger.error(f"❌ Failed to get SVG icon for {module_id}: {e}")
            # Final fallback to emoji
            emoji_icon = self.get_module_icon(module_id)
            return f'<span style="font-size: {size_px}px;">{emoji_icon}</span>'

    def get_availability_display(self, availability: str) -> str:
        """
        Get availability display with icon (UISymbols-based) - CORRECTED to match aps_modules.py

        Args:
            availability: Availability status string (READY, BUSY, BLOCKED, etc.)

        Returns:
            Display string with icon from UISymbols
        """
        # Exact match with aps_modules.py logic
        if availability == "READY":
            icon = UISymbols.get_status_icon("available")
            return f"{icon} Available"
        elif availability == "BUSY":
            icon = UISymbols.get_status_icon("busy")
            return f"{icon} Busy"
        elif availability == "BLOCKED":
            icon = UISymbols.get_status_icon("blocked")
            return f"{icon} Blocked"
        else:
            # For any other status, show with unknown icon
            icon = UISymbols.get_status_icon("unknown")
            return f"{icon} {availability}"

    def get_connection_display(self, connected: bool) -> str:
        """
        Get connection display with icon (UISymbols-based)

        Args:
            connected: Connection status

        Returns:
            Display string with icon from UISymbols
        """
        if connected:
            icon = UISymbols.get_status_icon("connected")
            return f"{icon} Connected"
        else:
            icon = UISymbols.get_status_icon("disconnected")
            return f"{icon} Disconnected"

    def is_module_configured(self, module_id: str, factory_config: Dict[str, Any] = None) -> bool:
        """
        Check if module is configured (has factsheet message)

        Args:
            module_id: Module identifier (serial number)
            factory_config: Factory configuration (not used anymore, kept for compatibility)

        Returns:
            True if module has factsheet (configured), False otherwise
        """
        try:
            # Check if factsheet exists in State-Holder
            configured = module_id in self.factsheet_status and self.factsheet_status[module_id].get(
                "configured", False
            )
            logger.debug(
                f"📋 Module {module_id} configured check: {configured} (factsheet exists: {module_id in self.factsheet_status})"
            )
            return configured
        except Exception as e:
            logger.error(f"❌ Error checking configured status for {module_id}: {e}")
            return False

    def get_module_position(self, module_id: str) -> Optional[List[int]]:
        """
        Get module position from shopfloor layout

        Args:
            module_id: Module identifier (serial number)

        Returns:
            Position as [row, col] or None if not found
        """
        try:
            factory_config = self.get_factory_configuration()
            modules = factory_config.get("modules", [])

            for module in modules:
                if module.get("serialNumber") == module_id:
                    return module.get("position")

            return None
        except Exception:
            return None

    def get_module_position_display(self, module_id: str) -> str:
        """
        Get module position display string

        Args:
            module_id: Module identifier (serial number)

        Returns:
            Position display string like "[0,1]" or "Not Positioned"
        """
        position = self.get_module_position(module_id)
        if position:
            position_display = f"[{position[0]},{position[1]}]"
            logger.debug(f"📋 Module {module_id} position: {position_display}")
            return position_display
        else:
            logger.debug(f"📋 Module {module_id} position: Not Positioned")
            return "Not Positioned"

    def get_configuration_display(self, configured: bool) -> str:
        """
        Get configuration display with icon (UISymbols-based)

        Args:
            configured: Configuration status

        Returns:
            Display string with icon from UISymbols
        """
        if configured:
            icon = UISymbols.get_status_icon("configured")
            return f"{icon} Configured"
        else:
            icon = UISymbols.get_status_icon("not_configured")
            return f"{icon} Not Configured"

    def get_factory_configuration(self) -> Dict[str, Any]:
        """
        Get factory configuration from shopfloor layout (with caching)

        Returns:
            Factory configuration dict from shopfloor_layout.json
        """
        # Return cached data if available
        if self._factory_config_cache is not None:
            logger.debug("📋 Using cached shopfloor layout")
            return self._factory_config_cache

        try:
            from omf2.ccu.config_loader import get_ccu_config_loader

            config_loader = get_ccu_config_loader()
            layout_data = config_loader.load_shopfloor_layout()

            # Cache the result
            self._factory_config_cache = layout_data

            logger.debug(f"📋 Loaded and cached shopfloor layout: {len(layout_data.get('modules', []))} modules")
            return layout_data
        except Exception as e:
            logger.error(f"❌ Failed to load shopfloor layout: {e}")
            return {}

    def invalidate_factory_config_cache(self):
        """
        Invalidate the factory configuration cache
        Call this when shopfloor layout changes
        """
        self._factory_config_cache = None
        logger.debug("📋 Factory configuration cache invalidated")

    def get_factsheet_status(self) -> Dict[str, Any]:
        """
        Get factsheet status for all modules

        Returns:
            Dict with factsheet status for all modules
        """
        return self.factsheet_status.copy()

    def get_module_factsheet_status(self, module_id: str) -> Dict[str, Any]:
        """
        Get factsheet status for a specific module

        Args:
            module_id: Module identifier

        Returns:
            Dict with factsheet status or empty dict if not found
        """
        return self.factsheet_status.get(module_id, {})

    def get_module_status_from_state(self, module_id: str = None) -> Dict[str, Any]:
        """
        NEU: Liest Module-Status aus State-Holder (für UI)

        Args:
            module_id: Spezifische Module-ID (optional)

        Returns:
            Module-Status aus State-Holder
        """
        if module_id:
            return self.module_status.get(module_id, {})
        return dict(self.module_status)

    def get_module_state(self) -> Dict[str, Any]:
        """
        NEU: Gibt aktuellen Module-State zurück

        Returns:
            Vollständiger Module-State
        """
        return {
            "module_status": dict(self.module_status),
            "total_modules": len(self.module_status),
            "module_ids": list(self.module_status.keys()),
            "last_update": max([status.get("last_update", "") for status in self.module_status.values()], default=""),
        }


# Singleton Factory
_ccu_module_manager = None


def get_ccu_module_manager() -> CcuModuleManager:
    """
    Factory-Funktion für CCU Module Manager Singleton

    Returns:
        CCU Module Manager instance
    """
    global _ccu_module_manager
    if _ccu_module_manager is None:
        _ccu_module_manager = CcuModuleManager()
    return _ccu_module_manager
