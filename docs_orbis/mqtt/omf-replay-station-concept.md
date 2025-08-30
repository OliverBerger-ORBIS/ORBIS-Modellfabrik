# 🎬 OMF Replay Station - Konzept

## 📋 Übersicht

Die **OMF Replay Station** ist eine separate Anwendung, die als lokaler MQTT-Broker fungiert und aufgezeichnete Session-Daten 1:1 wiedergibt. Dies ermöglicht realistische Tests ohne echte APS-Modellfabrik-Verbindung.

## 🏗️ Architektur

### **✅ Komponenten-Struktur:**
```
🎬 OMF Replay Station
├── 📡 Lokaler MQTT-Broker (localhost:1884)
├── 🎮 Session Player
├── ⏱️ Replay Controller
└── 📊 Session Manager

📊 OMF Dashboard
├── 🔗 MQTT-Client → localhost:1884 (Replay-Modus)
├── 📡 Nachrichtenzentrale
└── 🎯 Normale Dashboard-Funktionen
```

### **✅ Datenfluss:**
```
Session-Datei (.db/.log) → Session Player → Lokaler Broker → Dashboard
```

## 🎯 Funktionalität

### **✅ 1. Session-Player:**
- **Session-Loading:** SQLite-DB oder Log-Dateien laden
- **Message-Parsing:** Nachrichten mit Timestamps extrahieren
- **Timing-Replay:** Original-Nachrichtenfolgen mit korrektem Timing

### **✅ 2. Replay-Controller:**
- **Play/Pause:** Replay starten/stoppen
- **Speed-Control:** 0.1x - 5x Geschwindigkeit
- **Loop-Modus:** Endlose Wiederholung
- **Filter-Replay:** Nur bestimmte Topics

### **✅ 3. Lokaler MQTT-Broker:**
- **Port 1884:** Dedizierter Replay-Port
- **Message-Forwarding:** Nachrichten an Dashboard weiterleiten
- **Topic-Subscription:** Alle relevanten Topics

## 🔧 Dashboard-Integration

### **✅ Broker-Switching:**
```yaml
# mqtt_config.yml
broker:
  aps:
    host: "192.168.0.100"  # Live-Modus
    port: 1883
  replay:
    host: "localhost"      # Replay-Modus
    port: 1884
```

### **✅ Replay-Modus Settings:**
- **Checkbox:** Replay-Modus aktivieren/deaktivieren
- **Status-Anzeige:** Aktueller Modus (Live/Replay)
- **Automatischer Wechsel:** Broker-Konfiguration anpassen

## 🚀 Vorteile

### **✅ 1. Saubere Trennung:**
- **Dashboard:** Nur UI/UX, keine Replay-Logik
- **Replay-Station:** Dedizierte Replay-Funktionalität
- **MQTT-Client:** Unverändert, nur Broker wechseln

### **✅ 2. Realistische Tests:**
- **Echte MQTT-Nachrichten:** Kein Mock mehr
- **Original-Timing:** Realistische Nachrichtenfolgen
- **Vollständige Integration:** Alle Dashboard-Features

### **✅ 3. Flexibilität:**
- **Live-Modus:** Echte APS-Verbindung
- **Replay-Modus:** Session-Tests
- **Einfacher Wechsel:** Über Settings

## 📋 Implementierungs-Plan

### **✅ Phase 1: Replay-Station**
1. **LocalMQTTBroker** implementieren
2. **SessionPlayer** entwickeln
3. **Replay-Controller** erstellen

### **✅ Phase 2: Dashboard-Integration**
1. **Replay-Modus** in Settings hinzufügen
2. **Broker-Switching** implementieren
3. **Nachrichtenzentrale** testen

### **✅ Phase 3: Erweiterte Features**
1. **Speed-Control** (0.1x - 5x)
2. **Loop-Modus** (endlose Wiederholung)
3. **Filter-Replay** (nur bestimmte Topics)

## 🎮 Replay-Kontrollen

### **✅ Replay-Station UI:**
```python
# Streamlit-App für Replay-Kontrolle
- Session-Datei auswählen
- Play/Pause/Stop Buttons
- Speed-Slider (0.1x - 5x)
- Progress-Bar
- Loop-Checkbox
```

### **✅ Dashboard-Integration:**
```python
# Settings-Tab
- Replay-Modus Checkbox
- Status-Anzeige (Live/Replay)
- Broker-Information
```

## 📊 Technische Details

### **✅ Session-Format:**
- **SQLite-DB:** Strukturierte Nachrichten-Daten
- **Log-Dateien:** Text-basierte Nachrichten
- **JSON-Export:** Standardisiertes Format

### **✅ MQTT-Integration:**
- **Port 1884:** Dedizierter Replay-Port
- **Topic-Structure:** Identisch zu APS
- **Message-Format:** JSON-Payloads

### **✅ Performance:**
- **Memory-Efficient:** Streaming von Session-Daten
- **Real-time:** Minimale Latenz
- **Scalable:** Große Session-Dateien

## 🎯 Nächste Schritte

1. **Nachrichtenzentrale** im Dashboard implementieren
2. **OMF Replay Station** als separate Anwendung entwickeln
3. **Integration** zwischen beiden Systemen
4. **Testing** mit echten Session-Daten
