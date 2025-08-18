#!/usr/bin/env python3
"""
APS Session Logger - Fischertechnik APS
Organized session-based MQTT logging for different processes
"""

import os
import sys
import signal
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from mqtt.loggers.aps_persistent_logger import APSPersistentLogger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_session_label(process_type, source, color, status):
    """
    Create standardized session label
    Format: Order_{source}_{color}_{status}
    """
    return f"Order_{source}_{color}_{status}"

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='APS Session Logger')
    parser.add_argument('--session-label', type=str, help='Custom session label')
    parser.add_argument('--auto-start', action='store_true', help='Start logger automatically without prompts')
    parser.add_argument('--process-type', type=str, choices=['order_processing', 'wareneingang', 'transport', 'storage', 'production', 'quality_control', 'system_status', 'custom'], help='Process type')
    parser.add_argument('--source', type=str, choices=['cloud', 'local'], help='Order source (for order processing)')
    parser.add_argument('--color', type=str, choices=['blue', 'red', 'yellow', 'white'], help='Order color (for order processing)')
    parser.add_argument('--status', type=str, choices=['ok', 'nok'], help='Order status (for order processing)')
    
    return parser.parse_args()

def main():
    """Main function with session management"""
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Session configuration
    print("🎯 APS Session Logger - Fischertechnik APS")
    print("=" * 50)
    
        # If session label is provided via command line, use it
    if args.session_label:
        session_label = args.session_label
        print(f"📝 Verwendeter Session Label: {session_label}")
    else:
        # Interactive mode
        # Process type selection
        print("\n📋 Prozess-Typ auswählen:")
        print("1. Order Processing (Bestellung)")
        print("2. Wareneingang")
        print("3. Transport")
        print("4. Storage")
        print("5. Production")
        print("6. Quality Control")
        print("7. System Status")
        print("8. Custom")
        
        process_choice = input("\nWähle Prozess (1-8): ").strip()
        
        process_types = {
            "1": "order_processing",
            "2": "wareneingang", 
            "3": "transport",
            "4": "storage",
            "5": "production",
            "6": "quality_control",
            "7": "system_status",
            "8": "custom"
        }
        
        process_type = process_types.get(process_choice, "order_processing")
        
        # For order processing, get additional details
        if process_type == "order_processing":
            print("\n🌐 Bestellungs-Quelle:")
            print("1. Cloud")
            print("2. Local")
            source_choice = input("Wähle Quelle (1-2): ").strip()
            source = "cloud" if source_choice == "1" else "local"
            
            print("\n🎨 Farbe:")
            print("1. Blue (Blau)")
            print("2. Red (Rot)")
            print("3. Yellow (Gelb)")
            print("4. White (Weiß)")
            color_choice = input("Wähle Farbe (1-4): ").strip()
            
            colors = {"1": "blue", "2": "red", "3": "yellow", "4": "white"}
            color = colors.get(color_choice, "blue")
            
            print("\n✅ Status:")
            print("1. OK")
            print("2. NOK (Error)")
            status_choice = input("Wähle Status (1-2): ").strip()
            status = "ok" if status_choice == "1" else "nok"
            
            session_label = create_session_label(process_type, source, color, status)
            
        else:
            # For other processes, use timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_label = f"{process_type}_{timestamp}"
    
    print(f"\n🎯 Session Label: {session_label}")
    
    # Ensure sessions directory exists
    sessions_dir = Path("mqtt-data/sessions")
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Sessions Directory: {sessions_dir}")
    
    # Confirm start (skip if auto-start is enabled)
    if not args.auto_start:
        confirm = input("\n🚀 Logger starten? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Abgebrochen")
            return
    
    # Initialize logger with session label
    logger_instance = APSPersistentLogger(session_label=session_label)
    
    # Signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Logger gestoppt für Session: {session_label}")
        if hasattr(logger_instance, 'stop'):
            logger_instance.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"\n✅ Logger gestartet für Session: {session_label}")
    print("📊 Daten werden gespeichert in:")
    print(f"   - Log: {sessions_dir}/aps_persistent_traffic_{session_label}.log")
    print(f"   - DB: {sessions_dir}/aps_persistent_traffic_{session_label}.db")
    print("\n🔄 Drücke 'q' + Enter zum Beenden")
    
    try:
        # Start logging
        logger_instance.start()
        
        # Keep running until user types 'q'
        while True:
            user_input = input().strip().lower()
            if user_input == 'q':
                print(f"\n🛑 Logger wird beendet für Session: {session_label}")
                break
            elif user_input == 's':
                print(f"📊 Status: {logger_instance.message_count} Nachrichten empfangen")
            elif user_input == 'h':
                print("📋 Befehle:")
                print("   q - Logger beenden")
                print("   s - Status anzeigen")
                print("   h - Hilfe anzeigen")
            else:
                print("❓ Unbekannter Befehl. Drücke 'h' für Hilfe.")
                
    except KeyboardInterrupt:
        print(f"\n🛑 Logger gestoppt für Session: {session_label}")
    except Exception as e:
        logger.error(f"Fehler im Logger: {e}")
        print(f"❌ Fehler: {e}")
    finally:
        # Graceful shutdown
        if hasattr(logger_instance, 'stop'):
            logger_instance.stop()
            print(f"✅ Logger ordnungsgemäß beendet - {logger_instance.message_count} Nachrichten gespeichert")

if __name__ == "__main__":
    main()
