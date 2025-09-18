# MQTT Integration Documentation

## Overview

Diese Dokumentation beschreibt die MQTT-Integration der APS-Modellfabrik basierend auf einer detaillierten Analyse der Mosquitto-Logs vom 18. September 2025.

## Documents

### **Core Architecture**
- **[APS MQTT Findings](aps-mqtt-findings.md)** - **GESICHERTE ERKENNTNISSE** - Referenz für alle Entwicklungen
- **[APS MQTT Architecture](aps-mqtt-architecture.md)** - Vollständige System-Architektur und Kommunikationsmuster
- **[MQTT Topic Reference](mqtt-topic-reference.md)** - Detaillierte Referenz aller MQTT-Topics
- **[MQTT Diagrams](mqtt-diagrams.md)** - Graphische Pub/Sub-Diagramme und Sequenz-Flows

### **Legacy Documents (Deprecated)**
- **[mqtt-analysis.md](mqtt-analysis.md)** - ⚠️ **DEPRECATED** - Alte, fehlerbehaftete Analyse

## Key Findings

### **System Architecture**
- **DPS = CCU**: DPS-TXT Controller fungiert als zentrale Steuerungseinheit
- **4 TXT Controllers**: DPS, AIQS, CGW, FTS
- **3+ Node-RED Instanzen**: Spezialisierte Pub/Sub-Architektur
- **Selective NodeRed-Prefix**: Nur Module mit eigenem TXT Controller

### **Communication Patterns**
- **Module ohne TXT Controller** (HBW, MILL, DRILL): Direkte Kommunikation
- **Module mit TXT Controller** (DPS, AIQS): NodeRed-Präfix für spezielle Befehle
- **Universal Load Types**: Alle Module unterstützen WHITE, RED, BLUE

### **Camera Systems**
- **DPS Camera**: Überwachung der gesamten APS-Fabrik
- **AIQS Camera**: Produktkamera für Qualitätskontrolle + AI-Bilderkennung

## Analysis Methodology

### **Data Sources**
- **Mosquitto Logs**: System-Log (Client-Verbindungen, Pub/Sub)
- **Payload Logs**: Vollständige MQTT-Nachrichten mit Topics
- **Filtering**: Intelligente Filterung periodischer Sensor-Daten

### **Analysis Period**
- **Zeitraum**: 18. September 2025, 15:59-16:24
- **Aktivitäten**: 12 manuelle Dashboard-Befehle + automatische Prozesse
- **Filtering**: 90% Reduktion der Log-Größe

### **Key Commands Analyzed**
1. Docke an
2. Rohware-RED Eingang (automatisch)
3. Bestellung-BLUE
4. Rohware RED Eingang (Aussortierung)
5. FTS-Laden
6. FTS-Laden beenden
7. Kamera-Justierung (4x 10°)
8. NFC-Lesen
9. NFC-Löschen
10. Kalibrierung AIQS
11. Bestellung-WHITE
12. Factory-Reset

## Technical Details

### **Client Identification**
- **TXT Controllers**: `auto-*` Client-IDs
- **Node-RED**: `nodered_*` Client-IDs
- **Frontend**: `mqttjs_*` Client-IDs

### **Topic Statistics**
- **DPS Dominance**: 913 Nachrichten (Hauptaktivität)
- **FTS Activity**: 317 Nachrichten (Transport-System)
- **CCU Management**: 807 Pairing-Nachrichten
- **Total Messages**: ~1,500+ (nach Filtering)

### **QoS and Retained Messages**
- **QoS 0**: Sensor-Daten, Telemetrie
- **QoS 1**: Status-Updates, Verbindungsstatus
- **QoS 2**: Kritische Befehle, Bestellungen
- **Retained**: State, Factsheet, Layout Topics

## Next Steps

### **Immediate Actions**
1. **DPS-TXT Analysis**: RoboPro-basierte Analyse der DPS-Logik
2. **Node-RED Flow Analysis**: Verständnis der verschiedenen Monitoring-Instanzen
3. **CGW Analysis**: Cloud-Integration und externe Anbindungen

### **Integration Tasks**
1. **OMF-Dashboard Integration**: MQTT-Topics für OMF-Dashboard
2. **Template System**: MQTT-Templates für OMF
3. **Monitoring Integration**: Real-time Monitoring der APS-Komponenten

## Files and Data

### **Analysis Files**
- **`docs/analysis/mqtt/`** - Temporäre Analyse-Dateien
- **`data/aps-data/mosquitto/`** - Log-Dateien und gefilterte Daten

### **Log Files**
- **`mosquitto_current.log`** - System-Log (Client-Verbindungen)
- **`mosquitto_filtered.log`** - Gefilterte Payload-Logs
- **`mosquitto_payload_timestamp.log`** - Vollständige Payload-Logs

---

*Erstellt: 18. September 2025*  
*Status: Vollständige MQTT-Integration dokumentiert*  
*Nächster Schritt: DPS-TXT Analyse über RoboPro*
