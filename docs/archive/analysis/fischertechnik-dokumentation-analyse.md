# 📄 Fischertechnik APS-Dokumentation Analyse

## 📋 Dokumentations-Übersicht

**Dokument:** `Dokumentation_APS_DE-02-2025.rtf`
**Version:** 4.0 (Model revision: 1.x)
**Datum:** Februar 2025
**Sprache:** Deutsch

## 🎯 Wichtige Erkenntnisse aus der Dokumentation

### 🏭 **System-Architektur**

#### **Zentrale Komponenten:**
- **Raspberry Pi 4B**: Herzstück des Systems mit zentraler Steuerungssoftware
- **MQTT-Broker**: Port 1883 auf 192.168.0.100 (default/default)
- **Node-RED**: Port 1880 auf 192.168.0.100 (Gateway zwischen OPC-UA und MQTT)
- **Router**: TP-Link TL-WR902AC (192.168.0.1, admin/admin1)

#### **Modul-Controller:**
- **TXT 4.0 Controller**: Kommuniziert via MQTT mit zentraler Steuerung
- **SPS S7-1200**: Individueller OPC-UA Server pro Modul

### 📡 **Netzwerk-Konfiguration**

#### **IP-Adressen der Module:**
```
MILL:    192.168.0.40-45  ✅ In unserer APS vorhanden
DRILL:   192.168.0.50-55  ✅ In unserer APS vorhanden
OVEN:    192.168.0.60-65  ❌ Optional - nicht in unserer APS
AIQS:    192.168.0.70-75  ✅ In unserer APS vorhanden
HBW:     192.168.0.80-83  ✅ In unserer APS vorhanden
DPS:     192.168.0.90     ✅ In unserer APS vorhanden
```

#### **Zugangsdaten:**
- **MQTT-Broker**: 192.168.0.100:1883 (default/default)
- **Node-RED**: 192.168.0.100:1880
- **SSH Raspberry Pi**: 192.168.0.100:22 (ff22/ff22+)
- **TXT 4.0 SSH**: 192.168.0.x:22 (ft/fischertechnik)
- **TXT 4.0 Web**: 192.168.0.x:80 (ft/fischertechnik)

### 🤖 **Modul-Übersicht**

#### **5 Hauptmodule in unserer APS:**
1. **Wareneingang/-ausgang** mit 6-Achs-Roboter, Raspberry Pi 4B, WLAN-Router, Sensorstation
2. **Hochregallager** (9 Lagerplätze)
3. **Bohrstation** (DRILL)
4. **Frässtation** (MILL)
5. **Qualitätssicherung mit KI** (AIQS)
6. **Ladestation** (CHRG)

#### **Optional (nicht in unserer APS):**
- **OVEN-Modul**: Ofen/Heizmodul (192.168.0.60-65)

#### **Transport-System:**
- **FTS** (Fahrerloses Transportsystem) mit Akku-Betrieb
- **3 Lagerplätze** für Werkstücke
- **VDA5050-Standard** für MQTT-Kommunikation

### 🔧 **Technische Standards**

#### **Kommunikations-Protokolle:**
- **MQTT**: Publish/Subscribe-Architektur für Modul-Kommunikation
- **OPC-UA**: Für SPS-Module (Port 4840)
- **VDA5050**: Standard für FTS-Kommunikation
- **Node-RED**: Übersetzung OPC-UA ↔ MQTT

#### **Entwicklungsumgebung:**
- **TIA Portal V18** für SPS-Programmierung
- **SIMATIC S7-1200** mit CPU1512SP
- **Strukturierter Text (ST/SCL)** als Programmiersprache

### 🌐 **Cloud-Integration**

#### **fischertechnik Cloud:**
- **Gateway** auf TXT 4.0 Controller des Wareneingang/-ausgangs
- **Weiterleitung** relevanter Nachrichten an Cloud-Broker
- **Web-Interface**: https://www.fischertechnik-cloud.com

### 📚 **Programmieraufgaben**

#### **Aufgabe 1: Mehrfach Fräsen**
- **Ziel**: Werkstück zweimal fräsen mit 1-Sekunde Pause
- **Fokus**: Programmablauf verstehen und anpassen

#### **Aufgabe 2: OPC-UA Schnittstelle erweitern**
- **Ziel**: Konfigurierbare Werte über OPC-UA
- **Fokus**: Flexibilität ohne SPS-Programmierung

### 🔗 **GitHub-Ressourcen**
- **Repository**: https://github.com/fischertechnik/Agile-Production-Simulation-24V
- **Update-Blog**: https://www.fischertechnik.de/agile-production-simulation/update-blog

## ⚠️ **Kritische MQTT-Probleme identifiziert**

### **Aktuelle MQTT-Command-Probleme:**
- ❌ **PICK, DROP, STORE, CHECK_QUALITY** funktionieren nicht zuverlässig
- ❌ **ORDER-ID Probleme**: Eindeutigkeit und Timing-Probleme
- ❌ **Zeitliche Abhängigkeiten**: Module müssen bereit sein
- ❌ **Interner Modul-Status**: Verfügbarkeit nicht korrekt erkannt
- ❌ **Workflow-Abhängigkeiten**: Korrekte Reihenfolge fehlt

### **Ursachen der Probleme:**
1. **ORDER-ID Management**: Keine eindeutige Auftragsverwaltung
2. **Modul-Status-Monitoring**: Verfügbarkeit wird nicht korrekt erkannt
3. **Timing-Probleme**: Commands werden zu früh gesendet
4. **Workflow-Engine**: Fehlt für koordinierte Abläufe
5. **Error-Handling**: Keine automatische Fehlerbehandlung

## 🎯 **Integration mit unserem System**

### ✅ **Bereits Kompatible Elemente:**
- **MQTT-Broker**: Unsere Verbindung zu 192.168.0.100:1883 ist korrekt
- **Modul-IPs**: Unsere bekannten Module stimmen mit Dokumentation überein
- **VDA5050**: FTS-Kommunikation basiert auf diesem Standard

### 🔄 **Kritische Anpassungen erforderlich:**
- **ORDER-ID Management**: Eindeutige Auftragsverwaltung implementieren
- **Modul-Status-Monitoring**: Verfügbarkeit korrekt erkennen
- **Workflow-Engine**: Koordinierte Abläufe implementieren
- **Error-Handling**: Automatische Fehlerbehandlung
- **Node-RED Integration**: Verstehen der OPC-UA ↔ MQTT Übersetzung
- **VDA5050 Standard**: Implementierung für FTS-Kommunikation

### 📊 **Nächste Schritte:**
1. **ORDER-ID Management System** implementieren
2. **Modul-Status-Monitoring** verbessern
3. **Workflow-Engine** für koordinierte Abläufe
4. **Node-RED Flows analysieren** (Port 1880)
5. **VDA5050 Standard studieren** für FTS-Kontrolle

## 🚀 **Implementierungs-Prioritäten**

### **Phase 1: MQTT-Probleme lösen (KRITISCH)**
- 🔄 **ORDER-ID Management**: Eindeutige Auftragsverwaltung
- 🔄 **Modul-Status-Monitoring**: Verfügbarkeit korrekt erkennen
- 🔄 **Workflow-Engine**: Koordinierte Abläufe
- 🔄 **Error-Handling**: Automatische Fehlerbehandlung

### **Phase 2: Erweiterte Funktionen**
- 🔄 **Node-RED Integration**: OPC-UA ↔ MQTT Gateway
- 🔄 **VDA5050 für FTS**: Vollständige FTS-Kontrolle
- 🔄 **Cloud-Integration**: Remote-Steuerung

### **Phase 3: Optimierung**
- 🔄 **Performance-Monitoring**: Durchsatz-Optimierung
- 🔄 **Advanced Analytics**: Predictive Maintenance
- 🔄 **API-Development**: Externe Integration

---

**Quelle:** Fischertechnik APS-Dokumentation Version 4.0 (Februar 2025)
**Analyse erstellt:** $(date)
**Status:** ⚠️ **KRITISCHE MQTT-PROBLEME IDENTIFIZIERT** - ORDER-ID Management erforderlich
