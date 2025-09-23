# TXT-DPS Integration

## 📋 Übersicht

**TXT-DPS** ist der DPS TXT Controller der APS Modellfabrik.

## 🔍 Komponenten-Details

### **Hardware**
- **IP-Adresse:** DHCP-vergeben (nicht fix)
- **Controller:** TXT4.0
- **Modul:** DPS (Delivery and Pickup Station)
- **Controller-ID:** Bekannt (nicht IP-abhängig)

### **Software**
- **Haupt-Script:** `FF_DPS_24V.py` (5.96 KB)
- **Konfiguration:** `.project.json`
- **Bibliotheken:** `lib/` Verzeichnis
- **Daten:** `data/` Verzeichnis

## 🔗 MQTT-Integration

### **VDA5050 Standard**
- **Namespace:** `module/v1/ff/NodeRed/{controller_id}/`
- **Topics:** State, Order, InstantAction, Connection, Factsheet
- **QoS:** 2 (Reliable delivery)

### **Sensor-Daten**
- **BME680:** Environmental sensor
- **LDR:** Light sensor
- **Camera:** Image processing
- **Broadcast:** System-wide messages

## 📚 Dokumentation

**Archivierte Analyse:**
- **`docs/archive/analysis/dps/FF_DPS_24V_ANALYSIS.md`** - Vollständige Analyse
- **`docs/archive/analysis/dps/DPS_ANALYSIS_PLAN.md`** - Analyse-Plan

## 🚀 Nächste Schritte

1. **Browser-Interface erkunden** - `http://192.168.0.102`
2. **Dateien analysieren** - Code und Konfiguration
3. **Integration testen** - Mit OMF-Dashboard

---

*Erstellt: 23. September 2025*  
*Status: Vorbereitung - Bereit für Integration*
