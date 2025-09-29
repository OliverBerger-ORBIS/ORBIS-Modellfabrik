# Registry v2 - OMF Message Template System

## 📋 Übersicht

Die Registry v2 ist die **zentrale Konfiguration** für das OMF Message Template System. Sie enthält alle Templates, Mappings und Konfigurationen für MQTT-Kommunikation.

## 🏗️ Struktur

```
registry/model/v2/
├── modules.yml              # UI-Module (Dashboard-Anzeige)
├── stations.yml             # Physische Hardware-Stationen
├── txt_controllers.yml       # TXT-Controller Konfiguration
├── mqtt_clients.yml         # MQTT-Client Definitionen
├── topics/                  # Topic-Definitionen
│   ├── ccu.yml
│   ├── module.yml
│   ├── nodered.yml
│   ├── fts.yml
│   └── txt.yml
├── templates/               # Message-Templates
│   ├── module.*.yml
│   ├── ccu.*.yml
│   ├── txt.*.yml
│   └── fts.*.yml
└── mappings/
    └── topic_templates.yml  # Topic → Template Mappings
```

## 🎯 Prinzipien

### **Keine Redundanz**
- **Jede Information nur einmal** gespeichert
- **Klare Trennung** zwischen UI-Modulen und Hardware-Stationen
- **QoS/Retain** nur in `topics/` für MQTT-Konfiguration

### **Trennung der Verantwortlichkeiten**
- **`modules.yml`**: UI-Module für Dashboard-Anzeige
- **`stations.yml`**: Physische Hardware mit IP-Adressen
- **`txt_controllers.yml`**: TXT-Controller spezifisch
- **`mqtt_clients.yml`**: MQTT-Client Konfiguration (QoS/Retain nur zur Info)
- **`topics/`**: Topic-Definitionen mit QoS/Retain für MQTT-Konfiguration
- **`templates/`**: Message-Strukturen (ohne QoS/Retain)
- **`mappings/`**: Topic → Template Zuordnungen

## 📊 Verwendung

### **MessageTemplateGenerator**
```python
# 1. Topic auswählen
topic = "module/v1/ff/SVR3QA0022/state"

# 2. Template-Mapping finden
template_key = mappings.get_template_for_topic(topic)

# 3. Template laden
template = load_template(template_key)

# 4. Message generieren
message = generate_message(template, params)

# 5. QoS/Retain aus topics/ (nicht aus mqtt_clients.yml)
qos, retain = get_topic_config(topic)
```

### **Gateway-Integration**
```python
# Gateway nutzt Registry v2
gateway = CCUGateway()
gateway.send_message(topic, params)  # Nutzt Registry v2
```

## 🔧 Wartung

- **Templates**: Nur Message-Struktur, keine QoS/Retain
- **Topics**: QoS/Retain-Parameter für MQTT-Konfiguration
- **Mappings**: Topic → Template Zuordnungen
- **Clients**: MQTT-Client Konfiguration (QoS/Retain nur zur Info)

## 📝 Changelog

- **v2.0.0**: Registry v2 mit sauberer Trennung
- **QoS/Retain**: Aus Templates entfernt, nur in Topics/ für MQTT-Konfiguration
- **Redundanz**: Eliminiert zwischen modules.yml und stations.yml
