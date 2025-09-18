# APS MQTT Analysis - Gesicherte Erkenntnisse

## Overview

Dieses Dokument enthält die **gesicherten Erkenntnisse** aus der detaillierten MQTT-Analyse der APS-Modellfabrik vom 18. September 2025. Diese Erkenntnisse sind **validiert** und sollten als **Referenz** für alle zukünftigen Entwicklungen verwendet werden.

## Gesicherte System-Architektur

### **TXT Controller (Hardware)**
- **192.168.0.102** = **DPS TXT Controller** (`auto-AC941349-4637-28AC-2662-E51FFA998712`)
  - **Funktion**: Warenein- und -ausgang, NFC-Reader, Kamera-Überwachung
  - **KRITISCH**: **DPS = CCU** - Zentrale Steuerungseinheit der gesamten APS-Fabrik
  - **Verwaltet**: Layout, Config, Flows, Stock, Pairing, Bestellungen

- **192.168.0.103** = **AIQS TXT Controller** (`auto-B9109AD9-6D76-62F1-C918-40D00FC40FF4`)
  - **Funktion**: Qualitätskontrolle, Produktkamera, AI-Bilderkennung
  - **Besonderheit**: Verwendet **NodeRed-Präfix** für spezielle Kommunikation

- **192.168.0.104** = **CGW TXT Controller** (`auto-9BD9E2A9-61B6-66B2-CDC8-591CAEBB5591`)
  - **Funktion**: Cloud-Gateway, externe Anbindungen

- **192.168.0.105** = **FTS TXT Controller** (`auto-F6DFC829-567D-0985-C27D-262A31EC52D5`)
  - **Funktion**: Transport-System, FTS-Steuerung

### **Node-RED Instanzen (Message Processing)**
- **`nodered_abe9e421b6fe3efd`** = **Node-RED(Pub)** - Monitoring/Subscriber (16:25:09)
  - **Funktion**: Überwacht alle Module und FTS
  - **Subscriptions**: 55 direkte Modul-Topics + NodeRed-vermittelte Topics

- **`nodered_94dca81c69366ec4`** = **Node-RED(Sub)** - Command/Publisher (16:25:47)
  - **Funktion**: Sendet Befehle an Module
  - **Publications**: 645 direkte Modul-Topics + 3 NodeRed-Präfix Topics
  - **NodeRed-Präfix nur für**: DPS und AIQS `instantAction`

- **`nodered_2767ab1e285b62e0`** = **Node-RED(Pub)** - Dashboard-Refresh (16:30:12)
  - **Funktion**: Monitoring-Instanz nach Dashboard-Refresh/F5
  - **Auslöser**: Dashboard muss MQTT-Messages empfangen für Status-Anzeige

### **Frontend (User Interface)**
- **`mqttjs_17ecbee3`** = **APS-Dashboard Frontend** (Web-Interface)
  - **Funktion**: Benutzeroberfläche für Steuerung und Überwachung

### **External Systems**
- **192.168.0.106** = **MacBook (User)** - DHCP nach APS-Start
  - **Funktion**: Analyse-Workstation, keine aktive MQTT-Teilnahme

## Gesicherte Kommunikationsmuster

### **DPS = CCU (KRITISCH)**
- **DPS-TXT Controller** fungiert als **zentrale Steuerungseinheit**
- **Empfängt**: Alle CCU-Topics (Layout, Config, Flows, Stock, Pairing)
- **Verwaltet**: Zentrale Steuerung der gesamten APS-Fabrik
- **Besonderheit**: DPS = CCU + Modul-Funktionalität

### **Node-RED-Architektur**
- **Node-RED(Pub)**: Überwacht alle Module und FTS
- **Node-RED(Sub)**: Sendet Befehle an Module
- **NodeRed-Präfix**: Nur für Module mit eigenem TXT Controller (DPS, AIQS)

### **Module-Kommunikation**
- **Module ohne TXT Controller** (HBW, MILL, DRILL): Direkte Kommunikation
- **Module mit TXT Controller** (DPS, AIQS): NodeRed-Präfix für spezielle Befehle

### **Load Type Support**
- **Alle Module** unterstützen **alle Load-Types** (WHITE, RED, BLUE)
- **Universelles System** - Load-Type-unabhängige Architektur

## Gesicherte Kamera-Systeme

### **DPS Camera (192.168.0.102)**
- **Funktion**: Überwachungskamera der gesamten APS-Fabrik-Anlage
- **Steuerung**: Kamera-Justierung (hoch, rechts, runter, links)
- **Integration**: Über DPS-TXT Controller

### **AIQS Camera (192.168.0.103)**
- **Funktion**: Produktkamera für Qualitätskontrolle
- **AI-Integration**: Bilderkennung für Produktqualität
- **Entscheidungslogik**: 
  - Produktion erfolgreich → weiter im Prozess
  - Produktion nicht erfolgreich → Aussortierung + neuer Produktionsauftrag

## Gesicherte FTS-Zustände

### **Charging Station Behavior**
- **CHRG0-Modul**: Passiv, keine aktive Kommunikation
- **FTS-Status**: 
  - **"BLOCKED"** wenn an CHRG0 (Ladestation)
  - **"READY"** wenn frei von Ladestation
- **Battery Management**: Automatisches Laden/Entladen

## Gesicherte Topic-Hierarchie

### **Module Topics (`module/v1/ff/`)**
- **`SVR4H73275`** (DPS) - **913 Nachrichten** - Hauptaktivität + CCU-Funktionen
- **`SVR4H76530`** (AIQS) - **118 Nachrichten** - Qualitätskontrolle
- **`SVR4H76449`** (HBW) - **114 Nachrichten** - Lagerverwaltung
- **`SVR3QA0022`** (MILL) - **99 Nachrichten** - Fräsen
- **`SVR3QA2098`** (DRILL) - **96 Nachrichten** - Bohren
- **`NodeRed`** - **66 Nachrichten** - Node-RED-vermittelte Topics

### **FTS Topics (`fts/v1/ff/`)**
- **`5iO4`** (FTS) - **317 Nachrichten** - Transport-System

### **CCU Topics (`ccu/`)**
- **`pairing`** - **807 Nachrichten** - Modul-Pairing
- **`order`** - **63 Nachrichten** - Bestellungen
- **`state`** - **24 Nachrichten** - System-Status
- **`set`** - **7 Nachrichten** - Konfiguration
- **`global`** - **1 Nachricht** - Global-Reset

### **TXT Topics (`/j1/txt/1/`)**
- **`f/i/order`** - **50 Nachrichten** - Bestellungen
- **`f/i/stock`** - **17 Nachrichten** - Lager-Status

## Korrigierte Interpretationen

### **Vorherige Fehler (KORRIGIERT)**
1. **CCU als separate Komponente** → **DPS = CCU** ✅
2. **Node-RED als einfache Instanz** → **Komplexe Pub/Sub-Architektur** ✅
3. **Kamera-Systeme verwechselt** → **DPS = Überwachung, AIQS = Qualität** ✅
4. **192.168.0.106 unbekannt** → **MacBook User** ✅
5. **NodeRed-Präfix für alle Module** → **Nur für DPS und AIQS** ✅

### **Neue Erkenntnisse (GESICHERT)**
1. **DPS = CCU** - Zentrale Steuerungseinheit
2. **Node-RED-Architektur** - Komplexe Pub/Sub-Instanzen
3. **Selective NodeRed-Prefix** - Nur Module mit eigenem TXT Controller
4. **Universal Load Types** - Alle Module unterstützen alle Workpiece-Types
5. **Dual Camera System** - Separate Kameras für Überwachung und Qualitätskontrolle

## Analyse-Statistiken (Gesichert)

### **Message Statistics (Analysis Period: 15:59-16:24)**
- **Total Messages**: ~1,500+ (nach Filtering)
- **DPS Dominance**: 913 Nachrichten (Hauptaktivität)
- **FTS Activity**: 317 Nachrichten (Transport-System)
- **CCU Management**: 807 Pairing-Nachrichten
- **Filtering Success**: 90% Reduktion der Log-Größe

### **Client-IDs (Gesichert)**
- **TXT Controllers**: `auto-*` Client-IDs
- **Node-RED**: `nodered_*` Client-IDs
- **Frontend**: `mqttjs_*` Client-IDs

## Nächste Schritte (Basierend auf gesicherten Erkenntnissen)

1. **DPS-TXT Analysis**: RoboPro-basierte Analyse der DPS-Logik (CCU-Funktionalität)
2. **Node-RED Flow Analysis**: Verständnis der verschiedenen Monitoring-Instanzen
3. **CGW Analysis**: Cloud-Integration und externe Anbindungen
4. **OMF-Dashboard Integration**: MQTT-Topics für OMF-Dashboard basierend auf gesicherten Erkenntnissen

---

*Erstellt: 18. September 2025*  
*Basiert auf: Mosquitto-Log-Analyse (15:59-16:24)*  
*Status: Gesicherte Erkenntnisse - Referenz für alle zukünftigen Entwicklungen*
