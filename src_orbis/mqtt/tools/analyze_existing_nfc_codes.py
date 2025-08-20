#!/usr/bin/env python3
"""
Analyze Existing NFC Codes
Analysiert bestehende Session-Daten nach NFC-Codes und Farb-Zuordnung
"""

import os
import sys
import json
import sqlite3
import glob
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def analyze_nfc_codes_in_sessions():
    """Analysiert NFC-Codes in allen Session-Datenbanken"""
    print("🔍 Analyse bestehender NFC-Codes in Session-Daten")
    print("=" * 60)
    
    # Session-Datenbanken finden
    sessions_dir = project_root / "mqtt-data" / "sessions"
    db_files = list(sessions_dir.glob("*.db"))
    
    if not db_files:
        print("❌ Keine Session-Datenbanken gefunden!")
        return
    
    print(f"📁 {len(db_files)} Session-Datenbanken gefunden")
    print()
    
    # Alle NFC-Codes sammeln
    all_nfc_codes = set()
    nfc_usage = defaultdict(int)
    nfc_sessions = defaultdict(set)
    nfc_colors = defaultdict(set)
    
    for db_file in db_files:
        session_name = db_file.stem
        print(f"📊 Analysiere: {session_name}")
        
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Prüfen ob mqtt_messages Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mqtt_messages'")
            if not cursor.fetchone():
                print(f"  ⚠️  Keine mqtt_messages Tabelle in {session_name}")
                conn.close()
                continue
            
            # Nachrichten mit workpieceId suchen
            cursor.execute("""
                SELECT topic, payload FROM mqtt_messages 
                WHERE payload LIKE '%workpieceId%'
            """)
            
            session_nfc_codes = set()
            for topic, payload in cursor.fetchall():
                nfc_codes = extract_nfc_codes_from_payload(payload)
                colors = extract_colors_from_payload(payload)
                
                for nfc_code in nfc_codes:
                    all_nfc_codes.add(nfc_code)
                    nfc_usage[nfc_code] += 1
                    nfc_sessions[nfc_code].add(session_name)
                    session_nfc_codes.add(nfc_code)
                    
                    # Farb-Zuordnung
                    for color in colors:
                        nfc_colors[nfc_code].add(color)
            
            print(f"  ✅ {len(session_nfc_codes)} NFC-Codes gefunden")
            for code in sorted(session_nfc_codes):
                print(f"    {code}")
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ Fehler bei {session_name}: {e}")
    
    print()
    print("📊 GESAMTANALYSE")
    print("=" * 60)
    
    # Alle gefundenen NFC-Codes analysieren
    print(f"🏷️  Eindeutige NFC-Codes gefunden: {len(all_nfc_codes)}")
    print()
    
    # Nach Verwendung sortieren
    sorted_nfc_codes = sorted(nfc_usage.items(), key=lambda x: x[1], reverse=True)
    
    print("🔍 NFC-Code Analyse:")
    print("-" * 60)
    
    for nfc_code, usage_count in sorted_nfc_codes:
        colors = nfc_colors.get(nfc_code, set())
        sessions = nfc_sessions.get(nfc_code, set())
        
        # Farb-Analyse basierend auf letzter Ziffer
        last_digit = nfc_code[-1]
        if last_digit == "1":
            expected_color = "🔴 ROT"
        elif last_digit == "0":
            expected_color = "⚪ WEISS/🔵 BLAU"
        else:
            expected_color = "❓ UNBEKANNT"
        
        print(f"📱 {nfc_code}")
        print(f"   🎯 Erwartete Farbe: {expected_color}")
        print(f"   🎨 Gefundene Farben: {', '.join(colors) if colors else 'Keine'}")
        print(f"   📊 Verwendung: {usage_count} mal")
        print(f"   📁 Sessions: {len(sessions)}")
        if sessions:
            print(f"      {', '.join(sorted(sessions))}")
        print()
    
    # Farb-Zusammenfassung
    print("🎨 FARB-ZUSAMMENFASSUNG")
    print("-" * 60)
    
    red_codes = []
    white_blue_codes = []
    
    for nfc_code in all_nfc_codes:
        last_digit = nfc_code[-1]
        if last_digit == "1":
            red_codes.append(nfc_code)
        elif last_digit == "0":
            white_blue_codes.append(nfc_code)
    
    print(f"🔴 Rote Werkstücke (Endung '1'): {len(red_codes)}")
    for code in sorted(red_codes):
        print(f"   {code}")
    
    print(f"\n⚪ Weiße/🔵 Blaue Werkstücke (Endung '0'): {len(white_blue_codes)}")
    for code in sorted(white_blue_codes):
        print(f"   {code}")
    
    print()
    print("💡 EMPFEHLUNGEN")
    print("-" * 60)
    print("1. 🔴 Rote Werkstücke sind vollständig identifiziert")
    print("2. ⚪ Weiße/🔵 Blaue Werkstücke müssen physisch zugeordnet werden")
    print("3. 📱 Neue NFC-Analyse Session für vollständige Zuordnung")
    print("4. 🏷️  Mapping-Datei mit allen gefundenen Codes aktualisieren")


def extract_nfc_codes_from_payload(payload):
    """Extrahiert NFC-Codes aus JSON Payload"""
    nfc_codes = []
    
    try:
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
            value = get_nested_value(data, path)
            if value and isinstance(value, str) and len(value) >= 10:
                # Prüfen ob es ein NFC-Code Format ist
                if value.startswith("04") and len(value) == 12:
                    nfc_codes.append(value)
        
        return list(set(nfc_codes))
        
    except Exception:
        return []


def extract_colors_from_payload(payload):
    """Extrahiert Farben aus JSON Payload"""
    colors = []
    
    try:
        if isinstance(payload, str):
            data = json.loads(payload)
        else:
            data = payload
        
        # Verschiedene Pfade für Farben prüfen
        color_paths = [
            ["type"],
            ["metadata", "workpiece", "type"],
            ["action", "metadata", "type"],
            ["workpiece", "type"]
        ]
        
        for path in color_paths:
            value = get_nested_value(data, path)
            if value and isinstance(value, str):
                colors.append(value.upper())
        
        return list(set(colors))
        
    except Exception:
        return []


def get_nested_value(data, path):
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


def main():
    """Hauptfunktion"""
    analyze_nfc_codes_in_sessions()


if __name__ == "__main__":
    main()
