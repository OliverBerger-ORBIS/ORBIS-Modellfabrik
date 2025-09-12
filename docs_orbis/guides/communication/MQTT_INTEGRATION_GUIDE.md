# MQTT Integration Guide

## 📋 Overview

Das **OMF Dashboard** verwendet die **Per-Topic-Buffer Architektur** für MQTT-Nachrichtenverarbeitung. Diese moderne Architektur kombiniert das **MQTT-Singleton Pattern** mit effizienten **Per-Topic-Buffers** für optimale Performance und Einfachheit.

## ✅ Aktuelle MQTT Architektur

### 1. **MQTT-Singleton Pattern**
- **Eine MQTT-Client-Instanz** pro Streamlit-Session
- **Zentraler Zugriff** über `st.session_state["mqtt_client"]`
- **Automatische Verbindung** beim Dashboard-Start
- **Umgebungswechsel** (live/mock/replay) ohne Verbindungsabbruch

### 2. **Per-Topic-Buffer System**
- **Topic-spezifische Buffer** für jede MQTT-Subscription
- **Automatische Nachrichtensammlung** in separaten Buffers
- **Effiziente Verarbeitung** ohne Message-Processor Overhead
- **Direkte Buffer-Zugriffe** für optimale Performance

### 3. **Hybrid-Architektur für Publishing**
- **MessageGenerator** für Payload-Erstellung
- **Session State** für Preview/Edit-Funktionalität
- **MqttGateway** für finales Publishing
- **WorkflowOrderManager** für orderId/orderUpdateId Verwaltung

## 🎮 Dashboard MQTT Features

### **1. Connection Status**
```
🟢 Live Mode: 192.168.0.100:1883
🟡 Replay Mode: localhost:1884
🔴 Mock Mode: Simulated
```

### **2. Topic Management**
- **Automatische Subscription** aller relevanten Topics
- **Per-Topic-Buffer** für effiziente Nachrichtenverarbeitung
- **Friendly Names** für bessere Benutzerfreundlichkeit

### **3. Message Publishing**
- **Template-basierte** Nachrichtenerstellung
- **Preview-Funktion** vor dem Senden
- **Order-Management** mit automatischen IDs

## 🔧 Setup & Konfiguration

### **Live Mode (Produktiv)**
```python
# Verbindung zur echten APS-Fabrik
broker_host = "192.168.0.100"
broker_port = 1883
```

### **Replay Mode (Test)**
```python
# Verbindung zum lokalen Replay-Broker
broker_host = "localhost"
broker_port = 1884
```

### **Mock Mode (Entwicklung)**
```python
# Simulierte Verbindung ohne echte Hardware
broker_host = "mock"
broker_port = 0
```

## 📚 Weitere Dokumentation

- **[MQTT Control Summary](./mqtt/mqtt-control-summary.md)** - Modul-Steuerung und Commands
- **[State Machine Notes](./mqtt/state-machine-notes.md)** - FTS und Modul State Management
- **[Nachrichtenzentrale Implementation](./mqtt/nachrichtenzentrale-implementation.md)** - Technische Details
- **[Setup Guides](./mqtt/setup/)** - Remote Control und Traffic Logging

## 🚀 Quick Start

1. **Dashboard starten:** `streamlit run src_orbis/omf/dashboard/omf_dashboard.py`
2. **Verbindungsmodus wählen:** Live/Replay/Mock
3. **Topics abonnieren:** Automatisch konfiguriert
4. **Messages senden:** Über Template-System

## ⚠️ Troubleshooting

### **Verbindungsprobleme**
- **Live Mode:** Netzwerk-Verbindung zur APS prüfen
- **Replay Mode:** Lokalen Broker starten
- **Mock Mode:** Funktioniert immer (simuliert)

### **Topic-Probleme**
- **Friendly Names:** In `topic_config.yml` konfigurieren
- **Buffer-Overflow:** Per-Topic-Buffer automatisch verwaltet
- **Message-Loss:** Singleton-Pattern verhindert Duplikate

## 🔄 Migration von alter Architektur

### **Vorher (MessageMonitorService)**
```python
# Alte Architektur - DEPRECATED
message_monitor = MessageMonitorService()
```

### **Nachher (OMFMqttClient)**
```python
# Neue Architektur - AKTUELL
mqtt_client = OMFMqttClient()
```

## 📊 Performance

- **Memory-Effizienz:** Per-Topic-Buffer statt globaler Buffer
- **CPU-Optimierung:** Direkte Buffer-Zugriffe
- **Network-Effizienz:** Singleton-Pattern verhindert Mehrfach-Verbindungen
- **Scalability:** Automatische Topic-Verwaltung

---

*Letzte Aktualisierung: Januar 2025*
*Status: Produktiv einsatzbereit*
