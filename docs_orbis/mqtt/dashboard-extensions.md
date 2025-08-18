# 🎮 APS Dashboard Extensions - Serial Numbers & MQTT Control

## 📋 Overview

Das **APS Dashboard** wurde erfolgreich erweitert um:
1. **Serial Numbers der Module** in allen Ansichten anzuzeigen
2. **MQTT Control Interface** für direkte Modul-Steuerung
3. **Funktionierende MQTT-Nachrichten** aus der Bibliothek

## ✅ Neue Features

### 1. **Serial Numbers Integration**

#### **Message Table**
- **Neue Spalte**: `serial_number` zeigt die echte Serial-ID des Moduls
- **Beispiel**: `MILL (SVR3QA2098)`, `DRILL (SVR4H76449)`
- **Automatische Extraktion** aus MQTT-Topics

#### **Module Detection**
```python
# Automatische Serial-Number-Extraktion
if 'svr3qa0022' in topic_lower:
    return 'HBW', 'SVR3QA0022'
elif 'svr4h73275' in topic_lower:
    return 'DPS', 'SVR4H73275'
# ... weitere Module
```

### 2. **MQTT Control Tab**

#### **Neuer Tab**: "🎮 MQTT Control"
- **Modul-Übersicht** mit Serial Numbers
- **Template-basierte Steuerung**
- **Benutzerdefinierte Befehle**
- **Detaillierte Modul-Informationen**

## 🏭 Module Overview

### **Verfügbare Module mit Serial Numbers:**

| Modul | Serial Number | IP Address | Working Commands |
|-------|---------------|------------|------------------|
| **MILL** | `SVR3QA2098` | `192.168.0.40` | `PICK`, `DROP` |
| **DRILL** | `SVR4H76449` | `192.168.0.50` | `PICK`, `DROP` |
| **AIQS** | `SVR4H76530` | `192.168.0.70` | `PICK`, `DROP`, `CHECK_QUALITY` |
| **HBW** | `SVR3QA0022` | `192.168.0.80` | `PICK`, `DROP`, `STORE` |
| **DPS** | `SVR4H73275` | `192.168.0.90` | `PICK`, `DROP` |

## 🎮 MQTT Control Interface

### **1. Template Message Control**

#### **Verfügbare Templates:**
- `DRILL_PICK_WHITE` - DRILL PICK für WHITE Workpiece
- `MILL_PICK_WHITE` - MILL PICK für WHITE Workpiece
- `HBW_STORE_WHITE` - HBW STORE für WHITE Workpiece
- `AIQS_CHECK_QUALITY_WHITE` - AIQS CHECK_QUALITY für WHITE Workpiece

#### **Template Details:**
- **Modul**: Automatisch erkannt
- **Befehl**: Vordefiniert
- **Beschreibung**: Detaillierte Erklärung
- **Erwartete Antwort**: `RUNNING` oder `FINISHED`
- **Notizen**: Test-Ergebnisse und Hinweise

#### **MQTT Message Preview:**
```json
{
  "serialNumber": "SVR4H76449",
  "orderId": "993e21ec-88b5-4e50-a478-a3f64a43097b",
  "orderUpdateId": 1,
  "action": {
    "id": "5f5f2fe2-1bdd-4f0e-84c6-33c44d75f07e",
    "command": "PICK",
    "metadata": {
      "priority": "NORMAL",
      "timeout": 300,
      "type": "WHITE"
    }
  }
}
```

### **2. Custom Order Control**

#### **Modul-Auswahl:**
- Dropdown mit allen verfügbaren Modulen
- **Serial Number** wird automatisch angezeigt
- **IP-Adresse** wird angezeigt
- **Verfügbare Befehle** werden gelistet

#### **Befehl-Konfiguration:**
- **Befehl-Auswahl**: Nur funktionierende Befehle
- **Workpiece Type**: WHITE, BLUE, RED
- **Priority**: NORMAL, HIGH, LOW
- **Timeout**: 60-600 Sekunden (Slider)

#### **Live Message Preview:**
- **JSON-Format** wird live generiert
- **Validierung** der Parameter
- **Send-Button** für sofortigen Versand

### **3. Module Overview**

#### **Detaillierte Modul-Informationen:**
- **Serial Number**: Echte Module-ID
- **IP Address**: Netzwerk-Adresse
- **Working Commands**: Anzahl verfügbarer Befehle
- **Schnell-Befehle**: Direkte Buttons für jeden Befehl

#### **Expandable Sections:**
- Jedes Modul in einem **Expandable Panel**
- **Modul-Informationen** und **Verfügbare Befehle**
- **Schnell-Befehle** für direkten Zugriff

## 🔧 Technische Implementation

### **1. Serial Number Extraction**

```python
def extract_module_from_topic(topic):
    topic_lower = topic.lower()
    
    # Module patterns in topics - more specific patterns first
    if 'svr3qa0022' in topic_lower:
        return 'HBW', 'SVR3QA0022'
    elif 'svr4h73275' in topic_lower:
        return 'DPS', 'SVR4H73275'
    # ... weitere Module
```

### **2. MQTT Message Library Integration**

```python
# Import message library
from mqtt_message_library import MQTTMessageLibrary, create_message_from_template

# Initialize library
self.message_library = MQTTMessageLibrary()

# Create working message
message = self.message_library.create_order_message("DRILL", "PICK")
```

### **3. Dashboard Tab Structure**

```python
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📊 Übersicht", "⏰ Timeline", "📋 Nachrichten", 
    "📡 Topics", "📊 Status", "📦 Payload", "🏷️ Sessions", "🎮 MQTT Control"
])
```

## 📊 Enhanced Data Display

### **Message Table Columns:**
1. **timestamp** - Zeitstempel der Nachricht
2. **topic** - MQTT Topic
3. **module_type** - Modul-Typ (MILL, DRILL, etc.)
4. **serial_number** - **NEU**: Serial Number des Moduls
5. **status** - Status der Nachricht
6. **process_label** - Prozess-Label
7. **session_label** - Session-Label

### **Serial Number Examples:**
- `module/v1/ff/SVR4H76449/order` → `DRILL (SVR4H76449)`
- `module/v1/ff/SVR3QA2098/state` → `MILL (SVR3QA2098)`
- `module/v1/ff/SVR3QA0022/connection` → `HBW (SVR3QA0022)`

## 🚀 Usage Examples

### **1. Template Message Senden**
1. **Tab öffnen**: "🎮 MQTT Control"
2. **Methode wählen**: "Template Message"
3. **Template auswählen**: `DRILL_PICK_WHITE`
4. **Details prüfen**: Modul, Befehl, Beschreibung
5. **Message senden**: Button klicken

### **2. Custom Order Erstellen**
1. **Methode wählen**: "Custom Order"
2. **Modul auswählen**: DRILL
3. **Befehl wählen**: PICK
4. **Metadaten konfigurieren**: Type, Priority, Timeout
5. **Message senden**: Button klicken

### **3. Module Overview Nutzen**
1. **Methode wählen**: "Module Overview"
2. **Modul expandieren**: DRILL (SVR4H76449)
3. **Schnell-Befehl wählen**: PICK Button
4. **Bestätigung**: Message wird gesendet

## 📝 Important Notes

### **1. MQTT Versand (Placeholder)**
- **Aktuell**: Placeholder-Implementation
- **Zukünftig**: Direkte MQTT-Verbindung
- **Workaround**: Verwendung der Command-Line-Tools

### **2. Template Verfügbarkeit**
- **Alle Templates**: Aus der MQTT Message Library
- **Validierung**: Nur funktionierende Nachrichten
- **Erweiterung**: Neue Templates können hinzugefügt werden

### **3. Serial Number Accuracy**
- **Automatische Erkennung**: Aus MQTT-Topics
- **Fallback**: "unknown" für nicht erkannte Module
- **Manuelle Korrektur**: Über die Bibliothek möglich

## 🔄 Future Enhancements

### **1. Direkte MQTT-Verbindung**
- **Real-time Versand**: Direkt aus dem Dashboard
- **Status-Monitoring**: Live-Feedback von Modulen
- **Error Handling**: Automatische Fehlerbehandlung

### **2. Erweiterte Templates**
- **Sequenz-Templates**: Mehrere Befehle in Folge
- **Conditional Templates**: Bedingte Ausführung
- **Custom Templates**: Benutzerdefinierte Templates

### **3. Advanced Monitoring**
- **Live Status**: Echtzeit-Modul-Status
- **Performance Metrics**: Ausführungszeiten
- **Error Tracking**: Fehlerprotokollierung

## 📄 Files

### **Modified Files:**
- **`aps_dashboard.py`**: Haupt-Dashboard mit Erweiterungen
- **`mqtt_message_library.py`**: Importierte Bibliothek

### **New Features:**
- **Serial Number Display**: In allen Tabellen
- **MQTT Control Tab**: Neuer Steuerungs-Tab
- **Template Integration**: Vordefinierte Nachrichten
- **Custom Order Interface**: Benutzerdefinierte Befehle

---

**Status**: ✅ **COMPLETED** - Dashboard erfolgreich erweitert mit Serial Numbers und MQTT Control
