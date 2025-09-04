# Overview Modul-Status Fix - Januar 2025

## 🎯 **Problem gelöst**

Das **Overview Modul-Status** zeigte **falsche Availability-Status** und **Connection-Informationen** an, da es die **falschen MQTT-Topics** verwendete.

## ❌ **Vorher (Problem):**

### **Falsche Topics:**
- `module/v1/ff/{module_id}/connection` → **nur Connection-Status**
- `module/v1/ff/{module_id}/state` → **nur Module-State**

### **Falsche Availability-Logik:**
- Suchte nach `"available"`, `"busy"`, `"blocked"` in falschen Topics
- Zeigte **statische IP-Adressen** aus Konfiguration
- **Keine echten Availability-Werte** verfügbar

## ✅ **Nachher (Lösung):**

### **Korrekte Topics:**
- `ccu/pairing/state` → **komplette Modul-Informationen**

### **Korrekte Availability-Logik:**
- `"available": "READY"` → 🟢 Verfügbar
- `"available": "BUSY"` → 🟡 Beschäftigt  
- `"available": "BLOCKED"` → 🔴 Blockiert

### **Echte Daten:**
- **Dynamische IP-Adressen** aus MQTT-Nachrichten
- **Connection-Status:** `true`/`false` statt `ONLINE`/`OFFLINE`
- **Vollständige Modul-Informationen:** Version, Kalibrierung, etc.

## 🔧 **Implementierte Änderungen:**

### **1. Topic-Config erweitert (`topic_config.yml`):**
```yaml
"ccu/pairing/state":
  category: "CCU"
  sub_category: "State"
  friendly_name: "CCU : pairing : state"
  description: "Modul-Pairing-Status mit Availability, Connection und IP-Adressen"
  template: "ccu/state"
  template_direction: "inbound"
```

### **2. Topic-Message-Mapping erweitert (`topic_message_mapping.yml`):**
```yaml
"ccu/pairing/state":
  template: "ccu/state"
  direction: "inbound"
  description: "Modul-Pairing-Status mit Availability, Connection und IP-Adressen empfangen"
  semantic_purpose: "Modul-Verfügbarkeit und Verbindungsstatus überwachen"
```

### **3. Overview Module Status korrigiert (`overview_module_status.py`):**

#### **Neue Topic-Pattern:**
```python
pairing_pattern = re.compile(r"^ccu/pairing/state$")
```

#### **Korrekte Availability-Logik:**
```python
available = real_time_status.get("available", "Unknown")
if available == "READY":
    availability_display = f"{get_status_icon('available')} Verfügbar"
elif available == "BUSY":
    availability_display = f"{get_status_icon('busy')} Beschäftigt"
elif available == "BLOCKED":
    availability_display = f"{get_status_icon('blocked')} Blockiert"
```

#### **Echte IP-Adressen:**
```python
ip_address = real_time_status.get("ip", module_info.get("ip_range", "Unknown"))
```

#### **MQTT-Subscribe:**
```python
mqtt_client.subscribe("ccu/pairing/state", qos=1)
```

### **4. Message-Template erweitert (`ccu/state.yml`):**

#### **BUSY/BLOCKED Beispiele hinzugefügt:**
```yaml
- modules:
  - assigned: true
    available: BUSY
    connected: true
    # ... weitere Felder
  - assigned: false
    available: BLOCKED
    connected: true
    # ... weitere Felder
```

#### **Vollständige Template-Struktur:**
```yaml
template_structure:
  modules:
    type: array
    items:
      properties:
        available:
          enum: ["READY", "BUSY", "BLOCKED"]
          description: "Verfügbarkeitsstatus des Moduls"
        connected:
          type: boolean
          description: "Verbindungsstatus zum Modul"
        # ... alle weiteren Felder
```

#### **Validation-Rules:**
```yaml
validation_rules:
- "available muss in [READY, BUSY, BLOCKED] sein"
- "connected muss boolean sein"
- "assigned muss boolean sein"
- "ip muss gültige IPv4-Adresse sein"
```

## 📊 **Verfügbare Modul-Daten aus ccu/pairing/state:**

### **Module:**
- `serialNumber`: Eindeutige Seriennummer
- `type`: "MODULE"
- `connected`: `true`/`false`
- `available`: "READY"|"BUSY"|"BLOCKED"
- `assigned`: `true`/`false`
- `subType`: "HBW"|"DRILL"|"MILL"|"DPS"|"AIQS"|"CHRG"
- `ip`: IPv4-Adresse
- `version`: Firmware-Version
- `hasCalibration`: `true`/`false`
- `lastSeen`: ISO 8601 Timestamp
- `pairedSince`: ISO 8601 Timestamp
- `productionDuration`: Sekunden (nur Produktionsmodule)

### **Transports (FTS):**
- `serialNumber`: Eindeutige Seriennummer
- `type`: "FTS"
- `connected`: `true`/`false`
- `available`: "READY"|"BUSY"|"BLOCKED"
- `ip`: IPv4-Adresse
- `version`: Firmware-Version
- `batteryPercentage`: 0-100
- `batteryVoltage`: 0-15 Volt
- `charging`: `true`/`false`
- `lastSeen`: ISO 8601 Timestamp
- `pairedSince`: ISO 8601 Timestamp
- `lastLoadPosition`: Letzte Lade-Position
- `lastModuleSerialNumber`: Zuletzt transportiertes Modul
- `lastNodeId`: Letzte Node-ID

## 🎯 **Ergebnis:**

**Overview Modul-Status** zeigt jetzt **korrekte, echte Daten** aus den **MQTT-Nachrichten** an:

- ✅ **Availability-Status:** READY, BUSY, BLOCKED
- ✅ **Connection-Status:** Echte Verbindungsdaten
- ✅ **IP-Adressen:** Dynamische IPs aus MQTT
- ✅ **Modul-Informationen:** Vollständige Daten
- ✅ **Real-time Updates:** Automatische Aktualisierung

## 📅 **Datum:** 2025-01-XX
## 👤 **Implementiert von:** AI Assistant
## 🔗 **Verwandte Dateien:**
- `src_orbis/omf/dashboard/components/overview_module_status.py`
- `src_orbis/omf/config/topic_config.yml`
- `src_orbis/omf/config/topic_message_mapping.yml`
- `src_orbis/omf/config/message_templates/templates/ccu/state.yml`
