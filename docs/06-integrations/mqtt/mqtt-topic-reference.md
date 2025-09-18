# MQTT Topic Reference

## Overview

Vollständige Referenz aller MQTT-Topics in der APS-Modellfabrik, basierend auf der Log-Analyse vom 18. September 2025.

## Topic Categories

### **Module Topics (`module/v1/ff/`)**

#### **DPS Module (SVR4H73275)**
```
module/v1/ff/SVR4H73275/connection
module/v1/ff/SVR4H73275/state
module/v1/ff/SVR4H73275/instantAction
module/v1/ff/SVR4H73275/factsheet
module/v1/ff/NodeRed/SVR4H73275/state
module/v1/ff/NodeRed/SVR4H73275/factsheet
```
- **Funktion**: Warenein- und -ausgang, NFC-Reader, Kamera-Überwachung
- **Besonderheit**: CCU-Funktionalität, zentrale Steuerung
- **NodeRed-Präfix**: Für spezielle `instantAction`-Befehle

#### **AIQS Module (SVR4H76530)**
```
module/v1/ff/SVR4H76530/connection
module/v1/ff/SVR4H76530/state
module/v1/ff/SVR4H76530/instantAction
module/v1/ff/SVR4H76530/factsheet
module/v1/ff/NodeRed/SVR4H76530/state
module/v1/ff/NodeRed/SVR4H76530/factsheet
```
- **Funktion**: Qualitätskontrolle, Produktkamera, AI-Bilderkennung
- **NodeRed-Präfix**: Für spezielle `instantAction`-Befehle

#### **HBW Module (SVR4H76449)**
```
module/v1/ff/SVR4H76449/connection
module/v1/ff/SVR4H76449/state
module/v1/ff/SVR4H76449/instantAction
module/v1/ff/SVR4H76449/factsheet
```
- **Funktion**: Lagerverwaltung, Workpiece-Storage
- **Direkte Kommunikation**: Kein NodeRed-Präfix

#### **MILL Module (SVR3QA0022)**
```
module/v1/ff/SVR3QA0022/connection
module/v1/ff/SVR3QA0022/state
module/v1/ff/SVR3QA0022/instantAction
module/v1/ff/SVR3QA0022/factsheet
```
- **Funktion**: Fräsen von Workpieces
- **Direkte Kommunikation**: Kein NodeRed-Präfix

#### **DRILL Module (SVR3QA2098)**
```
module/v1/ff/SVR3QA2098/connection
module/v1/ff/SVR3QA2098/state
module/v1/ff/SVR3QA2098/instantAction
module/v1/ff/SVR3QA2098/factsheet
```
- **Funktion**: Bohren von Workpieces
- **Direkte Kommunikation**: Kein NodeRed-Präfix

### **FTS Topics (`fts/v1/ff/`)**

#### **FTS System (5iO4)**
```
fts/v1/ff/5iO4/connection
fts/v1/ff/5iO4/state
fts/v1/ff/5iO4/instantAction
fts/v1/ff/5iO4/order
fts/v1/ff/5iO4/factsheet
```
- **Funktion**: Transport-System, Workpiece-Bewegung
- **Status**: "BLOCKED" (an CHRG0), "READY" (frei)

### **CCU Topics (`ccu/`)**

#### **Pairing Management**
```
ccu/pairing/state
ccu/pairing/pair_fts
```
- **Funktion**: Modul-Pairing, System-Konfiguration
- **Publisher**: DPS (CCU-Funktionalität)

#### **Order Management**
```
ccu/order/request
ccu/order/active
ccu/order/cancel
ccu/order/completed
```
- **Funktion**: Bestellungsverwaltung, Produktionsaufträge
- **Load Types**: WHITE, RED, BLUE (universell unterstützt)

#### **System State**
```
ccu/state/layout
ccu/state/config
ccu/state/flows
ccu/state/stock
ccu/state/version-mismatch
```
- **Funktion**: System-Status, Konfiguration, Layout
- **Publisher**: DPS (CCU-Funktionalität)

#### **System Control**
```
ccu/set/reset
ccu/set/layout
ccu/set/flows
ccu/set/calibration
ccu/set/module-duration
ccu/set/delete-module
ccu/set/park
ccu/set/charge
ccu/set/default_layout
ccu/set/config
```
- **Funktion**: System-Steuerung, Konfiguration
- **Publisher**: APS-Dashboard, OMF-Dashboard

#### **Global Operations**
```
ccu/global
```
- **Funktion**: Globale Operationen (z.B. Factory-Reset)
- **Publisher**: APS-Dashboard

### **TXT Topics (`/j1/txt/1/`)**

#### **Order Processing**
```
/j1/txt/1/f/i/order
/j1/txt/1/f/o/order
```
- **Funktion**: Bestellungsverarbeitung, TXT-Controller-Kommunikation

#### **Stock Management**
```
/j1/txt/1/f/i/stock
```
- **Funktion**: Lager-Status, Workpiece-Verwaltung

#### **Sensor Data (Filtered)**
```
/j1/txt/1/i/cam
/j1/txt/1/i/bme680
/j1/txt/1/i/ldr
/j1/txt/1/c/cam
/j1/txt/1/c/bme680
/j1/txt/1/c/ldr
```
- **Funktion**: Sensor-Daten (Kamera, Temperatur, Licht)
- **Filtering**: Nur erste 10 Beispiele pro Topic behalten

## Message Patterns

### **Connection Messages**
- **Pattern**: `{component}/connection`
- **QoS**: 1 (At least once)
- **Retained**: No
- **Function**: Verbindungsstatus der Komponenten

### **State Messages**
- **Pattern**: `{component}/state`
- **QoS**: 1-2 (At least once / Exactly once)
- **Retained**: Yes
- **Function**: Aktueller Status der Komponenten

### **Instant Action Messages**
- **Pattern**: `{component}/instantAction`
- **QoS**: 2 (Exactly once)
- **Retained**: No
- **Function**: Sofort-Aktionen, Befehle

### **Order Messages**
- **Pattern**: `ccu/order/*` oder `/j1/txt/1/f/*/order`
- **QoS**: 2 (Exactly once)
- **Retained**: No
- **Function**: Bestellungsverarbeitung

## QoS Levels

### **QoS 0 (At most once)**
- **Verwendung**: Telemetrie-Daten, Sensor-Daten
- **Beispiele**: Kamera-Daten, Sensor-Messungen

### **QoS 1 (At least once)**
- **Verwendung**: Status-Updates, Verbindungsstatus
- **Beispiele**: `connection`, `state` Topics

### **QoS 2 (Exactly once)**
- **Verwendung**: Kritische Befehle, Bestellungen
- **Beispiele**: `instantAction`, `order` Topics

## Retained Messages

### **Retained Topics**
- **`state`** Topics: Letzter Status wird gespeichert
- **`factsheet`** Topics: Modul-Informationen werden gespeichert
- **`layout`** Topics: System-Layout wird gespeichert

### **Non-Retained Topics**
- **`instantAction`** Topics: Befehle werden nicht gespeichert
- **`order`** Topics: Bestellungen werden nicht gespeichert
- **`connection`** Topics: Verbindungsstatus wird nicht gespeichert

## Client-Specific Topics

### **Node-RED Topics**
- **Monitoring**: Alle `module/v1/ff/+/state` Topics
- **Commands**: Alle `module/v1/ff/+/instantAction` Topics
- **NodeRed-Präfix**: Nur für DPS und AIQS `instantAction`

### **Dashboard Topics**
- **Subscriptions**: Alle relevanten Topics für Überwachung
- **Publications**: `ccu/set/*` Topics für Steuerung

### **TXT Controller Topics**
- **Publications**: Sensor-Daten, Bestellungen
- **Subscriptions**: Befehle, Konfiguration

---

*Erstellt: 18. September 2025*  
*Basiert auf: Mosquitto-Log-Analyse (15:59-16:24)*  
*Status: Vollständige Topic-Referenz*
