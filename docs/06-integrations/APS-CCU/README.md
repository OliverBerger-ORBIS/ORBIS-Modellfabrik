# APS-CCU Integration Dokumentation

> 📖 **Zentrale Referenz:** [00-REFERENCE](../00-REFERENCE/README.md) - Verifizierte APS-Architektur
> 
> - [Module Serial Mapping](../00-REFERENCE/module-serial-mapping.md) - Module-IDs & Hardware
> - [CCU-Backend Orchestration](../00-REFERENCE/ccu-backend-orchestration.md) - Order-Management Details

## 📋 Übersicht

**APS-CCU** ist das Herz der APS Modellfabrik - die zentrale Steuerungseinheit.

## 🔍 Komponenten-Details

### **Hardware**
- **IP-Adresse:** 172.18.0.4 (Docker-Network)
- **Controller:** Raspberry Pi 4 Model B
- **Rolle:** Zentrale Steuerung der gesamten Fabrik
- **Netzwerk:** Docker-Container mit MQTT-Broker

### **Software**
- **MQTT-Broker:** Mosquitto (Port 1883)
- **Node-RED:** Gateway zwischen MQTT und OPC-UA
- **Dashboard:** Web-Interface (Port 80)
- **Docker:** Container-Orchestrierung

## 🔗 MQTT-Integration

### **Zentrale Kommunikation**
- **Broker:** 172.18.0.4:1883
- **Topics:** Zentrale Message-Routing-Infrastruktur
- **QoS:** Commands (QoS 2), Sensor (QoS 1)
- **Will Messages:** Connection-Monitoring

### **Dashboard-Integration**
- **Frontend:** `http://192.168.0.100/dashboard`
- **Client-ID:** `mqttjs_bba12050`
- **Routing:** 192.168.0.100 → 172.18.0.5

## 🏭 Fabrik-Steuerung

### **Module-Koordination**
- **TXT-Controller:** DPS, AIQS, FTS (192.168.0.102-105)
- **Production Modules:** MILL, DRILL, AIQS, DPS, HBW, OVEN
- **OPC-UA:** Kommunikation mit SPS Siemens S7 1200
- **VDA 5050:** FTS-Standard-Implementierung

### **System-Funktionen**
- **Factory Reset:** System-weite Reset-Funktion
- **Order Management:** Auftragssteuerung
- **State Machine:** Modul-Status-Verwaltung
- **Remote Monitoring:** Camera-Integration

## 📚 Verwandte Dokumentation

### **APS-Ecosystem:**
- **[APS System Overview](../APS-Ecosystem/aps-system-overview.md)** - High-Level funktionale Beschreibung
- **[System Overview](../APS-Ecosystem/system-overview.md)** - Technische System-Architektur
- **[Component Mapping](../APS-Ecosystem/component-mapping.md)** - Client-ID Mapping

### **Komponenten:**
- **[APS-NodeRED](../APS-NodeRED/README.md)** - Node-RED Gateway und Flows
- **[Mosquitto](../mosquitto/README.md)** - MQTT-Broker Log-Analyse
- **[TXT-Controller](../TXT-*/README.md)** - TXT-DPS, TXT-AIQS, TXT-FTS

### **Architektur:**
- **[Architektur-Übersicht](../../02-architecture/README.md)** – OSF-Systemkontext
- **[APS Data Flow](../../02-architecture/aps-data-flow.md)** – MQTT-Kommunikation

## 🚀 Nächste Schritte

1. **Docker-Container analysieren** - Container-Konfiguration
2. **Node-RED Flows dokumentieren** - Gateway-Logik
3. **Dashboard-Integration testen** - Web-Interface
4. **OSF-Integration vorbereiten** - Phase 1 Planung

---

*Erstellt: 24. September 2025*  
*Status: Herz der Fabrik - Zentrale Steuerungseinheit*