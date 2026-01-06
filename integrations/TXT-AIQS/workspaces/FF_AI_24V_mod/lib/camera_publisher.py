# Camera MQTT Publisher für AIQS
# Publiziert Kamera-Bilder über MQTT (analog zu TXT-DPS)

import base64
import cv2
import time
import threading
from lib.camera import *
from lib.controller import *
from lib.mqtt_utils import *

def timestamp_utcnow():
    """Erstellt UTC-Timestamp im Format für MQTT"""
    from datetime import datetime
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

def frame_to_base64(frame):
    """Konvertiert Frame zu Base64-String (analog zu TXT-DPS)"""
    result = ""
    success, image = cv2.imencode(".jpeg", frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
    if success:
        result = "data:image/jpeg;base64," + base64.b64encode(image).decode("utf-8")
    return result

def publish_camera():
    """Publiziert Kamera-Bilder über MQTT (analog zu TXT-DPS publish_camera)"""
    global camera_frame
    camera_frame = None
    
    while True:
        try:
            # Lese Frame von Kamera
            frame = TXT_SLD_M_USB1_1_camera.read_frame()
            if frame is not None:
                # Konvertiere zu Base64
                base64_data = frame_to_base64(frame)
                
                # Erstelle Payload (analog zu TXT-DPS Format)
                payload = '{{"ts":"{}","data":"{}"}}'.format(timestamp_utcnow(), base64_data)
                
                # Publiziere über MQTT (Topic: aiqs/camera)
                mqtt_publish('aiqs/camera', payload)
            
            # Warte bis zum nächsten Frame (15 FPS = ~66ms)
            time.sleep(1.0 / 15.0)
        except Exception as e:
            print(f"Error in publish_camera: {e}")
            time.sleep(1.0)

# Thread für kontinuierliche Kamera-Publikation
_camera_publisher_thread = None

def start_camera_publisher():
    """Startet den Kamera-Publisher Thread"""
    global _camera_publisher_thread
    if _camera_publisher_thread is None or not _camera_publisher_thread.is_alive():
        _camera_publisher_thread = threading.Thread(target=publish_camera, daemon=True)
        _camera_publisher_thread.start()
        print("Camera publisher started")

def stop_camera_publisher():
    """Stoppt den Kamera-Publisher Thread"""
    global _camera_publisher_thread
    # Thread wird automatisch beendet wenn daemon=True
    _camera_publisher_thread = None
    print("Camera publisher stopped")

