#!/usr/bin/env python3
"""
NFC Analysis Session
Startet eine neue Session zur NFC-Code Analyse
"""

import os
import sys
import time
import json
import sqlite3
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src_orbis.mqtt.loggers.aps_session_logger import APSSessionLogger
from src_orbis.mqtt.tools.remote_mqtt_client import RemoteMQTTClient


class NFCAnalysisSession:
    """NFC Analysis Session für Werkstück-Code Auslesung"""
    
    def __init__(self, session_name="nfc_analysis_session"):
        self.session_name = session_name
        self.logger = None
        self.mqtt_client = None
        self.session_start_time = None
        
    def start_session(self):
        """Startet die NFC-Analyse Session"""
        print("🔍 NFC Analysis Session Start")
        print("=" * 50)
        
        # Session starten
        self.session_start_time = datetime.now()
        session_id = f"{self.session_name}_{self.session_start_time.strftime('%Y%m%d_%H%M%S')}"
        
        print(f"📅 Session ID: {session_id}")
        print(f"⏰ Start: {self.session_start_time}")
        print()
        
        # Logger initialisieren
        self.logger = APSSessionLogger(session_id)
        print("✅ Logger initialisiert")
        
        # MQTT Client initialisieren
        self.mqtt_client = RemoteMQTTClient(
            broker_host="192.168.0.100",
            broker_port=1883,
            username="default",
            password="default"
        )
        
        # Message Handler für NFC-Codes registrieren
        self.mqtt_client.set_message_callback(self._handle_nfc_message)
        
        # Verbindung aufbauen
        if self.mqtt_client.connect():
            print("✅ MQTT Verbindung hergestellt")
            
            # Topics für NFC-Code Analyse abonnieren
            nfc_topics = [
                "ccu/order/request",      # Wareneingang Requests
                "ccu/order/response",     # CCU Responses mit ORDER-IDs
                "module/v1/ff/*/order",   # Modul Orders
                "module/v1/ff/*/state"    # Modul States
            ]
            
            for topic in nfc_topics:
                self.mqtt_client.subscribe(topic)
                print(f"📡 Topic abonniert: {topic}")
            
            print()
            print("🎯 NFC-Code Analyse gestartet!")
            print("📱 Bitte jetzt die Werkstücke mit NFC-Reader auslesen...")
            print("⏹️  Session beenden mit Ctrl+C")
            print()
            
            return True
        else:
            print("❌ MQTT Verbindung fehlgeschlagen")
            return False
    
    def _handle_nfc_message(self, topic, payload):
        """Behandelt MQTT Nachrichten und extrahiert NFC-Codes"""
        try:
            # Nachricht loggen
            self.logger.log_message(topic, payload)
            
            # NFC-Code extrahieren
            nfc_codes = self._extract_nfc_codes(topic, payload)
            
            if nfc_codes:
                for nfc_code in nfc_codes:
                    print(f"🏷️  NFC-Code gefunden: {nfc_code}")
                    self._analyze_nfc_code(nfc_code, topic)
                    
        except Exception as e:
            print(f"❌ Fehler beim Verarbeiten der Nachricht: {e}")
    
    def _extract_nfc_codes(self, topic, payload):
        """Extrahiert NFC-Codes aus MQTT Nachrichten"""
        nfc_codes = []
        
        try:
            # JSON Payload parsen
            if isinstance(payload, str):
                data = json.loads(payload)
            else:
                data = payload
            
            # Verschiedene Pfade für NFC-Codes prüfen
            nfc_paths = [
                ["workpieceId"],
                ["metadata", "workpiece", "workpieceId"],
                ["action", "metadata", "workpiece", "workpieceId"],
                ["workpiece", "workpieceId"]
            ]
            
            for path in nfc_paths:
                value = self._get_nested_value(data, path)
                if value and isinstance(value, str) and len(value) >= 10:
                    # Prüfen ob es ein NFC-Code Format ist
                    if value.startswith("04") and len(value) == 12:
                        nfc_codes.append(value)
            
            # Duplikate entfernen
            return list(set(nfc_codes))
            
        except Exception as e:
            # Ignore parsing errors
            return []
    
    def _get_nested_value(self, data, path):
        """Holt einen verschachtelten Wert aus einem Dictionary"""
        try:
            current = data
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return None
            return current
        except:
            return None
    
    def _analyze_nfc_code(self, nfc_code, topic):
        """Analysiert einen NFC-Code"""
        # Farb-Analyse basierend auf letzter Ziffer
        last_digit = nfc_code[-1]
        if last_digit == "1":
            color = "🔴 ROT"
            processing = "MILL (Fräsen)"
        elif last_digit == "0":
            # Weitere Analyse für Weiß/Blau
            color = "⚪ WEISS/🔵 BLAU"
            processing = "DRILL (Bohren) / DRILL+MILL"
        else:
            color = "❓ UNBEKANNT"
            processing = "Unbekannt"
        
        print(f"   🎨 Farbe: {color}")
        print(f"   ⚙️  Verarbeitung: {processing}")
        print(f"   📡 Topic: {topic}")
        print()
    
    def stop_session(self):
        """Stoppt die NFC-Analyse Session"""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            print("📡 MQTT Verbindung getrennt")
        
        if self.logger:
            self.logger.close()
            print("📝 Logger geschlossen")
        
        session_duration = datetime.now() - self.session_start_time
        print(f"⏱️  Session Dauer: {session_duration}")
        print("✅ NFC Analysis Session beendet")
    
    def get_session_summary(self):
        """Gibt eine Zusammenfassung der Session"""
        if not self.logger:
            return None
        
        db_file = self.logger.db_file
        if not os.path.exists(db_file):
            return None
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Anzahl Nachrichten
            cursor.execute("SELECT COUNT(*) FROM mqtt_messages")
            message_count = cursor.fetchone()[0]
            
            # Eindeutige NFC-Codes
            cursor.execute("""
                SELECT DISTINCT payload FROM mqtt_messages 
                WHERE payload LIKE '%workpieceId%'
            """)
            nfc_messages = cursor.fetchall()
            
            nfc_codes = set()
            for row in nfc_messages:
                codes = self._extract_nfc_codes("", row[0])
                nfc_codes.update(codes)
            
            conn.close()
            
            return {
                "session_name": self.session_name,
                "message_count": message_count,
                "nfc_codes_found": len(nfc_codes),
                "nfc_codes": sorted(list(nfc_codes)),
                "db_file": db_file
            }
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Zusammenfassung: {e}")
            return None


def main():
    """Hauptfunktion für NFC Analysis Session"""
    print("🔍 ORBIS NFC Analysis Session")
    print("=" * 50)
    print()
    
    # Session erstellen
    session = NFCAnalysisSession()
    
    try:
        # Session starten
        if session.start_session():
            # Session laufen lassen
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n⏹️  Session wird beendet...")
        
        # Session stoppen
        session.stop_session()
        
        # Zusammenfassung anzeigen
        summary = session.get_session_summary()
        if summary:
            print("\n📊 Session Zusammenfassung:")
            print("=" * 30)
            print(f"📁 Session: {summary['session_name']}")
            print(f"📨 Nachrichten: {summary['message_count']}")
            print(f"🏷️  NFC-Codes gefunden: {summary['nfc_codes_found']}")
            
            if summary['nfc_codes']:
                print("\n🔍 Gefundene NFC-Codes:")
                for i, code in enumerate(summary['nfc_codes'], 1):
                    print(f"  {i:2d}. {code}")
            
            print(f"\n💾 Datenbank: {summary['db_file']}")
    
    except Exception as e:
        print(f"❌ Fehler: {e}")
        session.stop_session()


if __name__ == "__main__":
    main()
