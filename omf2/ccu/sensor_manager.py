#!/usr/bin/env python3
"""
CCU Sensor Manager - Business Logic für Sensor-Daten-Verarbeitung
Schema-basierte Verarbeitung von BME680, LDR, CAM Topics
"""

import json
import time
import logging
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
        
        # NEU: State-Holder für Sensor-Daten
        self.sensor_data = {}  # {topic: processed_sensor_data}
        
        logger.info("🌡️ CCU Sensor Manager initialized with MessageManager and State-Holder")
    
    def process_sensor_message(self, topic: str, payload: Dict[str, Any]):
        """
        NEU: Verarbeitet eingehende Sensor-Message und updated State
        Wird vom MQTT-Client über Business-Function-Callback aufgerufen
        
        Args:
            topic: MQTT Topic (String)
            payload: Payload-Daten (Dict ohne MQTT-Metadaten)
        """
        try:
            logger.debug(f"🔔 SensorManager received message for topic: {topic}")
            
            # Verarbeite Sensor-Daten direkt mit Payload
            processed_data = self._extract_sensor_data(topic, payload)
            
            if processed_data:
                # Update State-Holder
                self.sensor_data[topic] = processed_data
                logger.info(f"✅ Updated sensor state for {topic}: {processed_data}")
            else:
                logger.warning(f"⚠️ No processed data for sensor topic: {topic}")
                
        except Exception as e:
            logger.error(f"❌ Failed to process sensor message for topic {topic}: {e}")
    
    def process_sensor_messages(self, ccu_gateway) -> Dict[str, Any]:
        """
        Process all sensor messages from CCU Gateway buffers
        
        Args:
            ccu_gateway: CCU Gateway instance
            
        Returns:
            Dictionary with processed sensor data by topic
        """
        try:
            logger.debug("🔍 SENSOR DEBUG: Starting sensor message processing")
            
            # Initialize sensor data store
            sensor_data = {}
            
            # Get all buffers via CCU Gateway (Gateway-Pattern)
            if not ccu_gateway:
                logger.warning("⚠️ No CCU Gateway available")
                return {}
            
            # Get buffers via Gateway (Gateway-Pattern)
            all_buffers = ccu_gateway.get_all_message_buffers()
            logger.debug(f"🔍 SENSOR DEBUG: Got {len(all_buffers)} message buffers")
            print(f"🔍 SENSOR DEBUG: Got {len(all_buffers)} message buffers")
            logger.info(f"📊 Retrieved {len(all_buffers)} buffers via CCU Gateway")
            
            for topic, messages in all_buffers.items():
                if not messages:
                    continue
                
                # Check if this is a sensor topic
                if self._is_sensor_topic(topic):
                    logger.debug(f"📡 Processing sensor topic: {topic} with {1} messages")
                    
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
    
    def _extract_sensor_data(self, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sensor data from payload using MessageManager (Schema-based)
        
        Args:
            topic: MQTT topic
            payload: Payload-Daten (Dict ohne MQTT-Metadaten)
            
        Returns:
            Processed sensor data dictionary
        """
        if not payload:
            return {}
        
        logger.debug(f"🔍 SENSOR DEBUG: Raw payload keys: {list(payload.keys())}")
        logger.debug(f"🔍 SENSOR DEBUG: Raw payload structure: {payload}")
        
        # DEBUG: Print to console as well (nur bei Debug-Level)
        if logger.isEnabledFor(logging.DEBUG):
            print(f"🔍 SENSOR DEBUG: Raw payload keys: {list(payload.keys())}")
            print(f"🔍 SENSOR DEBUG: Raw payload: {payload}")
        
        # Payload ist bereits ein Dict - keine JSON-Parsing nötig!
        sensor_payload = payload
        
        logger.debug(f"🔍 SENSOR DEBUG: Processing sensor payload for {topic}: {sensor_payload}")
        if logger.isEnabledFor(logging.DEBUG):
            print(f"🔍 SENSOR DEBUG: Processing sensor payload for {topic}: {sensor_payload}")
        
        # Check if payload is empty (common in live MQTT data)
        if not sensor_payload or sensor_payload == {}:
            logger.debug(f"🔍 SENSOR DEBUG: Empty payload for {topic} - returning fallback data")
            if logger.isEnabledFor(logging.DEBUG):
                print(f"🔍 SENSOR DEBUG: Empty payload for {topic} - returning fallback data")
            return {
                'raw_data': {},
                'timestamp': sensor_payload.get('ts', ''),
                'message_count': 1,
                'status': 'empty_payload'
            }
        
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
                        "timestamp": sensor_payload.get("timestamp", ""),
                        "message_count": 1
                    }
                elif "/ldr" in topic:
                    return {
                        "light": validated_payload.get("ldr", 0.0),      # ✅ Korrekt: "ldr" (nicht "l")
                        "timestamp": sensor_payload.get("timestamp", ""),
                        "message_count": 1
                    }
                elif "/cam" in topic:
                    return {
                        "image_data": validated_payload.get("data", ""),
                        "timestamp": validated_payload.get("ts", sensor_payload.get("timestamp", "")),
                        "message_count": 1
                    }
            else:
                logger.warning(f"⚠️ Payload validation failed for {topic}: {validation_result.get('error', 'Unknown error')}")
                print(f"⚠️ Payload validation failed for {topic}: {validation_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Registry validation error for {topic}: {e}")
            print(f"❌ Registry validation error for {topic}: {e}")
        
        # Fallback for unknown sensor topics or validation errors
        return {
            "raw_data": sensor_payload,
            "timestamp": sensor_payload.get("timestamp", ""),
            "message_count": 1
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
    
    def get_sensor_data(self, sensor_id: str = None) -> Dict[str, Any]:
        """
        NEU: Liest Sensor-Daten aus State-Holder (für UI)
        
        Args:
            sensor_id: Spezifischer Sensor-Topic (optional)
            
        Returns:
            Sensor-Daten aus State-Holder
        """
        if sensor_id:
            return self.sensor_data.get(sensor_id, {})
        return dict(self.sensor_data)
    
    def get_sensor_state(self) -> Dict[str, Any]:
        """
        NEU: Gibt aktuellen Sensor-State zurück
        
        Returns:
            Vollständiger Sensor-State
        """
        return {
            "sensor_data": dict(self.sensor_data),
            "total_sensors": len(self.sensor_data),
            "sensor_topics": list(self.sensor_data.keys()),
            "last_update": max([data.get("timestamp", "") for data in self.sensor_data.values()], default="")
        }


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
