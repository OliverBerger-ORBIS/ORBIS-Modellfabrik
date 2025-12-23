# TXT-DPS Integration

## 📋 Übersicht

**TXT-DPS** ist der Haupt-TXT-Controller für das DPS-Modul der APS Modellfabrik.

## 🔍 Komponenten-Details

### **Hardware**
- **IP-Adresse:** `192.168.0.101` (aktuell, DHCP-assigned)
- **Controller-ID:** `TXT4.0-p0F4`
- **Controller:** TXT4.0
- **Modul:** DPS (Delivery and Pickup Station)
- **Status:** ✅ **Relevant für Fabrik-Prozesse** (steuert DPS-Modul, liefert Sensordaten)

### **⚠️ Wichtig: Zwei TXT-Controller im DPS-Modul**

Im DPS-Modul (`SVR4H73275`) gibt es **zwei** TXT-Controller:

1. **TXT-DPS** (`192.168.0.101`, `TXT4.0-p0F4`) - ✅ **Relevant**
   - Steuert das DPS-Modul
   - Liefert Sensordaten (NFC-Reader, Sensoren)
   - MQTT-Integration für Fabrik-Prozesse
   - **Dieser Controller ist für die Analyse relevant**

2. **TXT-CGW** (`192.168.0.102`, `TXT4.0-WiY4`) - ⚠️ **Nicht relevant**
   - Cloud Gateway
   - Transportiert MQTT-Topics in Fischertechnik-Cloud
   - **Nicht relevant für lokale Fabrik-Prozesse**
   - Wird im Configuration-Tab korrekt angezeigt, aber nicht für Funktionalität benötigt

**Siehe auch:** `integrations/TXT-CGW/` für CGW-Sourcen (nur zur Vollständigkeit)

### **Software**
- **Haupt-Script:** `FF_DPS_24V.py` (5.96 KB) - Formatierte Version
- **Original-Sourcen:** `FF_DPS_24V/main.py` - Original vom Controller
- **Bibliotheken:** `FF_DPS_24V/lib/` - Alle lib/*.py Dateien vom Controller
- **Konfiguration:** `.project.json`, `data/` Verzeichnis

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

## 📁 Projekt-Struktur

```
integrations/TXT-DPS/
├── FF_DPS_24V/              # Original-Dateien vom Controller (komplett)
│   ├── main.py              # Original main.py vom Controller
│   └── lib/                 # Alle lib/*.py Dateien (wird vom Controller geladen)
│       ├── camera.py        # Kamera-Funktionalität
│       ├── DPS.py           # DPS-Modul-Logik
│       ├── mqtt_utils.py    # MQTT-Utilities
│       └── ...              # Weitere lib-Dateien
├── FF_DPS_24V.py            # Formatierte/refactorierte Version (optional)
├── FF_DPS_24V.blockly       # Blockly-Datei
├── data/                    # Konfigurationen
│   ├── config.json
│   ├── factsheet.json
│   └── robot_config.json
├── .project.json            # Projekt-Metadaten
└── README.md                # Diese Datei
```

**Status (2025-12-22):**
- ✅ `FF_DPS_24V/main.py` vorhanden (Original vom Controller)
- 🔄 `FF_DPS_24V/lib/` - In Arbeit (2 von ~30 Dateien bereits vorhanden)
  - ✅ `DPS.py` - DPS-Modul-Logik
  - ✅ `Factory.py` - Factory-Funktionen
  - ⏳ Weitere lib-Dateien werden nach und nach geladen
  - 📋 Siehe `FF_DPS_24V/lib/README.md` für vollständige Liste
- ✅ `data/` Konfigurationen vorhanden

## 🚀 Nächste Schritte

1. **Vollständige Sourcen laden** - `lib/` Verzeichnis vom Controller via Web-Interface/SSH holen
2. **Browser-Interface erkunden** - `http://192.168.0.102` für HTTP-Endpoint-Ermittlung
3. **Dateien analysieren** - Code und Konfiguration (insbesondere `lib/camera.py` für HTTP-Endpoints)
4. **Integration testen** - Mit OSF-Dashboard

---

*Erstellt: 23. September 2025*  
*Aktualisiert: 22. Dezember 2025*  
*Status: Vorbereitung - Bereit für Analyse mit vollständigen Sourcen*
