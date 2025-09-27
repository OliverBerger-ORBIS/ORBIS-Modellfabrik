#!/usr/bin/env python3
"""
CCU Gateway - Business logic layer for CCU MQTT operations
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .ccu_mqtt_client import CCUMqttClient

logger = logging.getLogger(__name__)


class CCUGateway:
    """
    CCU Gateway - Encapsulates all CCU-related MQTT operations
    
    This gateway provides business logic methods for CCU operations,
    using the CCU MQTT client as the underlying transport.
    """
    
    def __init__(self, mqtt_client: CCUMqttClient):
        self.client = mqtt_client
        self.logger = logger
        
        # CCU-specific topic patterns
        self.topics = {
            "state": "ccu/state",
            "status": "ccu/status", 
            "control": "ccu/control",
            "workflow": "ccu/workflow",
            "connection": "ccu/connection"
        }
        
        # Subscribe to CCU topics on initialization
        self._subscribe_to_ccu_topics()
        
        logger.info("🏭 CCU Gateway initialized")
    
    def _subscribe_to_ccu_topics(self):
        """Subscribe to all CCU-related topics"""
        ccu_topics = [
            "ccu/+",  # All CCU topics
            "ccu/state",
            "ccu/status", 
            "ccu/control",
            "ccu/workflow/+",
            "ccu/connection"
        ]
        self.client.subscribe_many(ccu_topics)
    
    def _utc_timestamp(self) -> str:
        """Generate UTC timestamp"""
        return datetime.now(timezone.utc).isoformat()
    
    def send_status_update(self, module: str, state: str, details: Optional[Dict] = None) -> bool:
        """
        Send CCU status update
        
        Args:
            module: Module name (e.g., "Bohrstation", "Frässtation")
            state: Current state (e.g., "running", "idle", "error")
            details: Additional status details
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "module": module,
            "state": state,
            "details": details or {}
        }
        
        return self.client.publish_json(self.topics["status"], payload)
    
    def send_control_command(self, command: str, target: str, parameters: Optional[Dict] = None) -> bool:
        """
        Send CCU control command
        
        Args:
            command: Command to execute (e.g., "start", "stop", "reset")
            target: Target module or system
            parameters: Command parameters
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "command": command,
            "target": target,
            "parameters": parameters or {}
        }
        
        return self.client.publish_json(self.topics["control"], payload)
    
    def send_workflow_update(self, workflow_id: str, step: str, status: str, data: Optional[Dict] = None) -> bool:
        """
        Send workflow update
        
        Args:
            workflow_id: Unique workflow identifier
            step: Current workflow step
            status: Step status (e.g., "started", "completed", "failed")
            data: Additional workflow data
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "workflow_id": workflow_id,
            "step": step,
            "status": status,
            "data": data or {}
        }
        
        topic = f"{self.topics['workflow']}/{workflow_id}"
        return self.client.publish_json(topic, payload)
    
    def send_connection_status(self, component: str, connected: bool, details: Optional[Dict] = None) -> bool:
        """
        Send connection status update
        
        Args:
            component: Component name
            connected: Connection status
            details: Additional connection details
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "component": component,
            "connected": connected,
            "details": details or {}
        }
        
        return self.client.publish_json(self.topics["connection"], payload)
    
    def get_latest_state(self) -> Optional[Dict[str, Any]]:
        """Get latest CCU state"""
        buffer = self.client.get_buffer(self.topics["state"])
        if buffer:
            return buffer[-1]["payload"]
        return None
    
    def get_status_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get CCU status history"""
        buffer = self.client.get_buffer(self.topics["status"])
        return list(buffer)[-limit:]
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status for specific workflow"""
        topic = f"{self.topics['workflow']}/{workflow_id}"
        buffer = self.client.get_buffer(topic)
        if buffer:
            return buffer[-1]["payload"]
        return None
    
    def is_connected(self) -> bool:
        """Check if CCU MQTT client is connected"""
        return self.client.connected
    
    def add_status_callback(self, callback):
        """Add callback for status updates"""
        self.client.add_callback(self.topics["status"], callback)
    
    def add_control_callback(self, callback):
        """Add callback for control commands"""
        self.client.add_callback(self.topics["control"], callback)
    
    def add_workflow_callback(self, callback):
        """Add callback for workflow updates"""
        self.client.add_callback(f"{self.topics['workflow']}/+", callback)