#!/usr/bin/env python3
"""
CCU Sensor Manager - Business Logic für Sensor-Daten-Verarbeitung
Schema-basierte Verarbeitung von BME680, LDR, CAM Topics
"""

from typing import Any, Dict, Optional

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

    def process_sensor_message(self, topic: str, payload: Dict[str, Any], meta: Optional[Dict] = None):
        """
        NEU: Verarbeitet eingehende Sensor-Message und updated State
        Wird vom Gateway über Topic-Routing aufgerufen

        Args:
            topic: MQTT Topic (String)
            payload: Payload-Daten (Dict ohne MQTT-Metadaten)
            meta: Metadaten (timestamp, raw, qos, retain)
        """
        try:
            logger.debug(f"🔔 SensorManager received message for topic: {topic}")

            # Verarbeite Sensor-Daten direkt mit Payload
            processed_data = self._extract_sensor_data(topic, payload)

            if processed_data:
                # Update State-Holder
                self.sensor_data[topic] = processed_data
                logger.debug(f"✅ Updated sensor state for {topic}: {processed_data}")
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

            # Initialize sensor data store
            sensor_data = {}

            # Get all buffers via CCU Gateway (Gateway-Pattern)
            if not ccu_gateway:
                logger.warning("⚠️ No CCU Gateway available")
                return {}

            # Get buffers via Gateway (Gateway-Pattern)
            all_buffers = ccu_gateway.get_all_message_buffers()
            logger.debug(f"📊 Retrieved {len(all_buffers)} buffers via CCU Gateway")

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

            logger.debug(f"📊 Processed sensor data for {len(sensor_data)} sensor topics")
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
            "/j1/txt/1/i/ldr",  # LDR Sensor
            "/j1/txt/1/i/cam",  # Camera
        ]

        return topic in sensor_topics

    def _extract_sensor_data(self, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract sensor data from payload (Business Logic only - already validated by CCU Gateway)

        Args:
            topic: MQTT topic
            payload: Payload-Daten (Dict ohne MQTT-Metadaten) - bereits validiert

        Returns:
            Processed sensor data dictionary
        """
        if not payload:
            return {}

        # Payload-Struktur wird nur bei Debug-Level geloggt
        logger.debug(f"Raw payload keys: {list(payload.keys())}")
        logger.debug(f"Raw payload structure: {payload}")

        # Payload ist bereits ein Dict - keine JSON-Parsing nötig!
        sensor_payload = payload

        logger.debug(f"Processing sensor payload for {topic}: {sensor_payload}")

        # Check if payload is empty (common in live MQTT data)
        if not sensor_payload or sensor_payload == {}:
            logger.debug(f"Empty payload for {topic} - returning fallback data")
            return {
                "raw_data": {},
                "timestamp": sensor_payload.get("ts", ""),
                "message_count": 1,
                "status": "empty_payload",
            }

        # ARCHITEKTUR-FIX: Keine Validierung in Business Manager
        # CCU Gateway hat bereits validiert - hier nur Business Logic
        logger.debug(f"Processing validated payload for {topic} (already validated by CCU Gateway)")

        # Schema-based field extraction based on topic (Business Logic only)
        if "/bme680" in topic:
            return {
                "temperature": sensor_payload.get("t", 0.0),  # ✅ Korrekt: "t"
                "humidity": sensor_payload.get("h", 0.0),  # ✅ Korrekt: "h"
                "pressure": sensor_payload.get("p", 0.0),  # ✅ Korrekt: "p"
                "air_quality": sensor_payload.get("iaq", 0.0),  # ✅ Korrekt: "iaq" (nicht "aq")
                "timestamp": sensor_payload.get("timestamp", ""),
                "message_count": 1,
            }
        elif "/ldr" in topic:
            return {
                "light": sensor_payload.get("ldr", 0.0),  # ✅ Korrekt: "ldr" (nicht "l")
                "timestamp": sensor_payload.get("timestamp", ""),
                "message_count": 1,
            }
        elif "/cam" in topic:
            return {
                "image_data": sensor_payload.get("data", ""),
                "timestamp": sensor_payload.get("ts", sensor_payload.get("timestamp", "")),
                "message_count": 1,
            }

        # Fallback for unknown sensor topics or validation errors
        return {"raw_data": sensor_payload, "timestamp": sensor_payload.get("timestamp", ""), "message_count": 1}

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
            "total_messages": sum(data.get("message_count", 0) for data in sensor_data.values()),
        }

        # Add specific sensor statistics
        if "/j1/txt/1/i/bme680" in sensor_data:
            bme680_data = sensor_data["/j1/txt/1/i/bme680"]
            stats.update(
                {
                    "temperature": bme680_data.get("temperature", 0.0),
                    "humidity": bme680_data.get("humidity", 0.0),
                    "pressure": bme680_data.get("pressure", 0.0),
                    "air_quality": bme680_data.get("air_quality", 0.0),
                }
            )

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
            "last_update": max([data.get("timestamp", "") for data in self.sensor_data.values()], default=""),
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
