#!/usr/bin/env python3
"""
Test MQTT Replay Broker
"""

import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}, Payload: {msg.payload.decode()}")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("#")

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

try:
    print("Connecting to localhost:1883...")
    client.connect("localhost", 1883, 60)
    client.loop_start()
    
    print("Waiting for messages for 10 seconds...")
    time.sleep(10)
    
    client.loop_stop()
    client.disconnect()
    print("Test completed")
    
except Exception as e:
    print(f"Error: {e}")
