#!/usr/bin/env python3
"""
Node-RED Gateway - Business logic layer for Node-RED MQTT operations
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .nodered_mqtt_client import NodeREDMqttClient

logger = logging.getLogger(__name__)


class NodeREDGateway:
    """
    Node-RED Gateway - Encapsulates all Node-RED-related MQTT operations
    
    This gateway provides business logic methods for Node-RED integration,
    using the Node-RED MQTT client as the underlying transport.
    """
    
    def __init__(self, mqtt_client: NodeREDMqttClient):
        self.client = mqtt_client
        self.logger = logger
        
        # Node-RED specific topic patterns
        self.topics = {
            "input": "nodered/input",
            "output": "nodered/output",
            "flow": "nodered/flow",
            "status": "nodered/status",
            "control": "nodered/control"
        }
        
        # Subscribe to Node-RED topics on initialization
        self._subscribe_to_nodered_topics()
        
        logger.info("🔴 Node-RED Gateway initialized")
    
    def _subscribe_to_nodered_topics(self):
        """Subscribe to all Node-RED-related topics"""
        nodered_topics = [
            "nodered/+",  # All Node-RED topics
            "nodered/input/+",
            "nodered/output/+", 
            "nodered/flow/+",
            "nodered/status",
            "nodered/control"
        ]
        self.client.subscribe_many(nodered_topics)
    
    def _utc_timestamp(self) -> str:
        """Generate UTC timestamp"""
        return datetime.now(timezone.utc).isoformat()
    
    def send_input_data(self, flow_id: str, data: Dict[str, Any]) -> bool:
        """
        Send input data to Node-RED flow
        
        Args:
            flow_id: Node-RED flow identifier
            data: Input data for the flow
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "flow_id": flow_id,
            "data": data
        }
        
        topic = f"{self.topics['input']}/{flow_id}"
        return self.client.publish_json(topic, payload)
    
    def send_control_command(self, command: str, flow_id: Optional[str] = None, parameters: Optional[Dict] = None) -> bool:
        """
        Send control command to Node-RED
        
        Args:
            command: Command to execute (e.g., "start", "stop", "deploy")
            flow_id: Optional specific flow ID
            parameters: Command parameters
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "command": command,
            "flow_id": flow_id,
            "parameters": parameters or {}
        }
        
        return self.client.publish_json(self.topics["control"], payload)
    
    def send_status_update(self, status: str, details: Optional[Dict] = None) -> bool:
        """
        Send Node-RED status update
        
        Args:
            status: Current status (e.g., "running", "stopped", "error")
            details: Additional status details
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "status": status,
            "details": details or {}
        }
        
        return self.client.publish_json(self.topics["status"], payload)
    
    def deploy_flow(self, flow_config: Dict[str, Any]) -> bool:
        """
        Deploy a Node-RED flow
        
        Args:
            flow_config: Flow configuration
            
        Returns:
            bool: Success status
        """
        payload = {
            "timestamp": self._utc_timestamp(),
            "action": "deploy",
            "config": flow_config
        }
        
        return self.client.publish_json(self.topics["flow"], payload)
    
    def get_flow_output(self, flow_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get output data from Node-RED flow"""
        topic = f"{self.topics['output']}/{flow_id}"
        buffer = self.client.get_buffer(topic)
        return list(buffer)[-limit:]
    
    def get_latest_status(self) -> Optional[Dict[str, Any]]:
        """Get latest Node-RED status"""
        buffer = self.client.get_buffer(self.topics["status"])
        if buffer:
            return buffer[-1]["payload"]
        return None
    
    def is_connected(self) -> bool:
        """Check if Node-RED MQTT client is connected"""
        return self.client.connected
    
    def add_output_callback(self, flow_id: str, callback):
        """Add callback for flow output"""
        pattern = f"{self.topics['output']}/{flow_id}"
        self.client.add_callback(pattern, callback)
    
    def add_status_callback(self, callback):
        """Add callback for status updates"""
        self.client.add_callback(self.topics["status"], callback)
    
    def add_control_callback(self, callback):
        """Add callback for control commands"""
        self.client.add_callback(self.topics["control"], callback)