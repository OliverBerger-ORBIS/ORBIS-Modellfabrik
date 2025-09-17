#!/usr/bin/env python3
"""
TXT Controller Data Extractor
Extrahiert Daten von Fischertechnik TXT-Controllern über HTTP
"""

import requests
import json
import os
from pathlib import Path
import time

# TXT Controller IP-Adressen
CONTROLLERS = {
    "CGW": "192.168.0.102",
    "DPS": "192.168.0.103", 
    "AIQS": "192.168.0.104",
    "FTS": "192.168.0.105"
}

def test_controller(ip):
    """Teste ob Controller erreichbar ist"""
    try:
        response = requests.get(f"http://{ip}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def extract_file_via_api(ip, filename):
    """Versuche Datei über verschiedene API-Endpunkte zu extrahieren"""
    endpoints = [
        f"http://{ip}/{filename}",
        f"http://{ip}/api/{filename}",
        f"http://{ip}/data/{filename}",
        f"http://{ip}/files/{filename}",
        f"http://{ip}/download/{filename}",
        f"http://{ip}/get/{filename}"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200 and not response.text.startswith("<!DOCTYPE"):
                return response.text
        except:
            continue
    return None

def extract_via_directory_listing(ip):
    """Versuche Verzeichnislisting zu extrahieren"""
    endpoints = [
        f"http://{ip}/",
        f"http://{ip}/files/",
        f"http://{ip}/data/",
        f"http://{ip}/api/",
        f"http://{ip}/list/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            if response.status_code == 200:
                return response.text
        except:
            continue
    return None

def main():
    """Hauptfunktion"""
    print("🔍 TXT Controller Data Extractor")
    print("=" * 50)
    
    # Erstelle Ausgabeverzeichnis
    output_dir = Path("data/aps-data/txt-controllers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for name, ip in CONTROLLERS.items():
        print(f"\n📡 Teste {name} Controller ({ip})...")
        
        if not test_controller(ip):
            print(f"❌ {name} Controller nicht erreichbar")
            continue
            
        print(f"✅ {name} Controller erreichbar")
        
        # Versuche Verzeichnislisting zu extrahieren
        listing = extract_via_directory_listing(ip)
        if listing:
            with open(output_dir / f"{name}_directory_listing.html", "w") as f:
                f.write(listing)
            print(f"📁 Verzeichnislisting gespeichert: {name}_directory_listing.html")
        
        # Bekannte Dateien versuchen zu extrahieren
        known_files = [
            "deviceid.json",
            "FactoryCalib.json", 
            "FactoryCalibration.json",
            "ServoCalib_DPS.json",
            "config.json",
            "status.json",
            "info.json"
        ]
        
        for filename in known_files:
            print(f"  🔍 Suche {filename}...")
            content = extract_file_via_api(ip, filename)
            if content:
                output_file = output_dir / f"{name}_{filename}"
                with open(output_file, "w") as f:
                    f.write(content)
                print(f"  ✅ {filename} extrahiert: {output_file}")
            else:
                print(f"  ❌ {filename} nicht gefunden")
        
        time.sleep(1)  # Kurze Pause zwischen Controllern
    
    print(f"\n🎉 Extraktion abgeschlossen!")
    print(f"📁 Daten gespeichert in: {output_dir}")

if __name__ == "__main__":
    main()

