#!/usr/bin/env python3
"""
CCU Module Manager - Business-Logik für Module-Status-Verarbeitung
Entspricht der overview_module_status.py Funktionalität, aber für CCU
"""

import json
import time
from typing import Dict, List, Any, Optional
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
        self.MODULE_ICONS = self._load_module_icons_from_registry()
        
        # NEU: State-Holder für Module-Status
        self.module_status = {}  # {module_id: module_status_data}
        
        logger.info("🏗️ CCU Module Manager initialized with State-Holder")
    
    def process_module_message(self, topic: str, payload: Dict[str, Any]):
        """
        NEU: Verarbeitet eingehende Module-Message und updated State
        Wird vom MQTT-Client über Business-Function-Callback aufgerufen
        
        Args:
            topic: MQTT Topic (String)
            payload: Payload-Daten (Dict ohne MQTT-Metadaten)
        """
        try:
            logger.debug(f"🔔 ModuleManager received message for topic: {topic}")
            
            # Extract module ID from topic
            module_id = self._extract_module_id_from_topic(topic)
            if not module_id:
                logger.debug(f"⚠️ Could not extract module ID from topic: {topic}")
                return
            
            logger.info(f"🔍 Processing module message for {module_id} from topic: {topic}")
            
            # Update module status in State-Holder (mit Topic-Kontext)
            self.update_module_status(module_id, payload, self.module_status, topic)
            
            logger.info(f"✅ Updated module state for {module_id}")
                
        except Exception as e:
            logger.error(f"❌ Failed to process module message for topic {topic}: {e}")
    
    def _load_module_icons_from_registry(self) -> Dict[str, str]:
        """Loads module icons from registry (NO HARDCODED STRINGS)."""
        try:
            # Get all modules from Registry
            modules = self.registry_manager.get_modules()
            module_icons = {}
            
            for module_id, module_info in modules.items():
                # Get icon from Registry module info
                icon = module_info.get('icon', '❓')
                module_icons[module_id] = icon
                
                # NO duplicate mapping by name - only use Module IDs
            
            logger.info(f"📊 Loaded {len(module_icons)} module icons from Registry")
            return module_icons
            
        except Exception as e:
            logger.error(f"❌ Failed to load module icons from Registry: {e}")
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
            
            logger.info(f"📊 Loaded {len(modules)} modules from registry")
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
            return {
                "connected": False,
                "available": "Unknown",
                "message_count": 0,
                "last_update": "Never"
            }
        
        return status_store[module_id]
    
    def update_module_status(self, module_id: str, payload: Dict[str, Any], status_store: Dict[str, Any], topic: str = "") -> None:
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
                    "last_update": "Never"
                }
            
            # Payload ist bereits ein Dict - keine JSON-Parsing nötig!
            # (Business-Manager Pattern: direkte Payload-Verarbeitung)
            
            # DEBUG: Log payload structure
            logger.debug(f"Module {module_id} payload keys: {list(payload.keys())}")
            
            # Extract connection state from payload (Business-Manager Pattern)
            if "/connection" in topic:
                # Connection message: check for connected field
                if "connected" in payload:
                    connected = payload.get("connected", False)
                    status_store[module_id]["connected"] = connected
                    logger.debug(f"Module {module_id} connection state from payload: {connected}")
                else:
                    logger.warning(f"⚠️ Module {module_id} connection message without 'connected' field: {list(payload.keys())}")
                    
            elif "/state" in topic:
                # State message: check for available field
                if "available" in payload:
                    available = payload.get("available")
                    status_store[module_id]["available"] = available
                    logger.debug(f"Module {module_id} available state from payload: {available}")
                else:
                    logger.warning(f"⚠️ Module {module_id} state message without 'available' field: {list(payload.keys())}")
            
            # Update message count and timestamp
            status_store[module_id]["message_count"] += 1
            # Always use string format for last_update to avoid Arrow conversion issues
            from datetime import datetime
            status_store[module_id]["last_update"] = datetime.now().strftime('%H:%M:%S')
            
            logger.debug(f"📊 Updated status for {module_id}: {status_store[module_id]}")
            
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
            logger.info(f"📊 Retrieved {len(all_buffers)} buffers via CCU Gateway")
            
            for topic, messages in all_buffers.items():
                if not messages:
                    continue
                
                logger.debug(f"📡 Processing topic: {topic} with {len(messages)} messages")
                
                # Extract module ID from topic
                module_id = self._extract_module_id_from_topic(topic)
                if not module_id:
                    logger.debug(f"⚠️ Could not extract module ID from topic: {topic}")
                    continue
                
                logger.info(f"🔍 DEBUG: Extracted module ID: {module_id} from topic: {topic}")
                
                # Process latest message for status
                latest_message = messages[-1] if messages else None
                if latest_message:
                    logger.info(f"🔍 DEBUG: Processing latest message for {module_id}:")
                    logger.info(f"🔍 DEBUG: Message structure: {latest_message}")
                    logger.info(f"🔍 DEBUG: Message payload: {latest_message.get('payload', 'NO_PAYLOAD')}")
                    
                    # Add topic information to message for processing
                    latest_message["topic"] = topic
                    self.update_module_status(module_id, latest_message, status_store)
            
            logger.info(f"📊 Processed module messages for {len(status_store)} modules")
            
            # DEBUG: Log detailed status for each module
            for module_id, status in status_store.items():
                logger.info(f"🔍 DEBUG Module {module_id}: connected={status.get('connected')}, available={status.get('available')}, messages={status.get('message_count')}")
            
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
                pattern = pattern_info['pattern']
                module_id_position = pattern_info['module_id_position']
                
                if topic.startswith(pattern):
                    parts = topic.split("/")
                    if len(parts) >= module_id_position + 1:
                        potential_module_id = parts[module_id_position]
                        # Check if this module ID exists in Registry
                        if potential_module_id in module_ids:
                            logger.debug(f"📊 Extracted module ID {potential_module_id} from topic {topic}")
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
            ccu_client = mqtt_clients.get('ccu_mqtt_client', {})
            subscribed_topics = ccu_client.get('subscribed_topics', [])
            
            # Extract patterns from subscribed topics
            patterns = set()
            for topic_info in subscribed_topics:
                if isinstance(topic_info, dict):
                    topic = topic_info.get('topic', '')
                else:
                    topic = str(topic_info)
                
                # Extract pattern from topic (e.g., "module/v1/ff/+/state" -> "module/v1/ff/")
                if topic.startswith("module/v1/ff/"):
                    patterns.add('module/v1/ff/')
                elif topic.startswith("fts/v1/ff/"):
                    patterns.add('fts/v1/ff/')
            
            # Convert to pattern info list
            topic_patterns = []
            for pattern in patterns:
                if pattern == 'module/v1/ff/':
                    topic_patterns.append({
                        'pattern': pattern,
                        'module_id_position': 3,
                        'type': 'module'
                    })
                elif pattern == 'fts/v1/ff/':
                    topic_patterns.append({
                        'pattern': pattern,
                        'module_id_position': 3,
                        'type': 'fts'
                    })
            
            logger.debug(f"📊 Loaded {len(topic_patterns)} topic patterns from Registry: {[p['pattern'] for p in topic_patterns]}")
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
        return self.MODULE_ICONS.get(module_id, "❓")  # Unknown module
    
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
            icon = UISymbols.get_status_icon('available')
            return f"{icon} Available"
        elif availability == "BUSY":
            icon = UISymbols.get_status_icon('busy')
            return f"{icon} Busy"
        elif availability == "BLOCKED":
            icon = UISymbols.get_status_icon('blocked')
            return f"{icon} Blocked"
        else:
            # For any other status, show with unknown icon
            icon = UISymbols.get_status_icon('unknown')
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
            icon = UISymbols.get_status_icon('connected')
            return f"{icon} Connected"
        else:
            icon = UISymbols.get_status_icon('disconnected')
            return f"{icon} Disconnected"
    
    def is_module_configured(self, module_id: str, factory_config: Dict[str, Any]) -> bool:
        """
        Check if module is configured in factory - CORRECTED to match aps_modules.py
        
        Args:
            module_id: Module identifier
            factory_config: Factory configuration from shopfloor.yml
            
        Returns:
            True if module is configured
        """
        try:
            if not factory_config:
                return False
            
            # Check positions array like in aps_modules.py
            positions = factory_config.get("positions", [])
            for position in positions:
                if position.get("type") == "MODULE" and position.get("module_serial") == module_id:
                    return position.get("enabled", False)
            
            return False
        except Exception:
            return False
    
    def get_configuration_display(self, configured: bool) -> str:
        """
        Get configuration display with icon (UISymbols-based)
        
        Args:
            configured: Configuration status
            
        Returns:
            Display string with icon from UISymbols
        """
        if configured:
            icon = UISymbols.get_status_icon('configured')
            return f"{icon} Configured"
        else:
            icon = UISymbols.get_status_icon('not_configured')
            return f"{icon} Not Configured"
    
    def get_factory_configuration(self) -> Dict[str, Any]:
        """
        Get factory configuration - PLACEHOLDER until shopfloor.yml location is decided
        
        Returns:
            Factory configuration dict (empty until shopfloor.yml is integrated)
        """
        try:
            # TODO: shopfloor.yml integration - location not yet decided!
            # Options: registry/model/v1/shopfloor.yml OR config/shopfloor.yml
            logger.info("📋 TODO: shopfloor.yml integration needed for 'Configured' status")
            logger.info("📋 Decision needed: registry vs config location for shopfloor.yml")
            return {}
            
        except Exception as e:
            logger.error(f"❌ Failed to get factory configuration: {e}")
            return {}
    
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
            "last_update": max([status.get("last_update", "") for status in self.module_status.values()], default="")
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
