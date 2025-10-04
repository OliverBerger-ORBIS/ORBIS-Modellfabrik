#!/usr/bin/env python3
"""
CCU Sensor Manager - Business Logic für Sensor-Daten-Verarbeitung
Schema-basierte Verarbeitung von BME680, LDR, CAM Topics
"""

from typing import Dict, List, Any, Optional
from omf2.common.logger import get_logger
from omf2.common.message_manager import get_ccu_message_manager
from omf2.registry.manager.registry_manager import get_registry_manager

logger = get_logger(__name__)


class SensorManager:
    """
    CCU Sensor Manager - Business Logic für Sensor-Daten-Verarbeitung
    
    Verarbeitet Sensor-Messages aus MQTT-Buffers mit Schema-basierter Feld-Extraktion
    Analog zu ModuleManager für Module-Status-Verarbeitung
    """
    
    def __init__(self):
        """Initialize Sensor Manager"""
        self.registry_manager = get_registry_manager()
        self.message_manager = get_ccu_message_manager()
        logger.info("🌡️ CCU Sensor Manager initialized with MessageManager")
    
    def process_sensor_messages(self, ccu_gateway) -> Dict[str, Any]:
        """
        Process all sensor messages from CCU Gateway buffers
        
        Args:
            ccu_gateway: CCU Gateway instance
            
        Returns:
            Dictionary with processed sensor data by topic
        """
        try:
            # Initialize sensor data store
            sensor_data = {}
            
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
                
                # Check if this is a sensor topic
                if self._is_sensor_topic(topic):
                    logger.debug(f"📡 Processing sensor topic: {topic} with {len(messages)} messages")
                    
                    # Extract sensor data from messages
                    processed_data = self._extract_sensor_data(topic, messages)
                    if processed_data:
                        sensor_data[topic] = processed_data
                        logger.info(f"🔍 DEBUG: Processed sensor data for {topic}: {processed_data}")
            
            logger.info(f"📊 Processed sensor data for {len(sensor_data)} sensor topics")
            return sensor_data
            
        except Exception as e:
            logger.error(f"❌ Failed to process sensor messages: {e}")
            return {}
    
    def _is_sensor_topic(self, topic: str) -> bool:
        """
        Check if topic is a sensor topic
        
        Args:
            topic: MQTT topic string
            
        Returns:
            True if topic is a sensor topic
        """
        sensor_topics = [
            "/j1/txt/1/i/bme680",  # BME680 Sensor
            "/j1/txt/1/i/ldr",     # LDR Sensor
            "/j1/txt/1/i/cam"      # Camera
        ]
        
        return topic in sensor_topics
    
    def _extract_sensor_data(self, topic: str, messages: List[Dict]) -> Dict[str, Any]:
        """
        Extract sensor data from messages using MessageManager (Schema-based)
        
        Args:
            topic: MQTT topic
            messages: List of messages for this topic
            
        Returns:
            Processed sensor data dictionary
        """
        if not messages:
            return {}
        
        # Get latest message
        latest_message = messages[-1]
        
        logger.info(f"🔍 SENSOR DEBUG: Raw message keys: {list(latest_message.keys())}")
        logger.info(f"🔍 SENSOR DEBUG: Raw message structure: {latest_message}")
        
        # CRITICAL: Print to console as well
        print(f"🔍 SENSOR DEBUG: Raw message keys: {list(latest_message.keys())}")
        print(f"🔍 SENSOR DEBUG: Raw message: {latest_message}")
        
        # Extract payload from message (Schema is for payload, not full message)
        payload = latest_message.copy()
        
        # Remove metadata fields that are not part of the sensor schema
        metadata_fields = ['timestamp', 'ts']  # Keep sensor data fields
        sensor_payload = {k: v for k, v in payload.items() if k not in metadata_fields}
        
        logger.info(f"🔍 SENSOR DEBUG: Extracted sensor payload for {topic}: {sensor_payload}")
        print(f"🔍 SENSOR DEBUG: Extracted sensor payload for {topic}: {sensor_payload}")
        
        # Use Registry Manager for schema-based validation (like SchemaTester)
        try:
            # Validate payload using Registry Manager (Schema-based) - like SchemaTester
            validation_result = self.registry_manager.validate_topic_payload(topic, sensor_payload)
            logger.info(f"🔍 SENSOR DEBUG: Registry validation for {topic}: {validation_result}")
            print(f"🔍 SENSOR DEBUG: Registry validation for {topic}: {validation_result}")
            
            # Extract validated payload
            if validation_result.get("valid", False):
                validated_payload = sensor_payload  # Use extracted payload
                logger.info(f"🔍 SENSOR DEBUG: Validated payload for {topic}: {validated_payload}")
                print(f"🔍 SENSOR DEBUG: Validated payload for {topic}: {validated_payload}")
                
                # Schema-based field extraction based on topic
                if "/bme680" in topic:
                    return {
                        "temperature": validated_payload.get("t", 0.0),  # ✅ Korrekt: "t"
                        "humidity": validated_payload.get("h", 0.0),     # ✅ Korrekt: "h" 
                        "pressure": validated_payload.get("p", 0.0),     # ✅ Korrekt: "p"
                        "air_quality": validated_payload.get("iaq", 0.0), # ✅ Korrekt: "iaq" (nicht "aq")
                        "timestamp": latest_message.get("timestamp", ""),
                        "message_count": len(messages)
                    }
                elif "/ldr" in topic:
                    return {
                        "light": validated_payload.get("ldr", 0.0),      # ✅ Korrekt: "ldr" (nicht "l")
                        "timestamp": latest_message.get("timestamp", ""),
                        "message_count": len(messages)
                    }
                elif "/cam" in topic:
                    return {
                        "image_data": validated_payload.get("data", ""),
                        "timestamp": validated_payload.get("ts", latest_message.get("timestamp", "")),
                        "message_count": len(messages)
                    }
            else:
                logger.warning(f"⚠️ Payload validation failed for {topic}: {validation_result.get('error', 'Unknown error')}")
                print(f"⚠️ Payload validation failed for {topic}: {validation_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Registry validation error for {topic}: {e}")
            print(f"❌ Registry validation error for {topic}: {e}")
        
        # Fallback for unknown sensor topics or validation errors
        return {
            "raw_data": latest_message.get("payload", {}),
            "timestamp": latest_message.get("timestamp", ""),
            "message_count": len(messages)
        }
    
    def get_sensor_statistics(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get sensor statistics from processed data
        
        Args:
            sensor_data: Processed sensor data from process_sensor_messages
            
        Returns:
            Statistics dictionary
        """
        stats = {
            "total_sensors": len(sensor_data),
            "bme680_available": "/j1/txt/1/i/bme680" in sensor_data,
            "ldr_available": "/j1/txt/1/i/ldr" in sensor_data,
            "camera_available": "/j1/txt/1/i/cam" in sensor_data,
            "total_messages": sum(data.get("message_count", 0) for data in sensor_data.values())
        }
        
        # Add specific sensor statistics
        if "/j1/txt/1/i/bme680" in sensor_data:
            bme680_data = sensor_data["/j1/txt/1/i/bme680"]
            stats.update({
                "temperature": bme680_data.get("temperature", 0.0),
                "humidity": bme680_data.get("humidity", 0.0),
                "pressure": bme680_data.get("pressure", 0.0),
                "air_quality": bme680_data.get("air_quality", 0.0)
            })
        
        if "/j1/txt/1/i/ldr" in sensor_data:
            ldr_data = sensor_data["/j1/txt/1/i/ldr"]
            stats["light"] = ldr_data.get("light", 0.0)
        
        return stats


# Singleton Factory
_ccu_sensor_manager = None


def get_ccu_sensor_manager() -> SensorManager:
    """
    Get CCU Sensor Manager singleton instance
    
    Returns:
        SensorManager instance
    """
    global _ccu_sensor_manager
    if _ccu_sensor_manager is None:
        _ccu_sensor_manager = SensorManager()
        logger.info("🌡️ CCU Sensor Manager singleton created")
    return _ccu_sensor_manager
