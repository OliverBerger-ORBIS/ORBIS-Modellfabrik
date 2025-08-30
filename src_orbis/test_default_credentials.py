#!/usr/bin/env python3
"""
Test Default Credentials für APS Modellfabrik
Orbis Development - Test der Default-Login-Daten
"""

import logging
import time

import paho.mqtt.client as mqtt

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def test_default_credentials():
    """Teste Default-Credentials für APS MQTT-Broker"""

    logger.info("🔍 Teste Default-Credentials für APS Modellfabrik")
    logger.info("=" * 50)

    # Default APS Credentials
    host = "192.168.0.100"
    port = 1883
    username = "default"
    password = "default"

    logger.info(f"📡 MQTT Broker: {host}:{port}")
    logger.info(f"👤 Username: {username}")
    logger.info(f"🔑 Password: {password}")

    # Create MQTT client
    client = mqtt.Client()
    client.username_pw_set(username, password)

    # Setup callbacks
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("✅ Verbindung erfolgreich mit Default-Credentials!")
            logger.info("🎉 Default-Login funktioniert!")
            client.disconnect()
        elif rc == 5:
            logger.error("❌ Default-Credentials nicht autorisiert (Return Code 5)")
        else:
            logger.error(f"❌ Verbindung fehlgeschlagen (Return Code {rc})")

    def on_disconnect(client, userdata, rc):
        logger.info("Disconnected from MQTT broker")

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        logger.info("🔗 Verbinde mit MQTT-Broker...")
        client.connect(host, port, 10)
        client.loop_start()

        # Wait for connection
        time.sleep(5)

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        logger.error(f"❌ Verbindungsfehler: {e}")


if __name__ == "__main__":
    test_default_credentials()
