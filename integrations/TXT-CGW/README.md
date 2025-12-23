# TXT-CGW Integration

## 📋 Übersicht

**TXT-CGW** ist der Cloud Gateway TXT Controller im DPS-Modul.

## ⚠️ Wichtig: Nicht relevant für Fabrik-Prozesse

**Status:** ⚠️ **Dieser Controller ist für lokale Fabrik-Prozesse nicht relevant**

- **Funktion:** Transportiert MQTT-Topics in die Fischertechnik-Cloud
- **Verwendung:** Nur Cloud-Forwarding, keine lokale Fabrik-Steuerung
- **Analyse:** Nicht erforderlich für OSF-Integration

## 🔍 Komponenten-Details

### **Hardware**
- **IP-Adresse:** `192.168.0.102` (aktuell, DHCP-assigned)
- **Controller-ID:** `TXT4.0-WiY4`
- **Modul:** DPS (aber funktional getrennt)
- **Role:** Cloud Gateway

### **Software**
- **Source:** `FF_CGW` from TXT-Controller
- **Haupt-Script:** `FF_CGW.py`
- **Key Files:** `lib/RemoteGateway.py` - MQTT-Forwarding-Logik

## 📁 Projekt-Struktur

```
integrations/TXT-CGW/
└── workspaces/
    └── FF_CGW/
        ├── FF_CGW.py
        ├── lib/
        │   └── RemoteGateway.py
        └── data/
```

## 🔗 MQTT-Integration

- **Function:** Forwarding von MQTT-Topics zu Fischertechnik-Cloud
- **Lokale Verwendung:** Nicht relevant

## ⚠️ Hinweis

Dieser Controller wird im Configuration-Tab korrekt angezeigt (technisch richtig), ist aber **nicht für die Funktionalität der lokalen Fabrik-Prozesse erforderlich**. Für OSF-Integration und Analyse ist nur **TXT-DPS** relevant.

**Siehe:** [TXT-DPS README](../TXT-DPS/README.md) für den relevanten Controller.

