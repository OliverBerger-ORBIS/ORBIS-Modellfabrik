# OMF Message Template Definition

## **📋 Was ist ein Template?**

### **✅ Korrekte Definition:**
Ein **Template** ist eine **Message-Struktur-Definition** die Syntax und Semantik einer MQTT-Nachricht definiert.

### **❌ Falsche Definition:**
Ein Template ist **NICHT** eine Beispiel-Nachricht oder eine generierte Instanz.

## **🔧 Template-Komponenten:**

### **1. SYNTAX (Struktur)**
```yaml
structure:
  required_fields: ["module_id", "connected", "timestamp"]
  optional_fields: ["ip", "serialNumber", "version"]
  
  field_definitions:
    module_id:
      type: "string"
      pattern: "enum"
      description: "Serial Number des Moduls"
```

### **2. SEMANTICS (Validierung)**
```yaml
validation_rules:
  - "timestamp muss ISO 8601 Format haben"
  - "module_id muss gültige Serial Number sein"
  - "connected muss boolean sein"
```

### **3. VARIABLE FIELDS (Enum-Werte)**
```yaml
variable_fields:
  module_id:
    type: "enum"
    values: ["SVR3QA0022", "SVR4H76449", "SVR3QA2098"]
```

### **4. MQTT INTEGRATION**
```yaml
mqtt:
  topic_pattern: "module/v1/ff/{module_id}/connection"
  direction: "bidirectional"
  qos: 1
```

## **📦 Unterschied: Template vs. Beispiel-Nachricht**

### **📋 Template (Message-Struktur-Definition):**
```yaml
template:
  name: "module/connection"
  structure:
    required_fields: ["module_id", "connected", "timestamp"]
  validation_rules:
    - "timestamp muss ISO 8601 Format haben"
  variable_fields:
    module_id:
      values: ["SVR3QA0022", "SVR4H76449", ...]
```

### **📦 Beispiel-Nachricht (Generated Message):**
```json
{
  "module_id": "SVR3QA0022",
  "connected": true,
  "ip": "192.168.0.80",
  "timestamp": "2025-08-29T10:00:00Z"
}
```

## **🎯 Verwendung im MessageGenerator:**

### **1. Template laden:**
```python
template = load_template("module/connection")
```

### **2. Parameter validieren:**
```python
validate_parameters(template, {"module_id": "SVR3QA0022"})
```

### **3. Nachricht generieren:**
```python
topic, payload = generate_message(template, module_id="SVR3QA0022")
```

## **📁 Datei-Struktur:**

```
message_templates/
├── templates/
│   ├── module/
│   │   ├── connection_template.yml    # Template (Struktur-Definition)
│   │   └── connection_generated.yml   # Generierte Beispiele (nicht Template!)
│   ├── ccu/
│   │   └── control_template.yml       # Template
│   └── txt/
│       └── order_input_template.yml   # Template
└── TEMPLATE_DEFINITION.md             # Diese Dokumentation
```

## **🔍 Template-Typen:**

### **1. Module Templates:**
- `module/connection` - Verbindungsstatus
- `module/state` - Modul-Zustand
- `module/order` - Modul-Befehle
- `module/factsheet` - Modul-Konfiguration

### **2. CCU Templates:**
- `ccu/control` - CCU-Befehle
- `ccu/state/config` - CCU-Konfiguration
- `ccu/state/status` - CCU-Status

### **3. TXT Templates:**
- `txt/order_input` - Auftragseingang
- `txt/stock_input` - Lagerbestand
- `txt/sensor_control` - Sensor-Steuerung

### **4. Node-RED Templates:**
- `node_red/dashboard_state` - Dashboard-Status

## **✅ Zusammenfassung:**

- **Template = Blaupause** für Nachrichten-Generierung
- **Template = Schema** mit Validierungsregeln
- **Template = Struktur-Definition** (nicht Beispiel!)
- **MessageGenerator** verwendet Templates um konkrete Nachrichten zu generieren
