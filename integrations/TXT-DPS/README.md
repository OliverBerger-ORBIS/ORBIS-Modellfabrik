# TXT-DPS Integration

## 📋 Übersicht

**TXT-DPS** ist der Haupt-TXT-Controller für das DPS-Modul der APS Modellfabrik.

## 🔍 Komponenten-Details

### **Hardware**
- **IP-Adresse:** DHCP im FT-/Demo-LAN (vor Ort gemessen u. a. `192.168.0.186`; historisch oft `.101`)
- **Controller:** TXT4.0
- **Modul:** DPS (Delivery and Pickup Station) / DE: Warenein- und ausgang
- **Status:** ✅ Relevant für Fabrik-Prozesse (NFC, VGR, MQTT)

### **⚠️ Zwei TXT im DPS-Bereich**

1. **TXT-DPS** — ✅ relevant (dieses Verzeichnis)
2. **TXT-CGW** — Cloud Gateway, siehe `integrations/TXT-CGW/`

### **Software / Deployment**
- **Baseline:** `archives/FF_DPS_24V.ft`
- **OSF-Variante (NFC logische ID):** `archives/FF_DPS_24V_osf_nfc.ft`
- **Analyse:** `workspaces/FF_DPS_24V/` (u. a. `lib/VGR.py`)
- **How-To:** [TXT-Controller Deployment](../../docs/04-howto/txt-controller-deployment.md)

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

**Referenz:**
- **`docs/06-integrations/00-REFERENCE/`** - Zentrale DPS-relevante Dokumentation (archive/analysis/dps aufgelöst)

## 📁 Projekt-Struktur

```
integrations/TXT-DPS/
├── archives/                     # .ft für ROBO Pro (Startpunkt)
│   ├── FF_DPS_24V.ft             # Baseline (GitLab)
│   └── FF_DPS_24V_osf_nfc.ft     # OSF: logische workpieceId (B-soft)
├── workspaces/                   # Entpackt nur für Analyse
│   └── FF_DPS_24V/
│       └── lib/VGR.py            # u. a. handle_NFC, delivery_*
└── README.md
```

**Status (2026-07-17):**
- ✅ `archives/` mit Baseline + `_osf_nfc` (Blockly-Änderungen lokal; Deploy/Test vor Ort ausstehend)
- ✅ `workspaces/FF_DPS_24V/` Analyse-Spiegel

## 🚀 Nächste Schritte

1. Vor Ort: `FF_DPS_24V_osf_nfc.ft` deployen (How-To) + Wareneingang/Ausgang testen
2. Bei Erfolg: `.ft` committen, Sprint-26-NFC-Task abhaken

---

*Aktualisiert: 17.07.2026*
