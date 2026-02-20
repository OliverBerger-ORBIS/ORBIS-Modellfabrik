# APS-Ecosystem - Phase 0 "as IS"

## 🎯 **Übersicht**

Dieser Ordner dokumentiert das **Fischertechnik APS-System im aktuellen Zustand** (Phase 0) - bevor OSF-Integration.

## 📁 **Struktur**

> 📖 **Zentrale Referenz:** [00-REFERENCE](../00-REFERENCE/README.md) - Verifizierte APS-Architektur als Single Source of Truth

- **[aps-system-overview.md](aps-system-overview.md)** - High-Level funktionale Beschreibung (Fischertechnik)
- **[system-overview.md](system-overview.md)** - Technische System-Architektur und MQTT-Kommunikation
- ~~[component-mapping.md](component-mapping.md)~~ - **Archiviert** → Siehe [Module Serial Mapping](../00-REFERENCE/module-serial-mapping.md)
- **[README.md](README.md)** - Diese Übersicht

## 🔗 **Verwandte Dokumentation**

### **Komponenten-spezifische Details:**
- **[Mosquitto Analysis](../../06-integrations/mosquitto/)** - MQTT-Broker Log-Analyse
- **[APS-NodeRED](../../06-integrations/APS-NodeRED/)** - Node-RED Flows und OPC-UA
- **[APS-CCU](../APS-CCU/README.md)** - Central Control Unit (Herz der Fabrik)
- **[TXT-Controller](../../06-integrations/TXT-*/)** - TXT-DPS, TXT-AIQS, TXT-FTS

### **Architektur-Prinzipien:**
- **[Architektur-Übersicht](../../02-architecture/README.md)** – OSF-Systemkontext
- **[APS Data Flow](../../02-architecture/aps-data-flow.md)** – MQTT-Kommunikation

## 🚀 **Phase 0 Ziele**

1. **APS-System verstehen** - Wie funktioniert das Fischertechnik-System?
2. **MQTT-Kommunikation analysieren** - Welche Topics, QoS, Patterns?
3. **Komponenten-Mapping** - Wer ist wer im System?
4. **UI-Interaktionen verstehen** - Wie reagiert das System auf User-Aktionen?

## 📊 **Aktuelle Erkenntnisse**

### **MQTT-Kommunikation:**
- **TXT-Controller** senden Connect + Will Messages
- **Node-RED** arbeitet mit Dual-Instanzen (SUB/PUB)
- **QoS-Patterns** sind konsistent (Commands: QoS 2, Sensor: QoS 1)
- **Factory Reset** löst automatisch `ccu/global` aus

### **Komponenten:**
- **Dashboard Frontend:** `mqttjs_bba12050` (172.18.0.5)
- **Node-RED (SUB):** `nodered_abe9e421b6fe3efd` (172.18.0.4)
- **Node-RED (PUB):** `nodered_94dca81c69366ec4` (172.18.0.4)
- **TXT-Controller:** `auto-*` (192.168.0.102-105)

## 🔄 **Nächste Schritte**

1. **System-Overview** mit MQTT-Diagrammen erstellen
2. **Component-Mapping** detailliert dokumentieren
3. **UI-Interaktions-Patterns** analysieren
4. **Vorbereitung für Phase 1** (OSF-Integration)

---

**"Phase 0: APS as IS - Verstehen bevor Integrieren"** 🎯
